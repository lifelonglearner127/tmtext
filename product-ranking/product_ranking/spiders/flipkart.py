#TODO:
#1) marketplace
#2) buyer reviews
#3) description (?)
#4) variants (with OOS status)
#5) brand
#6) is_out_of_stock
#7) UPC (?)
#8) image_url
#9) model (?)
#10) XML fields version file

from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import urlparse
import urllib
import string
import re

from scrapy.log import ERROR, DEBUG
from scrapy.http import Request

from product_ranking.items import SiteProductItem, RelatedProduct, Price
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set, cond_set_value, FLOATING_POINT_RGEX


class FlipkartProductsSpider(BaseProductsSpider):
    name = 'flipkart_products'
    allowed_domains = ["flipkart.com"]
    start_urls = []

    SEARCH_URL = "http://www.flipkart.com/search?q={search_term}&as=off&as-show=on&otracker=start" \
        "&p%5B%5D=sort%3D{search_sort}"

    SEARCH_SORT = {
        'best_match': 'relevance',
        'price_asc': 'price_asc',
        'price_desc': 'price_desc',
        'best_sellers': 'popularity',
    }

    related_links = [
         ('buyers_also_bought',
          '/dynamic/recommendation/bullseye/getBookRecommendations'),
         ('buyers_also_bought',
          '/dynamic/recommendation/bullseye/getCrossVerticalRecommendationsForProductPage'),
         ('recommended',
          '/dynamic/recommendation/bullseye/getSameVerticalRecommendationsForProductPage'),
         #USED RARELY
         #('buyers_also_bought',
         #'/dynamic/recommendation/carousel/getCrossSellingTopRecommendations'),
         ('recommended',
          '/dynamic/recommendation/bullseye/getHorizontallyOrientedSameVerticalRecommendationsForProductPage'),
    ]
    def __init__(self, search_sort='best_match', *args, **kwargs):
        super(FlipkartProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self.SEARCH_SORT[search_sort]
            ),
            *args, **kwargs)

    def clear_desc(self, l):
        return " ".join(
            [it for it in map(string.strip, l) if it])

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(product, 'title',
                 response.xpath('//h1[@itemprop="name"]/text()').extract(),
                 string.strip)

        cond_set(product, 'image_url',
                 response.xpath('//img[@id="visible-image-small"]/@src').extract())

        price = response.xpath(
            '//meta[@itemprop="price"]/@content').re(FLOATING_POINT_RGEX)
        #currency = response.xpath('//meta[@itemprop="priceCurrency"]/@content').extract()
        if price:
            product['price'] = Price(price=price[0],
                                     priceCurrency='INR')

        brand = response.xpath('//a[contains(@href, "~brand/")]/@href').extract()
        if brand:
            brand = re.search(r'/([a-zA-Z0-9 \.]{2,30})~brand/', brand[0])
            brand = brand.group(1)
            if brand:
                product['brand'] = brand.strip()

        cond_set_value(product, 'description', self.clear_desc(
            response.xpath(
                '//div[@id="description"]/div[contains(@class,"item_desc_text")]//text()'
            ).extract()))

        cond_set_value(product, 'locale', 'en-IN')

        cond_set_value(product, 'related_products', {})

        #Get product id (for related requests)
        url_parts = urlparse.urlsplit(response.url)
        query_string = urlparse.parse_qs(url_parts.query)
        response.meta['pid'] = query_string.get('pid', [0])[0]

        #get some token
        FK = response.xpath(
            '//input[@name="__FK"][1]/@value').extract()
        if FK:
            response.meta['FK'] = FK[0]

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

        if  product['related_products'].get(key):
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
            meta=response.meta)

    def _scrape_total_matches(self, response):
        totals = response.xpath('//div[@id="searchCount"]/*[@class="items"]/text()').extract()

        total = None
        if totals:
            total = int(totals[0].strip().replace(',', ''))
        else:
            self.log(
                "Failed to find 'total matches' for %s" % response.url,
                ERROR
            )

        #response.meta['total_matches'] = total
        return total

    def _scrape_product_links(self, response):

        items = response.xpath(
            '//div[@id="products"]//a[@data-tracking-id="prd_title"]/@href'
        ).extract()

        #try to find in BOOKS category
        if not items:
            items = response.xpath(
                '//div[@id="products"]//a[@class="lu-title"]/@href'
            ).extract()

        if not items:
            self.log("Found no product links.", ERROR)

        response.meta['prods_per_page'] = len(items)

        for link in items:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):

        url_parts = urlparse.urlsplit(response.url)
        query_string = urlparse.parse_qs(url_parts.query)

        current_start = int(query_string.get("start", [1])[0])
        next_start = current_start + response.meta.get('prods_per_page',0)

        total = self._scrape_total_matches(response)

        if not total or next_start > total:
            link = None
        else:
            query_string['start'] = [next_start]
            url_parts = url_parts._replace(
                query=urllib.urlencode(query_string,True))
            link = urlparse.urlunsplit(url_parts)
        return link

    def _parse_single_product(self, response):
        return self.parse_product(response)
