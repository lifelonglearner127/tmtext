from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re

from scrapy.selector import Selector
from scrapy.log import ERROR, WARNING

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set


class BestBuyProductSpider(BaseProductsSpider):
    name = 'bestbuy_products'
    allowed_domains = ["bestbuy.com"]

    SEARCH_URL = "http://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-" \
                 "8&_dynSessConf=&id=pcat17071&type=page&sc=Global&cp=1&nrp=15&sp=&qp=" \
                 "&list=n&iht=y&usc=All+Categories&ks=960&st={search_term}"

    def parse_product(self, response):
        sel = Selector(response)
        prod = response.meta['product']

        self._populate_from_schemaorg(response.url, sel, prod)

        self._populate_from_html(response.url, sel, prod)

        cond_set(prod, 'locale', ['en-US'])  # Default locale.

        return prod

    def _populate_from_schemaorg(self, url, sel, product):
        product_tree = sel.xpath("//*[@itemtype='http://schema.org/Product']")

        cond_set(product, 'title', product_tree.xpath(
            "descendant::*[not (@itemtype)]/meta[@itemprop='name']/@content"
        ).extract())
        cond_set(product, 'image_url', product_tree.xpath(
            "descendant::*[not (@itemtype)]/img[@itemprop='image']/@src"
        ).extract())
        cond_set(product, 'model', product_tree.xpath(
            "descendant::*[not (@itemtype)]/*[@itemprop='model']/text()"
        ).extract())
        cond_set(product, 'upc', product_tree.xpath(
            "descendant::*[not (@itemtype)]/*[@itemprop='productID']/text()"
        ).extract())
        cond_set(product, 'url', product_tree.xpath(
            "descendant::*[not (@itemtype)]/*[@itemprop='url']/@content"
        ).extract())
        cond_set(
            product,
            'description',
            product_tree.xpath(
                "descendant::*[not (@itemtype)]/"
                "*[@itemprop='description']/node()"
            ).extract(),
            conv=lambda desc_parts: ''.join(desc_parts).strip(),
        )

        offer_tree = product_tree.xpath(
            ".//*[@itemtype='http://schema.org/Offer']"
        )
        cond_set(product, 'price', offer_tree.xpath(
            "descendant::*[not (@itemtype) and @itemprop='price']/@content"
        ).extract())

        brand_tree = product_tree.xpath(
            ".//*[@itemtype='http://schema.org/Brand']"
        )
        cond_set(product, 'brand', brand_tree.xpath(
            "descendant::*[not (@itemtype) and @itemprop='name']/@content"
        ).extract())

    def _populate_from_html(self, url, sel, product):
        title = sel.css("#sku-title ::text").extract()[0]
        brand, _ = re.split(r'\s+-\s+', title, 1)
        cond_set(product, 'title', [title])
        cond_set(product, 'brand', [brand])

        cond_set(product, 'upc', sel.css("#sku-value ::text").extract())
        cond_set(product, 'model', sel.css("#model-value ::text").extract())

    def _scrape_product_links(self, sel):
        links = sel.xpath(
            "//*[@itemtype='http://schema.org/Product']"
            "/descendant::*[not (@itemtype)]//a[@itemprop='url']/@href"
        ).extract()
        if not links:
            self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_total_matches(self, sel):
        num_results = sel.css("#searchstate > b:nth-child(1)::text").extract()
        if num_results and num_results[0]:
            return int(num_results[0])
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_next_results_page_link(self, sel):
        next_pages = sel.css("a.next::attr(href)").extract()
        next_page = None
        if next_pages:
            next_page = next_pages[0]
            if len(next_pages) > 2:
                self.log("Found more than two 'next page' links.", WARNING)
        return next_page
