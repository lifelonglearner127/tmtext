import re
import json
import urlparse
from product_ranking.items import SiteProductItem
from .cvs import CvsProductsSpider
from scrapy import Request
import urllib

class CvsShelfPagesSpider(CvsProductsSpider):
    name = 'cvs_shelf_urls_products'
    allowed_domains = ["cvs.com", "api.bazaarvoice.com"]

    SEARCH_URL_AJAX = "https://www.cvs.com/" \
                      "retail/frontstore/OnlineShopService?" \
                      "apiKey=c9c4a7d0-0a3c-4e88-ae30-ab24d2064e43&" \
                      "apiSecret=4bcd4484-c9f5-4479-a5ac-9e8e2c8ad4b0&" \
                      "appName=CVS_WEB&" \
                      "channelName=WEB&" \
                      "contentZone=resultListZone&" \
                      "deviceToken=7780&" \
                      "deviceType=DESKTOP&" \
                      "lineOfBusiness=RETAIL&" \
                      "navNum=100&" \
                      "operationName=getProductResultList&" \
                      "pageNum={page_num}&" \
                      "referer={referer}&" \
                      "serviceCORS=False&" \
                      "serviceName=OnlineShopService&" \
                      "sortBy=highestRated&" \
                      "version=1.0" \

    use_proxies = True

    def __init__(self, *args, **kwargs):
        super(CvsShelfPagesSpider, self).__init__(*args, **kwargs)
        self.product_url = kwargs['product_url']
        self.products_per_page = 100

        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1

        self.current_page = 1
        self.shelf_categories = ''

    @staticmethod
    def valid_url(url):
        if not re.findall(r"http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta={'remaining': self.quantity,
                            'search_term': ''})

    def parse(self, response):
        try:
            self.total_matches = int(json.loads(response.body_as_unicode()).get('response').get(
                'details').get('skuGroupCount'))
        except:
            self.total_matches = None
        if not self.referer:
            self.referer = response.url
        shelf_categories_text = response.xpath(
            '//script[contains(text(), "breadcrumb")]/text()').re(
            'breadcrumb : (\[.+?\])'
        )
        if not self.shelf_categories:
            self.shelf_categories = json.loads(shelf_categories_text[0])[2:]
        return super(CvsShelfPagesSpider, self).parse(response)

    def _scrape_product_links(self, response):
        all_links_iter = re.finditer(
            'detailsLink"\s*:\s*"(.*?)(\?skuId=\d+)?",', response.body)

        # Clean the links for the different variants of a product
        links_without_dup = []
        [links_without_dup.append(item) for item in map((lambda x: x.group(1)), all_links_iter)
         if item not in links_without_dup]
        # parse shelf category

        for link in links_without_dup:
            item = SiteProductItem()
            if self.shelf_categories:
                item['shelf_name'] = self.shelf_categories
            if self.shelf_categories:
                item['shelf_path'] = self.shelf_categories[-1]
            yield link, item

    def _scrape_next_results_page_link(self, response):
        if self.current_page > self.num_pages or self.current_page > (self.total_matches_int/self.products_per_page) + 1:
            return
        url_parts = urlparse.urlsplit(response.url)
        query_string = urlparse.parse_qs(url_parts.query)

        ajax_search_url = self.SEARCH_URL_AJAX.format(
            referer=urllib.quote_plus(self.referer, ':'),
            page_num=self.current_page)
        self.current_page += 1

        headers = {'Accept': 'application/json, text/plain, */*',
                   'Cache-Control': 'no-cache',
                   'Connection': 'keep-alive',
                   'Host': 'www.cvs.com',
                   'Pragma': 'no-cache',
                   'Referer': self.referer,
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)'
                                 ' AppleWebKit/537.36 (KHTML, like Gecko)'
                                 ' Chrome/49.0.2623.110 Safari/537.36'}

        return Request(ajax_search_url,
                       self.parse,
                       headers=headers,
                       meta=response.meta,
                       priority=1)

    def parse_product(self, response):
        return super(CvsShelfPagesSpider, self).parse_product(response)

    def _scrape_results_per_page(self, response):
        return 100

    def _get_products(self, response):
        return super(CvsShelfPagesSpider, self)._get_products(response)

    def _scrape_total_matches(self, response):
        if self.total_matches:
            self.total_matches_int = self.total_matches
        else:
            self.total_matches_int = self.products_per_page

        return self.total_matches
