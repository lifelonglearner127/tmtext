import os.path
import re
import urlparse
import requests
import json

import scrapy
from scrapy.http import Request
from scrapy import Selector

from product_ranking.items import SiteProductItem
from .kohls import KohlsProductsSpider

is_empty = lambda x: x[0] if x else None


class KohlsShelfPagesSpider(KohlsProductsSpider):
    name = 'kohls_shelf_urls_products'
    allowed_domains = ['kohls.com', 'www.kohls.com']

    def _setup_class_compatibility(self):
        """ Needed to maintain compatibility with the SC spiders baseclass """
        self.quantity = 99999
        self.site_name = self.allowed_domains[0]
        self.user_agent_key = None
        self.zipcode = '12345'
        self.current_page = 1

    def _setup_meta_compatibility(self):
        """ Needed to prepare first request.meta vars to use """
        return {'remaining': 99999, 'search_term': ''}.copy()

    def __init__(self, *args, **kwargs):
        self._setup_class_compatibility()
        self.product_url = kwargs['product_url']

        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1

        self.user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64))" \
            " AppleWebKit/537.36 (KHTML, like Gecko)" \
            " Chrome/37.0.2062.120 Safari/537.36"

    @staticmethod
    def valid_url(url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta=self._setup_meta_compatibility())

    def _scrape_product_links(self, response):
        prod_urls = re.findall(
                r'"prodSeoURL"\s?:\s+\"(.+)\"',
                response.body_as_unicode()
            )
        print(prod_urls)

    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1
        return super(KohlsProductsSpider,
                     self)._scrape_next_results_page_link(response)

