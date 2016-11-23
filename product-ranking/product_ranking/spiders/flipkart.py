from __future__ import division, absolute_import, unicode_literals

import urlparse
import urllib
import string
import json
from datetime import datetime

from scrapy.log import ERROR
from scrapy.http import Request

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set, cond_set_value, FLOATING_POINT_RGEX
from product_ranking.settings import ZERO_REVIEWS_VALUE
from spiders_shared_code.flipkart_variants import FlipkartVariants


class FlipkartProductsSpider(BaseProductsSpider):
    """ flipkart.com product ranking spider

    Missing fields:
    * upc

    Takes `search_sort` argument with the following values:
    * `best_match` - default, most relevance
    * `price_asc`, price_desc
    * `best_sellers` - most selling (popular)
    """
    name = 'flipkart_products'
    allowed_domains = ["flipkart.com"]
    start_urls = []

    SEARCH_URL = ("http://www.flipkart.com/"
                  "search?q={search_term}&"
                  "as=off&as-show=on&otracker=start&p%5B%5D="
                  "sort%3D{search_sort}")

    SEARCH_SORT = {
        'best_match': 'relevance',
        'price_asc': 'price_asc',
        'price_desc': 'price_desc',
        'best_sellers': 'popularity',
    }

    related_links = [
        ('buyers_also_bought', '/dynamic/recommendation/bullseye/'
                               'getBookRecommendations'),
        ('buyers_also_bought', '/dynamic/recommendation/bullseye/'
                               'getCrossVerticalRecommendationsForProductPage'),
        ('recommended', '/dynamic/recommendation/bullseye/'
                        'getSameVerticalRecommendationsForProductPage'),
        # USED RARELY
        # ('buyers_also_bought',
        # '/dynamic/recommendation/carousel/getCrossSellingTopRecommendations'),
        ('recommended', '/dynamic/recommendation/bullseye/getHorizontally'
                        'OrientedSameVerticalRecommendationsForProductPage'),
    ]

    def __init__(self, search_sort='best_match', *args, **kwargs):
        super(FlipkartProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self.SEARCH_SORT[search_sort]
            ),
            *args, **kwargs)

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(product, 'title',
                 response.xpath('//h1[@itemprop="name"]/text()').extract(),
                 string.strip)

        # image_url
        image_url = response.css('.mainImage > .imgWrapper > '
                                 'img::attr(data-src)')
        cond_set(product, 'image_url', image_url.extract())
        # reviews
        cond_set_value(
            product, 'buyer_reviews', self.parse_buyer_reviews(response))
        # last review date
        last_review = response.xpath('//div[@class="recentReviews"]'
                                     '/div[contains(@class,"review")][1]')
        if not last_review:
            last_review = response.xpath('//div[@class="helpfulReviews"]'
                                         '/div[contains(@class,"review")][1]')
        last_review = last_review.xpath('//p[@class="review-date"]/text()')
        if last_review:
            cond_set_value(
                product, 'last_buyer_review_date',
                datetime.strptime(last_review[0].extract(),
                                  '%b %d, %Y').strftime('%d-%m-%Y'))
        # description
        cond_set_value(
            product, 'description', ''.join(
                response.css('.rpdSection, .description.specSection').extract()
            )
        )
        # variants
        fv = FlipkartVariants()
        fv.setupSC(response)
        cond_set_value(product, 'variants', fv._variants())
        # model
        model = response.css('.reviewSection::attr(data-pid)').extract()
        cond_set(product, 'model', model)
        # price
        price = response.xpath(
            '//meta[@itemprop="price"]/@content').re(FLOATING_POINT_RGEX)
        if price:
            product['price'] = Price(price=price[0], priceCurrency='INR')
        else:
            price = response.css('li#tab-0 .selling-price::attr(data-evar48)')
            if price:
                product['price'] = Price(price=price[0].extract(),
                                         priceCurrency='INR')
        # marketplace
        cond_set_value(product, 'marketplace', self.parse_marketplace(response))
        if 'marketplace' not in product:
            seller_name = response.css('.shop-section '
                                       '.seller-name::text').extract()
            if seller_name and 'price' in product:
                marketplace = dict(price=product['price'], name=seller_name[0])
                cond_set_value(product, 'marketplace', [marketplace])
        # brand
        brand = response.css('div.title-wrap::attr(data-prop41)')
        cond_set(product, 'brand', brand.extract())
        # out of stock
        oos = response.css('.coming-soon, .out-of-stock')
        cond_set_value(product, 'is_out_of_stock', oos, bool)

        cond_set_value(product, 'locale', 'en-IN')
        cond_set_value(product, 'related_products', {})
        # Get product id (for related requests)
        url_parts = urlparse.urlsplit(response.url)
        query_string = urlparse.parse_qs(url_parts.query)
        response.meta['pid'] = query_string.get('pid', [0])[0]
        # get some token
        fk = response.xpath(
            '//input[@name="__FK"][1]/@value').extract()
        if not fk:
            fk = response.xpath('//div[@id="login-signup-newDialog"]//'
                                'preceding-sibling::'
                                'script[1]/text()').re('\s?=\s?"(.+)";')
        if fk:
            response.meta['FK'] = fk[0]
        response.meta['iter'] = iter(self.related_links)
        return self._generate_related_request(response)

    def _parse_related(self, response):
        product = response.meta['product']
        key = response.meta['key']
        related_products = []

        aa = response.xpath('//a[@data-tracking-id="prd_img"]')
        for a in aa:
            title = a.xpath('./img/@alt').extract()
            link = a.xpath('./@href').extract()
            if title and link:
                related_products.append(RelatedProduct(title[0], link[0]))

        aa = response.css('div.recom-mini-item a.image-wrapper')
        for a in aa:
            title = a.xpath('./@title').extract()
            link = a.xpath('./@href').extract()
            if title and link:
                related_products.append(RelatedProduct(title[0], link[0]))

        if product['related_products'].get(key):
            product['related_products'][key] += related_products
        else:
            product['related_products'][key] = related_products

        return self._generate_related_request(response)

    def _generate_related_request(self, response):

        it = response.meta['iter']
        product = response.meta['product']
        try:
            key, link = next(it)
        except StopIteration:
            # remove related products if empty
            if all([not bool(p) for p in product['related_products'].values()]):
                del product['related_products']
            return product

        url_parts = urlparse.urlsplit(link)
        query_string = {
            'pid': response.meta['pid'],
            '__FK': response.meta.get('FK', '')
        }
        url_parts = url_parts._replace(
            query=urllib.urlencode(query_string))
        link = urlparse.urlunsplit(url_parts)

        url = urlparse.urljoin(response.url, link)

        response.meta['key'] = key
        return Request(
            url,
            callback=self._parse_related,
            dont_filter=True,
            meta=response.meta)

    def _scrape_total_matches(self, response):
        totals = response.xpath(
            '//div[@id="searchCount"]/*[@class="items"]/text()').extract()
        total = None
        if totals:
            total = int(totals[0].strip().replace(',', ''))
        else:
            self.log(
                "Failed to find 'total matches' for %s" % response.url, ERROR)
        return total

    def _scrape_product_links(self, response):

        items = response.xpath(
            '//div[@id="products"]//a[@data-tracking-id="prd_title"]/@href'
        ).extract()

        # try to find in BOOKS category
        if not items:
            items = response.xpath(
                '//div[@id="products"]//a[@class="lu-title"]/@href').extract()
        if not items:
            self.log("Found no product links.", ERROR)
        response.meta['prods_per_page'] = len(items)

        for link in items:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):

        url_parts = urlparse.urlsplit(response.url)
        query_string = urlparse.parse_qs(url_parts.query)

        current_start = int(query_string.get("start", [1])[0])
        next_start = current_start + response.meta.get('prods_per_page', 0)

        total = self._scrape_total_matches(response)

        if not total or next_start > total:
            link = None
        else:
            query_string['start'] = [next_start]
            url_parts = url_parts._replace(
                query=urllib.urlencode(query_string, True))
            link = urlparse.urlunsplit(url_parts)
        return link

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_marketplace(self, response):
        marketplace_section = response.css(
            '.seller-table-wrap::attr(data-config)')
        if not marketplace_section:  # no marketplaces
            return None
        json_data = json.loads(marketplace_section[0].extract())
        marketplace = []
        for item in json_data.get('dataModel', []):
            mp = dict(
                name=item['sellerInfo']['name'],
                price=Price(
                    price=item['priceInfo']['sellingPrice'],
                    priceCurrency='INR'
                )
            )
            marketplace.append(mp)
        return marketplace or None

    def parse_buyer_reviews(self, response):
        review_section = response.css('.reviewSection')

        total_rating = review_section.css('.bigStar::text').extract()
        total_review = review_section.css(
            '.avgWrapper > .subText:last-child::text').re(FLOATING_POINT_RGEX)
        if not total_rating or not total_review:
            return ZERO_REVIEWS_VALUE

        reviews_list = review_section.css('ul.ratingsDistribution > li > a')
        reviews = {}
        for item in reviews_list:
            stars = item.css('span::text').re('\d+')
            count = item.css('.progress::text').extract()
            if stars and count:
                reviews[stars[0]] = int(count[0].replace(',', ''))

        return BuyerReviews(
            int(total_review[0].replace(',', '')),
            float(total_rating[0]),
            reviews
        )
