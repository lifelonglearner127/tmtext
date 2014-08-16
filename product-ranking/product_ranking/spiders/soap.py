from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json

from scrapy.selector import Selector
from scrapy.log import ERROR, WARNING
from scrapy import Request

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set


class SoapProductSpider(BaseProductsSpider):
    name = 'soap_products'
    allowed_domains = ["soap.com"]

    SEARCH_URL = "http://www.soap.com/buy?s={search_term}"

    def parse_product(self, response):
        sel = Selector(response)
        prod = response.meta['product']

        self._populate_from_open_graph(response.url, sel, prod)

        self._populate_from_html(response.url, sel, prod)

        cond_set(prod, 'locale', ['en-US'])  # Default locale.

        json_link = sel.xpath("//*[@id='soapcom']/head/link[@type='application/json+oembed']/@href").extract()[0]

        return Request(json_link, self._parse_json, meta=response.meta.copy(), )

    def _parse_json(self, response):

        product = response.meta['product']

        data = json.loads(response.body)

        brand = data.get('brand')
        title = data.get('title')

        cond_set(product, 'brand', [brand])
        cond_set(product, 'title', [title])

        return product

    def _populate_from_html(self, url, sel, product):

        price = sel.xpath("//*[@id='priceDivClass']/span/text()").extract()[0]

        # desc is a possible <p> or just the text of the class, each page is different
        desc = sel.xpath(
            "//*[@class='pIdDesContent']/p/text() | //*[@class='pIdDesContent']/text()"
            "| //*[@class='pIdDesContent']/b/text()"
            "| //*[@class='pIdDesContent']/p/strong/text()").extract()[0]

        upc = sel.xpath("//*[@class='skuHidden']/@value").extract()[0]

        cond_set(product, 'price', [price])
        cond_set(product, 'description', [desc])
        cond_set(product, 'upc', [upc])

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

        next_pages = sel.css("a:nth-child(3).result-pageNum-iconWrap::attr(href)").extract()

        next_page = None
        if next_pages:
            next_page = next_pages[0]
            if len(next_pages) > 2:
                self.log("Found more than two 'next page' links.", WARNING)
        return next_page