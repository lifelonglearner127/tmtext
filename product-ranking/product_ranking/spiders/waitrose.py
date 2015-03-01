# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals

import json
import re
import urlparse

from scrapy.http.request.form import FormRequest

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider
from product_ranking.spiders import cond_set_value


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
        product = response.meta['product']
        xpath = '//div[@class="product_disclaimer"]/node()[normalize-space()]'
        cond_set_value(product, 'description', response.xpath(xpath).extract(),
                       ''.join)
        return product

    def _scrape_total_matches(self, response):
        data = WaitroseProductsSpider._get_data(response)
        return data['totalCount']

    def _scrape_product_links(self, response):
        data = WaitroseProductsSpider._get_data(response)
        for product_data in data['products']:
            product = SiteProductItem()
            missing_values = False

            for product_key, data_key in self._PRODUCT_TO_DATA_KEYS.items():
                value = product_data.get(data_key, 'null')
                if value != 'null':
                    product[product_key] = product_data[data_key]
                else:
                    missing_values = True

            # This one is not in the mapping since it requires transformation.
            product['upc'] = int(product_data['productid'])

            if product.get('price', None):
                price = product['price']
                price = price.replace('&pound;', 'p')
                price = re.findall('p? *[\d ,.]+ *p? *', price)
                price = price[0] if price else ''
                if 'p' in price:
                    price = re.sub('[p ,]', '', price)
                    product['price'] = Price(
                        priceCurrency='GBP',
                        price=price
                    )
                else:
                    self.log('Unknown price format at %s' % response)

            if not product.get('url', '').startswith('http'):
                product['url'] = urlparse.urljoin(
                    'http://www.waitrose.com', product['url'])

            if missing_values:
                yield product['url'], product
            else:
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
