from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set_value
from scrapy.log import ERROR
from scrapy import Selector

import json
import urllib
import urllib2
import urlparse


class ColesonlineProductsSpider(BaseProductsSpider):
    name = 'colesonline_products'
    allowed_domains = ["coles.com.au"]
    start_urls = []

    SEARCH_URL = "http://shop.coles.com.au/online/SearchDisplay?storeId=10601" \
                 "&catalogId=10576&langId=-1&beginIndex=0&browseView=false&searchSource=Q" \
                 "&sType=SimpleSearch&resultCatEntryType=2&showResultsPage=true" \
                 "&pageView=image&searchTerm={search_term}"

    def parse_product(self, response):
        raise AssertionError("This method should never be called.")

    def _scrape_total_matches(self, response):
        num_results = response.xpath(
            "//p[@class='pageInfo']/span/text()").re('(\d+)')[0]

        if num_results:
            return int(num_results)
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _get_next_page(self, response, index):

        url = 'http://shop.coles.com.au/online/ColesSearchView'
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                     'Chrome/36.0.1985.143 Safari/537.36'
        headers = {'User-Agent': user_agent}
        searchterm = response.meta['search_term']

        values = {
            'refreshId': 'searchView',
            'multiSearch': '',
            'productView': 'list',
            'searchTerm': searchterm,
            'orderBy': '',
            'beginIndex': index,
            'pageSize': '40',
            'storeId': '10601',
            'catalogId': '10576',
            'browseView': 'false',
            'langId': '-1',
            'sequence': '1',
            'context': 'refreshController.+refreshArea',
            'serviceId': 'ColesSearchView',
            'expectedType': 'text',
        }
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data, headers)
        resp = urllib2.urlopen(req)
        next_page = resp.read()
        sel = Selector(text=next_page)

        return sel

    def _scrape_product_links(self, response):

        totalhits = 0

        index = response.xpath("//li[@class='next']/a/@data-beginindex").extract()[0]

        sel = self._get_next_page(response, index)

        num_results = sel.xpath(
            "//p[@class='pageInfo']/span/text()").re('(\d+)')[0]

        # cannot seem to get any of the data here to load
        # json_data = sel.xpath("//div[@id='share']/@data-social/").extract()[0]
        # json_data = re.sub('\s+', '', json_data)
        # thedata = json.loads(json_data)

        brands = sel.xpath("//span[@class='brand']/text()").extract()

        urls = sel.xpath("//span/a[@class='product-url']/@href").extract()

        img_urls = sel.xpath("//img[@class='photo']/@src").extract()


        # descriptions = sel.xpath(
        # "//div[@id='share']/@data-social").extract()
        # cond_set(product, 'description', descriptions)

        # tag_re = re.compile(r'<[^>]+>')
        # desc = tag_re.sub('', description).strip()
        # desc = ' '.join(desc.split())

        titles = sel.xpath("//div[@class='list']/a/span/text()").extract()

        prices = sel.xpath("//div[@class='price']/text()").extract()

        totalhits += len(urls)

        while totalhits <= int(num_results):
            for x in range(0, len(urls)):
                product = SiteProductItem()
                cond_set_value(product, 'title', titles[x])
                cond_set_value(product, 'brand', brands[x])
                cond_set_value(product, 'url', urls[x])
                cond_set_value(product, 'image_url', urlparse.urljoin(response.url, img_urls[x]))
                cond_set_value(product, 'price', prices[x])
                cond_set_value(product, 'locale', 'en-AU')

                yield None, product
            totalhits += len(urls)
            if totalhits < int(num_results):
                index = sel.xpath("//li[@class='next']/a/@data-beginindex").extract()[0]
                sel = self._get_next_page(response, index)
                brands = sel.xpath("//span[@class='brand']/text()").extract()
                urls = sel.xpath("//span/a[@class='product-url']/@href").extract()
                img_urls = sel.xpath("//img[@class='photo']/@src").extract()
                titles = sel.xpath("//div[@class='list']/a/span/text()").extract()
                prices = sel.xpath("//div[@class='price']/text()").extract()

    def _scrape_next_results_page_link(self, response):
        raise AssertionError("This method should never be called.")