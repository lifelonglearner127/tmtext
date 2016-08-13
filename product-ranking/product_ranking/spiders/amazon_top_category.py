# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
import re
from scrapy import Request
import urlparse
from scrapy.conf import settings
from product_ranking.amazon_tests import AmazonTests
from product_ranking.amazon_base_class import AmazonBaseClass
from product_ranking.validators.amazonca_validator import AmazoncaValidatorSettings
from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider,FormatterWithDefaults, \
    cond_set, cond_set_value, FLOATING_POINT_RGEX
from requests.auth import HTTPProxyAuth
from product_ranking.settings import CRAWLERA_APIKEY
import json
from scrapy.log import INFO, WARNING

class AmazonBestSellersProductsSpider(AmazonTests, AmazonBaseClass):
    name = 'amazon_top_categories_products'
    allowed_domains = ["amazon.com", "asintoupc.com", "walmart.com", "target.com"]

    settings = AmazoncaValidatorSettings
    ASIN_UPC_URL = "http://asintoupc.com/?__EVENTVALIDATION=%2FwEdAAMFqOzoH1a8XwCofuUjrlmPM0K3g6Ucd7mv%2FKHQcK9QwZ%" \
                  "2BI%2FHPZ86NEZcbXwR9jxA4x0nggqK%2FxAM5I8ZALxidoKUw7uSVwqO3jL8TFRtYRzQ%3D%3D&__VIEWSTATE=" \
                  "%2FwEPDwULLTExNDk1NTA3MzUPZBYCZg9kFgICAw9kFgICAw9kFgQCBQ8PFgIeB1Zpc2libGVoZBY" \
                  "IAgEPDxYCHgRUZXh0ZWRkAgMPDxYCHwFlZGQCBw8PFgIfAWVkZAIJDw8WAh4ISW1hZ2VVcmxlZGQCBw8" \
                  "PFgIfAWVkZGRL0SMg3%2BJmPP6c%2FkOeHOL0SszKS1HpppYAmGE%2FAgS8rA%3D%3D&__VIEWSTATEGENERATOR" \
                  "=CA0B0334&ctl00%24MainContent%24btnSearch=Search&ctl00%24MainContent%24txtASIN={}"

    def __init__(self, *args, **kwargs):
        super(AmazonBestSellersProductsSpider, self).__init__(*args, **kwargs)

        # String from html body that means there's no results ( "no results.", for example)
        self.total_match_not_found_re = 'did not match any products.'
        # Regexp for total matches to parse a number from html body
        self.total_matches_re = r'of\s?([\d,.\s?]+)'

        # Default price currency
        self.price_currency = 'USD'
        self.price_currency_view = '$'

        # Locale
        self.locale = 'en-US'
        # settings.overrides['CRAWLERA_ENABLED'] = True

    def start_requests(self):
        if self.product_url:
            yield Request(self.product_url)
        if self.products_url:
            urls = self.products_url.split('||||')
            for url in urls:
                yield Request(url)

    def parse(self, response):
        url = response.url + '&pg={}&ajax=1&isAboveTheFold={}'
        for page in range(1, 6):
            for position in [1, 0]:
                request = Request(url=url.format(page, position),
                                  callback=self._scrape_product_links,
                                  dont_filter=True)
                request.meta['shelf_name'] = response.xpath(
                    '//h1/span[@class="category"]/text()').extract()
                request.meta['shelf_path'] = response.xpath(
                    '//li[@class="zg_browseUp"]/a/text()').extract()[1:] + response.xpath(
                    '//span[@class="zg_selected"]/text()').extract()
                yield request

    def _scrape_product_links(self, response):
        products = response.xpath('//div[@class="zg_itemImmersion"]')
        for product in products:
            url = product.xpath('.//div[@class="zg_title"]/a/@href').extract()[0].strip()
            request = Request(url=url, callback=self.parse_product)
            request.meta['shelf_name'] = response.meta.get('shelf_name')
            request.meta['shelf_path'] = response.meta.get('shelf_path')
            request.meta['ranking'] = product.xpath('.//span[@class="zg_rankNumber"]/text()').re('\d+')[0]
            yield request

    def parse_product(self, response):
        product = SiteProductItem()
        cond_set_value(product, 'shelf_path', response.meta.get('shelf_path'))
        cond_set_value(product, 'shelf_name', response.meta.get('shelf_name'))
        title = response.xpath('//h1/span/text()').extract()[0].strip()
        cond_set_value(product, 'title', title)
        data_body = response.xpath('//script[contains(text(), '
                                   '"merchantID")]/text()').extract()
        try:
            asin = re.findall(r'"ASIN" : "(\w+)"', data_body[0])[0]
        except IndexError:
            asin = re.findall('\/([A-Z0-9]{10})', response.url)[0]
        cond_set_value(product, 'asin', asin)
        cond_set_value(product, 'url', response.url)
        cond_set_value(product, 'ranking', response.meta.get('ranking'))
        req = Request(url=self.ASIN_UPC_URL.format(asin), callback=self.threadsafe_ASIN2UPC, dont_filter=True)
        req.meta['product'] = product
        yield req

    def threadsafe_ASIN2UPC(self, response):
        # TODO rework this using amazon API, and use this external service as backup option
        product = response.meta.get('product')
        if 'WSE101: An asynchronous operation raised an exception.' in response.body_as_unicode():
            req = Request(url=response.url, callback=self.threadsafe_ASIN2UPC, dont_filter=True)
            req.meta['product'] = product
            self.log("Page error, retrying", level=WARNING)
            yield req
        else:
            upc = response.xpath("//span[@id='MainContent_lblUPC']/text()").extract()
            self.log("Got UPC: {}".format(upc), level=INFO)
            upc = upc[0] if upc else None
            if upc:
                cond_set_value(product, 'upc', upc)
                req = Request('http://www.walmart.com/search/?query={}'.format(upc),
                              callback=self._match_walmart_threadsafe)
                req.meta['product'] = product
                yield req
            else:
                yield product

    def _match_walmart_threadsafe(self, response):
        product = response.meta.get('product')
        upc = product.get('upc')
        walmart_category = response.xpath('//p[@class="dept-head-list-heading"]/a/text()').extract()
        walmart_url = response.xpath('//a[@class="js-product-title"][1]/@href').extract()
        if walmart_url:
            walmart_exists = True
            walmart_url = urlparse.urljoin('http://www.walmart.com/', walmart_url[0])
        else:
            walmart_exists = False
        cond_set_value(product, 'walmart_url', walmart_url)
        cond_set_value(product, 'walmart_category', walmart_category)
        cond_set_value(product, 'walmart_exists', walmart_exists)

        target_url = 'http://tws.target.com/searchservice/item/search_results/v2/by_keyword?search_term={}&alt=json&' \
                     'pageCount=24&response_group=Items&zone=mobile&offset=0'
        req = Request(target_url.format(upc), callback=self._match_target_threadsafe)
        req.meta['product'] = product
        yield req

    def _match_target_threadsafe(self, response):
        product = response.meta.get('product')
        json_response = json.loads(response.body_as_unicode())
        try:
            item = json_response['searchResponse']['items']['Item']
            item = item[0] if item else None
            if item:
                target_category = item['itemAttributes']['merchClass']
                target_url = item['productDetailPageURL']
                if target_url:
                    target_exists = True
                    target_url = urlparse.urljoin('http://www.target.com/', target_url)
                else:
                    target_exists = False
                cond_set_value(product, 'target_url', target_url)
                cond_set_value(product, 'target_category', [target_category])
                cond_set_value(product, 'target_exists', target_exists)
            else:
                target_exists = False
                cond_set_value(product, 'target_url', [])
                cond_set_value(product, 'target_category', [])
                cond_set_value(product, 'target_exists', target_exists)
        except Exception:
            pass
        yield product