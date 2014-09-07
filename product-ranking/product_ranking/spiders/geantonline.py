from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse

from scrapy.log import ERROR, DEBUG

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
     cond_set, cond_set_value


class GeantonlineProductsSpider(BaseProductsSpider):
    name = 'geantonlines_products'
    allowed_domains = ["geantonline.ae"]
    start_urls = []

    SEARCH_URL = "http://www.geantonline.ae/mixedsearch.aspx?k={search_term}"
    
    def clear_desc(self, l):
       return " ".join(
            [it for it in map(string.strip, l) if it])
            
    def parse_product(self, response):
        product = response.meta['product']
                 
        cond_set(product, 'title', response.css(
            'div.holder div.description h1::text'
        ).extract())  

        cond_set(product, 'price', response.css(
            'div.holder div.price strong::text'
        ).extract())

        img_url = response.xpath(
            '//div[@class="holder"]//div[@class="slideshow"]'
            '/div[@class="slide"][1]/a/@href'
        ).extract()
        
        if img_url:
            cond_set_value(product, 'image_url',
                           urlparse.urljoin(response.url, img_url[0]))
        
        cond_set_value(product,'description', self.clear_desc(
            response.css('div.tabs div.tab div.c') \
                    .xpath('.//text()') \
                    .extract()
        ))
        
        cond_set_value(product, 'locale', "ar-AE")

        rel_links = response.css('.BoughtItems p.BoughtProductName a')
        
        buyers_also_bought = {} 
        for rl in rel_links:
            buyers_also_bought[rl.xpath('./text()').extract()[0]] = \
                urlparse.urljoin(response.url, rl.xpath('./@href').extract()[0])
                
        cond_set_value(product, 'related_products', 
                       {'buyers_also_bought':buyers_also_bought})        
        return product

    def _scrape_total_matches(self, response):
        return response.meta['products_per_page']

    def _scrape_product_links(self, response):
        links = response.css(
            'ul.product-list li div.box div.details a::attr(href)'
        ).extract()
        
        if not links:
            self.log("Found no product links.", DEBUG)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        return None
