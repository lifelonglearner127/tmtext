from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json
import urllib
import urllib2
import urlparse
import re

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set_value


# FIXME Overrides USER AGENT unconditionally.
# FIXME Makes a request using urllib.

class WaitroseProductsSpider(BaseProductsSpider):
    name = "waitrose_products"
    allowed_domains = ["waitrose.com"]
    start_urls = []

    SEARCH_URL = "http://www.waitrose.com/shop/HeaderSearchCmd" \
        "?searchTerm={search_term}&defaultSearch=GR&search="

    _USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
        '(KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36'

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
        total_pages = response.xpath(
            '//input[@id="number-of-pages"]/@value').extract()[0]
        links = response.xpath(
            '//a[@class="m-product-open-modal"]/@href').extract()

        # FIXME Only use a hardcoded user agent if the default wasn't overrided.
        url = 'http://www.waitrose.com/shop/BrowseAjaxCmd'
        headers = {'User-Agent': WaitroseProductsSpider._USER_AGENT}

        browse_url = response.xpath('//input[@id="browse-url"]/@value').extract()[0]
        for page in range(1, int(total_pages)):
            values = {
                'browse': urlparse.urljoin(
                    browse_url,
                    '/sort_by/NONE/sort_direction/descending/page/' + str(page)
                ),
            }
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data, headers)
            # FIXME: Why do this? Return a Request for Scrapy to make the request.
            resp = urllib2.urlopen(req)
            json_data = json.load(resp)

            for prod_data in json_data['products']:
                import pdb; pdb.set_trace()
                prod = SiteProductItem()
                regex = re.compile("(\d+.\d+)")
                p = regex.search(prod_data['price'])
                if p:
                    price = p.group(1)
                else:
                    # FIXME: Don't!
                    price = '0.00'
                cond_set_value(prod, 'title', prod_data['name'])
                cond_set_value(prod, 'price', price)
                cond_set_value(prod, 'upc', int(prod_data['id']))
                cond_set_value(prod, 'model', prod_data['productid'])
                cond_set_value(prod, 'image_url', prod_data['image'])
                cond_set_value(
                    prod,
                    'url',
                    urlparse.urljoin(response.url, prod_data['url']),
                )

                # Some products do not have a summary.
                cond_set_value(prod, 'description', prod_data.get('summary'))

                prod['locale'] = "en-GB"

                yield None, prod

    def _scrape_next_results_page_link(self, response):
        raise AssertionError("This method should never be called.")