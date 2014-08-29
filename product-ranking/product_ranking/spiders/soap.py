from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json

from scrapy.log import ERROR, WARNING
from scrapy import Request

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value, \
    populate_from_open_graph


class SoapProductSpider(BaseProductsSpider):
    name = 'soap_products'
    allowed_domains = ["soap.com"]

    SEARCH_URL = "http://www.soap.com/buy?s={search_term}"

    def parse_product(self, response):
        prod = response.meta['product']

        populate_from_open_graph(response, prod)

        self._populate_from_html(response, prod)

        cond_set_value(prod, 'locale', 'en-US')  # Default locale.

        json_link = response.xpath(
            "//*[@id='soapcom']/head/link[@type='application/json+oembed']"
            "/@href"
        ).extract()[0]

        # This additional request is necessary to get the brand.
        return Request(json_link, self._parse_json, meta=response.meta.copy())

    def _parse_json(self, response):
        product = response.meta['product']

        data = json.loads(response.body_as_unicode())

        cond_set_value(product, 'brand', data.get('brand'))
        cond_set_value(product, 'model', data.get('title'))

        return product

    def _populate_from_html(self, response, product):
        prices = response.xpath(
            "//*[@id='priceDivClass']/span/text()").extract()
        cond_set(product, 'price', prices)

        # The description is a possible <p> or just the text of the class,
        # each page is different.
        desc = response.xpath("//*[@class='pIdDesContent']").extract()
        cond_set_value(product, 'description', desc, conv=''.join)

        upcs = response.xpath("//*[@class='skuHidden']/@value").extract()
        cond_set(product, 'upc', upcs)

        # Override the title from other sources. This is the one we want.
        cond_set(
            product, 'title', response.css('.productTitle h1 ::text').extract())

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//*[contains(concat( ' ', @class, ' ' ), concat( ' ', 'pdpLinkable', ' '))]/a/@href"
        ).extract()
        if not links:
            self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_total_matches(self, response):
        num_results = response.xpath(
            "//*[@class='result-pageNum-info']/span/text()").extract()
        if num_results and num_results[0]:
            return int(num_results[0])
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_next_results_page_link(self, response):
        next_pages = response.css(
            "a:nth-child(3).result-pageNum-iconWrap::attr(href)").extract()

        next_page = None
        if next_pages:
            next_page = next_pages[0]
            if len(next_pages) > 2:
                self.log("Found more than two 'next page' links.", WARNING)
        return next_page
