from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string

from scrapy.log import ERROR

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set


# FIXME Lacks the brand.
# FIXME Fails when there are no matches.
# FIXME Some duplicates are filtered.

class WoolworthsProductsSpider(BaseProductsSpider):
    name = 'woolworths_products'
    allowed_domains = ["woolworthsonline.com.au"]
    start_urls = []

    SEARCH_URL = "http://www2.woolworthsonline.com.au/Shop/SearchProducts" \
        "?search={search_term}"

    def parse_product(self, response):
        product = response.meta['product']

        self._populate_from_open_graph(response, product)

        price = response.xpath(
            "//span[@class='price']/text()"
            "| //span[@class='price special-price']/text()"
        ).extract()
        cond_set(product, 'price', price, string.strip)

        cond_set(product, 'upc', response.xpath(
            "//input[@id='stockcode']/@value").extract())

        product['locale'] = "en-AU"

        return product

    def _populate_from_open_graph(self, response, product):
        """See about the Open Graph Protocol at http://ogp.me/"""
        # Extract all the meta tags with an attribute called property.
        metadata_dom = response.xpath("/html/head/meta[@property]")
        props = metadata_dom.xpath("@property").extract()
        conts = metadata_dom.xpath("@content").extract()

        # Create a dict of the Open Graph protocol.
        metadata = {p[3:]: c for p, c in zip(props, conts)
                    if p.startswith('og:')}

        # the following type for every page I checked was a website and not a product
        # even though every item was for a product, removed raise assertion for now
        # JR: This is because the Open Graph vocabulary to describe a website is
        #     used, not the prod.
        # FIXME Implement OpenGraph for type website in parent class. Is it useful?
        if metadata.get('type') != 'product':
            # This response is not a product?
            self.log("Page of type '%s' found." % metadata.get('type'), ERROR)
        #   raise AssertionError("Type missing or not a product.")

        # Basic Open Graph metadata.
        product['url'] = metadata['url']  # Canonical URL for the product.
        product['image_url'] = metadata['image']
        product['description'] = metadata['description']
        product['title'] = metadata['title']

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
