from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set
from scrapy import Request
from scrapy.http import FormRequest
from scrapy.log import ERROR


class BitiklaProductsSpider(BaseProductsSpider):
    name = 'bitikla_products'
    allowed_domains = ["bitikla.com"]
    start_urls = []
    SEARCH_URL = "https://www.bitikla.com/index.php?route=product/search&filter_name={search_term}"
    # Search "ari" - 87 results and 75 on page!
    # Diffs in bolge_no !

    def parse(self, response):
        if response.url == 'http://www.bitikla.com/bolge_secimi/':
            main_url = "http://www.bitikla.com/index.php"
            data = {'bolge_no': '0', 'redirect': 'http://www.bitikla.com/index.php'}
            new_meta = response.meta.copy()
            return FormRequest.from_response(
                response=response,
                url=main_url,
                method='POST',
                formdata=data,
                meta=new_meta)

        elif response.url == 'http://www.bitikla.com/index.php' and response.request.method == 'POST' and \
            'redirect_urls' in response.meta:

            new_meta = response.meta.copy()
            url = new_meta['redirect_urls'][0]

            if 'redirect_urls' in new_meta:
                del new_meta['redirect_urls']

            request = Request(
                url=url,
                method='GET',
                meta=new_meta,
                dont_filter=True)
            return request
        else:
            return super(BitiklaProductsSpider, self).parse(response)

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(product, 'title', map(string.strip, response.xpath(
            "//div[@id='content']/h1/text()").extract()))

        cond_set(product, 'price', map(string.strip, response.xpath(
            "//div[@class='price']/text()").re(r'.*:(.*)')))

        cond_set(product, 'image_url', response.xpath(
            "//div[@class='image']/a/img/@src").extract())

        cond_set(product, 'upc', map(int, response.xpath(
            "//div[@class='cart']/div/input[@name='product_id']/@value").extract()))

        cond_set(product, 'locale', response.xpath(
            "//html/@lang").extract())

        cond_set(product, 'brand', response.xpath(
            "//div[@class='description']/a/text()").extract())

        desc = response.xpath(
            "//div[@class='description']/text() | //div[@class='description']/descendant::*[text()]/text()").extract()
        info = " ".join([x.strip() for x in desc if len(x.strip()) > 0])
        product['description'] = info

        return product

    def _scrape_total_matches(self, response):
        total = response.xpath("//div[@class='pagination']/div[@class='results']/text()").re(r'.*toplam (\d+).*')
        if len(total) > 0:
            total = total[0].replace(".", "")
            try:
                return int(total)
            except ValueError:
                return 0
        else:
            return 0

    def _scrape_product_links(self, response):
        links = response.xpath("//div[@class='product-list']/div/div[@class='name']/a/@href").extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath("//div[@class='links']/a[text()='>']/@href")
        if len(next) > 0:
            return next.extract()[0]
