from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
from scrapy.log import ERROR

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set


class BolProductsSpider(BaseProductsSpider):
    name = 'bol_products'
    allowed_domains = ["bol.com"]
    start_urls = []
    SEARCH_URL = "http://www.bol.com/nl/s/algemeen/zoekresultaten/Ntt/{search_term}/N/0/Nty/1/search/true/searchType/qck/sc/media_all/index.html"   ## ?_requestid=2229"

    def __init__(self, *args, **kwargs):
        super(BolProductsSpider, self).__init__(
            #url_formatter=FormatterWithDefaults(pagenum=1, prods_per_page=32),
            *args, **kwargs)

    def parse_product(self, response):
        product = response.meta['product']
        cond_set(product, 'brand', response.xpath(
            "//div/span/a[@itemprop='brand']/text()").extract())

        cond_set(product, 'title', map(string.strip, response.xpath(
            "//div[contains(@class,'product_heading')]/h1[@itemprop='name']/text()").extract()))

        cond_set(product, 'image_url', response.xpath(
            "//div[contains(@class,'product_zoom_wrapper')]/img[@itemprop='image']/@src").extract())

        cond_set(product, 'price', response.xpath(
            "//span[@class='offer_price']/meta[@itemprop='price']/@content").extract())

        j = response.xpath("//div[contains(@class,'product_description')]/div/div[@class='content']"
                "/descendant::*[text()]/text()")
        info = "\n".join([x.strip() for x in j.extract() if len(x.strip())>0])
        product['description'] = info

        cond_set(product, 'upc', map(int, response.xpath(
            "//meta[@itemprop='sku']/@content").extract()))

        cond_set(product, 'locale', response.xpath(
            "//html/@lang").extract())
        
        rel = response.xpath("//div[contains(@class,'tst_inview_box')]/div/div[@class='product_details_mini']/span/a")
        prodlist = []
        for r in rel:
            try:
                href = r.xpath('@href').extract()[0]
                title = r.xpath('@title').extract()[0]
                prodlist.append(RelatedProduct(title, href))
            except:
                pass
        product['related_products'] = {"recomended": prodlist }

        return product

    def _scrape_total_matches(self, response):
        total = response.xpath("//h1[@itemprop='name']/span[@id='sab_header_results_size']/text()").extract()
        #print "total=",total
        if len(total) > 0:
            total = total[0].replace(".","")
            try:
                return int(total)
            except:
                return 0    
        else:
            return 0

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//div[contains(@class,'productlist_block')]/div[@class='product_details_thumb']"
            "/div/div/a[@class='product_name']/@href").extract()
        # for no, link in enumerate(links):
        #     print no,link

        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath("//div[contains(@class,'tst_searchresults_next')]/span/a/@href")
        if len(next) > 0:
            return next.extract()[0]
