from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import urlparse
import urllib
import re
# Please $ pip install python-cjson
# https://pypi.python.org/pypi/python-cjson
#import cjson as json


#import requests
from scrapy.http import Request
from scrapy.selector import Selector

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set_value


class WalmartBrProductsSpider(BaseProductsSpider):
    name = "walmartbr_products"
    allowed_domains = ["walmart.com.br"]
    start_urls = []

    SEARCH_URL = "http://www.walmart.com.br/busca/?ft={search_term}"

    def start_requests(self):
        """Generate Requests from the SEARCH_URL and the search terms."""
        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(self.SEARCH_URL,
                                          search_term=urllib.quote_plus(st)),
                callback=self.parse_departments,
                meta={'search_term': st, 'remaining': self.quantity})

    def parse_departments(self, response):
        """
        Pre-calculate department pages. Use these as normal pages
        """
        new_meta = dict(response.meta)
        new_meta['total_matches'] = self.scrape_total_matches(response)

        links = []
        for link in response.xpath(
                '//div[@class="if-search-block-head"]/a/@href').extract():
            link = urlparse.urljoin(response.url, link)
            links.append(link)
        url = links.pop()
        new_meta['pages'] = links

        yield Request(url, callback=self.parse, meta=new_meta)

    def parse_product(self, response):

        data_js = response.xpath(
            '//script/text()').re("var dataLayer = \[(\{.+\})\];")
        if data_js:
            # Remove object properties with improperly value
            data_str = re.sub(
                '("[\w\d\-\_]+":[\s]*,)','', data_js[0])

            data = json.decode(data_str)
            prod_data = data['product'][0]

            prod = response.meta['product']

            model = prod_data.get('productSku', '')
            cond_set_value(prod, 'model', model)

            title = prod_data.get('productName', '')
            cond_set_value(prod, 'title', title)

            price = prod_data.get('productPrice', '')
            cond_set_value(prod, 'price', price)

            img_url = prod_data.get('productImage', '')
            cond_set_value(prod, 'image_url', img_url)

            brand = prod_data.get('productBrandName', '')
            cond_set_value(prod, 'brand', brand)

            description = prod_data.get('productDescription', '')
            cond_set_value(prod, 'description', description)

            prod['url'] = response.url

            prod['locale'] = 'pt-BR'

            return prod

    def scrape_total_matches(self, response):
        # Keyword is not correct and no items found for this keyword.
        incorrect_keyword = response.xpath(
            '//p[@class="bigger single"]/text()').extract()
        if incorrect_keyword:
            return 0

        count = response.xpath(
            '//span[@class="result-items"]/text()').re('(\d+)')
        if count:
            return int(count[0])
        return 0

    def _scrape_product_links(self, response):
        """
        This method need to get all prod links from a department
        """
        links = self.get_all_department_prod_links(response)
        for link in links:
            yield link, SiteProductItem()

    def get_all_department_prod_links(self, response):
        """
        Get all prod links of a department
        """
        url = response.url + "&PageNumber={page_number}"

        max_pages = response.css(
            '.next').xpath('@data-max-pages').extract()
        if max_pages:
            max_pages = int(max_pages[0])
        else:
            max_pages = 1

        links = []
        for i in range(1, max_pages+1):
            body = requests.get(url.format(page_number=i)).text
            for link in self.get_department_page_prod_links(body):
                link = urlparse.urljoin(response.url, link)
                links.append(link)
        return links

    def get_department_page_prod_links(self, body):
        """
        Get prod links from a page of a department
        """
        response = Selector(text=body)
        for li in response.xpath('//*[@itemprop="itemListElement"]'):
            link = li.xpath('.//a[@itemprop="url"]/@href').extract()
            if link:
                yield link[0]

    def _scrape_next_results_page_link(self, response):
        pages = response.meta['pages']
        if pages:
            link = pages.pop()
            response.meta["pages"] = pages
            return link
        else:
            return None
