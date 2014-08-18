from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse

from scrapy.log import ERROR, DEBUG

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value


class OcadoProductsSpider(BaseProductsSpider):
    name = 'ocado_products'
    allowed_domains = ["ocado.com"]
    start_urls = []

    SEARCH_URL = "https://www.ocado.com/webshop/getSearchProducts.do?"\
        "clearTabs=yes&isFreshSearch=true&entry={search_term}"

    def parse_product(self, response):
        product = response.meta['product']
        
        title_list = response.xpath("//h1[@class='productTitle'][1]//text()").extract()
        
        if len(title_list) >=2:
            cond_set_value(product, 'title',
             " ".join(map(string.strip,title_list[-2:])))

        cond_set(product, 'price',response.xpath(
            "//div[@id='bopRight']//meta[@itemprop='price']/@content"
        ).extract())     
        
        img_url = response.xpath(
            "//ul[@id='galleryImages']/li[1]/a/@href"
            ).extract()
            
        if len(img_url):  
            cond_set_value(product, 'image_url',urlparse.urljoin(response.url,img_url[0]))
            
        
        cond_set_value(product, 'description',
            " ".join(
                map(
                    string.strip,
                    response.xpath("//div[@id='bopBottom']//*[@itemprop='description']//text()"
                    ).extract()
                )))
            
        cond_set_value(product, 'locale',"en_GB")
        
        cond_set(product, 'brand', response.xpath(
            "string(//div[@id='bopBottom']//*[@itemprop='brand'])"
            ).extract(),
            string.strip)
        
        return product
        
    def _scrape_total_matches(self, response):
        
        totals = response.xpath("string(//h3[@id='productCount'])").re(
            r'(\d+) products')
        if len(totals) > 1:
            self.log(
                "Found more than one 'total matches' for %s" % response.url,
                ERROR
            )
        elif totals:
            total = totals[0].strip()
            return int(total)
            
        else:
            self.log(
                "Failed to find 'total matches' for %s" % response.url,
                ERROR
            )
        
        return None

    def _scrape_product_links(self, response):
    
        links = response.xpath('//h4[@class="productTitle"]/a/@href').extract()
        if not links:
            self.log("Found no product links.", ERROR)
            
        for link in links:
            yield link, SiteProductItem()
            

    def _scrape_next_results_page_link(self, response):

        link = response.css('ul.pages a.next::attr(href)').extract()

        if not len(link):
            self.log("Next page link not found.", DEBUG)
            return None

        return link[0]
