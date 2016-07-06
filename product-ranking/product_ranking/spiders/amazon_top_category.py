# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from datetime import datetime
import re
from scrapy import Request
from lxml import html
import requests
from product_ranking.amazon_tests import AmazonTests
from product_ranking.amazon_base_class import AmazonBaseClass
from product_ranking.validators.amazonca_validator import AmazoncaValidatorSettings
from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider,FormatterWithDefaults, \
    cond_set, cond_set_value, FLOATING_POINT_RGEX


class AmazonProductsSpider(AmazonTests, AmazonBaseClass):
    name = 'amazonca_top_categories_products'
    allowed_domains = ["amazon.com"]

    settings = AmazoncaValidatorSettings
    ROOT_CATEGORIES_URL = 'https://www.amazon.com/Best-Sellers/zgbs/'
    def __init__(self, *args, **kwargs):
        super(AmazonProductsSpider, self).__init__(*args, **kwargs)

        # String from html body that means there's no results ( "no results.", for example)
        self.total_match_not_found_re = 'did not match any products.'
        # Regexp for total matches to parse a number from html body
        self.total_matches_re = r'of\s?([\d,.\s?]+)'

        # Default price currency
        self.price_currency = 'USD'
        self.price_currency_view = '$'

        # Locale
        self.locale = 'en-US'

    def start_requests(self):
        yield Request(self.ROOT_CATEGORIES_URL,
                       callback=self._scrape_categories)

    def _scrape_categories(self, response):
        categories = response.xpath('//ul[@id="zg_browseRoot"]/ul/li/a')
        for category in categories:
            name = category.xpath('text()').extract()[0]
            link = category.xpath('@href').extract()[0]
            request = Request(url=link,
                              callback=self._scrape_sub_categories)
            request.meta['Category'] = name
            yield request

    def _scrape_sub_categories(self, response):
        sub_categories = response.xpath('//ul[@id="zg_browseRoot"]/ul/ul/li/a')
        for category in sub_categories:
            name = category.xpath('text()').extract()[0]
            link = category.xpath('@href').extract()[0]
            request = Request(url=link,
                              callback=self._request_product_links)
            request.meta['Subcategory'] = name
            request.meta['Category'] = response.meta.get('Category')
            yield request

    def _request_product_links(self, response):
        url = response.url + '&pg={}&ajax=1&isAboveTheFold={}'
        for page in range(1, 6):
            for position in [1, 0]:
                request =  Request(url=url.format(page, position),
                              callback=self._scrape_product_links,
                              dont_filter=True)
                request.meta['Subcategory'] = response.meta.get('Subcategory')
                request.meta['Category'] = response.meta.get('Category')
                yield request

    def _scrape_product_links(self, response):
        products = response.xpath('//div[@class="zg_itemImmersion"]')
        for product in products:
            url = product.xpath('.//div[@class="zg_title"]/a/@href').extract()[0].strip()
            request = Request(url=url, callback=self.parse_product)
            request.meta['Subcategory'] = response.meta.get('Subcategory')
            request.meta['Category'] = response.meta.get('Category')
            request.meta['ranking'] = product.xpath('.//span[@class="zg_rankNumber"]/text()').re('\d+')[0]
            yield request

    def parse_product(self, response):
        product = SiteProductItem()
        cond_set_value(product, 'category', response.meta.get('Category'))
        cond_set_value(product, 'subcategory', response.meta.get('Subcategory'))
        title = response.xpath('//h1/span/text()').extract()[0].strip()
        cond_set_value(product, 'title', title)
        asin = re.findall('\/([A-Z0-9]{10})', response.url)[0]
        cond_set_value(product, 'asin', asin)
        cond_set_value(product, 'url',response.url)
        cond_set_value(product, 'upc', self.convert_ASIN2UPC(asin))
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

                response2 = s.post("http://asintoupc.com/", data=payload)

                # print(response2.content)
                # soup = BeautifulSoup(response2.content)
                tree = html.fromstring(response2.content)
                upc = tree.xpath("//span[@id='MainContent_lblUPC']")[0].text
            except:
                pass
        return upc
