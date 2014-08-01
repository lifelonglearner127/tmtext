from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
from future_builtins import *

import re
import urlparse
import urllib

from scrapy.log import ERROR, WARNING
from scrapy.http import Request

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set


class CostcoProductsSpider(BaseProductsSpider):
    name = "costco_products"
    allowed_domains = ["costco.com"]
    start_urls = []
    SEARCH_URL = "http://www.costco.com/CatalogSearch?pageSize=96" \
                 "&catalogId=10701&langId=-1&storeId=10301" \
                 "&currentPage=1&keyword={search_term}"

    def parse_product(self, response):
        prod = response.meta['product']

        model = response.xpath('//div[@id="product-tab1"]//text()').re(
            'Model[\W\w\s]*')
        if len(model) > 0:
            cond_set(prod, 'model', model)
            if prod.has_key('model'):
                prod['model'] = re.sub(r'Model\W*', '', prod['model'].strip())

        title = response.xpath('//h1[@itemprop="name"]/text()').extract()
        cond_set(prod, 'title', title)

        tab2 = ''.join(
            response.xpath('//div[@id="product-tab2"]//text()').extract()
        ).strip()
        brand = ''
        for i in tab2.split('\n'):
            if 'Brand' in i.strip():
                brand = i.strip()
        brand = re.sub(r'Brand\W*', '', brand)
        if brand:
            prod['brand'] = brand

        price = response.xpath(
            '//input[contains(@name,"price")]/@value'
        ).extract()
        cond_set(prod, 'price', price)
        set_price = prod.get('price', '')
        if not set_price or set_price == '$0.00':
            del prod['price']

        des = response.xpath('//div[@id="product-tab1"]//text()').extract()
        des = ' '.join([i.strip() for i in des])
        if des.strip():
            prod['description'] = des.strip()

        img_url = response.xpath('//img[@itemprop="image"]/@src').extract()
        cond_set(prod, 'image_url', img_url)

        cond_set(prod, 'locale', ['en-US'])
        prod['url'] = response.url

        return prod

    def _get_next_products_page(self, response, prods_found):
        link_page_attempt = response.meta.get('link_page_attempt', 1)

        result = None
        if prods_found > 0:
            # This was a real product listing page.
            remaining = response.meta['remaining']
            remaining -= prods_found
            if remaining > 0:
                next_page = self._scrape_next_results_page_link(response)
                if next_page is not None:
                    url = urlparse.urljoin(response.url, next_page)
                    new_meta = dict(response.meta)
                    new_meta['remaining'] = remaining
                    result = Request(url, self.parse, meta=new_meta, priority=1)
        elif link_page_attempt > 2:
            self.log(
                "Giving up on results page after %d attempts: %s" % (
                    link_page_attempt, response.request.url),
                ERROR
            )
        else:
            self.log(
                "Will retry to get results page (attempt %d): %s" % (
                    link_page_attempt, response.request.url),
                WARNING
            )

            # Found no product links. Probably a transient error, lets retry.
            new_meta = dict(response.meta)
            new_meta['link_page_attempt'] = link_page_attempt + 1
            # Add an attribute so that Scrapy doesn't discard as duplicate.
            url = response.url + "&_=%d" % link_page_attempt
            result = Request(url, self.parse, meta=new_meta, priority=1)

        return result

    def _search_page_error(self, response):
        if not self._scrape_total_matches(response):
            self.log("Costco: unable to find a match", ERROR)
            return True
        return False

    def _scrape_total_matches(self, sel):
        try:
            count = sel.xpath(
                '//*[@id="secondary_content_wrapper"]/div/p/span/text()'
            ).re('(\d+)')[-1]
            if count:
                return int(count)
            return 0
        except IndexError:
            return 0

    def _scrape_product_links(self, sel):
        links = sel.xpath(
            '//div[contains(@class,"product-tile-image-container")]/a/@href'
        ).extract()
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        url_parse = urlparse.urlsplit(response.url)
        paras = urlparse.parse_qs(url_parse.query)
        new_paras = {}
        for key in paras:
            new_paras[key] = paras[key][0]
        new_paras['currentPage'] = int(new_paras.get("currentPage", 1)) + 1
        link = urlparse.urlunsplit((
            url_parse.scheme,
            url_parse.netloc,
            url_parse.path,
            urllib.urlencode(new_paras),
            url_parse.fragment,
        ))
        return link
