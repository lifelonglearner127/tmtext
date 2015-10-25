from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re

from scrapy.log import ERROR

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value


class CostcoProductsSpider(BaseProductsSpider):
    name = "costco_products"
    allowed_domains = ["costco.com"]
    start_urls = []

    SEARCH_URL = "http://www.costco.com/CatalogSearch?pageSize=96" \
        "&catalogId=10701&langId=-1&storeId=10301" \
        "&currentPage=1&keyword={search_term}"

    DEFAULT_CURRENCY = u'USD'

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        prod = response.meta['product']

        if response.xpath('//h1[text()="Product Not Found"]'):
            prod['not_found'] = True
            return prod

        model = response.xpath('//div[@id="product-tab1"]//text()').re(
            'Model[\W\w\s]*')
        if len(model) > 0:
            cond_set(prod, 'model', model)
            if 'model' in prod:
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


        price_value = response.xpath(
            '//input[contains(@name,"price")]/@value').re('[\d.]+')

        if price_value:
            price_value = u''.join(price_value)
            if price_value != '0.00':
                price = Price(
                    priceCurrency=self.DEFAULT_CURRENCY,
                    price=u''.join(price_value)
                )

                cond_set_value(prod, 'price', price)

        des = response.xpath('//div[@id="product-tab1"]//text()').extract()
        des = ' '.join(i.strip() for i in des)
        if des.strip():
            prod['description'] = des.strip()

        img_url = response.xpath('//img[@itemprop="image"]/@src').extract()
        cond_set(prod, 'image_url', img_url)

        cond_set_value(prod, 'locale', 'en-US')
        prod['url'] = response.url

        return prod

    def _search_page_error(self, response):
        if not self._scrape_total_matches(response):
            self.log("Costco: unable to find a match", ERROR)
            return True
        return False

    def _scrape_total_matches(self, response):
        try:
            count = response.xpath(
                '//*[@id="secondary_content_wrapper"]/div/p/span/text()'
            ).re('(\d+)')[-1]
            if count:
                return int(count)
            return 0
        except IndexError:
            count = response.xpath(
                '//*[@id="secondary_content_wrapper"]'
                '//span[contains(text(), "Showing results")]/text()'
            ).extract()
            return int(count[0].split(' of ')[1].replace('.', '').strip())

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[contains(@class,"product-tile-image-container")]/a/@href'
        ).extract()
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        links = response.xpath(
            "//*[@class='pagination']"
            "/ul[2]"  # [1] is for the Items Per Page section which has .active.
            "/li[@class='active']"
            "/following-sibling::li[1]"  # [1] is to get just the next sibling.
            "/a/@href"
        ).extract()
        if links:
            link = links[0]
        else:
            link = None

        return link
