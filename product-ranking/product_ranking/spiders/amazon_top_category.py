# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from datetime import datetime
import re
from scrapy import Request, Selector
from lxml import html
import requests
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


class AmazonBestSellersProductsSpider(AmazonTests, AmazonBaseClass):
    name = 'amazon_top_categories_products'
    allowed_domains = ["amazon.com"]

    settings = AmazoncaValidatorSettings

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
        #settings.overrides['CRAWLERA_ENABLED'] = True

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
        upc = self.convert_ASIN2UPC(asin)
        cond_set_value(product, 'upc', upc)
        if upc:
            self._match_walmart(product, upc)
        cond_set_value(product, 'ranking', response.meta.get('ranking'))
        yield product

    def convert_ASIN2UPC(self, asin):
        upc = ""
        payload = {
            r"ctl00$MainContent$txtASIN": asin,
            r"ctl00$MainContent$btnSearch": "Search",
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36'}

        with requests.session() as s:
            s.headers = headers
            try:
                response = s.get('http://asintoupc.com/')

                # soup = BeautifulSoup(response.content)
                tree = html.fromstring(response.content)

                for input_name in ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION']:
                    # payload[input_name] = soup.find('input', {'name': input_name}).get('value', '')
                    payload[input_name] = tree.xpath("//input[@name='%s']/@value" % input_name)[0]
                for i in range(1, 30):
                    response2 = s.post("http://asintoupc.com/", data=payload)
                    if 'WSE101: An asynchronous operation raised an exception.' not in response2.text:
                        break

                # print(response2.content)
                # soup = BeautifulSoup(response2.content)
                tree = html.fromstring(response2.content)
                upc = tree.xpath("//span[@id='MainContent_lblUPC']")[0].text
            except:
                pass
        return upc

    @staticmethod
    def _match_walmart(product, upc):
        url = 'http://www.walmart.com/search/?query={}'
        walmart_selector = Selector(text=requests.get(
            url.format(upc)).text)
        walmart_category = walmart_selector.xpath('//p[@class="dept-head-list-heading"]/a/text()').extract()
        walmart_url = walmart_selector.xpath('//a[@class="js-product-title"][1]/@href').extract()
        if walmart_url:
            walmart_exists = True
            walmart_url = urlparse.urljoin('http://www.walmart.com/', walmart_url[0])
        else:
            walmart_exists = False
        cond_set_value(product, 'walmart_url', walmart_url)
        cond_set_value(product, 'walmart_category', walmart_category)
        cond_set_value(product, 'walmart_exists', walmart_exists)


