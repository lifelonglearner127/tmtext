# -*- coding: utf-8 -*-#

import json
import re
import string

from scrapy.http import FormRequest, Request
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set_value
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi

is_empty = lambda x, y=None: x[0] if x else y


class HalfordsProductSpider(BaseProductsSpider):

    name = 'halfords_products'
    allowed_domains = [
        "halfords.com",
        "halfords.ugc.bazaarvoice.com"
    ]

    SEARCH_URL = "http://www.halfords.com/webapp/wcs/stores/servlet/SearchCmd?storeId=10001" \
                 "&catalogId=10151&langId=-1&srch={search_term}&categoryId=-1&action=listrefine&" \
                 "tabNo=1&qcon=fh_location=%2F%2Fcatalog_10151%2Fen_GB%2F%24s%3Dblah%3Bt%3Ddefault" \
                 "%2Fattr_78cdb44b%3D1&channel=desktop&sort={sort}"
    BUYER_REVIEWS_URL = "http://halfords.ugc.bazaarvoice.com/4028-redes/{product_id}/" \
                        "reviews.djs?format=embeddedhtml"

    _SORT_MODES = {
        'price asc': 'price-low-to-high',
        'price desc': 'price-high-to-low',
        'best seller': 'best-seller',
        'star rating': 'star-rating',
        'recommended': 'we-recommend'
    }

    def __init__(self, search_sort='recommended', *args, **kwargs):
        self.br = BuyerReviewsBazaarApi(called_class=self)

        super(HalfordsProductSpider, self).__init__(
            site_name=self.allowed_domains[0],
            url_formatter=FormatterWithDefaults(
                sort=self._SORT_MODES[search_sort]
            ),
            *args, **kwargs)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        # Set locale
        product['locale'] = 'en_GB'

        # Set product id
        product_id = is_empty(
            response.xpath(
                '//input[@name="catCode"]/@value'
            ).extract(), '0'
        )
        response.meta['product_id'] = product_id

        # Set title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title, conv=string.strip)

        # Set price
        price = self._parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse buyer reviews
        reqs.append(
            Request(
                url=self.BUYER_REVIEWS_URL.format(product_id=product_id),
                dont_filter=True,
                callback=self.br.parse_buyer_reviews
            )
        )

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_title(self, response):
        title = is_empty(
            response.xpath(
                '//h1[@class="productDisplayTitle"]/text()'
            ).extract()
        )

        return title

    def _parse_price(self, response):
        price = is_empty(
            response.xpath(
                '//div[@id="priceAndLogo"]/h2/text()'
            ).extract(), 0.00
        )
        if price:
            price = price.strip().replace(u'£', '')

        return Price(
            price=price,
            priceCurrency='GBP'
        )

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
                '//*[@id="resultsTabs"]/.//a[@data-tabname="products"]'
                '/span/text()'
            ).extract(), '0'
        )

        return int(total_matches)

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """
        num = is_empty(
            response.xpath(
                '//*[@id="pgSize"]/option[@selected="selected"]'
                '/@value'
            ).extract(), '0'
        )

        return int(num)

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """

        items = response.xpath(
            '//ul[@id="product-listing"]/li'
        )

        if items:
            for item in items:
                link = is_empty(
                    item.xpath('././/span[@class="productTitle"]/a/@href').extract()
                )
                res_item = SiteProductItem()
                yield link, res_item
        else:
            self.log("Found no product links in {url}".format(url=response.url), INFO)

    def _scrape_next_results_page_link(self, response):
        url = is_empty(
            response.xpath(
                '//section[@class="pagination"]/./'
                '/a[contains(@class,"next")]/@href'
            ).extract()
        )

        if url:
            return url
        else:
            self.log("Found no 'next page' links", WARNING)
            return None
