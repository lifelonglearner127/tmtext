import os.path
import re
import urlparse
import requests
import json

import scrapy
from scrapy.log import WARNING, ERROR
from scrapy.http import Request
from scrapy import Selector

from product_ranking.items import SiteProductItem
from spiders_shared_code.walmart_categories import WalmartCategoryParser

is_empty = lambda x: x[0] if x else None

from .walmart import WalmartProductsSpider


class WalmartShelfPagesSpider(WalmartProductsSpider):
    name = 'walmart_shelf_urls_products'
    allowed_domains = ["walmart.com", "msn.com", 'api.walmartlabs.com']  # without this find_spiders() fails

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
        super(WalmartShelfPagesSpider, self).__init__(*args, **kwargs)
        self._setup_class_compatibility()

        self.product_url = kwargs['product_url']

        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0

        # variants are switched off by default, see Bugzilla 3982#c11
        self.scrape_variants_with_extra_requests = False
        if 'scrape_variants_with_extra_requests' in kwargs:
            scrape_variants_with_extra_requests = kwargs['scrape_variants_with_extra_requests']
            if scrape_variants_with_extra_requests in (1, '1', 'true', 'True', True):
                self.scrape_variants_with_extra_requests = True

    @staticmethod
    def valid_url(url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "https://" + url
        return url

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta=self._setup_meta_compatibility(),
                      headers={"X-Forwarded-For": "127.0.0.1"})  # meta is for SC baseclass compatibility

    def _scrape_product_links(self, response):
        item = response.meta.get('product', SiteProductItem())
        meta = response.meta
        urls = response.xpath(
            '//li/div/a[contains(@class, "js-product-title")]/@href').extract()

        if not urls:
            urls = response.xpath(
                '//h4[contains(@class, "tile-heading")]/a/@href').extract()
        if not urls:
            urls = response.xpath(
                '//div[contains(@class, "js-product-image-zone")]' \
                '//div[contains(@class, "js-tile tile")]' \
                '/a[1][contains(@class, "tile-section")]' \
                '[contains(@href, "/ip/")]/@href'
            ).extract()

            data = is_empty(re.findall(
                "window._WML.MIDAS_CONTEXT\s+\=\s+([^\;].*)", response.body
            ))
            if data:
                try:
                    data = json.loads(data[0:-1])
                    pageId = is_empty(
                        re.findall("\:(\d+)", data["categoryPathId"]))
                    keyword = data["categoryPathName"]
                except Exception:
                    pass
            if pageId and keyword:
                get_rec = "https://www.walmart.com/msp?"\
                    "&module=wpa&type=product&min=7&max=20"\
                    "&platform=desktop&pageType=category"\
                    "&pageId=%s&keyword=%s" % (pageId, keyword)
                #print "-"*50
                #print get_rec
                #print "-"*50
                resp = requests.get(get_rec)
                urls_get = Selector(text=resp.text).xpath(
                    '//div[contains(@class, "js-module-sponsored-products")]' \
                    '//div[contains(@class, "js-tile tile")]' \
                    '/a[1][contains(@class, "tile-section")]/@href'
                ).extract()
                for url in urls_get:
                    r = requests.get(urlparse.urljoin(response.url, url), allow_redirects=True)
                    urls += (r.url, )

        urls = [urlparse.urljoin(response.url, x) for x in urls]

        # parse shelf category
        shelf_categories = [c.strip() for c in response.css('ol.breadcrumb-list ::text').extract()
                            if len(c.strip()) > 1]
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
        return super(WalmartShelfPagesSpider, self)._scrape_next_results_page_link(response)

    def parse_product(self, response):
        product = response.meta['product']
        # scrape Shelf Name, e.g. Diapers, and Shelf Path, e.g. Baby/Diapering/Diapers
        wcp = WalmartCategoryParser()
        wcp.setupSC(response)
        try:
            product['categories'] = wcp._categories_hierarchy()
        except Exception as e:
            self.log('Category not parsed: '+str(e), WARNING)
        try:
            product['category'] = wcp._category()
        except Exception as e:
            self.log('No department to parse: '+str(e), WARNING)
        response.meta['product'] = product
        return super(WalmartShelfPagesSpider, self).parse_product(response)