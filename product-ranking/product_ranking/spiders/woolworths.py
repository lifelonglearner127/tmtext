from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string

from scrapy.log import ERROR

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set, populate_from_open_graph


class WoolworthsProductsSpider(BaseProductsSpider):
    name = 'woolworths_products'
    allowed_domains = ["woolworthsonline.com.au"]
    start_urls = []

    SEARCH_URL = "http://www2.woolworthsonline.com.au/Shop/SearchProducts" \
                 "?search={search_term}"

    def parse_product(self, response):

        if self._search_page_error(response):
            self.log(
                "Got 404 when coming from %s." % response.request.url, ERROR)
            return

        product = response.meta['product']

        populate_from_open_graph(response, product)

        price = response.xpath(
            "//span[@class='price']/text()"
            "| //span[@class='price special-price']/text()"
        ).extract()
        cond_set(product, 'price', price, string.strip)

        cond_set(product, 'upc', response.xpath(
            "//input[@id='stockcode']/@value").extract())

        title = response.xpath("//h2[@class='description']/text()").extract()

        cond_set(product, 'title', [title])

        product['locale'] = "en-AU"

        return product

    def _search_page_error(self, response):
        check_result = response.xpath("//div[@class='light-green-box-middle']/h3/text()").extract()
        if check_result[0] == 'Quickfix':
            return True
        elif check_result is None:
            return None

    def _scrape_total_matches(self, response):
        num_results = response.xpath(
            "//div[@class='paging-description']/text()").re('of\s(\d+)')[1]

        if num_results:
            return int(num_results)
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//div[@class='name-container']/a/@href").extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next_pages = response.xpath("//li[@class='next']/a/@href").extract()
        next_page = None
        if len(next_pages) == 2:
            next_page = next_pages[0]
        elif len(next_pages) == 0:
            self.log("Found no 'next page' link.", ERROR)
        return next_page
