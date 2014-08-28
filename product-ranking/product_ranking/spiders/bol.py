from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string

from scrapy.log import ERROR

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value


class BolProductsSpider(BaseProductsSpider):
    name = 'bol_products'
    allowed_domains = ["bol.com"]
    start_urls = []
    SEARCH_URL = "http://www.bol.com/nl/s/algemeen/zoekresultaten/Ntt/" \
        "{search_term}/N/0/Nty/1/search/true/searchType/qck/sc/media_all/" \
        "index.html"

    def parse_product(self, response):
        product = response.meta['product']
        cond_set(product, 'brand', response.xpath(
            "//div/span/a[@itemprop='brand']/text()").extract())

        cond_set(
            product,
            'title',
            response.xpath(
                "//div[contains(@class,'product_heading')]"
                "/h1[@itemprop='name']/text()"
            ).extract(),
            conv=string.strip)

        cond_set(
            product,
            'image_url',
            response.xpath(
                "//div[contains(@class,'product_zoom_wrapper')]"
                "/img[@itemprop='image']/@src"
            ).extract(),
            conv=string.strip,
        )

        cond_set(
            product,
            'price',
            response.xpath(
                "//span[@class='offer_price']/meta[@itemprop='price']/@content"
            ).extract())

        j = response.xpath(
            "//div[contains(@class,'product_description')]/div"
            "/div[@class='content']/descendant::*[text()]/text()"
        )
        cond_set_value(product, 'description', "\n".join(
            x.strip() for x in j.extract() if x.strip()))

        cond_set(
            product,
            'upc',
            response.xpath("//meta[@itemprop='sku']/@content").extract(),
            conv=int,
        )

        cond_set(product, 'locale', response.xpath("//html/@lang").extract())

        rel = response.xpath(
            "//div[contains(@class,'tst_inview_box')]/div"
            "/div[@class='product_details_mini']/span/a")
        recommended_prods = []
        for r in rel:
            try:
                href = r.xpath('@href').extract()[0]
                title = r.xpath('@title').extract()[0]
                recommended_prods.append(RelatedProduct(title, href))
            except IndexError:
                pass
        if recommended_prods:
            product['related_products'] = {"recommended": recommended_prods}

        return product

    def _scrape_total_matches(self, response):
        totals = response.xpath(
            "//h1[@itemprop='name']/span[@id='sab_header_results_size']/text()"
        ).extract()
        if totals:
            total = totals[0].replace(".", "")
            try:
                total_matches = int(total)
            except ValueError:
                self.log(
                    "Failed to parse number of matches: %r" % total, ERROR)
                total_matches = None
        elif "Geen zoekresultaat" in response.body_as_unicode():
            total_matches = 0
        else:
            total_matches = None

        return total_matches

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//div[contains(@class,'productlist_block')]"
            "/div[@class='product_details_thumb']"
            "/div/div/a[@class='product_name']/@href").extract()
        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next_page_links = response.xpath(
            "//div[contains(@class,'tst_searchresults_next')]/span/a/@href")
        if next_page_links:
            return next_page_links.extract()[0]
