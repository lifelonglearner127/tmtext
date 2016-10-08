# -*- coding: utf-8 -*-

import json
import urlparse
import re
from itertools import ifilter
from decimal import Decimal, InvalidOperation
import string

from scrapy.http import Request

from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import cond_replace, cond_replace_value
from product_ranking.spiders import cond_set_value, cond_set
from contrib.product_spider import ProductsSpider
from product_ranking.items import Price, BuyerReviews
from product_ranking.guess_brand import guess_brand_from_first_words


SYM_GBP = '£'


def unify_decimal(ignored, float_dots):
    """ Create a function to convert various floating point textual
    representations to it's equivalent that can be converted to float directly.

    Usage:
       unify_float([ignored, float_dots])(string_:str) -> string

    Arguments:
       ignored - list of symbols to be removed from string
       float_dots - decimal/real parts separator

    Raises:
       `ValueError` - resulting string cannot be converted to float.
    """

    def unify_float_wr(string_):
        try:
            result = ''.join(['.' if c in float_dots else c for c in
                              string_ if c not in ignored])
            return str(Decimal(result))
        except InvalidOperation:
            raise ValueError('Cannot convert to decimal')

    return unify_float_wr


def unify_price(currency_codes, currency_signs, unify_decimal,
                default_currency=None):
    """Convert textual price representation to `Price` object.

    Usage:
       unify_price(currency_codes, currency_signs, unify_float,
       [default_currency])(string_) -> Price

    Arguments:
       currency_codes - list of possible currency codes (like ['EUR', 'USD'])
       currency_signs - dictionary to convert substrings to currency codes
       unify_decimal - function to convert price part into decimal
       default_currency - default currency code

    Raises:
       `ValueError` - no currency code found and default_curreny is None.
    """

    def unify_price_wr(string_):
        string_ = string_.strip()
        sorted_ = sorted(currency_signs.keys(), None, len, True)
        sign = next(ifilter(string_.startswith, sorted_), '')
        string_ = currency_signs.get(sign, '') + string_[len(sign):]
        sorted_ = sorted(currency_codes, None, len, True)
        currency = next(ifilter(string_.startswith, sorted_), None)

        if currency is None:
            currency = default_currency
        else:
            string_ = string_[len(currency):]

        if currency is None:
            raise ValueError('Could not get currency code')

        float_string = unify_decimal(string_.strip())

        return Price(currency, float_string)

    return unify_price_wr


class SainsburysProductSpider(ProductsSpider):
    """ sainsburys.co.uk product ranking spider

    Spider takes `order` argument.

    Allowed sorting orders are:

    * `relevance`: relevance. This is default.
    * `price_asc`: price per unit (ascending).
    * `price_desc`: price per unit (descending).
    * `name_asc`: product title (ascending).
    * `name_desc`: product title (descending).
    * `best`: best sellers first.
    * `rating`: average user rating (descending).

    There are following caveats:

    * if price per unit is not found, the spider will try other pricing
      variants.
    * `brand` might not be scraped for some products, or scraped incorrectly,
       but this is very unlikely.
    * `model`, `is_out_of_stock`, `is_in_store_only` and `upc` fields are not
       scraped
    """

    name = "sainsburys_uk_products"

    allowed_domains = [
        "sainsburys.co.uk",
        "sainsburysgrocery.ugc.bazaarvoice.com"
    ]

    SEARCH_URL = "http://www.sainsburys.co.uk/" \
                 "webapp/wcs/stores/servlet/SearchDisplayView" \
                 "?catalogId=10122&langId=44&storeId=10151" \
                 "&categoryId=&parent_category_rn=&top_category=" \
                 "&pageSize=30&orderBy={sort_mode}" \
                 "&searchTerm={search_term}" \
                 "&beginIndex=0&categoryFacetId1="

    SORT_MODES = {
        'default': 'RELEVANCE',
        'relevance': 'RELEVANCE',
        'price_asc': 'PRICE_ASC',
        'price_desc': 'PRICE_DESC',
        'name_asc': 'NAME_ASC',
        'name_desc': 'NAME_DESC',
        'best': 'TOP_SELLERS',
        'rating': 'RATINGS_DESC'
    }

    OPTIONAL_REQUESTS = {'reviews': True}

    ROOT_REVS_URL = "http://sainsburysgrocery.ugc.bazaarvoice.com/"\
                    "{code}/{prod_id}/reviews.djs?format=embeddedhtml"

    HARDCODED_FIELDS = {'locale': 'en_GB'}

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse(self, response):
        if '/groceries/' in response.url:
            if 'orderBy' not in response.url:
                sorted_url = response.url + '?orderBy=' + self.sort_mode
                return Request(sorted_url, callback=self.parse,
                               meta=response.meta.copy())
        return super(SainsburysProductSpider, self).parse(response)

    def _total_matches_from_html(self, response):
        text = response.xpath(
            '//div[@class="section"]/h1[@id="resultsHeading"]/text()'
        ).extract()
        if text:
            matches = re.findall(r'(\d+)\sproduct', text[0])
            if matches:
                matches = matches[0]
        else:
            try:
                text = response.css('#resultsHeading::text').extract()[0]
                matches = re.search('We found (\d+)', text).group(1)
            except (IndexError, AttributeError):
                matches = 0
        return int(matches)

    def _scrape_next_results_page_link(self, response):
        link = response.css('.next a::attr(href)')
        return link.extract()[0] if link else None

    def _fetch_product_boxes(self, response):
        # Collect brand names before scraping products
        if 'brands' not in response.meta:
            css = 'label[for*=topBrands]::text'
            response.meta['brands'] = response.css(css).extract()

        return response.css('.product')

    def _link_from_box(self, box):
        url = box.css('.productInfo h3 a::attr(href)').extract()[0]
        return url

    def _populate_from_box(self, response, box, product):
        cond_set(product, 'title',
                 box.css('.productInfo h3 a::text').extract(),
                 unicode.strip)
        cond_set(product, 'price', box.css('.pricePerUnit::text').extract(),
                 unicode.strip)
        cond_set(product, 'price',
                 box.css('.pricing [class*=pricePer]').extract(),
                 unicode.strip)
        cond_set(product, 'image_url',
                 box.css('.productInfo h3 a img::attr(src)').extract(),
                 lambda url: urlparse.urljoin(response.url, url))

        # Try to find brand name in a title
        brands = response.meta.get('brands', [])
        brand = next((brand for brand in brands
                      if product.get('title', '').find(brand) == 0), None)
        cond_set_value(product, 'brand', brand)

    def _populate_from_html(self, response, product):
        cond_set(product, 'title',
                 response.css('.productSummary h1::text').extract())
        cond_set(product, 'price',
                 response.css('.pricePerUnit::text').extract(),
                 unicode.strip)
        cond_set(product, 'price',
                 response.css('.pricing [class*=pricePer]').extract(),
                 unicode.strip)
        xpath = '//*[@id="information"]' \
                '/node()[not(@class="access")][normalize-space()]'
        cond_set_value(product, 'description', response.xpath(xpath).extract(),
                       ''.join)
        cond_replace(product, 'image_url',
                     response.css('#productImageHolder img::attr(src)')
                     .extract(),
                     lambda url: urlparse.urljoin(response.url, url))

        reseller_id = response.xpath('.//*[@class="skuCode"]/text()').extract()
        cond_set(product, 'reseller_id', reseller_id, string.strip)

        title = product['title']
        brand = guess_brand_from_first_words(title, max_words=15)
        cond_set_value(product, 'brand', brand)
        self._unify_price(product)

        if not product.get("locale"):
            product["locale"] = "en_GB"

    def _unify_price(self, product):
        price = product['price'].encode('utf-8')
        price = unify_price(['GBP'], {SYM_GBP: 'GBP'},
                            unify_decimal(', ', '.'), 'GBP')(price)
        cond_replace_value(product, 'price', price)

    def _request_reviews(self, response):
        prod_id = re.findall(r"productId:\s'(.*)',", response.body)
        display_code = re.findall(r"displayCode:\s'(.*)',", response.body)
        if prod_id and display_code:
            url = self.ROOT_REVS_URL.format(code=display_code[0],
                                            prod_id=prod_id[0])
            return url
        return

    def _parse_reviews(self, response):
        res = re.findall(r'"attributes":(.*),"ciTrackingEnabled"',
                         response.body)
        if res:
            data = json.loads(res[0])
            avg = data['avgRating']
            avg = float(avg)
            total = data['numReviews']
            total = int(total)
        stars = {}
        materials = re.findall(r'materials=(.*),', response.body)
        if materials:
            data = json.loads(materials[0])
            all_revs = response.meta.get('all_revs', [])
            pattern = r'itemprop="ratingValue" class="BVRRNumber'\
                ' BVRRRatingNumber">(\d+)<'
            results = re.findall(pattern, data[data.keys()[0]])
            all_revs.extend(results)
            for number in range(1, 6):
                pattern = str(number)
                quantity = all_revs.count(pattern)
                stars[number] = quantity
        # Buyer reviews populated on page by 8, 9-38, 39-68..
        if total > 8:
            counter = (total-9) / 30
            page_counter = counter + 2
            meta = response.meta.copy()
            page_populated = 2
            if not response.meta.get('page_populated'):
                meta['page_populated'] = page_populated
            else:
                page_populated = int(response.meta['page_populated']) + 1
                meta['page_populated'] = page_populated

            initial_url = response.meta.get('initial_url')
            if not initial_url:
                initial_url = response.url
                meta['initial_url'] = initial_url
            if page_populated <= page_counter:
                meta['all_revs'] = all_revs
                next_page_url_part = "&page=%s" % page_populated
                next_page = initial_url + next_page_url_part
                return Request(next_page, callback=self._parse_reviews,
                               meta=meta)

        product = response.meta['product']
        cond_set_value(product, 'buyer_reviews',
                       BuyerReviews(total, avg, stars)
                       if total else ZERO_REVIEWS_VALUE)
