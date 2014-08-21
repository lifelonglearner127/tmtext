from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
from future_builtins import *

import urlparse

from scrapy.log import WARNING

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set


class PaodeacucarProductsSpider(BaseProductsSpider):
    name = "paodeacucar_products"
    allowed_domains = ["busca.paodeacucar.com.br"]
    start_urls = []

    SEARCH_URL = "http://busca.paodeacucar.com.br/search?view=grid&asug=&w={search_term}"


    def parse_product(self, response):
        prod = response.meta['product']

        title = response.xpath('//h1[@class="product-header__heading"]/text()').extract()
        if title:
            prod['title'] = title[0].strip()

        price = response.xpath('//span[@class="value inline--middle"]/text()').extract()
        if price:
            prod['price'] = price[0].strip()


        img_url = response.xpath('//div[@id="product-image"]/a/img/@src').extract()
        if img_url:
            img_url = urlparse.urljoin(response.url, img_url[0])
            prod['image_url'] = img_url


        prod['url'] = response.url

        prod['locale'] = 'en-US'

        des = response.xpath('//div[@class="product-info__text"]//text()').extract()
        if des:
            prod['description'] = ''.join([i.strip() for i in des])

        return prod


    def _scrape_total_matches(self, response):

        count = response.xpath(
            "//span[@class='sli_bct_total_records']/text()").extract()
        if count:
            return int(count[0])
        return 0

    def _scrape_product_links(self, response):

        links = response.xpath('//div[@class="showcase-item__info"]/h3/a/@href').extract()
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):

        next_pages = response.xpath('//a[@class="pageselectorlink"]/@href').extract()
        next_page = None
        if next_pages:
            next_page = next_pages[0]
            if len(next_pages) > 2:
                self.log("Found more than two 'next page' links.", WARNING)
        return next_page

