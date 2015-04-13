# -*- coding: utf-8 -*-

# TODO:
# 1) sorting options
# 2) buyer reviews
# 3) all the other fields that exist at the website


from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re

from scrapy.log import ERROR, DEBUG

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import (BaseProductsSpider, FormatterWithDefaults,
                                     cond_set, cond_set_value)


class ProswimwearCoUkSpider(BaseProductsSpider):
    name = 'proswimweark_co_uk_products'
    allowed_domains = ["proswimwear.co.uk"]
    start_urls = []

    SEARCH_URL = ('http://www.proswimwear.co.uk/catalogsearch/result/'
                  '?category=&q={search_term}')

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//h2[contains(@class, "product-name")]//a/@href').extract()
        for link in links:            
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath(
            '//li[contains(@class, "next")]'
            '//a[contains(@class, "next")]/@href'
        ).extract()
        return next[0] if next else None

    def _scrape_total_matches(self, response):
        totals = response.css('.sorter .amount ::text').extract()
        if not totals:
            self.log(
                "'total matches' string not found at %s" % response.url,
                ERROR
            )
            return
        total = totals[0]
        if 'total' in total.lower():  # like " Items 1 to 20 of 963 total "
            total = total.split('of ', 1)[1]
        total = re.search(r'([\d,\. ]+)', total)
        if not total:
            self.log(
                "'total matches' string not found at %s" % response.url,
                ERROR
            )
            return
        total = total.group(1).strip().replace(',', '').replace('.', '')
        if not total.isdigit():
            self.log(
                "'total matches' string not found at %s" % response.url,
                ERROR
            )
            return
        total = int(total)
        self.total_results = total  # remember num of results
        return total

    def parse_product(self, response):
        product = response.meta['product']

        title = response.css('.product-name h1').extract()
        cond_set(product, 'title', title)

        return product