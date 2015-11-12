from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json
import hjson
import re
import string
import urllib
import urlparse

from scrapy import Request, Selector
from scrapy.log import DEBUG

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FLOATING_POINT_RGEX, cond_set_value
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.validation import BaseValidator

from lxml import html

is_empty =lambda x,y=None: x[0] if x else y

def is_num(s):
    try:
        int(s.strip())
        return True
    except ValueError:
        return False


# TODO: implement
"""
class LeviValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = ['brand', 'price']
    ignore_fields = [
        'is_in_store_only', 'is_out_of_stock', 'related_products', 'upc',
        'google_source_site', 'description', 'special_pricing',
        'bestseller_rank',
    ]
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = True  # ... duplicated requests?
    ignore_log_filtered = True  # ... filtered requests?
    test_requests = {
        'sdfsdgdf': 0,  # should return 'no products' or just 0 products
        'benny benassi': 0,
        'red car': [20, 150],
        'red stone': [40, 150],
        'musci': [110, 210],
        'funky': [10, 110],
        'bunny': [7, 90],
        'soldering iron': [30, 120],
        'burger': [1, 40],
        'hold': [30, 200],
    }
"""

class LeviProductsSpider(BaseValidator, BaseProductsSpider):
    name = 'levi_products'
    allowed_domains = ["levi.com", "www.levi.com"]
    start_urls = []

    #settings = HomedepotValidatorSettings  # TODO

    SEARCH_URL = "http://www.levi.com/US/en_US/search?Ntt={search_term}"  # TODO: ordering

    PAGINATE_URL = ('http://www.levi.com/US/en_US/includes/searchResultsScroll/?nao={nao}'
                    '&url=%2FUS%2Fen_US%2Fsearch%2F%3FD%3D{search_term}%26Dx'
                    '%3Dmode%2Bmatchall%26N%3D4294960840%2B4294961101%2B4294965619%26Ns'
                    '%3Dp_price_US_USD%257C0%26Ntk%3DAll%26Ntt%3Dmen%26Ntx%3Dmode%2Bmatchall')
    CURRENT_NAO = 0
    PAGINATE_BY = 12  # 12 products
    TOTAL_MATCHES = None  # for pagination

    def __init__(self, *args, **kwargs):
        super(LeviProductsSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        product = response.meta.get('product', SiteProductItem())

        self.product_id = is_empty(response.xpath('//meta[@itemprop="model"]/@content').extract())

        title = self.parse_title(response)
        cond_set(product, 'title', title)

        image = self.parse_image(response)
        cond_set_value(product, 'image_url', image)

        return product

    def parse_title(self, response):
        title = response.xpath(
            '//h1[contains(@class, "title")]').extract()

        return title

    def parse_image(self, response):
        data = re.findall(r'var buyStackJSON = \'(.+)\'; ', response.body_as_unicode())
        data = re.sub(r'\\(.)', r'\g<1>', data[0])
        if data:
            try:
                image_data = json.loads(data)
                image = image_data['colorid'][self.product_id]['gridUrl']
            except:
                pass
        return image

    def _scrape_total_matches(self, response):
        totals = response.css('.productCount ::text').extract()
        if totals:
            totals = totals[0].replace(',', '').replace('.', '').strip()
            if totals.isdigit():
                if not self.TOTAL_MATCHES:
                    self.TOTAL_MATCHES = int(totals)
                return int(totals)

    def _scrape_product_links(self, response):
        for link in response.xpath(
            '//li[contains(@class, "product-tile")]'
            '//a[contains(@rel, "product")]/@href'
        ).extract():
            yield link, SiteProductItem()

    def _get_nao(self, url):
        nao = re.search(r'nao=(\d+)', url)
        if not nao:
            return
        return int(nao.group(1))

    def _replace_nao(self, url, new_nao):
        current_nao = self._get_nao(url)
        if current_nao:
            return re.sub(r'nao=\d+', 'nao='+str(new_nao), url)
        else:
            return url+'&nao='+str(new_nao)

    def _scrape_next_results_page_link(self, response):
        print '_'*8, response
        if self.CURRENT_NAO > self._scrape_total_matches(response)+self.PAGINATE_BY:
            return  # it's over
        self.CURRENT_NAO += self.PAGINATE_BY
        return Request(
            self.PAGINATE_URL.format(
                search_term=response.meta['search_term'],
                nao=str(self.CURRENT_NAO)),
            callback=self.parse, meta=response.meta
        )