from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urllib
import urlparse

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set
from scrapy.log import ERROR


class BootsProductsSpider(BaseProductsSpider):
    name = 'boots_products'
    allowed_domains = ["boots.com"]
    start_urls = []

    SEARCH_URL = \
        "http://www.boots.com/webapp/wcs/stores/servlet/SolrSearchLister" \
        "?storeId=10052&langId=-1&catalogId=11051" \
        "&stReq=1&searchTerm={search_term}#container"

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(product, 'title', map(string.strip, response.xpath(
            "//h1/span/text()").extract()))

        cond_set(product, 'upc', map(int, response.xpath(
            "//p[@class='itemNumber']/span/text()").extract()))

        cond_set(product, 'price', map(string.strip, response.xpath(
            "//p[@class='productOfferPrice']/text()").extract()))

        cond_set(product, 'brand', response.xpath(
            "//div[@class='brandLogo']/a/img/@alt").extract())

        cond_set(product, 'image_url', response.xpath(
            "//meta[@property='og:image']/@content").extract())

        content = response.xpath(
            "//div[@id='tab1content']"
            "/div[@id='productDescriptionContent']"
            "/descendant::*[text()]/text()")
        if content:
            product['description'] = "\n".join(content.extract())

        product['model'] = ""
        product['locale'] = "en-US"
        return product

    def _scrape_total_matches(self, response):
        total = response.xpath(
            "//div[@class='searchResultsSummary']"
            "/h1/span/text()").re(r'\((\d+)\)')
        if len(total) > 0:
            return int(total[0])
        else:
            return 0

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//div[@class='productSearchResults']"
            "/div[@id='ProductViewListGrid']"
            "/div[contains(@class,'product_item')]"
            "/*/*/div[@class='pl_productName']/h5/a/@href").extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath(
            "//li[contains(@class,'paginationTop')]/ul"
            "/li[@class='next']/a/@href").re(r'javascript:.*setPageNumber\((.*)\);')
        if len(next) > 0:
            x = next[0]
            x = x.split(',')
            x = [e.replace("'", '').strip() for e in x]
            pname = x[0] + "_page"
            pvalue = x[1]

            url_parts = urlparse.urlsplit(response.url)
            query_string = urlparse.parse_qs(url_parts.query)

            query_string[pname] = pvalue

            url_parts = url_parts._replace(
                query=urllib.urlencode(query_string, True))
            link = urlparse.urlunsplit(url_parts)
            return link
        else:
            return None
