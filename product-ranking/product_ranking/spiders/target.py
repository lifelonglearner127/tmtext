from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

from scrapy.log import ERROR, WARNING

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    cond_set_value, populate_from_open_graph


class TargetProductSpider(BaseProductsSpider):
    name = 'target_products'
    allowed_domains = ["target.com"]

    SEARCH_URL = "http://www.target.com/s?searchTerm={search_term}"

    def parse_product(self, response):
        prod = response.meta['product']

        populate_from_open_graph(response, prod)

        self._populate_from_html(response, prod)

        cond_set_value(prod, 'locale', 'en-US')  # Default locale.

        return prod

    def _populate_from_html(self, response, product):

        #brand = ''

        price = response.xpath(
            "//span[@itemprop='price']/text()|//*[@id='see-low-price']/a/text()"
        ).extract()
        # some prices are not listed so set those to $0.00
        if price[0] == 'See Low Price in Cart':
            # FIXME If you cannot get a datum, don't set an invalid value.
            cond_set(product, 'price', ['$0.00'])
        else:
            cond_set(product, 'price', price)
        #cond_set(product, 'brand', [brand])

    def _scrape_product_links(self, sel):
        links = sel.xpath(
            "//*[@class='productClick productTitle']/@href"
        ).extract()
        if not links:
            self.log("Found no product links.", ERROR)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_total_matches(self, response):
        num_results = response.css(
            "#breadcrumbResultArea > ul > li > strong:nth-child(2)::text"
        ).extract()
        if num_results:
            try:
                return int(num_results[0])
            except ValueError:
                self.log(
                    "Failed to parse total number of matches: %r"
                    % num_results[0],
                    level=ERROR
                )
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

        return None

    def _scrape_next_results_page_link(self, response):
        next_pages = response.xpath("//li[@class='next']/a/@href").extract()
        next_page = None
        if next_pages:
            next_page = 'http://www.target.com/%s' % next_pages[0]
            if len(next_pages) > 2:
                self.log("Found more than two 'next page' links.", WARNING)
        return next_page
