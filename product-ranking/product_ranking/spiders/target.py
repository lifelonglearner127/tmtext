from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

from scrapy.selector import Selector
from scrapy.log import ERROR, WARNING
from scrapy import Request

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set


class TargetProductSpider(BaseProductsSpider):
    name = 'target_products'
    allowed_domains = ["target.com"]

    SEARCH_URL = "http://www.target.com/s?searchTerm={search_term}"

    def parse_product(self, response):
        sel = Selector(response)

        prod = response.meta['product']

        self._populate_from_open_graph(response.url, sel, prod)

        self._populate_from_html(response.url, sel, prod)

        cond_set(prod, 'locale', ['en-US'])  # Default locale.

        return prod

    def _populate_from_html(self, url, sel, product):

        #brand = ''

        price = sel.xpath("//span[@itemprop='price']/text()|//*[@id='see-low-price']/a/text()").extract()
        # some prices are not listed so set those to $0.00
        if price[0] == 'See Low Price in Cart':
            cond_set(product, 'price', ['$0.00'])
        else:
            cond_set(product, 'price', [price[0]])
        #cond_set(product, 'brand', [brand])

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
        product['title'] = metadata['title']
        product['description'] = metadata['description']
        # some products do not have the upc listed anywhere
        if 'upc' in metadata:
            product['upc'] = metadata['upc']

    def _scrape_product_links(self, sel):

        links = sel.xpath(
            "//*[@class='productClick productTitle']/@href"
        ).extract()
        if not links:
            self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_total_matches(self, sel):

        num_results = sel.css("#breadcrumbResultArea > ul > li > strong:nth-child(2)::text").extract()
        if num_results and num_results[0]:
            return int(num_results[0])
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_next_results_page_link(self, sel):

        next_pages = sel.xpath("//li[@class='next']/a/@href").extract()
        next_page = None
        if next_pages:
            next_page = 'http://www.target.com/%s' % next_pages[0]
            if len(next_pages) > 2:
                self.log("Found more than two 'next page' links.", WARNING)
        return next_page
