# -*- coding: utf-8 -*-

# TODO:
# image url
# zip code "in stock" check
#

from __future__ import division, absolute_import, unicode_literals

import json
import re
from urllib import urlencode
import urlparse
import datetime
import os
import time

from scrapy import Request
from scrapy.http.request.form import FormRequest
from scrapy.dupefilter import RFPDupeFilter
from scrapy.conf import settings
from scrapy.utils.request import request_fingerprint

from product_ranking.items import SiteProductItem, Price, BuyerReviews, \
    RelatedProduct
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set
from product_ranking.spiders import cond_set_value


is_empty = lambda x, y=None: x[0] if x else y


class CustomHashtagFilter(RFPDupeFilter):
    """ Considers hashtags to be a unique part of URL """

    @staticmethod
    def rreplace(s, old, new, occurrence):
        li = s.rsplit(old, occurrence)
        return new.join(li)

    def _get_unique_url(self, url):
        return self.rreplace(url, '#', '_', 1)

    def request_seen(self, request):
        fp = self._get_unique_url(request.url)
        if fp in self.fingerprints:
            return True
        self.fingerprints.add(fp)
        if self.file:
            self.file.write(fp + os.linesep)


class ATTProductsSpider(BaseProductsSpider):
    name = "att_products"
    allowed_domains = ["att.com",
                       'api.bazaarvoice.com',
                       'recs.richrelevance.com']

    PAGINATE_URL = "https://www.att.com/global-search/search_ajax.jsp?q={search_term}" \
                   "&sort=score%20desc&fqlist=&colPath=--sep--Shop--sep--All--sep--" \
                   "&gspg={page_num}&dt={datetime}"

    SEARCH_URL = "https://www.att.com/global-search/search_ajax.jsp?q={search_term}" \
                 "&sort=score%20desc&fqlist=&colPath=--sep--Shop--sep--All--sep--" \
                 "&gspg=0&dt=" + str(time.time())

    VARIANTS_URL = "https://www.att.com/services/shopwireless/model/att/ecom/api/" \
                   "DeviceDetailsActor/getDeviceProductDetails?" \
                   "includeAssociatedProducts=true&includePrices=true&skuId={sku}"

    current_page = 0

    def __init__(self, *args, **kwargs):
        settings.overrides["DUPEFILTER_CLASS"] = 'product_ranking.spiders.att.CustomHashtagFilter'
        super(ATTProductsSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

    def _scrape_product_links(self, response):
        serp_links = response.xpath(
            '//ul[contains(@class, "resultList")]//'
            'a[contains(@class, "resultLink")]/@href').extract()
        #new_meta = response.meta
        #new_meta['product'] = SiteProductItem()
        for link in serp_links:
            #yield Request(link, meta=response.meta, dont_filter=True,
            #              callback=self.parse_product), SiteProductItem()
            yield link, SiteProductItem()

    def _parse_single_product(self, response):
        return self.parse_product(response)

    @staticmethod
    def _get_sku(response):
        sku = re.search(r'skuId=([a-zA-Z0-9]+)', response.url)
        if sku:
            return sku.group(1)
        sku = response.xpath('//meta[contains(@name, "sku")]/@CONTENT').extract()
        if not sku:
            sku = response.xpath('//meta[contains(@name, "sku")]/@content').extract()
        if sku:
            return sku[0]

    @staticmethod
    def _parse_title(response):
        title = response.xpath('//h1[contains(@id, "accPageTitle")]/text()').extract()
        if not title:
            title = response.xpath('//h1//text()').extract()
        if title:
            return title[0].strip()

    @staticmethod
    def _parse_ajax_variants(response):
        # TODO:
        pass

    def _parse_ajax_product_data(self, response):
        prod = response.meta['product']
        v = json.loads(response.body)
        prod['brand'] = v['result']['methodReturnValue'].get('manufacturer', '')
        prod['variants'] = self._parse_ajax_variants(
            v['result']['methodReturnValue'].get('skuItems', {}))
        # get data of selected (default) variant
        sel_v = v['result']['methodReturnValue'].get('skuItems', {}).get(
            response.meta['selected_sku'])
        prod['is_out_of_stock'] = sel_v['outOfStock']
        prod['model'] = sel_v.get('model', '')
        _price = sel_v.get('priceList', [{}])[0].get('listPrice', None)
        if _price:
            prod['price'] = Price(price=_price, priceCurrency='USD')
        prod['is_in_store_only'] = not sel_v.get('retailAvailable', True)
        prod['title'] = sel_v['displayName']
        prod['sku'] = response.meta['selected_sku']

        yield prod

    def parse_product(self, response):
        product = response.meta['product']
        product['_subitem'] = True
        product['title'] = self._parse_title(response)
        cond_set(
            product, 'description',
            response.xpath('//meta[contains(@property,"og:description")]/@content').extract())
        cond_set(
            product, 'image_url',
            response.xpath('//meta[contains(@property,"og:image")]/@content').extract())
        new_meta = response.meta
        new_meta['product'] = product
        new_meta['selected_sku'] = self._get_sku(response)
        if '{{' in product['title']:
            # we got a bloody AngularJS-driven page, parse it
            return Request(
                self.VARIANTS_URL.format(sku=self._get_sku(response)),
                callback=self._parse_ajax_product_data,
                meta=new_meta)
        return product

    def _scrape_next_results_page_link(self, response):
        self.current_page += 1
        if not list(self._scrape_product_links(response)):
            return  # end of pagination reached
        return self.PAGINATE_URL.format(
            search_term=self.searchterms[0], page_num=self.current_page,
            datetime=time.time())

    def _scrape_total_matches(self, response):
        result_count = response.xpath(
            '//span[contains(@class, "topResultCount")]/text()').extract()
        if result_count:
            result_count = result_count[0].replace(',', '').replace('.', '')\
                .replace(' ', '')
            if result_count.isdigit():
                return int(result_count)
        if u"Hmmm....looks like we don't have any results for" \
                in response.body_as_unicode():
            return 0
