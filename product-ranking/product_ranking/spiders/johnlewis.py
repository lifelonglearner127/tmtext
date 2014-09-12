from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider
from product_ranking.spiders import _extract_open_graph_metadata
from product_ranking.spiders import _populate_from_open_graph_product
from product_ranking.spiders import cond_set, cond_set_value
from scrapy.log import ERROR


class JohnlewisProductsSpider(BaseProductsSpider):
    name = 'johnlewis_products'
    allowed_domains = ["www.johnlewis.com"]
    start_urls = []
    SEARCH_URL = "http://www.johnlewis.com/search/{search_term}"

    def _populate_from_open_graph(self, response, product):
        metadata = _extract_open_graph_metadata(response)
        if metadata.get('type') == 'Product':
            metadata['type'] = 'product'
        _populate_from_open_graph_product(response, product, metadata=metadata)
        cond_set_value(product, 'title', metadata.get('title'))

    def parse_product(self, response):
        product = response.meta['product']

        self._populate_from_open_graph(response, product)

        cond_set(
            product,
            'brand',
            response.xpath(
                "//section/div[@id='prod-info-tab']"
                "/descendant::div[@itemprop='brand']"
                "/span[@itemprop='name']/text()").extract(),
            conv=string.strip
        )

        cond_set(
            product,
            'price',
            response.xpath(
                "//section/div[@id='prod-price']/p[@class='price']"
                "/strong/text()").extract(),
            conv=string.strip
        )

        cond_set(
            product,
            'upc',
            response.xpath(
                "//div[@id='prod-product-code']/p/text()").extract(),
            conv=int
        )
        return product

    def _scrape_total_matches(self, response):
        total = response.xpath(
            "//section[@class='search-results']/header/h1/span/text()"
        ).extract()
        print "TOTAL=", total

        if total:
            total = total[0]
            try:
                return int(total)
            except ValueError:
                return 0
        else:
            return 0

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//div[@class='result-row']"
            "/article/a[@class='product-link']/@href").extract()
        print "LINKS=", len(links)

        def full_url(url):
            return urlparse.urljoin(response.url, url)

        # for no, link in enumerate(links):
        #     print no, full_url(link)

        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield full_url(link), SiteProductItem()

    def _scrape_next_results_page_link(self, response):

        def full_url(url):
            return urlparse.urljoin(response.url, url)

        next = response.xpath(
            "//div[@class='pagination']/ul[@role='navigation']"
            "/li[@class='next']/a/@href").extract()
        if next:
            if next[0] == '#':
                return None
            next = full_url(next[0])
            return next
