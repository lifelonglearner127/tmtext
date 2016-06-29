# -*- coding: utf-8 -*-

import re
import json
import urllib
import sys
import urlparse

from scrapy import Request

from scrapy.selector import HtmlXPathSelector
import requests

from product_ranking.items import SiteProductItem, RelatedProduct, \
    Price, BuyerReviews
from product_ranking.spiders import cond_set, cond_set_value, \
    FLOATING_POINT_RGEX, cond_replace
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.guess_brand import guess_brand_from_first_words

from .target import TargetProductSpider

is_empty = lambda x: x[0] if x else None


class TargetShelfPagesSpider(TargetProductSpider):
    name = 'target_shelf_urls_products'
    allowed_domains = ["target.com", "recs.richrelevance.com",
                       'api.bazaarvoice.com']

    def _setup_class_compatibility(self):
        """ Needed to maintain compatibility with the SC spiders baseclass """
        self.quantity = sys.maxint
        self.site_name = self.allowed_domains[0]
        self.user_agent_key = None
        self.current_page = 1

    def _setup_meta_compatibility(self):
        """ Needed to prepare first request.meta vars to use """
        return {'remaining': sys.maxint, 'search_term': ''}.copy()

    def __init__(self, *args, **kwargs):
        super(TargetShelfPagesSpider, self).__init__(*args, **kwargs)
        self.product_url = kwargs['product_url']
        self._setup_class_compatibility()

        self.JSON_SEARCH_URL = "http://tws.target.com/searchservice/item/search_results/v2/by_keyword?" \
                               "callback=getPlpResponse&category={category}&faceted_value={faceted}" \
                               "&zone=PLP&pageCount=60&page={page}&start_results={index}"

        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0

        # variants are switched off by default, see Bugzilla 3982#c11
        self.scrape_variants_with_extra_requests = False
        if 'scrape_variants_with_extra_requests' in kwargs:
            scrape_variants_with_extra_requests = kwargs['scrape_variants_with_extra_requests']
            if scrape_variants_with_extra_requests in (1, '1', 'true', 'True', True):
                self.scrape_variants_with_extra_requests = True

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta=self._setup_meta_compatibility(),
                      dont_filter=True)

    @staticmethod
    def valid_url(url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def parse(self, response):
        searched = re.search('^http://[\w]*\.target\.com/[\w\/-]+/-/N-(\w+?)Z(\w+)#?', response.url) or \
            re.search('^http://[\w]*\.target\.com/[\w\/-]+/-/N-(\w+)#?', response.url)
        if not response.meta.get('json') and searched:
            new_meta = response.meta
            new_meta['json'] = True
            category = searched.group(1)
            try:
                faceted = searched.group(2)
            except:
                faceted = ""
            new_meta['category'] = category
            new_meta['faceted'] = faceted
            return Request(
                self.url_formatter.format(self.JSON_SEARCH_URL,
                                          category=category,
                                          index=60,
                                          page=1,
                                          faceted=faceted),
                meta=new_meta)
        return list(super(TargetShelfPagesSpider, self).parse(response))

    def _scrape_product_links_json(self, response):
        for item in self._get_json_data(response)['items']['Item']:
            # Skip Promotions and Ads
            if not item.get('title'):
                continue
            url = item['productDetailPageURL']
            url = urlparse.urljoin('http://intl.target.com', url)
            product = SiteProductItem()
            attrs = item.get('itemAttributes', {})
            cond_set_value(product, 'title', attrs.get('title'))
            cond_set_value(product, 'brand',
                           attrs.get('productManufacturerBrand'))
            p = item.get('priceSummary', {})
            priceattr = p.get('offerPrice', p.get('listPrice'))
            if priceattr:
                currency = priceattr['currencyCode']
                amount = priceattr['amount']

                if amount == 'Too low to display':
                    price = None
                else:
                    amount = is_empty(re.findall(
                        '\d+\.{0,1}\d+', priceattr['amount']
                    ))
                    if amount:
                        price = Price(priceCurrency=currency, price=amount)
                    else:
                        price = None
                cond_set_value(product, 'price', price)
            yield url, product

    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1
        return super(TargetShelfPagesSpider,
                    self)._scrape_next_results_page_link(response)

    def _scrape_next_results_page_link_json(self, response):
        args = self._json_get_args(self._get_json_data(response))
        current = int(args['currentPage'])
        total = int(args['totalPages'])
        per_page = int(args['resultsPerPage'])
        print "current %s, total %s, per_page %s" % (current, total, per_page)
        if current <= total:
            sort_mode = self.SORTING or ''
            new_meta = response.meta.copy()
            url = self.url_formatter.format(self.JSON_SEARCH_URL,
                                            index=per_page * current,
                                            page=current + 1,
                                            faceted=response.meta.get('faceted'),
                                            category=response.meta.get('category'))
            return Request(url, meta=new_meta)
