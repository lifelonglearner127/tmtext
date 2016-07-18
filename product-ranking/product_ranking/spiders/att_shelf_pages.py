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
        self.PAGINATE_URL = self.product_url.split('#')[0].split('?')[0].replace('.html','').replace('.htm','') + \
                            '.accessoryListGridView.html?showMoreListSize={more_list_size}'

    def start_requests(self):
        if self.product_url:
            # TODO fix wrong pagination at accessories also wrong items appear
            # TODO add params for accessory page to work correctly
            if 'accessories/cases.html' in self.product_url:
                proper_firstpage = self.PAGINATE_URL.format(more_list_size=30)
                yield Request(proper_firstpage,
                              meta={'search_term': '', 'remaining': self.quantity}, )
            else:
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

        if self.current_page == 1:
            self.page_size = len(item_urls) if item_urls else 0
        elif item_urls:
            # since page don't have proper pagination, we remove duplicate items from beginning of the list
            dup_items_quant = self.current_page * self.page_size
            item_urls = item_urls[dup_items_quant:]
        bc = response.xpath('.//*[@class="breadcrumb"]//*/text()').extract()
        shelf_categories = [c.replace('/', '').strip() for c in bc if len(c.strip()) > 1 and not c.strip() == "/"]
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
            self.current_page += 1
            more_list_size = self.current_page * self.page_size
            next_link = self.PAGINATE_URL.format(more_list_size=more_list_size)
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
