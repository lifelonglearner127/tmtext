from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import urllib
import urlparse

from scrapy.log import ERROR
from scrapy.selector import Selector

from scrapy.http import Request
from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FormatterWithDefaults

# scrapy crawl amazoncouk_products -a searchterms_str="iPhone"

class GandermountainProductsSpider(BaseProductsSpider):
    name = "gandermountain_products"
    allowed_domains = ["www.gandermountain.com"]
    start_urls = []

    
    SEARCH_URL = "http://www.gandermountain.com/search/{search_term}"

    

    def __init__(self, *args, **kwargs):
        # locations = settings.get('AMAZONFRESH_LOCATION')
        # loc = locations.get(location, '')
        super(GandermountainProductsSpider, self).__init__(*args, **kwargs)

    def parse_product(self, response):
        prod = response.meta['product']

        title = response.xpath('//div[@class="product-title"]/h1/text()').extract()
        cond_set(prod, 'title', title)

        price = response.xpath('//span[@class="regPrice"]/text()').re('([\d.]+)')
        
        if not price:
            price = response.xpath('//span[@id="sale-range"]/text()').re('([\d.]+)')
        if not price:
            price = response.xpath('//div[@class="saleprice"][position()=1]/span/text()').re('([\d.]+)')
            
        prod['price'] = Price(price=price[0], priceCurrency='USD')

        cond_set(prod, 'price', price)

        des = response.xpath('//td[@class="detailsText"]').extract()
        cond_set(prod, 'description', des)

        img_url = response.xpath('//div[@class="zoomPad"]/img/@src').extract()
        cond_set(prod, 'image_url', img_url)

        cond_set(prod, 'locale', ['en-US'])

        prod['url'] = response.url
        return prod

    def _search_page_error(self, response):
        sel = Selector(response)

        try:
            found1 = sel.xpath('//section[@class="search-no-message"]/h2/text()').extract()[0]
            found2 = sel.xpath(
                '//div[@class="warning"]/p/strong/text()'
            ).extract()[0]
            found = found1 + " " + found2
            if 'No Results Found' in found:
                self.log(found, ERROR)
                return True
            return False
        except IndexError:
            return False

    def _scrape_total_matches(self, response):
        
        
        if 'did not match any products.' in response.body_as_unicode():
            total_matches = 0
        else:
            count_matches = response.xpath(
                '//p[@class="page-numbers"][position()=1]/strong[position()=1]/text()').re('([\d,]+)')

            if count_matches and count_matches[-1]:
                total_matches = int(count_matches[-1])
            else:
                total_matches = None
        return total_matches

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//a[@class="browse-pdp-link"]/@href').extract()
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):

        page = response.xpath(
            '//p[@class="page-numbers"]/a[position()=last()]/@onclick'
        ).re('page=(\d+)')
        
        next_link = self.SEARCH_URL.replace('{search_term}', self.searchterms[0]) + "#filters?do=json&i=1&page=" +page[0] +"&q="+self.searchterms[0]+"&matched_cat=&ckey=i1page"+page[0]+"q"+self.searchterms[0]+"&cat_depth=0&matched_cat=0&is_refined=1"
        

        if next_link:
            return next_link
        return None



