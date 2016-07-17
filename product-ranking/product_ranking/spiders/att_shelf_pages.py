# -*- coding: utf-8 -*-


from __future__ import division, absolute_import, unicode_literals

import json
import re
from urllib import urlencode
import urlparse
import datetime
import itertools
import os
import copy
import time

from scrapy import Request
from scrapy.http.request.form import FormRequest
from scrapy.dupefilter import RFPDupeFilter
from scrapy.conf import settings
from scrapy.utils.request import request_fingerprint

from product_ranking.items import SiteProductItem, Price, BuyerReviews, \
    RelatedProduct
from product_ranking.guess_brand import guess_brand_from_first_words
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set
from product_ranking.spiders import cond_set_value
from product_ranking.spiders.att import ATTProductsSpider

is_empty = lambda x, y=None: x[0] if x else y



class ATTShelfPagesSpider(ATTProductsSpider):
    name = "att_shelf_urls_products"
    allowed_domains = ["att.com",
                       'api.bazaarvoice.com',
                       'recs.richrelevance.com']

    # PAGINATE_URL = '{base_url}.deviceListView.flowtype-NEW.deviceGeoTarget-US.' \
    #                '{device_group_type}.{payment_type}' \
    #                '.packageType-undefined.json?showMoreListSize=24'
    PAGINATE_URL = 'https://www.att.com/shop/wireless/devices/prepaidphones.accessoryListGridView.html' \
                   '?showMoreListSize=24'

    def __init__(self, *args, **kwargs):
        # settings.overrides["DUPEFILTER_CLASS"] = 'product_ranking.spiders.att.CustomHashtagFilter'
        super(ATTShelfPagesSpider, self).__init__(*args, **kwargs)
        self.current_page = 1
        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0
        if "quantity" in kwargs:
            self.quantity = int(kwargs['quantity'])
        self.shelf_categories = []
        self.page_size = 12

    def start_requests(self):
        if self.product_url:
            yield Request(self.product_url,
                          meta={'search_term': '', 'remaining': self.quantity}, )

    def _scrape_product_links(self, response):
        item_urls = []
        item_urls = response.xpath(
            './/*[@class="list-title" or @class="listGridAcc-title" or'
            ' @class="listGridAcc-titleWithBanner"]//a[contains(@class, "clickStreamSingleItem") '
            'or contains(@id, "list-title_")]/@href').extract()
        # No urls, maybe json page? Attempt to extract urls from json.
        if not item_urls:
            try:
                js_response = json.loads(response.body_as_unicode())
                item_list = js_response.get('devices')
                for item in item_list:
                    item_url = item.get('product').get('url')
                    if item_url:
                        item_urls.append(item_url)
            except BaseException:
                item_urls = []
                # No urls, give up
        self.page_size = len(item_urls) if item_urls else 0
        bc = response.xpath('.//*[@class="breadcrumb"]//*/text()').extract()
        # TODO maybe rework this categories stuff and send it thru meta
        if bc:
            shelf_categories = [c.replace('/','').strip() for c in bc if len(c.strip()) > 1 and not c.strip() == "/"]
            self.shelf_categories = shelf_categories
        else:
            shelf_categories = self.shelf_categories
        shelf_category = shelf_categories[-1] if shelf_categories else None
        for item_url in item_urls:
            item = SiteProductItem()
            if shelf_category:
                item['shelf_name'] = shelf_category
            if shelf_categories:
                item['shelf_path'] = shelf_categories
            yield urlparse.urljoin(response.url, item_url), item

    def _scrape_next_results_page_link(self, response):
        if not list(self._scrape_product_links(response)) or self.current_page >= self.num_pages:
            return  # end of pagination reached
        else:
            next_link = response.url.split('#')[0] + '#on={}page'.format(self.current_page)
            return next_link

    def _scrape_total_matches(self, response):
        # TODO this is not working as well
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        result_count = response.xpath(
            ".//*[@id='count']//*[contains(text(), 'of')]/following-sibling::*[1]/text()").extract()

        result_count = result_count[0] if result_count else ''
        if result_count.isdigit():
            return int(result_count)

        return 0
