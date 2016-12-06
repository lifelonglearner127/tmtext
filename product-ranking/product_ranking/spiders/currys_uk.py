# -*- coding: utf-8 -*-

import re
import urlparse
from itertools import ifilter
from decimal import Decimal, InvalidOperation

from scrapy import Request

from product_ranking.items import SiteProductItem
from product_ranking.items import valid_currency_codes
from product_ranking.spiders import cond_set, cond_set_value, \
    _populate_from_open_graph_product, cond_replace_value, dump_url_to_file
from product_ranking.spiders.contrib.contrib import populate_reviews
from product_ranking.spiders.contrib.product_spider import ProductsSpider
from product_ranking.items import Price


SYM_USD = '$'
SYM_GBP = '£'
SYM_CRC = '₡'
SYM_EUR = '€'
SYM_JPY = '¥'

CURRENCY_SIGNS = {
    SYM_USD: 'USD',
    SYM_GBP: 'GBP',
    SYM_CRC: 'CRC',
    SYM_EUR: 'EUR',
    SYM_JPY: 'JPY'
}


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


# TODO: related_products


class CurrysUkProductsSpider(ProductsSpider):
    """ currys.co.uk product ranking spider

    Spider takes `order` argument with possible sorting modes:

    * `relevance` (default)
    * `brand_asc`, `brand_desc`
    * `price_asc`, `price_desc`
    * `rating`

    Following fields are not scraped:

    * `model`, `upc`, `related_products`, `buyer_reviews`
    """

    name = 'currys_uk_products'

    allowed_domains = [
        'currys.co.uk'
    ]

    SEARCH_URL = "http://www.currys.co.uk/gbuk/search-keywords" \
                 "/xx_xx_xx_xx_xx/{search_term}/1_20" \
                 "/{sort_mode}/xx-criteria.html"

    SORT_MODES = {
        'default': 'relevance-desc',
        'relevance': 'relevance-desc',
        'brand_asc': 'brand-asc',
        'brand_desc': 'brand-desc',
        'price_asc': 'price-asc',
        'price_desc': 'price-desc',
        'rating': 'rating-desc'
    }

    REVIEWS_URL = "http://mark.reevoo.com/reevoomark/en-GB/" \
                  "product?sku=%s&trkref=CYS"

    HARDCODED_FIELDS = {
        'locale': 'en-GB'
    }

    OPTIONAL_REQUESTS = {
        'buyer_reviews': True
    }

    def start_requests(self):
        for req in super(CurrysUkProductsSpider, self).start_requests():
            req.meta.update({'dont_redirect': True,
                             'handle_httpstatus_list': [302]})
            yield req

    def parse(self, response):
        if response.status == 302:
            location = response.headers['Location']
            request = Request(urlparse.urljoin(response.url, location),
                              meta=response.meta, dont_filter=True)
            yield request
        else:
            for item in super(CurrysUkProductsSpider, self).parse(response):
                yield item


    def _total_matches_from_html(self, response):
        if self._is_product_page(response):
            return 1
        matches = response.css('.row.nosp strong::text')
        if len(matches) < 2:
            return 0
        matches = matches[1].extract()
        matches = re.search('1 - \d+ of (\d+) results', matches)
        return int(matches.group(1)) if matches else 0

    def _scrape_next_results_page_link(self, response):
        url = response.css('.pagination .next::attr(href)')
        return url[0].extract() if url else None

    def _is_product_page(self, response):
        return response.css('[property="og:type"][content=product]')

    def _scrape_product_links(self, response):
        if self._is_product_page(response):
            product = SiteProductItem()
            url = response.url
            response.meta['product'] = product
            request = Request(url, self.parse_product, meta=response.meta,
                              errback=self._handle_product_page_error,
                              dont_filter=True)
            yield request, product
        else:
            items = super(
                CurrysUkProductsSpider, self
            )._scrape_product_links(response)
            for item in items:
                yield item

    def _fetch_product_boxes(self, response):
        return response.css('article.product')

    def _link_from_box(self, box):
        return box.css('.productLink::attr(href)').extract()[0]

    def _populate_from_box(self, response, box, product):
        cond_set(product, 'title', box.css('.productTitle a::text').extract())
        cond_set(product, 'price',
                 box.css('.currentPrice ins::text').extract(), unicode.strip)
        cond_set_value(product, 'is_in_store_only',
                       len(box.css('.availability .available')) == 1)
        cond_set_value(product, 'is_out_of_stock',
                       not box.css('.availability .available'))

    def _populate_from_html(self, response, product):
        cond_set(product, 'image_url',
                 response.css('[itemprop=image]::attr(src)').extract(),
                 lambda url: urlparse.urljoin(response.url, url))
        _populate_from_open_graph_product(response, product)
        cond_set(product, 'price',
                 response.css('.currentPrice ins::text').extract(),
                 unicode.strip)
        cond_set(product, 'brand',
                 response.css('[itemprop=brand]::text').extract())
        if not product.get('brand', None):
            dump_url_to_file(response.url)

        cond_set(product, 'title',
                 response.css('[itemprop=name]::text').extract())
        css = '#longDesc article'
        desc = response.css(css).extract()
        desc = desc[0] if desc else None
        cond_set_value(product, 'description', desc)

        reseller_id_regex = "(\d+)-pdt"
        reseller_id = re.findall(reseller_id_regex, response.url)
        reseller_id = reseller_id[0] if reseller_id else None
        cond_set_value(product, 'reseller_id', reseller_id)

        self._unify_price(product)

    def _unify_price(self, product):
        price = product['price'].encode('utf-8')
        price = unify_price(valid_currency_codes, CURRENCY_SIGNS,
                            unify_decimal(', ', '.'))(price)
        cond_replace_value(product, 'price', price)

    def _request_buyer_reviews(self, response):
        sku = response.css('[name=sFUPID]::attr(value)')
        if not sku:
            return
        sku = sku.extract()[0]
        return "http://mark.reevoo.com/reevoomark/en-GB" \
               "/product?sku=%s&trkref=CYS" % sku

    def _parse_buyer_reviews(self, response):
        css = '.overall-scores .overall_score_stars::attr(title)'
        scores = map(float, filter(unicode.isdigit,
                                   response.css(css).extract()))
        populate_reviews(response, scores)

    def _parse_single_product(self, response):
        return self.parse_product(response)
