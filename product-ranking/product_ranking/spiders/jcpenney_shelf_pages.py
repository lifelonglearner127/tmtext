# TODO: check "product_per_page" fields, may be wrong

import re
import urlparse

import scrapy
from scrapy.http import Request

from product_ranking.items import SiteProductItem
from .jcpenney import JcpenneyProductsSpider

is_empty = lambda x: x[0] if x else None


class JCPenneyShelfPagesSpider(JcpenneyProductsSpider):
    name = 'jcpenney_shelf_urls_products'
    allowed_domains = ['jcpenney.com', 'www.jcpenney.com']

    current_page = 1

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
        self.product_url = kwargs['product_url']

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

    def parse(self, response):
        yield self.get_urls(response)
        request = self.next_pagination_link(response)
        if request is not None:
            yield request

    def get_urls(self, response):
        item = SiteProductItem()
        urls = response.xpath(
            '//div[contains(@class, "product_description")]'
            '//img[contains(@id, "ThumbnailImage")]/../../../a/@href'
        ).extract()
        urls = [urlparse.urljoin(response.url, x) if x.startswith('/') else x
                for x in urls]
        #print "-"*50
        #print len(urls)
        #print "-"*50
        assortment_url = {response.url: urls}
        item["assortment_url"] = assortment_url
        item['results_per_page'] = self._scrape_results_per_page(response)
        item['scraped_results_per_page'] = len(urls)
        return item

    def _scrape_results_per_page(self, response):
        num = None
        try:
            num = response.xpath(
                '//*[contains(text(), "items per page")]/..//strong//span/text()'
            ).re('\d+')[0]
        except IndexError:
            self.log('Failed to get num of results')
        if isinstance(num, (str, unicode)) and num.isdigit():
            return int(num)

    def next_pagination_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1

        next_link = is_empty(
            response.xpath('//a[contains(@title, "next page")]/@href').extract())

        if next_link:
            url = urlparse.urljoin(response.url, next_link)
            return Request(url=url)

    def valid_url(self, url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url