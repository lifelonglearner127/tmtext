from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set
from scrapy.log import ERROR


class WehkampProductsSpider(BaseProductsSpider):
    name = 'wehkamp_products'
    allowed_domains = ["wehkamp.nl"]
    start_urls = []
    SEARCH_URL = "http://www.wehkamp.nl/Winkelen/SearchOverview.aspx?N=186&Nty=1&Ntk=ART&Ztb=False&VIEW=Grid&Ntt={search_term}"

    def __init__(self, *args, **kwargs):
        super(WehkampProductsSpider, self).__init__(
            #url_formatter=FormatterWithDefaults(pagenum=1, prods_per_page=32),
            *args, **kwargs)

    def parse_product(self, response):

        product = response.meta['product']

        cond_set(product, 'title', map(string.strip, response.xpath(
            "//div[@class='pdp-topmatter']/h1[@itemprop='name']/text()").extract()))

        cond_set(product, 'brand', response.xpath(
            "//div[@class='merk']/a/img[@class='brandLogo']/@title").extract())

        cond_set(product, 'image_url', response.xpath(
            "//img[@id='mainImage']/@src").extract())

        cond_set(product, 'price', response.xpath(
            "//div[@class='priceblock']/span[@class='price']/text()").extract())

        cond_set(product, 'upc', map(int, response.xpath(
            "//input[@id='EanCode']/@value").extract()))

        cond_set(product, 'locale', response.xpath(
            "//html/@lang").extract())

        j = response.xpath("//div[@id='extraInformatie']/"
                "/descendant::*[text()]/text()")
        info = "\n".join([x.strip() for x in j.extract() if len(x.strip())>0])

        j2 = response.xpath("//div[@id='kenmerkenOverzicht']/"
                "/descendant::*[text()]/text()")
        info2 = " ".join([x.strip() for x in j2.extract() if len(x.strip())>0])

        product['description'] = info + info2
        
        rel = response.xpath("//div[@id='bijverkopen']/div[contains(@class,'product')]")
        prodlist = []
        for r in rel:
            try:
                href = r.xpath('a/@href').extract()[0]
                title = r.xpath('a/span/span/text()').extract()[0]
                prodlist.append(RelatedProduct(title, href))
            except:
                pass
        product['related_products'] = {"recomended": prodlist }

        return product

    def _scrape_total_matches(self, response):
        total = response.xpath("//div[@class='resultsHeader']/p/text()").re(r'" geeft (\d+) resultaten.')
        if len(total) > 0:
            total = total[0].replace(".","")
            try:
                return int(total)
            except:
                return 0    
        else:
            return 0

    def _scrape_product_links(self, response):
        links = response.xpath("//ul[@id='articleList']/li[contains(@class,'article-card')]/a/@href").extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        raise AssertionError("_scrape_next_results_page_link")
        next = response.xpath("//div[contains(@class,'tst_searchresults_next')]/span/a/@href")
        if len(next) > 0:
            return next.extract()[0]