# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re

from scrapy.log import ERROR, DEBUG

from product_ranking.items import SiteProductItem
from product_ranking.spiders import (BaseProductsSpider, FormatterWithDefaults,
                                     cond_set, cond_set_value)


def _get_next_page(current_url, offset_per_page):
    current_offset = re.search('offset=(\d+)', current_url)
    current_offset = int(current_offset.group(1).strip())
    new_offset = current_offset + offset_per_page
    return (
        re.sub('(offset=)(\d+)', '\g<1>'+str(new_offset), current_url),
        current_offset,
        new_offset
    )


class AhProductsSpider(BaseProductsSpider):
    name = 'ah_products'
    allowed_domains = ["ah.nl"]
    start_urls = []

    SEARCH_URL = ("http://www.ah.nl/appie/zoeken?rq={search_term}"
                  "&sorting={sort}")

    SORT_BY = {
        'relevance': 'relevance',
        'name': 'name_asc',
    }

    def __init__(self, *args, **kwargs):
        self.sort_by = self.SORT_BY.get(
            kwargs.get('order', 'relevance'), 'relevance')
        formatter = FormatterWithDefaults(sort=self.sort_by)
        super(AhProductsSpider, self).__init__(formatter, *args, **kwargs)

    def _scrape_product_links(self, response):
        products = response.xpath('//div[contains(@class, "canvas_card")]'
                                  '[contains(@class, "product")]')
        if not products:
            self.log("Found no product links.", ERROR)

        for product in products:
            item = SiteProductItem()
            cond_set(item, 'title',
                     product.css('div.detail h2::text').extract())
            if item.get('title'):
                item['title'] = item['title'].strip()
            cond_set(
                item, 'image_url',
                product.xpath(
                    './/div[contains(@class, "image")]'
                    '//img[not(contains(@src, "no-product-image"))]/@src'
                ).extract()
            )
            _base_price = product.xpath('.//*[contains(@class, "price")]/ins')
            _price_main = _base_price.xpath('text()').extract()[0]
            _price_extra = _base_price.xpath('./span/text()').extract()
            item['price'] = _price_main
            if len(_price_extra):
                item['price'] += _price_extra[0]

            if item.get('price') and not '€' in item.get('price'):
                item['price'] = item['price'].strip() + ' €'
            item['locale'] = 'nl-NL'

            _id = product.xpath('.//div[@class="detail"]/a[contains'
                                '(@href, "/product/")]/@href').extract()
            if not _id:
                self.log('Product details URL has not been found', ERROR)
                continue
            _id = _id[0].replace('/appie/producten/product/', '')
            if not '/' in _id:
                self.log('Invalid details URL: ' + _id, ERROR)
                continue
            _id = _id.split('/', 1)[0].strip()
            prod_url = ('http://www.ah.nl/appie/data_/producten/product/'
                        '%s/johma-kipsate-salade?pageType=PRODUCTS' % _id)
            yield prod_url, item

    def _scrape_next_results_page_link(self, response):
        # this website uses offsets instead of pagination, so we simple
        #  increase the offset param every time by `page_offset`
        num_items = min(response.meta.get('total_matches', 0), self.quantity)
        if not num_items:
            return
        page_offset = 60
        new_offset = page_offset
        url = response.url
        if not 'offset=' in url:
            url += '&offset=%i' % page_offset
        else:
            url, _, new_offset = _get_next_page(url, page_offset)
        if new_offset > getattr(self, 'total_results', 0):
            return  # if we've scraped all the items already
        return url

    def _scrape_total_matches(self, response):
        totals = response.css('div.page-controls').re('van (\d+)')
        if totals:
            total = int(totals[0])
        else:
            if 'geen producten gevonden' in response.body.lower():
                return 0  # nothing has been found
            else:
                self.log(
                    "'total matches' string not found at %s" % response.url,
                    ERROR
                )
                return
        self.total_results = total  # remember num of results
        return total

    def parse_product(self, response):
        product = response.meta['product']
        cond_set(
            product, 'image_url',
            response.xpath('//div[@class="product-detail__image"]'
                           '/a/img/@src').extract()
        )
        cond_set(
            product, 'brand',
            response.xpath('.//meta[@itemprop="brand"]/@content').extract()
        )
        cond_set(product, 'description',
                 response.xpath(
                     './/div[contains(@class, "product-detail__content")]'
                     '/div/p//text()'
                 ).extract())
        return product