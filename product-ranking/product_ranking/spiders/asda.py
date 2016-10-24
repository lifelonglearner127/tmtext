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
from product_ranking.validation import BaseValidator
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.validators.asda_validator import AsdaValidatorSettings

is_empty = lambda x, y=None: x[0] if x else y


class AsdaProductsSpider(BaseValidator, BaseProductsSpider):
    name = 'asda_products'
    allowed_domains = ["asda.com"]
    start_urls = []

    settings = AsdaValidatorSettings

    SEARCH_URL = "https://groceries.asda.com/api/items/search" \
        "?pagenum={pagenum}&productperpage={prods_per_page}" \
        "&keyword={search_term}&contentid=New_IM_Search_WithResults_promo_1" \
        "&htmlassociationtype=0&listType=12&sortby=relevance+desc" \
        "&cacheable=true&fromgi=gi&requestorigin=gi"

    PRODUCT_LINK = "https://groceries.asda.com/asda-webstore/landing" \
                   "/home.shtml?cmpid=ahc-_-ghs-d1-_-asdacom-dsk-_-hp" \
                   "/search/%s#/product/%s"

    API_URL = "https://groceries.asda.com/api/items/view?" \
              "itemid={id}&" \
              "responsegroup=extended&cacheable=true&" \
              "shipdate=currentDate&requestorigin=gi"

    REVIEW_URL = "https://groceries.asda.com/review/reviews.json?" \
                 "Filter=ProductId:%s&" \
                 "Sort=SubmissionTime:desc&" \
                 "apiversion=5.4&" \
                 "passkey=92ffdz3h647mtzgbmu5vedbq&limit=100"

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
            if pId is None:
                try:
                    pId = int(self.product_url.strip('/').split('/')[-1])
                except (ValueError, TypeError) as e:
                    self.log('Error while parse item id. ERROR: %s.' % str(e),
                             ERROR)
                    return
            url = "https://groceries.asda.com/api/items/view?" \
                "itemid=" + str(pId) + "&responsegroup=extended" \
                "&cacheable=true&shipdate=currentDate" \
                "&requestorigin=gi"

            prod = SiteProductItem()
            prod['is_single_result'] = True
            prod["url"] = self.product_url
            yield Request(url,
                          self._parse_single_product,
                          meta={'product': prod})

    def parse_product(self, response):
        product = response.meta['product']
        
        try:
            data = json.loads(response.body_as_unicode())
            item = data['items'][0]
            if item.get("images", {}).get("largeImage"):
                product["image_url"] = item.get("images").get("largeImage")
            product['upc'] = item['upcNumbers'][0]['upcNumber']
        except (IndexError, ValueError):
            pass

        product_id = re.findall('itemid=(\d+)', response.url)
        if product_id:
            url = self.REVIEW_URL % product_id[0]
            meta = {'product': product}
            return Request(url=url, meta=meta, callback=self._parse_review)
        return product

    def _parse_review(self, response):
        prod = response.meta['product']
        num, avg, by_star = prod['buyer_reviews']
        data = json.loads(response.body_as_unicode())
        by_star = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        reviews = data['Results']
        for review in reviews:
            by_star[review['Rating']] += 1

        prod['buyer_reviews'] = BuyerReviews(num, avg, by_star)
        return prod

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

            # Hardcoded, store seems not to have out of stock products
            prod['is_out_of_stock'] = False
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
                    urllib.quote(response.meta["search_term"]), pId)
            elif "imageURL" in item:
                prod["url"] = item['imageURL']

            prod['locale'] = "en-GB"

            products_ids = item['id']
            url = self.API_URL.format(id=products_ids)

            yield url, prod

    def _scrape_next_results_page_link(self, response):
        data = json.loads(response.body_as_unicode())

        max_pages = int(data.get('maxPages', 0))
        cur_page = int(data.get('currentPage', 0) or 0)
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
                if isinstance(p2, SiteProductItem):
                    if "search_term" in p2:
                        del p2["search_term"]
                    product = SiteProductItem(dict(p2.items() + product.items()))

        try:
            data = json.loads(response.body_as_unicode())
            item = data['items'][0]
            if item.get("images", {}).get("largeImage"):
                product["image_url"] = item.get("images").get("largeImage")
            product['upc'] = item['upcNumbers'][0]['upcNumber']
        except (IndexError, ValueError):
            pass

        product_id = re.findall('itemid=(\d+)', response.url)
        if product_id:
            url = self.REVIEW_URL % product_id[0]
            meta = {'product': product}
            return Request(url=url, meta=meta, callback=self._parse_review)

        return product