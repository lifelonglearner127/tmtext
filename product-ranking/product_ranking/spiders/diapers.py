from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re

from scrapy.selector import Selector
from scrapy.log import ERROR, WARNING
from scrapy import Request

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set

import json


class DiapersProductSpider(BaseProductsSpider):
    name = 'diapers_products'
    allowed_domains = ["diapers.com"]

    SEARCH_URL = "http://www.diapers.com/buy?s={search_term}"

    def parse_product(self, response):
        sel = Selector(response)
        prod = response.meta['product']

        self._populate_from_open_graph(response.url, sel, prod)

        self._populate_from_js(response.url, sel, prod)

        cond_set(prod, 'locale', ['en-US'])  # Default locale.

        json_link = sel.xpath("//*[@id='diaperscom']/head/link[@type='application/json+oembed']/@href").extract()[0]

        return Request(json_link, self._parse_json, meta=response.meta.copy(), )

    def _parse_json(self, response):

        product = response.meta['product']

        data = json.loads(response.body)

        brand = data.get('brand')
        title = data.get('title')

        cond_set(product, 'brand', [brand])
        product['title'] = title

        return product

    def _populate_from_js(self, url, sel, product):

        scripts = sel.xpath("//script[contains(text(), 'var pdpOptionsJson=')]")
        if not scripts:
            self.log("No JS matched in %s, parsing the html itself." % url, WARNING)
            self._populate_from_html(url, sel, product)
            return None, None

        myjson = scripts.re("var pdpOptionsJson=\s(.+\])")

        if not myjson:
            self.log("Could not get JSON match in %s" % url, WARNING)
            return None, None
        else:
            data = json.loads(myjson[0])
            product['upc'] = data[0].get("Sku")  # first one in list is the product being scraped
            product['price'] = data[0].get("DisplayPrice")
            product['description'] = data[0].get("Description")


    def _populate_from_html(self, url, sel, product):

        price = sel.xpath("//*[@id='priceDivClass']/span/text()").extract()[0]
        desc = sel.xpath("//*[@id='Tab5DetailInfo']/div/div/p[2]/text()").extract()[0]
        # I could not get either of the below to get a upc
        #upc = sel.xpath("//*[@id='pdpUniversalOption']/@data-displayunitprice").extract()
        #upc = sel.re('primarySku."(.+\d)"')
        product['price'] = price
        product['description'] = desc

    def _populate_from_open_graph(self, url, sel, product):
        """See about the Open Graph Protocol at http://ogp.me/"""
        # Extract all the meta tags with an attribute called property.
        metadata_dom = sel.xpath("/html/head/meta[@property]")
        props = metadata_dom.xpath("@property").extract()
        conts = metadata_dom.xpath("@content").extract()

        # Create a dict of the Open Graph protocol.
        metadata = {p[3:]: c for p, c in zip(props, conts)
                    if p.startswith('og:')}

        if metadata.get('type') != 'product':
            # This response is not a product?
            self.log("Page of type '%s' found." % metadata.get('type'), ERROR)
            raise AssertionError("Type missing or not a product.")

        # Basic Open Graph metadata.
        product['url'] = metadata['url']  # Canonical URL for the product.
        product['image_url'] = metadata['image']

    def _scrape_product_links(self, sel):
        links = sel.xpath(
            "//*[contains(concat( ' ', @class, ' ' ), concat( ' ', 'pdpLinkable', ' '))]/a/@href"
        ).extract()
        if not links:
            self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_total_matches(self, sel):

        num_results = sel.xpath("//*[@class='result-pageNum-info']/span/text()").extract()
        if num_results and num_results[0]:
            return int(num_results[0])
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_next_results_page_link(self, sel):
        # next_pages = sel.css("a.result-pageNum-iconWrap::attr(href)").extract()
        next_pages = sel.xpath('//span[contains(@class,"result-pageNum-link")]/a[2]/@href').extract()

        next_page = None
        if next_pages:
            next_page = next_pages[0]
            if len(next_pages) > 2:
                self.log("Found more than two 'next page' links.", WARNING)
        return next_page
