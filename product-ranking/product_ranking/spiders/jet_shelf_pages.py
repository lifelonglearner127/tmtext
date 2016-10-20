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

    def start_requests(self):
        yield Request(
            url=self.START_URL,
            meta={'search_term': "", 'remaining': self.quantity},
            dont_filter=True,
            callback=self.start_requests_with_csrf,
        )

    def start_requests_with_csrf(self, response):
        csrf = self.get_csrf(response)
        st = response.meta.get('search_term')
        if self.product_url:
            category_id = re.findall("category=(\d+)", self.product_url)
            category_id = category_id[0] if category_id else None
            yield Request(
                url=self.SEARCH_URL,
                # callback=self._get_products,
                method="POST",
                body=json.dumps({"categories": category_id, "origination": "PLP", "sort": self.sort}),
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

    def send_next_request(self, reqs, response):
        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)

    def _scrape_results_per_page(self, response):
        try:
            data = json.loads(response.body)
            prods = data['result'].get('products')
            results_per_page = len(prods)
        except Exception as e:
            print e
            results_per_page = 0

        return int(results_per_page)

    def _scrape_total_matches(self, response):
        try:
            data = json.loads(response.body)
            total_matches = data['result'].get('total')
            total_matches = int(total_matches) if total_matches else 0
        except Exception as e:
            print e
            total_matches = 0

        return int(total_matches)

    def _scrape_product_links(self, response):
        try:
            data = json.loads(response.body)
            prods = data['result'].get('products', [])
            shelf_categories = [l.get("categoryName") for l in data.get("categoryLevels", [])]
            shelf_category = shelf_categories[-1] if shelf_categories else None
        except Exception as e:
            self.log(
                "Failed parsing json at {} - {}".format(response.url, e)
                , WARNING)
            prods = []

        item = SiteProductItem()
        if shelf_categories:
            item['shelf_name'] = shelf_categories
        if shelf_category:
            item['shelf_path'] = shelf_category
        for prod in prods:
            prod_id = prod.get('id')
            # Construct product url
            prod_name = prod.get('title')
            prod_slug = self.slugify(prod_name)
            prod_url = "https://jet.com/product/{}/{}".format(prod_slug, prod_id)
            yield prod_url, item

    def _scrape_next_results_page_link(self, response):
        csrf = self.get_csrf(response) or response.meta.get("csrf")
        st = response.meta.get("search_term")
        if int(self.current_page) > self.num_pages:
            return None
        else:
            self.current_page += 1
            category_id = re.findall("category=(\d+)", self.product_url)
            category_id = category_id[0] if category_id else None
            return Request(
                url=self.SEARCH_URL,
                method="POST",
                body=json.dumps({"categories": category_id, "origination": "PLP"}),
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

