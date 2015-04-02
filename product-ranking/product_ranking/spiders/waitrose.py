# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals

import json
import re
import urlparse

from scrapy.http.request.form import FormRequest

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider, cond_set
from product_ranking.spiders import cond_set_value






# FIXME No reviews for page http://www.waitrose.com/shop/DisplayProductFlyout?productId=71298
# FIXME No 'also viewed' related products for http://www.waitrose.com/shop/DisplayProductFlyout?productId=71298
# FIXME Empty 'brand' field.
# FIXME Empty 'locale' field.
# FIXME Field image_url not started with 'http:' u'//d3l6n8hsebkot8.cloudfront.net/images/products/9/LN_504898_BP_9.jpg'

class WaitroseProductsSpider(BaseProductsSpider):
    name = "waitrose_products"
    allowed_domains = ["waitrose.com"]
    start_urls = []


    SEARCH_URL = "http://www.waitrose.com/shop/BrowseAjaxCmd"
    _DATA = "Groceries/refined_by/search_term/{search_term}/sort_by/{order}" \
            "/sort_direction/{direction}/page/{page}"

    _PRODUCT_TO_DATA_KEYS = {
        'title': 'name',
        'image_url': 'image',
        'url': 'url',
        'price': 'price',
        'description': 'summary',
    }

    SORT_MODES = {
        'default': ('NONE', 'descending'),
        'popularity': ('popularity', 'descending'),
        'rating': ('averagerating', 'descending'),
        'name_asc': ('name', 'ascending'),
        'name_desc': ('name', 'descending'),
        'price_asc': ('price', 'ascending'),
        'price_desc': ('price', 'descending')
    }

    def __init__(self, order='default', *args, **kwargs):
        super(WaitroseProductsSpider, self).__init__(*args, **kwargs)
        if order not in self.SORT_MODES:
            raise Exception('Sort mode %s not found' % order)
        self._sort_order = order

    @staticmethod
    def _get_data(response):
        return json.loads(response.body_as_unicode())

    def _create_request(self, meta):
        order, direction = self.SORT_MODES[self._sort_order]
        return FormRequest(
            url=WaitroseProductsSpider.SEARCH_URL,
            formdata={
                'browse': WaitroseProductsSpider._DATA.format(
                    search_term=meta['search_term'],
                    page=meta['current_page'],
                    order=order,
                    direction=direction)
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
        cond_set(product, 'brand',
                 response.css('.at-a-glance span::text').re('Brand (.+)'))
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
                price = re.findall('(p? *[\d ,.]+ *p?) *', price)
                price = price[0] if price else ''
                if price.endswith('p'):
                    price = '0.' + price.strip()
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
