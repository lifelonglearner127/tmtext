# -*- coding: utf-8 -*-

import re
import sys
import requests
import urllib
import json
from lxml import html

from scrapy import Request

from product_ranking.items import SiteProductItem

from .tesco import TescoProductsSpider

is_empty = lambda x: x[0] if x else None


class TescoShelfPagesSpider(TescoProductsSpider):
    name = 'tesco_shelf_urls_products'
    allowed_domains = ["tesco.com"]

    def _setup_class_compatibility(self):
        """ Needed to maintain compatibility with the SC spiders baseclass """
        self.quantity = sys.maxint
        self.site_name = self.allowed_domains[0]
        self.user_agent_key = None
        self.current_page = 1

    def _setup_meta_compatibility(self):
        """ Needed to prepare first request.meta vars to use """
        return {'remaining': sys.maxint, 'search_term': ''}.copy()

    def __init__(self, *args, **kwargs):
        super(TescoShelfPagesSpider, self).__init__(*args, **kwargs)
        self.product_url = kwargs['product_url']
        self._setup_class_compatibility()

        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0

        # variants are switched off by default, see Bugzilla 3982#c11
        self.scrape_variants_with_extra_requests = False
        if 'scrape_variants_with_extra_requests' in kwargs:
            scrape_variants_with_extra_requests = kwargs['scrape_variants_with_extra_requests']
            if scrape_variants_with_extra_requests in (1, '1', 'true', 'True', True):
                self.scrape_variants_with_extra_requests = True

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta=self._setup_meta_compatibility(),
                      dont_filter=True)

    @staticmethod
    def valid_url(url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def _scrape_product_links(self, response):
        shelf_categories = response.xpath(
            '//ul[@id="breadcrumbNav"]/li/a//text()'
        ).extract()
        shelf_category = response.xpath(
            '//ul[@id="breadcrumbNav"]/li/text()'
        ).extract()
        shelf_category = shelf_category[-1].strip()

        links = response.xpath(
            '//div[contains(@class,"productLists")]'
            '//ul[contains(@class,"products grid")]'
            '/li[contains(@class,"product")]//h2/a/@href'
        ).extract()
        for item_url in links:
            item = SiteProductItem()
            if shelf_category:
                item['shelf_name'] = shelf_category
            if shelf_categories:
                item['shelf_path'] = shelf_categories
            yield "http://www.tesco.com" + item_url, item


    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1
        links = response.xpath('//li[contains(@class, "nextWrap")]'
                               '//a[contains(text(), "next")]/@href').extract()
        if links:
            return links[0]
