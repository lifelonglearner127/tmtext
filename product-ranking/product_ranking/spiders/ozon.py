from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse

from scrapy.log import ERROR, DEBUG

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
     cond_set, cond_set_value, _extract_open_graph_metadata

def clear_text(l):
    """
    usefull for  clearing sel.xpath('.//text()').explode() expressions
    """
    return " ".join(
        [it for it in map(string.strip, l) if it])
        
class OzonProductsSpider(BaseProductsSpider):
    name = 'ozon_products'
    allowed_domains = ["ozon.ru"]
    start_urls = []

    SEARCH_URL = "http://www.ozon.ru/?context=search&text={search_term}&sort={search_sort}"
    
    SEARCH_SORT = {
        'default':'',
        'price':'price',
        'year':'year',
        'rate':'rate',
        'new':'new',
        'best_sellers':'bests'
    }
    
    def __init__(self, search_sort='default', *args, **kwargs):
        
        super(OzonProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self.SEARCH_SORT[search_sort]
            ),
            *args, **kwargs)
                                    
    def parse_product(self, response):
        product = response.meta['product']
        
        cond_set(product, 'title', response.xpath(
            '//h1[@itemprop="name"]/text()'
            ).extract(), string.strip)
        
        cond_set(product, 'image_url', response.xpath(
            '//img[@class="eBigGallery_ImageView"]/@src'
            ).extract())
        cond_set(product, 'image_url', response.xpath(
            '//*[@itemprop="image"]/@src'
            ).extract())                
        if product.get('image_url'):
            product['image_url'] = urlparse.urljoin(
                response.url, 
                product.get('image_url'))
              
        cond_set(product, 'price', response.xpath(
            '//div[@class="bSaleColumn"]//span[@itemprop="price"]/text()'
            ).extract(), string.strip)                
        
        desc = ''    
        
        desc1 = response.xpath('//div[@class="bDetailLogoBlock"]/node()') 
        brand = desc1.xpath('.//a[contains(@href, "/brand/")]/text()').extract()
        
        if brand:
            cond_set_value(product, 'brand', ', '.join(brand))

        if desc1:
            desc = clear_text(desc1.extract())             
        
        desc2 = response.xpath(
            '//div[@id="js_additional_properties"]'
            '/div[@class="bTechDescription"]/node()')
        brand = desc2.xpath('.//a[contains(@href, "/brand/")]/text()').extract()
        
        if brand:
            cond_set_value(product, 'brand', ', '.join(brand))
    
        if desc2:
            desc = '\n'.join([desc, clear_text(desc2.extract())])  
              
        desc3 = response.xpath(
                '//div[@itemprop="description"]/div/table//td/node()'
            ).extract()    
        if desc3:
            desc = '\n'.join([desc, clear_text(desc3)])
            
        cond_set_value(product, 'description', desc)
        cond_set_value(product, 'locale', 'ru-RU')

        also_bought = self._parse_related(response, response.css(
            '.bAlsoPurchased p.misc a'))
        
        recom = self._parse_related(response, response.css(
            '.detailUpsale p.misc a'))
                       
        cond_set_value(product, 'related_products', {
            'recommended': recom, 
            'buyers_also_bought': also_bought
            })   

        return product
            
    def _parse_related(self, response, link_selectors):
        related_products = []
        for related_link in link_selectors:
            title = related_link.xpath('@title').extract()
            url = related_link.xpath('@href').extract() 
            
            if not url or not title or url[0] in response.url: 
                continue
            
            related_products.append(RelatedProduct(
                title[0],
                urlparse.urljoin(response.url, url[0])
            ))
        return related_products   
        
    def _scrape_total_matches(self, response):
        total = None
        
        totals = response.xpath('//*[@class="bAlsoSearch"]/span[1]/text()') \
                         .re('\u041d\u0430\u0448\u043b\u0438 ([\d\s]+)')

        if totals:
            total = int(''.join(totals[0].split()))
                      
        elif not response.xpath("//div[@calss='bEmptSearch']"):
            self.log(
                "Failed to find 'total matches' for %s" % response.url,
                ERROR
            )
    
        return total    
        
    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[@itemprop="itemListElement"]/a[@itemprop="url"]/@href'
        ).extract()
        
        if not links:
            self.log("Found no product links.", DEBUG)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        
        next = response.css('.SearchPager .Active') \
                       .xpath('following-sibling::a[1]/@href') \
                       .extract()
        
        if not next:
            link = None
        else:
            link = urlparse.urljoin(response.url, next[0])    
        return link
                              
