from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json
import string
import urlparse

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value
from scrapy.log import ERROR


class TiresCanadiantireProductsSpider(BaseProductsSpider):
    name = 'tirescanadiantire_products'
    allowed_domains = ["tires.canadiantire.ca"]
    start_urls = []
    SEARCH_URL = "http://tires.canadiantire.ca/en/search/?searchterm={search_term}"

    def parse_product(self, response):
        # with open("/tmp/tires-item.html", "w") as f:
        #     f.write(response.body)

        product = response.meta['product']

        cond_set(product, 'title', map(string.strip, response.xpath(
            "//div[@class='productContent']/h1/div[@id='productName']/text()").extract()))

        cond_set(product, 'brand', response.xpath(
            "//script[contains(text(),'dim7')]/text()").re(r'.*"dim7":"([^"]*)"}.*'))

        productid = response.xpath("//p[@id='prodNo']/span[@id='metaProductID']/text()")
        if productid:
            productid = productid.extract()[0].strip().replace('P', '')
            try:
                product['upc'] = int(productid)
            except ValueError:
                self.log(
                    "Failed to parse upc number : %r" % productid, ERROR)

        cond_set(product, 'image_url', response.xpath(
            "//div[@class='bigImage']/img[@id='mainProductImage']/@src").extract())

        price = response.xpath(
            "//div[contains(@class,'bigPrice')]/descendant::*[text()]/text()")
        price = [x.strip() for x in price.extract()]
        price = " ".join(price)
        price = " ".join(price.split())
        cond_set_value(product, 'price', price)

        info = response.xpath("//div[@id='features']/div[@class='tabContent']/descendant::*[text()]/text()")
        if info:
            cond_set_value(product, 'description', " ".join(info.extract()))

        # Old style
        # info = response.xpath("//div[@class='features_wrap']")
        # cond_set_value(product, 'description', info.extract(), conv=''.join)

        #locale = response.xpath("//html")[0]
        #print "LANG=",dir(locale)
        cond_set_value(product, 'locale', "en-US")

        return product

    def _parse_json(self, response):
        product = response.meta['product']

        data = json.loads(response.body_as_unicode())
        prod_data = data[0]

        cond_set_value(product, 'price', prod_data.get('regularPrice'))
        cond_set_value(product, 'title', prod_data.get('name'))

        return product

    def _scrape_total_matches(self, response):
        total = response.xpath(
            "//div[@id='productListing']/strong/h2/text()").re(r'.* returned (\d+) results:')
        #print "TOTAL", len(total), total
        if total:
            return int(total[0])
        else:
            return 0

    def _scrape_product_links(self, response):
        #print response.url
        # with open("/tmp/tires.html","w") as f:
        #     f.write(response.body)
        links = response.xpath(
            "//ul[@id='productList']/li/div[@class='productImage']/a/@href"
        ).extract()
        # for link in links:
        #     print urlparse.urljoin(response.url, link)
        if not links:
            self.log("Found no product links.", ERROR)

        for link in links:
            yield urlparse.urljoin(response.url, link), SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next_page_links = response.xpath(
            "//div[@class='pageNumbering']/a[contains(@class,'pageNext')]/@href")
        #print "NEXT=",next_page_links.extract()

        if next_page_links:
            next_page_link = urlparse.urljoin(
                response.url, next_page_links.extract()[0])
        else:
            next_page_link = None
        return next_page_link
