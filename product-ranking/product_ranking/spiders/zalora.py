from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse
import json

from scrapy.log import ERROR, DEBUG
from scrapy.selector import Selector
from scrapy.http import Request

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
     cond_set, cond_set_value, _extract_open_graph_metadata


class ZaloraProductsSpider(BaseProductsSpider):
    name = 'zalora_products'
    allowed_domains = ["zalora.com.ph"]
    start_urls = []

    SEARCH_URL = "http://www.zalora.com.ph/catalog/?q={search_term}&sort={search_sort}"
    
    SEARCH_SORT = {
        'popularity': 'popularity',
        'low_price': 'lowest_price',
        'high_price': 'highest_price',
        'latest_arrival': 'latest arrival',
        'discount': 'discount'
    }
    
    RELATED_URL = 'http://www.zalora.com.ph/zrs/getproduct?key[]={sku}'
    
    def __init__(self, search_sort='popularity', *args, **kwargs):
        
        super(ZaloraProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self.SEARCH_SORT[search_sort]
            ),
            *args, **kwargs)
             
    def clear_desc(self, l):
        return " ".join(
            [it for it in map(string.strip, l) if it])
                                    
    def parse_product(self, response):
        product = response.meta['product']
                 
        og = _extract_open_graph_metadata(response)
        if og.get('image'):
            cond_set_value(product, 'image_url', og['image'])
        if og.get('title'):    
            cond_set_value(product, 'title', og['title'])
        if og.get('description'):    
            cond_set_value(product, 'description', og['description'])  
        cond_set(product, 'brand', response.xpath(
            '//div[@itemprop="brand"]/a/text()'
            ).extract(), string.strip)
        cond_set(product, 'title', response.xpath(
            '//div[@itemprop="name"]/text()'
            ).extract(), string.strip) 
        
        special_price = response.xpath(
            '//span[@itemprop="price"]/span/text()'
            ).extract()
        if special_price:      
            cond_set_value(product, 'price','\xa0'.join(special_price), string.strip)
        else:     
            cond_set(product, 'price', response.xpath(
                '//span[@itemprop="price"]/text()'
                ).extract(), string.strip) 

        cond_set_value(product, 'locale', 'en-PH')
        
        r = {}
        bundles = response.xpath('//a[@class="prd-bundle-item-name"]')
        for bundle in bundles:
            r[self.clear_desc(bundle.xpath('.//text()').extract())] = \
                 urlparse.urljoin(response.url, 
                                  bundle.xpath('@href').extract()[0])
        related_products = {'recommended': r }
        
        cond_set_value(product, 'related_products', related_products)          
        
        sku = response.xpath('//td[@itemprop="sku"]/text()').extract()
        
        if sku:
            return Request(
                self.RELATED_URL.format(sku=sku[0].strip()),
                callback=self._parse_related,
                meta=response.meta)
        
        return product
            
    def _parse_related(self,response):
        product = response.meta['product']
        
        sel = Selector(text=json.loads(response.body).get('html'))
        r = {}
        for a in sel.css('.rec-item-link'):
            brand = a.css('.rec-item-brand::text')
            title = a.css('.rec-item-title::text')
            
            if brand and title:
                title = brand[0].extract().strip() + \
                ' ' + title[0].extract().strip()
             
                r[title] = urlparse.urljoin(response.url, 
                                  a.xpath('@href').extract()[0])
                                  
        product['related_products']['recommended'].update(r)
        
        return product
        
    def _scrape_total_matches(self, response):
        total = None
        
        totals = response.css('.b-catalogList__searchCount::text').re('(\d+)')
        
        if totals:
            total = int(totals[0])
        else:
            totals = response.css('.b-catalogList__count h1::text').re('(\d+)')
            if totals:
                total = int(totals[0])
                       
            elif not response.xpath("//div[@id='noResultSearchPage']"):
                self.log(
                    "Failed to find 'total matches' for %s" % response.url,
                    ERROR
                )
        
        return total    
        
    def _scrape_product_links(self, response):
        links = response.css(
            '.catalog-box li.b-catalogList__itm a::attr(href)'
        ).extract()
        
        if not links:
            self.log("Found no product links.", DEBUG)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        paging = response.css('.b-catalogList__paging')
        if paging:
            next = paging[0].xpath('.//a[@title="Next"]/@href') \
                       .extract()
            if next:
                return next[0]
        else:
            self.log("Found no paging on the page.", ERROR)
          
        return None                       
