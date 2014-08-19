from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

from scrapy.log import ERROR

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value


class DrugstoreProductsSpider(BaseProductsSpider):
    name = 'drugstore_products'
    allowed_domains = ["drugstore.com"]
    start_urls = []

    SEARCH_URL = "http://www.drugstore.com/search/search_results.asp?"\
        "N=0&Ntx=mode%2Bmatchallpartial&Ntk=All&srchtree=5&Ntt={search_term}"

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(
            product,
            'title',
            response.xpath("string(//div[@id='divCaption']/h1[1])").extract(),
        )

        cond_set(product, 'image_url', response.xpath(
            "//div[@id='divPImage']//img/@src").extract())

        #TODO
        #cond_set(product, 'model',model) model not defined

        cond_set(product, 'price', response.xpath(
            "//div[@id='productprice']/*[@class='price']/text()").extract())

        cond_set_value(
            product,
            'description',
            " ".join(response.xpath(
                "//div[@id='divPromosPDetail']//text()").extract()),
        )

        product['locale'] = "en-US"

        return product

    def _scrape_total_matches(self, response):
        totals = response.xpath("//div[@class='SrchMsgHeader']/text()").re(
            r'([\d,]+) results found')
        total = None
        if len(totals) > 1:
            self.log(
                "Found more than one 'total matches' for %s" % response.url,
                ERROR
            )
        elif totals:
            total = int(totals[0].strip().replace(',', ''))
        elif not len(response.xpath("//div[@class='divZeroResult']")):
            self.log(
                "Failed to find 'total matches' for %s" % response.url,
                ERROR
            )
        
        return total

    def _scrape_product_links(self, response):
        items = response.css('div.itemGrid div.info')
        if not items:
            self.log("Found no product links.", ERROR)
            
        for item in items:
            link = item.xpath('.//a/@href').extract()[0]
            brand = item.xpath('.//span[@class="name"]/text()').extract()[0]
            yield link, SiteProductItem(brand=brand.strip(' -'))

    def _scrape_next_results_page_link(self, response):
        link = response.xpath(
            '//table[@class="srdSrchNavigation"]'
            '//a[@class="nextpage"]/@href'
        ).extract()
        
        if not len(link):
            return None

        return link[0]
