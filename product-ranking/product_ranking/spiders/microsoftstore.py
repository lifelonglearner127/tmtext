# -*- coding: utf-8 -*-#

import json
import re
import string
import itertools
import urllib

from scrapy.http import FormRequest, Request
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set_value
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi

is_empty = lambda x, y=None: x[0] if x else y


class MicrosoftStoreProductSpider(BaseProductsSpider):

    name = 'microsoftstore_products'
    allowed_domains = ["www.microsoftstore.com"]

    #SEARCH_URL = "http://www.debenhams.com/webapp/wcs/stores/servlet/" \
    #             "Navigate?langId=-1&storeId=10701&catalogId=10001&txt={search_term}"

    SEARCH_URL = "http://www.microsoftstore.com/store?keywords={search_term}" \
                 "&SiteID=msusa&Locale=en_US" \
                 "&Action=DisplayProductSearchResultsPage&" \
                 "result=&sortby=score%20descending&filters="

    PAGINATE_URL = 'http://www.microsoftstore.com/store/msusa/en_US/filterSearch/' \
                   'categoryID.{product_id}/startIndex.{start_index}/size.{size}/sort.score%' \
                   '20descending?keywords={search_term}&' \
                   'Env=BASE&callingPage=productSearchResultPage'

    index = 15

    def __init__(self, *args, **kwargs):
        self.br = BuyerReviewsBazaarApi(called_class=self)

        super(MicrosoftStoreProductSpider, self).__init__(*args, **kwargs)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        # # Set locale
        # product['locale'] = 'en_GB'
        #
        # # Parse title
        # title = self._parse_title(response)
        # cond_set_value(product, 'title', title, conv=string.strip)
        #
        # # Parse brand
        # brand = self._parse_brand(response)
        # cond_set_value(product, 'brand', brand)
        #
        # # Parse department
        # department = self._parse_department(response)
        # cond_set_value(product, 'department', department)
        #
        # # Parse categories
        # categories = self._parse_categories(response)
        # cond_set_value(product, 'categories', categories)
        #
        # # Parse price
        # price, currency = self._parse_price(response)
        # price = Price(price=float(price), priceCurrency=currency)
        # cond_set_value(product, 'price', price)
        #
        # # Parse special pricing
        # special_pricing = self._parse_special_pricing(response)
        # cond_set_value(product, 'special_pricing', special_pricing, conv=bool)
        #
        # # Parse image url
        # image_url = self._parse_image_url(response)
        # cond_set_value(product, 'image_url', image_url, conv=string.strip)
        #
        # # Parse description
        # description = self._parse_description(response)
        # cond_set_value(product, 'description', description, conv=string.strip)
        #
        # # Parse stock status
        # is_out_of_stock = self._parse_stock_status(response)
        # cond_set_value(product, 'is_out_of_stock', is_out_of_stock)
        #
        # # Parse upc
        # upc = self._parse_upc(response)
        # cond_set_value(product, 'upc', upc)
        #
        # # Parse variants
        # variants = self._parse_variants(response)
        # cond_set_value(product, 'variants', variants)
        #
        # # Parse buyer reviews
        # reqs.append(
        #     Request(
        #         url=self.BUYER_REVIEWS_URL.format(upc=upc),
        #         dont_filter=True,
        #         callback=self.br.parse_buyer_reviews
        #     )
        # )
        #
        # # Parse related products
        # related_products = self._parse_related_products(response)
        # cond_set_value(product, 'related_products', related_products)
        #
        # if reqs:
        #     return self.send_next_request(reqs, response)

        return product


    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """

        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _scrape_total_matches(self, response):
        """
        Scraping number of resulted product links
        """
        total_matches = is_empty(
            response.xpath(
                '//span[@class="product-count"]/text()').re(r'\d+'))
        if total_matches:
            total_matches = total_matches.replace(',', '')
            return int(total_matches)
        else:
            return 0

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """
        links = response.xpath(
            '//div[@class="product-row"]/a/@href'
        ).extract()

        per_page = len(links)
        return per_page

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """
        links = response.xpath(
            '//div[@class="product-row"]/a/@href'
        ).extract()

        if links:
            for link in links:
                yield 'http://www.microsoftstore.com/' + link, SiteProductItem()
        else:
            self.log("Found no product links in {url}".format(url=response.url), INFO)

    def _scrape_next_results_page_link(self, response):

        return Request(
            self.PAGINATE_URL.format(
                search_term=response.meta['search_term'],
                nao=str(self.CURRENT_NAO)),
            callback=self.parse, meta=response.meta
        )