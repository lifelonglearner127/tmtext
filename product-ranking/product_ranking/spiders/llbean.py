# coding=utf-8
from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re
import json
import urllib

from product_ranking.items import SiteProductItem, RelatedProduct, Price
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults


class LLBeanProductsSpider(BaseProductsSpider):
    name = 'llbean_products'
    allowed_domains = ["llbean.com"]
    start_urls = []

    SEARCH_URL = "http://www.llbean.com/llb/gnajax/2?storeId=1&catalogId=1" \
                 "&langId=-1&position={pagenum}&sort_field={search_sort}&freeText={search_term}"

    URL = "http://www.llbean.com"

    SEARCH_SORT = {
        'best_match': 'Relevance',
        'high_price': 'Price+(Descending)',
        'low_price': 'Price+(Ascending)',
        'best_sellers': 'Num_Of_Orders',
        'avg_review': 'Grade+(Descending)',
        'product_az': 'Name+(Ascending)',
    }

    image_url = "http://cdni.llbean.com/is/image/wim/"
    product_url = "http://www.llbean.com/"

    def __init__(self, search_sort='best_match', *args, **kwargs):
        super(LLBeanProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(pagenum=1,
                                                search_sort=self.SEARCH_SORT[search_sort]
            ),
            *args,
            **kwargs)

    def parse_product(self, response):
        raise AssertionError("This method should never be called.")

    def _scrape_total_matches(self, response):
        data = json.loads(response.body_as_unicode())
        response.meta['position'] = {}
        response.meta['position'] = data[0]['productsPerPage']
        return data[0]['pageFoundSize']

    def _scrape_product_links(self, response):
        data = json.loads(response.body_as_unicode())

        for item in data[0]['products']:
            prod = SiteProductItem()
            prod['title'] = item['name']
            prod['brand'] = item['brand']
            price=None
            if item['swatchPrice']:
                if re.match("\d+(.\d+){0,1}", item['swatchPrice'][0]['val']):
                    price = item['swatchPrice'][0]['val']
                prod['price'] = Price(priceCurrency="USD", price=price)
            prod['description'] = item['qrtxt']
            prod['upc'] = item['item'][0]['prodId']
            prod['image_url'] = self.image_url + item['img']
            prod['url'] = self.product_url + item['displayUrl']
            if item['item'][0]['stock'] == "IN":
                prod['is_out_of_stock'] = True
            else:
                prod['is_out_of_stock'] = False

            prod['locale'] = "en-US"

            yield None, prod

    def _scrape_next_results_page_link(self, response):
        data = json.loads(response.body_as_unicode())
        if response.meta['position'] == 48:
            pos = 49
            response.meta['position'] = pos
        else:
            pos = response.meta['position'] + data[0]['productsPerPage']
            response.meta['position'] = pos
        max_pages = data[0]['pageFoundSize']
        cur_page = pos
        if cur_page >= max_pages:
            return None

        st = urllib.quote(data[0]['originalSearchTerm'])
        return self.url_formatter.format(self.SEARCH_URL,
                                         search_term=st,
                                         pagenum=cur_page)
