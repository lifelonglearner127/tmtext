from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import urlparse

from scrapy.log import ERROR

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value


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

        if prod.get('price'):
            if not '$' in prod['price']:
                self.log('Unknown currency at %s' % response.url, level=ERROR)
            else:
                prod['price'] = Price(
                    priceCurrency='USD',
                    price=prod['price'].replace(',', '').replace(
                        ' ', '').replace('$', '').strip()
                )

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

        cond_set_value(
            prod,
            'description',
            ''.join(
                response.xpath('//div[@id="description-content"]').extract()),
        )

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

    def _parse_single_product(self, response):
        return self.parse_product(response)
