# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals

import json
import re
from urllib import urlencode
import urlparse
import datetime
import time

from scrapy import Request
from scrapy.http.request.form import FormRequest

from product_ranking.items import SiteProductItem, Price, BuyerReviews, \
    RelatedProduct
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set
from product_ranking.spiders import cond_set_value


is_empty = lambda x, y=None: x[0] if x else y


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

    current_page = 0

    def __init__(self, *args, **kwargs):
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

    @staticmethod
    def _parse_title(response):
        title = response.xpath('//h1[contains(@id, "accPageTitle")]/text()').extract()
        if not title:
            title = response.xpath('//h1//text()').extract()
        if title:
            return title[0].strip()

    def parse_product(self, response):
        product = response.meta['product']
        product['title'] = self._parse_title(response)
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
