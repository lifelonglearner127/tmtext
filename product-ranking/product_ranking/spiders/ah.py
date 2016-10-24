# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re
import json

from scrapy.log import ERROR, DEBUG
from scrapy.http import Request

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import (BaseProductsSpider, FormatterWithDefaults)


class AhProductsSpider(BaseProductsSpider):
    name = 'ah_products'
    allowed_domains = ["ah.nl"]
    BASE_URL = 'http://www.ah.nl'
    start_urls = []

    SEARCH_URL = BASE_URL + '/service/rest/delegate?url=' \
                                 '/zoeken?rq={search_term}&sorting={sort}'

    REST_PROD_URL = BASE_URL + '/service/rest/delegate?url=/producten/' \
                               'product/{product_id}/{product_name}'

    REGEXP_PROD_URL = re.compile('^(https?://)?(www.)?ah.nl/(producten/'
                                 'product/(?P<product_id>[^/]+)/'
                                 '(?P<product_name>[^/]+)/?)')

    SORT_BY = {
        'relevance': 'relevance',
        'name': 'name_asc',
    }

    PRICE_CURRENCY = 'EUR'

    def __init__(self, *args, **kwargs):
        self.sort_by = self.SORT_BY.get(
            kwargs.get('order', 'relevance'), 'relevance')
        formatter = FormatterWithDefaults(sort=self.sort_by)
        super(AhProductsSpider, self).__init__(formatter, *args, **kwargs)

    def _parse_single_product(self, response):
        product = self.REGEXP_PROD_URL.search(response.url)
        if not product:
            self.log('Can\'t parse product url.', ERROR)
            return
        product = product.groupdict()
        meta = response.meta
        meta.update(product)
        yield Request(
            self.REST_PROD_URL.format(
                product_name=product['product_name'],
                product_id=product['product_id']
            ),
            callback=self.parse_single_product,
            meta=meta
        )

    def parse_single_product(self, response):
        product_info = None
        try:
            body = json.loads(response.body)
            for lane in body['_embedded']['lanes']:
                _type = lane.get('type')
                if not _type or _type != 'ProductDetailLane':
                    continue
                product_info = \
                    lane['_embedded']['items'][0]['_embedded']['product']
                break
            if not product_info:
                raise Exception('Product was not found.')
        except Exception as e:
            self.log('Error while parse single product. ERROR: %s.' % str(e),
                     ERROR)
            return
        return self.__parse_product(response.meta['product'], product_info)

    def __parse_product(self, product, product_info):
        try:
            product['category'] = product_info['categoryName']
            product['description'] = product_info['description']
            if isinstance(product_info.get('images'), list):
                a = [img['height'] for img in product_info['images']
                     if 'height' in img]
                image = product_info['images'][a.index(max(a))]
                product['title'] = image['title']
                product['image_url'] = image['link']['href']
            product['brand'] = product_info.get('brandName')
            product['price'] = Price(
                priceCurrency=self.PRICE_CURRENCY,
                price=product_info['priceLabel']['now']
            )
        except Exception as e:
            self.log('Error while parse product. ERROR: %s.' % str(e), ERROR)
            return None
        return product

    def _get_products(self, response):
        product_list = None
        try:
            body = json.loads(response.body)
            for lane in body['_embedded']['lanes']:
                _type = lane.get('type')
                if not _type or _type != 'SearchLane':
                    continue
                product_list = lane['_embedded']['items']
                break
            if not product_list:
                self.log('Products was not found.', DEBUG)
                return
            for product_info in product_list:
                product = self.__parse_product(
                    SiteProductItem(),
                    product_info['_embedded']['product']
                )
                if not product:
                    continue
                product['url'] = \
                    self.BASE_URL + product_info['navItem']['link']['href']
                yield product
        except Exception as e:
            self.log('Can\'t parse product list body. ERROR: %s.' % str(e),
                     ERROR)
            return

    def _scrape_next_results_page_link(self, response):
        next_url = None
        try:
            body = json.loads(response.body)
            for lane in body['_embedded']['lanes']:
                _type = lane['type']
                if not _type or _type != 'LoadMoreLane':
                    continue
                next_url = lane['navItem']['link']['href']
                break
        except Exception as e:
            self.log('Can\'t find next page. ERROR: %s.' % str(e), ERROR)
            return None

        if not next_url:
            return None

        return Request(
            self.BASE_URL + next_url,
            callback=self._get_products
        )

    def _scrape_total_matches(self, response):
        try:
            body = json.loads(response.body)
            # Set total results
            self.total_results = \
                int(body['_meta']['analytics']['parameters']
                    ['ns_search_result'])
            return self.total_results
        except Exception as e:
            self.log('Error: %s' % str(e))
            return 0
