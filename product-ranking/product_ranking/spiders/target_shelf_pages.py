# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals

import re
import json
import urlparse

from scrapy import Request

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import cond_set_value

from .target import TargetProductSpider

is_empty = lambda x: x[0] if x else None


class TargetShelfPagesSpider(TargetProductSpider):
    name = 'target_shelf_urls_products'
    allowed_domains = ["target.com", "recs.richrelevance.com",
                       'api.bazaarvoice.com']

    def _setup_class_compatibility(self):
        """ Needed to maintain compatibility with the SC spiders baseclass """
        # self.quantity = sys.maxint
        self.site_name = self.allowed_domains[0]
        self.user_agent_key = None
        self.current_page = 1

    def _setup_meta_compatibility(self):
        """ Needed to prepare first request.meta vars to use """
        return {'remaining': self.quantity, 'search_term': ''}.copy()

    def __init__(self, *args, **kwargs):
        super(TargetShelfPagesSpider, self).__init__(*args, **kwargs)
        self.product_url = kwargs['product_url']
        self._setup_class_compatibility()

        # self.JSON_SEARCH_URL = "http://tws.target.com/searchservice/item/search_results/v2/by_keyword?" \
        #                         "alt=json&pageCount=24&response_group=Items&zone=mobile&" \
        #                         "offset={index}&category={category}"
        self.JSON_SEARCH_URL = "http://redsky.target.com/v1/plp/search?alt=json&count=24&" \
                               "response_group=Items%2Csurl&zone=mobile&offset={index}&" \
                               "category={category}&sort_by=&category_type=nid"

        self.SHELF_AJAX_LINK_URL = "http://redsky.target.com/v1/plp/search?" \
                                   "keyword={keyword}&" \
                                   "count={count}&" \
                                   "offset={offset}&" \
                                   "category={category}&" \
                                   "sort_by=relevance&" \
                                   "faceted_value={faceted_value}"

        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0

        # shelf scrapers should ignore quantity parameter
        self.quantity = 9999999

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
                                          index=0),
                meta=new_meta)

        import urlparse

        params = urlparse.parse_qs(urlparse.urlparse(response.url).query)

        if not response.meta.get('json') and \
                params and \
                params.get("category", None) and \
                params.get("facetedValue", None) and \
                params.get("searchTerm", None) and \
                params.get("sortBy", None):
            new_meta = response.meta
            new_meta['json'] = True
            new_meta['category'] = params["category"][0]
            new_meta['faceted'] = params["facetedValue"][0]

            return Request(
                self.url_formatter.format(self.SHELF_AJAX_LINK_URL,
                                          keyword=params["searchTerm"][0],
                                          count=24,
                                          offset=0,
                                          category=params["category"][0],
                                          faceted_value=params["facetedValue"][0]),
                meta=new_meta)

        return list(super(TargetShelfPagesSpider, self).parse(response))

    def _scrape_product_links_json(self, response):
        data = json.loads(response.body_as_unicode())
        data = data['search_response']
        for item in data['items']['Item']:
            # for item in self._get_json_data(response)['items']['Item']:
            # Skip Promotions and Ads
            if not item.get('title'):
                continue
            url = item['url']
            url = urlparse.urljoin('http://intl.target.com', url)
            product = SiteProductItem()
            shelf_path = data.get('breadCrumb_list')
            shelf_path = shelf_path[0]['breadCrumbValues'] if shelf_path else None
            if shelf_path:
                shelf_path = [s.get('label') for s in shelf_path]
            shelf_name = shelf_path[-1] if shelf_path else None
            cond_set_value(product, 'shelf_path', shelf_path)
            cond_set_value(product, 'shelf_name', shelf_name)
            attrs = item
            title = attrs.get('title')
            if '&$174;' in title:
                title = title.replace('&$174;', '®')
            cond_set_value(product, 'title', title)
            cond_set_value(product, 'brand',
                           attrs.get('brand'))
            priceattr = attrs.get('offer_price', attrs.get('list_price'))
            if priceattr:
                currency = priceattr.get('formatted_price')
                currency = currency[0] if currency else None
                currency = 'USD' if currency == '$' else None
                amount = priceattr.get('price')
                if amount == 'Too low to display':
                    price = None
                elif not currency:
                    price = None
                else:
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

    def _scrape_total_matches_json(self, response):
        data = json.loads(response.body_as_unicode())
        meta_data = data['search_response'].get('metaData')
        total = None
        for meta_dict in meta_data:
            if not total:
                total = meta_dict.get('value') if meta_dict.get('name') == 'total_results' else None
            if total:
                break
        total = int(total)
        return total

    def _scrape_next_results_page_link_json(self, response):
        data = json.loads(response.body_as_unicode())
        meta_data = data['search_response'].get('metaData')
        current = None
        total = None
        per_page = None
        for meta_dict in meta_data:
            if not current:
                current = meta_dict.get('value') if meta_dict.get('name') == 'currentPage' else None
            if not total:
                total = meta_dict.get('value') if meta_dict.get('name') == 'totalPages' else None
            if not per_page:
                per_page = meta_dict.get('value') if meta_dict.get('name') == 'count' else None
            if current and total and per_page:
                break
        current = int(current)
        total = int(total)
        per_page = int(per_page)
        # print "current %s, total %s, per_page %s" % (current, total, per_page)
        if current <= total:
            sort_mode = self.SORTING or ''
            new_meta = response.meta.copy()
            url = self.url_formatter.format(self.JSON_SEARCH_URL,
                                            index=per_page * current,
                                            category=response.meta.get('category'))
            return Request(url, meta=new_meta)
