# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json
import urlparse

from scrapy.http.request.form import FormRequest

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider


class WaitroseProductsSpider(BaseProductsSpider):
    name = "waitrose_products"
    allowed_domains = ["waitrose.com"]
    start_urls = []

    SEARCH_URL = "http://www.waitrose.com/shop/BrowseAjaxCmd"
    _DATA = "Groceries/refined_by/search_term/{search_term}/sort_by/NONE" \
        "/sort_direction/descending/page/{page}"

    _PRODUCT_TO_DATA_KEYS = {
        'title': 'name',
        'image_url': 'image',
        'url': 'url',
        'price': 'price',
        'description': 'summary',
    }

    @staticmethod
    def _get_data(response):
        """Helper function that parses JSON data from the response's body using
        a cache.
        """
        try:
            data = response.meta['parsed_data']
        except KeyError:
            data = json.loads(response.body_as_unicode())
            # Cache the parsed data.
            response.meta['parsed_data'] = data

        return data

    @staticmethod
    def _create_request(meta):
        return FormRequest(
            url=WaitroseProductsSpider.SEARCH_URL,
            formdata={
                'browse': WaitroseProductsSpider._DATA.format(
                    search_term=meta['search_term'], page=meta['current_page']),
            },
            meta=meta,
        )

    def start_requests(self):
        """Generates POSTs instead of GETs."""
        for st in self.searchterms:
            yield self._create_request(
                meta={
                    'search_term': st,
                    'remaining': self.quantity,
                    'current_page': 1,
                },
            )

    def parse_product(self, response):
        raise AssertionError("This method should never be called.")

    def _scrape_total_matches(self, response):
        data = WaitroseProductsSpider._get_data(response)
        return data['totalCount']

    def _scrape_product_links(self, response):
        data = WaitroseProductsSpider._get_data(response)
        for product_data in data['products']:
            product = SiteProductItem()

            for product_key, data_key in self._PRODUCT_TO_DATA_KEYS.items():
                product[product_key] = product_data[data_key]

            # This one is not in the mapping since it requires transformation.
            product['upc'] = int(product_data['productid'])

            if product.get('price', None):
                product['price'] = product['price'].replace('&pound;', '£')
                if not '£' in product['price']:
                    self.log('Unknown currency at %s' % self.response)
                else:
                    product['price'] = Price(
                        priceCurrency='GBP',
                        price=product['price'].replace('£', '').replace(
                            ' ', '').replace(',', '').strip()
                    )

            if not product.get('url', '').startswith('http'):
                product['url'] = urlparse.urljoin(
                    'http://www.waitrose.com', product['url'])

            yield None, product

    def _scrape_next_results_page_link(self, response):
        data = WaitroseProductsSpider._get_data(response)
        if response.meta['current_page'] >= data['numberOfPages']:
            request = None
        else:
            meta = response.meta.copy()
            meta['current_page'] += 1
            request = self._create_request(meta)

        return request
