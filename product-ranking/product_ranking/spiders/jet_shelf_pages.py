# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

import re
import json
import urllib
import urlparse
import unicodedata
from scrapy.conf import settings

from scrapy.http import Request

from itertools import islice
from scrapy.log import ERROR, WARNING, INFO
from product_ranking.items import Price
from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, FLOATING_POINT_RGEX
from product_ranking.spiders import cond_set, cond_set_value
from spiders_shared_code.jet_variants import JetVariants
from product_ranking.validators.jet_validator import JetValidatorSettings
from .jet import JetProductsSpider

is_empty = lambda x, y=None: x[0] if x else y


class JetShelfPagesSpider(JetProductsSpider):
    name = 'jet_shelf_urls_products'
    allowed_domains = ["jet.com"]

    def __init__(self, sort_mode=None, *args, **kwargs):
        super(JetShelfPagesSpider, self).__init__(*args, **kwargs)
        # settings.overrides['CRAWLERA_ENABLED'] = True
        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1
        self.quantity = self.num_pages * 24

    def start_requests(self):
        if self.product_url:
            yield Request(
                url=self.product_url,
                meta={'search_term': "", 'remaining': self.quantity},
                dont_filter=True,
                callback=self.start_requests_with_csrf,
            )

    def start_requests_with_csrf(self, response):
        csrf = self.get_csrf(response)
        st = response.meta.get('search_term')
        if self.product_url:
            body = self.construct_post_body()
            yield Request(
                url=self.SEARCH_URL,
                # callback=self._get_products,
                method="POST",
                body=body,
                meta={
                    'search_term': st,
                    'remaining': self.quantity,
                    'csrf': csrf
                },
                dont_filter=True,
                headers={
                    "content-type": "application/json",
                    "x-csrf-token": csrf,
                    "X-Requested-With":"XMLHttpRequest",
                    "jet-referer":"/search?term={}".format(st),

                },
            )

    def _scrape_product_links(self, response):
        shelf_categories = []
        try:
            data = json.loads(response.body)
            prods = data['result'].get('products', [])
            shelf_categories = [l.get("categoryName") for l in data['result'].get("categoryLevels", [])]
        except Exception as e:
            #from scrapy.shell import inspect_response
            #inspect_response(response, self)
            self.log(
                "Failed parsing json at {} - {}".format(response.url, e)
                , WARNING)
            prods = []

        item = SiteProductItem()
        if shelf_categories:
            item['shelf_name'] = shelf_categories[-1]
            item['shelf_path'] = shelf_categories
        for prod in prods:
            prod_id = prod.get('id')
            # Construct product url
            prod_name = prod.get('title')
            prod_slug = self.slugify(prod_name)
            prod_url = "https://jet.com/product/{}/{}".format(prod_slug, prod_id)
            yield prod_url, item

    def construct_post_body(self):
        # Helper func to construct post params for request
        category_id = re.findall("category=(\d+)", self.product_url)
        category_id = category_id[0] if category_id else None

        searchterm = re.findall("term=([\w\s]+)", urllib.unquote(self.product_url).decode('utf8'))
        searchterm = searchterm[0] if searchterm else None

        if searchterm and not category_id:
            body = json.dumps({"term": searchterm, "origination": "none",
                               "sort": self.sort, "page": self.current_page})
        elif category_id and not searchterm:
            body = json.dumps({"categories": category_id, "origination": "PLP",
                               "sort": self.sort, "page": self.current_page})
        else:
            body = json.dumps({"term": searchterm, "categories": category_id,
                               "origination": "PLP", "sort": self.sort, "page": self.current_page})
        return body

    def _scrape_next_results_page_link(self, response):
        csrf = self.get_csrf(response) or response.meta.get("csrf")
        st = response.meta.get("search_term")
        if int(self.current_page) >= self.num_pages:
            return None
        else:
            self.current_page += 1
            body = self.construct_post_body()
            return Request(
                url=self.SEARCH_URL,
                method="POST",
                body=body,
                meta={
                    'search_term': st,
                    'csrf': csrf
                },
                dont_filter=True,
                headers={
                    "content-type": "application/json",
                    "x-csrf-token": csrf,
                    "X-Requested-With": "XMLHttpRequest",
                },
            )

