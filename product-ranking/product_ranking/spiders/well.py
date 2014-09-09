from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string

from scrapy.log import ERROR

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set


class LondondrugsProductsSpider(BaseProductsSpider):
    name = 'well_products'
    allowed_domains = ["well.ca"]
    start_urls = []
    SEARCH_URL = "https://well.ca/searchresult.html?keyword={search_term}"

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(
            product,
            'title',
            response.xpath(
                "//div[@class='product_info_header']"
                "/div[contains(@class,'product_text_product_name')]/text()"
            ).extract(),
            conv=string.strip,
        )

        cond_set(
            product,
            'price',
            response.xpath(
                "//div[@class='product_text_price']/text()"
            ).extract(),
            conv=string.strip,
        )

        cond_set(
            product,
            'brand',
            response.xpath(
                "//div[@class='product_info_header']/div/a/text()"
            ).re(r'View all (.*) products'),
        )

        cond_set(
            product,
            'image_url',
            response.xpath(
                "//div[@class='product_main_image']/img/@src"
            ).extract(),
        )

        cond_set(
            product,
            'description',
            response.xpath(
                "//div[@class='products_description_container']/div/text()"
            ).extract(),
        )

        def make_list(rlist):
            prodlist = []
            for r in rlist:
                href = r.xpath("a/@href").extract()[0]
                text = r.xpath("a/text()").extract()[0]
                prodlist.append(RelatedProduct(text, href))
            return prodlist
        rlist = response.xpath(
            "//div[@id='recommended_container']"
            "/div[@class='related_product_grid']")
        related_list = make_list(rlist)

        rlist = response.xpath(
            "//div[@id='people_who_bought_also_bought']"
            "/div[@class='related_product_grid']")
        alsob_list = make_list(rlist)

        product['related_products'] = {
            "recommended": related_list,
            "also_bought": alsob_list,
        }

        cond_set(
            product,
            'upc',
            response.xpath(
                "//form[@name='cart_quantity']/div/input[@name='products_id']"
                "/@value"
            ).extract(),
            conv=int,
        )

        product['locale'] = "en-CA"

        return product

    def _scrape_total_matches(self, response):
        total = response.xpath(
            "//div[@class='title']/h3/small"
            "/text()").re(r'\((\d+) Products\)')
        if total:
            return int(total[0])
        return 0

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//div[@class='main_search_result']"
            "/div[@id='categories_main_content']"
            "/div[@class='product_grid_full_categories']/a/@href").extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        links = response.xpath(
            "//div[@class='main_search_result']/a[@id='next']/@href")
        next_page = None
        if links:
            next_page = links.extract()[0]
        return next_page
