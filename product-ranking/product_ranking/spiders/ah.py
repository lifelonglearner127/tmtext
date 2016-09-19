# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re

from scrapy.log import ERROR, DEBUG

from product_ranking.items import SiteProductItem, Price
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

is_empty = lambda x: x[0] if x else None


class AhProductsSpider(BaseProductsSpider):
    name = 'ah_products'
    allowed_domains = ["ah.nl"]
    start_urls = []

    SEARCH_URL = ("http://www.ah.nl/zoeken?rq={search_term}"
                  "&sorting={sort}")

    additional_url = "http://www.ah.nl/"

    SORT_BY = {
        'relevance': 'relevance',
        'name': 'name_asc',
    }

    def __init__(self, *args, **kwargs):
        self.sort_by = self.SORT_BY.get(
            kwargs.get('order', 'relevance'), 'relevance')
        formatter = FormatterWithDefaults(sort=self.sort_by)
        super(AhProductsSpider, self).__init__(formatter, *args, **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _scrape_product_links(self, response):

        links = response.xpath(
            './/div[@class="detail"]/a[contains(@href, "/product/")]/@href'
        ).extract() 

        for link in links:            
            yield self.additional_url + link, SiteProductItem()

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

    @staticmethod
    def _parse_reseller_id(url):
        regex = "(wi\d+)"
        reseller_id = re.findall(regex, url)
        reseller_id = reseller_id[0] if reseller_id else None
        return reseller_id

    def parse_product(self, response):
        product = response.meta['product']
        product['reseller_id'] = self._parse_reseller_id(response.url)
        title = response.xpath('//h1[@class="h1"]/text()[normalize-space()]').extract()
        cond_set(product, 'title', title)
        if product.get('title'):
            product['title'] = product['title']

        cond_set(
            product, 'image_url',
            response.xpath('//div[@class="product-detail__image"]'
                           '/a/img/@src').extract()
        )

        price = response.xpath(
            '//p/meta[@itemprop="price"]/@content'
        ).extract()
        priceCurrency = response.xpath(
            '//p/meta[@itemprop="priceCurrency"]/@content'
        ).extract()

        if price:
            product["price"] = Price(
                priceCurrency=is_empty(priceCurrency),
                price=price[0]
            )

        if not product.get('image_url'):
            cond_set(
                product, 'image_url',
                response.xpath('//div[@class="product-detail__image"]'
                               '//img/@src').extract()
            )
        cond_set(
            product, 'brand',
            response.xpath('.//meta[@itemprop="brand"]/@content').extract()
        )

        description = response.xpath(
            '//div[contains(@class, "row product-detail__content product-detail__border-row")]'
        ).extract()
        if description:
            cond_set(product, 'description', (description[0].replace("\t", "").replace("\n", ""),))
        return product