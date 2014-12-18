from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re
import urllib
import urlparse

from scrapy.log import ERROR
from scrapy.selector import Selector

from scrapy.http import Request
from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FormatterWithDefaults
from product_ranking.guess_brand import guess_brand_from_first_words

# scrapy crawl maplin_products -a searchterms_str="Earth"

class GandermountainProductsSpider(BaseProductsSpider):
    name = "maplin_products"
    allowed_domains = ["www.maplin.co.uk"]
    start_urls = []

    
    SEARCH_URL = "http://www.maplin.co.uk/search?text={search_term}&x=0&y=0"

    product_link = "http://www.maplin.co.uk"
    product_link_next_page = "http://www.maplin.co.uk/search"

   
    def __init__(self, *args, **kwargs):
        print 'debug init:'
        super(GandermountainProductsSpider, self).__init__(*args, **kwargs)    

    def parse_product(self, response):
        prod = response.meta['product']

        title = response.xpath('//div[@class="product-summary"]/h1/text()').extract()
        cond_set(prod, 'title', title)

        if prod.get("title"):
            brand = guess_brand_from_first_words(prod['title'])
            if brand:
                prod['brand'] = brand

        price = response.xpath(
            '//p[@class="new-price"]/meta[@itemprop="price"]/@content'
        ).extract()
        priceCurrency = response.xpath(
            '//p[@class="new-price"]/meta[@itemprop="priceCurrency"]/@content'
        ).extract()
        if price and priceCurrency:
            if re.match("\d+(.\d+){0,1}", price[0]):
                prod["price"] = Price(priceCurrency=priceCurrency[0], price=price[0])

        des = response.xpath('//div[@class="productDescription"]').extract()
        cond_set(prod, 'description', des)

        img_url = response.xpath('//div[@class="product-images"]/img/@src').extract()
        cond_set(prod, 'image_url', img_url)

        cond_set(prod, 'locale', ['en-US'])

        prod['url'] = response.url

        return prod

    def _scrape_total_matches(self, response):
        total_matches = None
        if 'No products found matching the search criteria' in response.body_as_unicode():
            total_matches = 0
        total = response.xpath(
            '//div[@class="list-summary clearfix"]/p/text()'
            ).extract()
        if total:
            total = re.findall("(\d+(,\d+){0,5})", total[0])
        total_matches = int(''.join(total[0][0].split(",")))

        return total_matches

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[@class="tileinfo"]/h3/a/@href').extract()

        for link in links:
            yield self.product_link + link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        link = response.xpath(
            '//ul[@class="pagination"]/li[last()]/a/@href'
        )
        if link:
            return self.product_link_next_page + link.extract()[0].strip()
        return None
