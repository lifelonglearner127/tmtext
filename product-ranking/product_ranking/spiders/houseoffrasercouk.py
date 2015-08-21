# -*- coding: utf-8 -*-#

import json
import re

from scrapy.http import FormRequest, Request
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set_value

is_empty = lambda x, y=None: x[0] if x else y


class HouseoffraserProductSpider(BaseProductsSpider):

    name = 'houseoffraser_products'
    allowed_domains = ["houseoffraser.co.uk"]

    SEARCH_URL = "http://www.houseoffraser.co.uk/on/demandware.store/Sites-hof-Site/default/Search-Show?" \
                 "q={search_term}&srule={sort_mode}"

    NEXT_PAGE_URL = "http://www.next.co.uk/search?w=jeans&isort=score&srt={start_pos}"

    _SORT_MODES = {
        "NAME_ASC": "product-name-asc",
        "NAME_DESC": "product-name-desc",
        "PRICE_ASC": "price-asc",
        "PRICE_DESC": "price-desc",
        "BRAND_ASC": "brand-asc",
        "BRAND_DESC": "brand-desc",
        "NEWEST": "Newness",
        "RATING": "bv-ratings",
    }

    def __init__(self, search_sort='NEWEST', *args, **kwargs):
        super(HouseoffraserProductSpider, self).__init__(
            site_name=self.allowed_domains[0],
            url_formatter=FormatterWithDefaults(
                sort_mode=self._SORT_MODES[search_sort]
            ),
            *args, **kwargs)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        if reqs:
            return self.send_next_request(reqs, response)

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

        num = is_empty(
            response.xpath('//p[@class="paging-items-summary"]/text()').extract(),
            '0'
        )

        if not num:
            self.log(
                "Failed to extract total matches from {url}".format(response.url),
                ERROR
            )
        else:
            num = is_empty(re.findall(r'of\s+(\d+)', num), '0')

        return int(num)

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """

        num = is_empty(
            response.xpath('//*[@class="paging-links"]/span/text()').extract(),
            '0'
        )

        if not num:
            self.log(
                "Failed to extract results per page from {url}".format(response.url), ERROR
            )

        self.items_per_page = int(num)

        return num

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """

        items = response.xpath('//*[@class="product-list-element"]')

        if items:
            for item in items:
                link = is_empty(
                    item.xpath('./div[@class="product-description"]/./'
                               '/a/@href').extract()
                )
                res_item = SiteProductItem()
                yield link, res_item
        else:
            self.log("Found no product links in {url}".format(response.url), INFO)

    def _scrape_next_results_page_link(self, response):
        next_page_url = response.xpath('//a[contains(@class, "nextPage")]/@href').extract()

        if len(next_page_url) == 1:
            next_page_url = next_page_url[0]
        elif len(next_page_url) > 1:
            self.log("Found more than one 'next page' link.", ERROR)

        return next_page_url
