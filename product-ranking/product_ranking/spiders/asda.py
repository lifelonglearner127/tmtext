# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json
import urllib

from scrapy.log import WARNING, ERROR

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults


class AsdaProductsSpider(BaseProductsSpider):
    name = 'asda_products'
    allowed_domains = ["asda.com"]
    start_urls = []

    SEARCH_URL = "http://groceries.asda.com/api/items/search" \
        "?pagenum={pagenum}&productperpage={prods_per_page}" \
        "&keyword={search_term}&contentid=New_IM_Search_WithResults_promo_1" \
        "&htmlassociationtype=0&listType=12&sortby=relevance+desc" \
        "&cacheable=true&fromgi=gi&requestorigin=gi"

    def __init__(self, *args, **kwargs):
        super(AsdaProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(pagenum=1, prods_per_page=32),
            *args, **kwargs)

    def parse_product(self, response):
        raise AssertionError("This method should never be called.")

    def _search_page_error(self, response):
        try:
            data = json.loads(response.body_as_unicode())
            is_error = data.get('statusCode') != '0'
            if is_error:
                self.log("Site reported error code '%s' and reason: %s"
                         % (data.get('statusCode'), data.get('statusMessage')),
                         WARNING)

            return is_error
        except Exception as e:
            self.log(
                "Error '%s' when handling page '%s'. Content:\n%s"
                % (e, response.url, response.body_as_unicode().strip()),
                ERROR
            )
            raise

    def _scrape_total_matches(self, response):
        data = json.loads(response.body_as_unicode())
        return int(data['totalResult'])

    def _scrape_product_links(self, response):
        data = json.loads(response.body_as_unicode())
        for item in data['items']:
            prod = SiteProductItem()
            prod['title'] = item['itemName']
            prod['brand'] = item['brandName']
            prod['price'] = item['price']
            if prod.get('price', None):
                prod['price'] = Price(
                    price=prod['price'].replace('£', '').replace(
                        ',', '').strip(),
                    priceCurrency='GBP'
                )
            # FIXME Verify by comparing a prod in another site.
            prod['upc'] = int(item['cin'])
            prod['model'] = item['id']
            prod['image_url'] = item['imageURL']
            prod['url'] = item['productURL']

            prod['locale'] = "en-GB"

            yield None, prod

    def _scrape_next_results_page_link(self, response):
        data = json.loads(response.body_as_unicode())

        max_pages = int(data['maxPages'])
        cur_page = int(data['currentPage'])
        if cur_page >= max_pages:
            return None

        st = urllib.quote(data['keyword'])
        return self.url_formatter.format(self.SEARCH_URL,
                                         search_term=st,
                                         pagenum=cur_page + 1)
