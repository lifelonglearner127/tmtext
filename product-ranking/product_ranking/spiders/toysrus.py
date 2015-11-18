# -*- coding: utf-8 -*-#

import json
import re
import string
import itertools
import urllib

from scrapy.http import FormRequest, Request
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set_value
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi

is_empty = lambda x, y=None: x[0] if x else y


class ToysrusProductSpider(BaseProductsSpider):

    name = 'toysrus_products'
    allowed_domains = ["toysrus.com"]

    # SEARCH_URL = "http://www.debenhams.com/webapp/wcs/stores/servlet/" \
    #              "Navigate?langId=-1&storeId=10701&catalogId=10001&txt={search_term}"
    #
    # items_per_page = 60
    #
    # BUYER_REVIEWS_URL = 'http://debenhams.ugc.bazaarvoice.com/9364redes-en_gb/{upc}/' \
    #                     'reviews.djs?format=embeddedhtml'

    def __init__(self, *args, **kwargs):
        self.br = BuyerReviewsBazaarApi(called_class=self)

        super(ToysrusProductSpider, self).__init__(*args, **kwargs)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        # Set locale
        product['locale'] = 'en_GB'

        # Parse title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title, conv=string.strip)

        # Parse brand
        brand = self._parse_brand(response)
        cond_set_value(product, 'brand', brand)

        # Parse department
        department = self._parse_department(response)
        cond_set_value(product, 'department', department)

        # Parse categories
        categories = self._parse_categories(response)
        cond_set_value(product, 'categories', categories)

        # Parse price
        price = self._parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse special pricing
        special_pricing = self._parse_special_pricing(response)
        cond_set_value(product, 'special_pricing', special_pricing, conv=bool)

        # Parse image url
        image_url = self._parse_image_url(response)
        cond_set_value(product, 'image_url', image_url, conv=string.strip)

        # Parse description
        description = self._parse_description(response)
        cond_set_value(product, 'description', description, conv=string.strip)

        # Parse stock status
        is_out_of_stock = self._parse_stock_status(response)
        cond_set_value(product, 'is_out_of_stock', is_out_of_stock)

        # Parse upc
        upc = self._parse_upc(response)
        cond_set_value(product, 'upc', upc)

        # Parse variants
        variants = self._parse_variants(response)
        cond_set_value(product, 'variants', variants)

        # Parse buyer reviews
        reqs.append(
            Request(
                url=self.BUYER_REVIEWS_URL.format(upc=upc),
                dont_filter=True,
                callback=self.br.parse_buyer_reviews
            )
        )

        # Parse related products
        related_products = self._parse_related_products(response)
        cond_set_value(product, 'related_products', related_products)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_title(self, response):
        pass

    def _parse_brand(self, response):
        pass

    def _parse_department(self, response):
        pass

    def _parse_categories(self, response):
        pass

    def _parse_price(self, response):
        pass

    def _parse_special_pricing(self, response):
        pass

    def _parse_image_url(self, response):
        pass

    def _parse_description(self, response):
        pass

    def _parse_stock_status(self, response):
        pass

    def _parse_upc(self, response):
        pass

    def _parse_variants(self, response):
        pass

    def _parse_related_products(self, response):
        pass

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """

        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _scrape_total_matches(self, response):
        """
        Scraping number of resulted product links
        """
        total_matches = is_empty(
            response.xpath(
                '//span[@class="products_count"]/text()'
            ).extract(), 0
        )

        if total_matches:
            return int(total_matches)
        else:
            return 0

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """
        return self.items_per_page

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """

        items = response.xpath(
            '//div[@id="productDisplay"]/./'
            '/tr[@class="item_container"]'
            '/td[contains(@class, "item")]'
        )

        if items:
            for item in items:
                link = is_empty(
                    item.xpath('././/input[@id="productTileImageUrl"]'
                               '/@value').extract()
                )
                res_item = SiteProductItem()
                yield link, res_item
        else:
            self.log("Found no product links in {url}".format(url=response.url), INFO)

    def _scrape_next_results_page_link(self, response):
        url = is_empty(
            response.xpath(
                '//a[text()="Next"]/@href'
            ).extract()
        )

        if url:
            return url
        else:
            self.log("Found no 'next page' links", WARNING)
            return None
