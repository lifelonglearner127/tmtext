from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import urlparse

from scrapy.log import ERROR

from product_ranking.items import SiteProductItem, Price, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, \
    FormatterWithDefaults, FLOATING_POINT_RGEX, cond_set


class BabySecurityProductSpider(BaseProductsSpider):
    name = 'babysecurity_products'
    allowed_domains = ["babysecurity.co.uk"]

    SEARCH_URL = "http://www.babysecurity.co.uk/catalogsearch/" \
                 "result/index/?dir={direction}&order={search_sort}&q={search_term}"

    SEARCH_SORT = {
        'best_sellers': 'bestsellers',
        'recommended': 'position',
        'name': 'name',
        'price': 'price',
    }

    def __init__(self, search_sort='best_sellers', direction='asc', *args, **kwargs):
        super(BabySecurityProductSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self.SEARCH_SORT[search_sort],
                direction=direction,
            ),
            *args,
            **kwargs)

    def _scrape_total_matches(self, response):
        nums = response.xpath(
            'string(//p[@class="amount"])').re('(\d+)')
        if not nums:
            return None

        return int(nums[-1])

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//li[@class="item"]'
            '//h2[@class="product-name"]/a/@href').extract()
        if not links:
            self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath(
            '//li[@class="next"]'
            '/a[contains(@class,"next")]/@href').extract()
        if next and next[0]:
            return next[0]
        else:
            return None

    def parse_product(self, response):
        prod = response.meta['product']
        prod['url'] = response.url
        prod['locale'] = 'en-GB'

        brand = response.xpath(
            '//div[contains(@class,"box-brand")]/a/img/@alt').extract()
        if brand:
            prod['brand'] = brand[0].strip()
        else:
            brand = response.xpath(
                '//div[contains(@class,"brand-name")]/text()').extract()
            cond_set(
                prod, 'brand', brand, lambda x: x.strip())

        title = response.xpath(
            'string(//h1[@itemprop="name"])').extract()
        cond_set(prod, 'title', title, lambda x: x.strip())

        img = response.xpath('//a[@id="zoom-btn"]/@href').extract()
        if img:
            prod['image_url'] = img[0]

        price = response.xpath(
            '//div[@class="product-type-data"]'
            '//span[@class="price"]/text()').re(FLOATING_POINT_RGEX)
        if price:
            if len(price) > 1:
                price = price[1]
            else:
                price = price[0]
            prod['price'] = Price(price=price,
                                  priceCurrency='GBP')

        description = response.xpath('string(//div[@class="std"])').extract()
        cond_set(prod, 'description', description, lambda x: x.strip())

        avail = response.xpath('//*[@itemprop="availability"]/@content').extract()
        if avail:
            if "http://schema.org/OutOfStock" in avail[0]:
                prod['is_out_of_stock'] = True
            else:
                prod['is_out_of_stock'] = False

        recommendations = []
        for a_tag in response.xpath(
                '//div[contains(@class,"box-up-sell")]'
                '//div[@class="item"]//h3[@class="product-name"]/a'):
            item_title = a_tag.xpath('string(.)').extract()
            item_url = a_tag.xpath('./@href').extract()
            if item_title and item_url:
                item = RelatedProduct(title=item_title[0].strip(),
                                      url=item_url[0].strip())
                recommendations.append(item)
        prod['related_products'] = {'recommended':recommendations}

        return prod
