from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set
from scrapy import Request
from scrapy.log import ERROR


class UlaboxProductsSpider(BaseProductsSpider):
    name = 'ulabox_products'
    allowed_domains = ["ulabox.com"]
    start_urls = []
    SEARCH_URL = "https://www.ulabox.com/busca?q={search_term}"

    def __init__(self, *args, **kwargs):
        super(UlaboxProductsSpider, self).__init__(
            #url_formatter=FormatterWithDefaults(pagenum=1, prods_per_page=32),
            *args, **kwargs)

    def parse_product(self, response):

        def full_url(url):
            return urlparse.urljoin(response.url, url)

        product = response.meta['product']

        cond_set(product, 'title', map(string.strip, response.xpath(
            "//div[@class='product-name__titles']/div[@class='grid']/div/h1/text()").extract()))

        cond_set(product, 'brand', response.xpath(
            "//div[@class='product-name__titles']/h2/a/text()").extract())

        cond_set(product, 'price', response.xpath(
            "//form/strong[@itemprop='price']/text()").extract())


        cond_set(product, 'image_url', map(full_url, response.xpath(
            "//div[@class='js-image-zoom']/img/@src").extract()))

        cond_set(product, 'upc', map(int, response.xpath(
            "//div[@class='grid']/div/div[@class='product-info']/../@data-product-id").extract()))

        cond_set(product, 'locale', response.xpath(
            "//html/@lang").extract())

        desc = response.xpath(
            "//section[@itemprop='description']/descendant::*[text()]/text()").extract()
        info = " ".join([x.strip() for x in desc if len(x.strip()) > 0])
        product['description'] = info

        # external recomendar part
        product['related_products'] = {}
        product_or_request = product

        recom = response.xpath("//include[contains(@src,'recomendar')]/@src")
        if len(recom) > 0:
            recom_url = recom.extract()[0] + '&device=desktop-wide'
            new_meta = response.meta.copy()
            product_or_request = Request(recom_url, self._parse_recomendar,
                headers={'x-requested-with': 'XMLHttpRequest'}, meta=new_meta)

        # internal related-products
        res = response.xpath("//section[contains(@class,'related-products')]/div[contains(@class,'grid__item')]/article")
        prodlist = []
        for r in res:
            try:
                title = r.xpath("@data-product-name").extract()[0]
                url = r.xpath("@data-product-url").extract()[0]
                prodlist.append(RelatedProduct(title, full_url(url)))
            except:
                pass
        product['related_products']["recomended"] = prodlist
        return product_or_request

    def _parse_recomendar(self, response):

        def full_url(url):
            return urlparse.urljoin(response.url, url)

        product = response.meta['product']

        res = response.xpath("//div[contains(@class,'grid__item')]/article")
        prodlist = []
        for r in res:
            try:
                title = r.xpath("@data-product-name").extract()[0]
                url = r.xpath("@data-product-url").extract()[0]
                prodlist.append(RelatedProduct(title, full_url(url)))
            except:
                pass
        product['related_products']["other_bought"] = prodlist
        return product

    def _scrape_total_matches(self, response):
        total = response.xpath("//section[@class='product-list']/div/h4/text()").re(r'(\d+)')
        if len(total) > 0:
            total = total[0].replace(".", "")
            try:
                return int(total)
            except:
                return 0
        else:
            return 0

    def _scrape_product_links(self, response):
        links = response.xpath("//div[@class='grid']/div/article/div/a[contains(@class,'product-item')]/@href"
            ).extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath("//ul[contains(@class,'pagination')]/li[contains(@class,'pagination-item--next')]/a/@href")
        if len(next) > 0:
            return next.extract()[0]