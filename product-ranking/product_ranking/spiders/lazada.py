from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json
import string

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set
from scrapy.log import ERROR

class LazadaProductsSpider(BaseProductsSpider):
    name = 'lazada_products'
    allowed_domains = ["lazada.com.ph"]
    start_urls = []
    SEARCH_URL = "http://www.lazada.com.ph/catalog/?q={search_term}"
    # NEED USER_AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36"
    # scrapy crawl myproject.com -o output.csv -t csv -s USER_AGENT="Mozilla...."
    # or
    # Move your USER_AGENT line to the settings.py file, and not in your scrapy.cfg file.
    # settings.py should be at same level as items.py if you use scrapy startproject command,
    # in your case it should be something like myproject/settings.py

    def __init__(self, *args, **kwargs):
        super(LazadaProductsSpider, self).__init__(
            #url_formatter=FormatterWithDefaults(pagenum=1, prods_per_page=32),
            *args, **kwargs)

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(product, 'title', map(string.strip, response.xpath(
            "//div[@class='prod_content']/h1[@id='prod_title']/text()").extract()))

        cond_set(product, 'locale', response.xpath(
            "//html/@lang").extract())

        desc = response.xpath(
            "//div[@id='productDetails']/descendant::*[text()]/text()").extract()
        info = ". ".join([x.strip() for x in desc if len(x.strip()) > 0])
        product['description'] = info

        self._populate_from_js(response, product)
        return product

    def _populate_from_js(self, response, product):
        jstext = response.xpath("//script[contains(text(),'var dataLayer')]").re(r'\svar dataLayer = (.*);')
        if len(jstext) > 0:
            try:
                jsdata = json.loads(jstext[0])
                if len(jsdata) > 0:
                    product['brand'] = jsdata[0].get('pdt_brand')
                    product['upc'] = jsdata[0].get('pdt_sku')
                    product['price'] = jsdata[0].get('pdt_amount')
                    product['image_url'] = jsdata[0].get('pdt_photo')
            except:
                pass
        return product

    def _scrape_total_matches(self, response):
        total = response.xpath("//span[@class='catalog__quantity']/text()").re(r'(\d+)')
        if len(total) > 0:
            total = total[0].replace(".", "")
            try:
                return int(total)
            except:
                return 0
        else:
            return 0

    def _scrape_product_links(self, response):
        links = response.xpath("//div[contains(@class,'product_list')]/a/@href").extract()
        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath("//span[contains(@class,'paging')]/a[@class='next_link']/@href")
        if len(next) > 0:
            return next.extract()[0].strip()
