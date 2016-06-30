import re
import urlparse

import scrapy
from scrapy.log import WARNING, ERROR
from scrapy.http import Request
from scrapy import Selector

from product_ranking.items import SiteProductItem

is_empty = lambda x: x[0] if x else None

from .wag import WagProductsSpider


class WagShelfPagesSpider(WagProductsSpider):
    name = 'wag_shelf_urls_products'
    allowed_domains = ["wag.com", "www.wag.com"]  # without this find_spiders() fails

    def _setup_class_compatibility(self):
        """ Needed to maintain compatibility with the SC spiders baseclass """
        self.quantity = 99999
        self.site_name = self.allowed_domains[0]
        self.user_agent_key = None
        self.zip_code = '12345'
        self.current_page = 1

    def _setup_meta_compatibility(self):
        """ Needed to prepare first request.meta vars to use """
        return {'remaining': 99999, 'search_term': ''}.copy()

    def __init__(self, *args, **kwargs):
        super(WagShelfPagesSpider, self).__init__(*args, **kwargs)
        self._setup_class_compatibility()

        self.product_url = kwargs['product_url']

        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0

        self.user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64))" \
            " AppleWebKit/537.36 (KHTML, like Gecko)" \
            " Chrome/37.0.2062.120 Safari/537.36"

        # variants are switched off by default, see Bugzilla 3982#c11
        self.scrape_variants_with_extra_requests = False
        if 'scrape_variants_with_extra_requests' in kwargs:
            scrape_variants_with_extra_requests = kwargs['scrape_variants_with_extra_requests']
            if scrape_variants_with_extra_requests in (1, '1', 'true', 'True', True):
                self.scrape_variants_with_extra_requests = True

    @staticmethod
    def valid_url(url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta=self._setup_meta_compatibility())  # meta is for SC baseclass compatibility

    def _scrape_product_links(self, response):
        urls = response.xpath('//a[@class="product-box-link"]/@href').extract()
        urls = [urlparse.urljoin(response.url, x) for x in urls]

        shelf_categories = response.xpath('//ol[@class="breadcrumb"]/li/a/text()'
                                            '| //ol[@class="breadcrumb"]/li/h1/text()').extract()
        shelf_category = response.xpath('//div[@class="left-nav-title"]/span/text()').extract()

        for url in urls:
            item = SiteProductItem()
            if shelf_category:
                item['shelf_name'] = shelf_category[0].replace('"', "").strip()
            if shelf_categories:
                item['shelf_path'] = shelf_categories
            yield url, item

    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1
        spliturl = self.product_url.split('?')
        nextlink = spliturl[0]
        if len(spliturl) == 1:
            return (nextlink + "?pg=%d" % self.current_page)
        else:
            nextlink += "?"
            for s in spliturl[1].split('&'):
                if not "pg=" in s:
                    nextlink += s + "&"
            return (nextlink + "pg=%d" % self.current_page)

    def parse_product(self, response):
        return super(WagShelfPagesSpider, self).parse_product(response)