from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import json
import urllib
import urllib2
import urlparse
import re

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set_value


class WaitroseProductsSpider(BaseProductsSpider):
    name = "waitrose_products"
    allowed_domains = ["waitrose.com"]
    start_urls = []

    SEARCH_URL = "http://www.waitrose.com/shop/HeaderSearchCmd?searchTerm={search_term}&defaultSearch=GR&search="

    def parse_product(self, response):
        raise AssertionError("This method should never be called.")

    def _scrape_total_matches(self, response):
        count = response.xpath(
            '//span[@id="current-breadcrumb"]/text()'
        ).re('(\d+)')
        if count:
            return int(count[0])
        return 0

    def _scrape_product_links(self, response):

        total_pages = response.xpath('//input[@id="number-of-pages"]/@value').extract()[0]
        browse_url = response.xpath('//input[@id="browse-url"]/@value').extract()[0]
        links = response.xpath('//a[@class="m-product-open-modal"]/@href').extract()

        url = 'http://www.waitrose.com/shop/BrowseAjaxCmd'
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                     'Chrome/36.0.1985.143 Safari/537.36'
        headers = {'User-Agent': user_agent}

        for page in range(1, int(total_pages)):
            values = {'browse': browse_url + '/sort_by/NONE/sort_direction/descending/page/' + str(page)}
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data, headers)
            resp = urllib2.urlopen(req)
            json_data = json.loads(resp.read())

            for products in json_data['products']:
                prod = SiteProductItem()
                regex = re.compile("(\d+.\d+)")
                p = regex.search(products['price'])
                if p:
                    price = p.group(1)
                else:
                    price = '0.00'
                cond_set_value(prod, 'title', products['name'])
                cond_set_value(prod, 'price', [price])
                cond_set_value(prod, 'upc', int(products['id']))
                cond_set_value(prod, 'model', products['productid'])
                cond_set_value(prod, 'image_url', products['image'])
                cond_set_value(prod, 'url', urlparse.urljoin(response.url, products['url']))

                # some products do not have a summary
                try:
                    cond_set_value(prod, 'description', products['summary'])
                except KeyError:
                    prod['description'] = ''

                prod['locale'] = "en-GB"

                yield None, prod

    def _scrape_next_results_page_link(self, response):
        raise AssertionError("This method should never be called.")