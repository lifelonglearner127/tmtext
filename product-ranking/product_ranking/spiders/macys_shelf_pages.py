# TODO: check "product_per_page" fields, may be wrong

import re
import urlparse

import scrapy
from scrapy.http import Request
from scrapy import Selector

from product_ranking.items import SiteProductItem
from .macys import MacysProductsSpider

is_empty = lambda x: x[0] if x else None


class MacysShelfPagesSpider(MacysProductsSpider):
    name = 'macys_shelf_urls_products'
    allowed_domains = ['macys.com', 'www1.macys.com', 'www.macys.com']

    def _setup_class_compatibility(self):
        """ Needed to maintain compatibility with the SC spiders baseclass """
        self.quantity = 99999
        self.site_name = self.allowed_domains[0]
        self.user_agent_key = None
        self.zipcode = '12345'
        self.current_page = 1

    def _setup_meta_compatibility(self):
        """ Needed to prepare first request.meta vars to use """
        return {'remaining': 99999, 'search_term': ''}.copy()

    def __init__(self, *args, **kwargs):
        super(MacysShelfPagesSpider, self).__init__(*args, **kwargs)
        self.product_url = kwargs['product_url']
        self._setup_class_compatibility()

        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0

        self.user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64))" \
            " AppleWebKit/537.36 (KHTML, like Gecko)" \
            " Chrome/37.0.2062.120 Safari/537.36"

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta=self._setup_meta_compatibility())

    @staticmethod
    def valid_url(url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def _scrape_product_links(self, response):
        urls = response.xpath(
            '//span[contains(@id, "main_images_holder")]/../../a/@href'
        ).extract()

        urls = ['http://www1.macys.com' + i for i in urls]

        sample = response.xpath('//div[@id="featureNav"]/ul/li//text()').extract()
        categories = [i.strip() for i in reversed(sample) if i.strip()]

        shelf_categories = categories[1:]
        shelf_category = shelf_categories[-1] if shelf_categories else None

        for url in urls:
            item = SiteProductItem()
            if shelf_category:
                item['shelf_name'] = shelf_category
            if shelf_categories:
                item['shelf_path'] = shelf_categories
            yield url, item

    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1
        return super(MacysShelfPagesSpider,
                     self)._scrape_next_results_page_link(response)

    def parse_product(self, response):
        return super(MacysShelfPagesSpider, self).parse_product(response)
