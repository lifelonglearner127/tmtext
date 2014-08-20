from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set
from scrapy.log import ERROR


class KruidvatProductsSpider(BaseProductsSpider):
    name = 'kruidvat_products'
    allowed_domains = ["kruidvat.nl"]
    start_urls = []
    SEARCH_URL = "http://www.kruidvat.nl/search?text={search_term}"

    def __init__(self, *args, **kwargs):
        super(KruidvatProductsSpider, self).__init__(
            #url_formatter=FormatterWithDefaults(pagenum=1, prods_per_page=32),
            *args, **kwargs)

    def parse_product(self, response):

        product = response.meta['product']
        cond_set(product, 'title', map(string.strip, response.xpath(
            "//section[@class='product-details']/div[@id='product-title']/h1/text()").extract()))

        def full_url(url):
            return urlparse.urljoin(response.url, url)

        cond_set(product, 'image_url', map(full_url, response.xpath(
            "//section[contains(@class,'product-imgviewer')]/div/img/@src").extract()))

        cond_set(product, 'price', response.xpath(
            "//p[@class='product-price']/meta[@itemprop='price']/@content").extract())

        try:
            cond_set(product, 'upc', map(int, response.xpath(
                "//section[@class='product-details']/meta[@itemprop='productID']/@content").extract()))
        except:
            pass

        cond_set(product, 'description', response.xpath(
            "//section[@class='product-details']/p/text()").extract())

        cond_set(product, 'locale', response.xpath(
            "//html/@lang").extract())

        cond_set(product, 'brand', response.xpath(
            "//var[@itemprop='brand']/text()").extract())

        res = response.xpath("//div[contains(@class,'component') and contains(@class,'grid-unit-beta') ][1]/*/*/div/article")
        prodlist = []
        for r in res:
            title = r.xpath("div/p[@class='product-info']/a/text()").extract()[0]
            href = r.xpath("div/p[@class='product-info']/a/@href").extract()[0]
            prodlist.append(RelatedProduct(title, full_url(href)))

        product['related_products'] = {"recomended": prodlist}
        return product

    def _scrape_total_matches(self, response):
        total = response.xpath("//section[contains(@class,'search-title')]/p/span/text()").extract()
        if len(total) > 0:
            total = total[0].replace(".", "")
            try:
                return int(total)
            except:
                return 0
        else:
            return 0

    def _scrape_product_links(self, response):
        links = response.xpath("//section[contains(@class,'search-result')]/article[@class='product-cell']"
            "/div/a[@class='product-link']/@href").extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath("//ul[@class='pages']/li[@class='next-page']/a/@href")
        if len(next) > 0:
            return next.extract()[0]
