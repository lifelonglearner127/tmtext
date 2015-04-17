# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re
import json
import urllib

from scrapy.http import Request
from scrapy.log import WARNING, ERROR

from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults

is_empty = lambda x, y=None: x[0] if x else y

class AsdaProductsSpider(BaseProductsSpider):
    name = 'asda_products'
    allowed_domains = ["asda.com"]
    start_urls = []

    SEARCH_URL = "http://groceries.asda.com/api/items/search" \
        "?pagenum={pagenum}&productperpage={prods_per_page}" \
        "&keyword={search_term}&contentid=New_IM_Search_WithResults_promo_1" \
        "&htmlassociationtype=0&listType=12&sortby=relevance+desc" \
        "&cacheable=true&fromgi=gi&requestorigin=gi"

    PRODUCT_LINK = "http://groceries.asda.com/asda-webstore/landing" \
                   "/home.shtml?cmpid=ahc-_-ghs-d1-_-asdacom-dsk-_-hp" \
                   "/search/%s#/product/%s"

    API_URL = "http://groceries.asda.com/api/items/view?" \
              "itemid={id}&" \
              "responsegroup=extended&cacheable=true&" \
              "shipdate=currentDate&requestorigin=gi"

    def __init__(self, *args, **kwargs):
        super(AsdaProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(pagenum=1, prods_per_page=32),
            *args, **kwargs)

    def start_requests(self):
        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=urllib.quote_plus(st.encode('utf-8')),
                ),
                meta={'search_term': st, 'remaining': self.quantity},
            )

        if self.product_url:
            pId = is_empty(re.findall("product/(\d+)", self.product_url))
            url = "http://groceries.asda.com/api/items/view?" \
                "itemid=" + pId + "&responsegroup=extended" \
                "&cacheable=true&shipdate=currentDate" \
                "&requestorigin=gi"

            prod = SiteProductItem()
            prod['is_single_result'] = True
            prod["url"] = self.product_url
            yield Request(url,
                          self._parse_single_product,
                          meta={'product': prod})


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
        products = []
        products_ids = ''
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
            total_stars = int(item['totalReviewCount'])
            avg_stars = float(item['avgStarRating'])
            prod['buyer_reviews'] = BuyerReviews(num_of_reviews=total_stars,
                                                 average_rating=avg_stars,
                                                 rating_by_star={})
            prod['model'] = item['cin']
            image_url = item.get('imageURL')
            if not image_url and "images" in item:
                image_url = item.get('images').get('largeImage')
            prod['image_url'] = image_url

            pId = is_empty(re.findall("itemid=(\d+)", item['productURL']))
            if pId and "search_term" in response.meta:
                prod['url'] = self.PRODUCT_LINK % (
                   response.meta["search_term"], pId)
            else:
                prod["url"] = item['imageURL']

            prod['locale'] = "en-GB"

            products_ids += item['id']+','
            products.append(prod)

        url = self.API_URL.format(id=products_ids)
        print url
        content = urllib.urlopen(url).read()

        data = json.loads(content)
        items = data['items']
        for i in range(0, len(products)):
            products[i]['upc'] = items[i]['upcNumbers'][0]['upcNumber']
            yield None, products[i]

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

    def _parse_single_product(self, response):
        product = response.meta["product"]
        result = self._scrape_product_links(response)
        for p in result:
            for p2 in p:
                if p2:
                    del p2["search_term"]
                    return SiteProductItem(dict(p2.items() + product.items()))