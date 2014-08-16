from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import urlparse

from scrapy.log import ERROR

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set


class WalGreensProductsSpider(BaseProductsSpider):
    name = "walgreens_products"
    allowed_domains = ["walgreens.com"]
    start_urls = []

    SEARCH_URL = "http://www.walgreens.com/search/results.jsp?Ntt={search_term}"

    def parse_product(self, response):
        prod = response.meta['product']

        model = response.xpath('//input[@id="skuId"]/@value').extract()
        cond_set(prod, 'model', model)

        title = response.xpath('//h1[@itemprop="name"]/text()').extract()
        if title:
            prod['title'] = title[0].strip()

        price = response.xpath('//b[@itemprop="price"]//text()').extract()
        if price:
            prod['price'] = price[0].strip()
        else:
            price = response.xpath(
                '//span[@id="price_amount"]/b/text()').extract()
            if price:
                prod['price'] = 'Priced per store'

        img_url = response.xpath(
            '//img[@id="main-product-image"]/@src').extract()
        if img_url:
            img_url = urlparse.urljoin(response.url, img_url[0])
            prod['image_url'] = img_url

        brand_text = response.xpath(
            '//div[@id="vpd_shop_more_link"]'
            '//div[contains(@class,"mrgTop5px")]//a/text()'
        ).extract()
        if brand_text:
            brand_text = brand_text[0].replace('Shop all', '').replace(
                'products', '')
            prod['brand'] = brand_text.strip()

        prod['url'] = response.url

        prod['locale'] = 'en-US'

        des = response.xpath(
            '//div[@id="description-content"]//text()').extract()
        if des:
            prod['description'] = ''.join(i.strip() for i in des)

        return prod

    def _scrape_total_matches(self, response):
        count = response.xpath(
            '//a[@title="Products - Tab - Active"]/text()'
        ).re('(\d+)')
        if count:
            return int(count[0])
        return 0

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[@class="prod-content-top"]'
            '/div[contains(@class,"product-name")]/a/@href'
        ).extract()
        for link in links:
            full_link = urlparse.urljoin(response.url, link)
            yield full_link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        links = response.xpath(
            '//div[contains(@class,"pagination")]//a[@title="Next Page"]/@href'
        ).extract()
        if links:
            return urlparse.urljoin(response.url, links[0])
        return None
