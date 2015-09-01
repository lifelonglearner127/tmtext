# -*- coding: utf-8 -*-#

import json
import re
import hjson
import urlparse

from scrapy.http import FormRequest, Request
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set_value

is_empty = lambda x, y=None: x[0] if x else y


class ClarksProductSpider(BaseProductsSpider):

    name = 'clarkscouk_products'
    allowed_domains = ["www.clarks.co.uk"]

    SEARCH_URL = "http://www.clarks.co.uk/s/{search_term}"

    NEXT_PAGE_URL = 'http://www.clarks.co.uk/ProductListWidget/Ajax/GetFilteredProducts?location={location}'

    items_per_page = 40
    page_num = 1

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

    def start_requests(self):
        """Generate Requests from the SEARCH_URL and the search terms."""
        requests = super(ClarksProductSpider, self).start_requests()

        for req in requests:
            new_url = req.url.replace('+', '%20')
            req = req.replace(url=new_url)
            yield req

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _scrape_total_matches(self, response):
        """
        Scraping number of resulted product links
        """
        total_matches = is_empty(
            response.xpath('//div[@id="product-list-paging-top"]/./'
                           '/span[@class="page-size-container"]/text()').extract()
        )

        try:
            total_matches = re.findall(
                r'Found (\d+) styles',
                total_matches
            )
            return int(
                is_empty(total_matches, '0')
            )
        except (KeyError, ValueError) as exc:
            total_matches = None
            self.log(
                "Failed to extract total matches from {url}: {exc}".format(
                    response.url, exc
                ), ERROR
            )

        return total_matches

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """
        return self.items_per_page

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """

        items = response.xpath(
            '//ul[@id="prod-list"]/li[contains(@class, "product-list-item")]'
        )

        if items:
            for item in items:
                link = is_empty(
                    item.xpath('./span[@class="product-name-header"]/'
                               'a/@href').extract()
                )
                res_item = SiteProductItem()
                yield link, res_item
        else:
            self.log("Found no product links.".format(response.url), INFO)

    def _scrape_next_results_page_link(self, response):
        if '/c/' in response.url:
            location = 'Category'
        else:
            location = 'Search'
        url_parse = urlparse.urlparse(response.url)
        self.page_num += 1
        query_criteria = is_empty(
            re.findall(
                r'\/s?c?\/(.+)',
                url_parse.path
            )
        )
        data = {
            "QueryCriteria": query_criteria,
            "ImageSize": "LargeListerThumbnail",
            "ViewName": "3Columns",
            "Location": location,
            "FilteredProductQueries": [
                {
                    "Behaviour": "kvp",
                     "FhName": "fh_view_size",
                     "DisplayName": "pagesize",
                     "DataSplit": "-or-",
                     "Priority": "secondary",
                     "Items": [self.items_per_page]
                },
                {
                    "Behaviour": "kvp",
                    "DataSplit": "-or-",
                    "DisplayName": "page",
                    "FhName": "fh_start_index",
                    "Items": [self.page_num]
                }
            ],
            "PathName": url_parse.path,
            "Scroll": "true",
            "DeviceType": "Desktop"
        }
        return Request(
            url=self.NEXT_PAGE_URL.format(location=location),
            method='POST',
            body=json.dumps(data),
            headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        )