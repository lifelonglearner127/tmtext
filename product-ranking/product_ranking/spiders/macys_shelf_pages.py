# TODO: check "product_per_page" fields, may be wrong

import re
import urlparse

import scrapy
from scrapy.http import Request
from scrapy import Selector

from product_ranking.items import SiteProductItem

is_empty = lambda x: x[0] if x else None


class MacysShelfPagesSpider(scrapy.Spider):
    name = 'macys_shelf_urls_products'
    allowed_domains = ['macys.com', 'www1.macys.com', 'www.macys.com']

    current_page = 1

    def __init__(self, *args, **kwargs):
        self.product_url = kwargs['product_url']

        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0

        self.user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64))" \
            " AppleWebKit/537.36 (KHTML, like Gecko)" \
            " Chrome/37.0.2062.120 Safari/537.36"

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url))

    def parse(self, response):
        yield self.get_urls(response)
        request = self.next_pagination_link(response)
        if request is not None:
            yield request

    def get_urls(self, response):
        item = SiteProductItem()
        urls = response.xpath(
            '//span[contains(@id, "main_images_holder")]/../../a/@href'
        ).extract()

        urls = [urlparse.urljoin(response.url, x) if x.startswith('/') else x
                for x in urls]
        assortment_url = {response.url: urls}
        item["assortment_url"] = assortment_url
        item['results_per_page'] = self._scrape_results_per_page(response)
        item['scraped_results_per_page'] = len(urls)
        return item

    def _scrape_results_per_page(self, response):
        num = ''.join(
            response.xpath(
                '//*[contains(@id, "productCount")]/text()').extract()
        ).strip()
        if num:
            num = num.strip()
            if num.isdigit():
                return int(num)

    def next_pagination_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1

        next_link = is_empty(
            response.xpath('//a[contains(@class, "arrowRight")]/@href').extract()
        )

        if next_link:
            url = urlparse.urljoin(response.url, next_link)
            return Request(url=url)

    def valid_url(self, url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url