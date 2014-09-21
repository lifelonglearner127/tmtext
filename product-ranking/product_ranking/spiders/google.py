from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse
import json
import re

from scrapy.log import ERROR, WARNING, DEBUG
from scrapy.selector import Selector
from scrapy.http import Request

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
     cond_set, cond_set_value

def clear_text(l):
    """
    usefull for  clearing sel.xpath('.//text()').explode() expressions
    """
    return " ".join(
        [it for it in map(string.strip, l) if it])
        
class GoogleProductsSpider(BaseProductsSpider):
    name = 'google_products'
    allowed_domains = ["www.google.com"]
    start_urls = []
    user_agent = 'Mozilla/5.0 (X11; Linux i686; rv:25.0) Gecko/20100101 Firefox/25.0'
    download_delay = 1
    
    SEARCH_URL = "https://www.google.com/search?tbm=shop&q={search_term}&num=100"
    
    SEARCH_SORT = {
        'default':'p_ord:r',
        'rating':'p_ord:rv',
        'low_price':'p_ord:p',
        'high_price':'p_ord:pd',
    }
    
    def __init__(self, search_sort=None, *args, **kwargs):
        super(GoogleProductsSpider, self).__init__(*args, **kwargs) 
        if search_sort in self.SEARCH_SORT: 
            self.sort = search_sort
        else:    
            self.sort = None
          
    def start_requests(self):
        yield Request(
            url="https://www.google.com/shopping",
            callback=self.parse_init)
        
    def parse_init(self, response):
        for request in super(GoogleProductsSpider, self).start_requests():
            if self.sort:
                request.callback = self.sort_request
            yield request           
                                          
    def sort_request(self,response):

        url = response.request.url

        if (self.sort):
            pattern = r'\,{}[\&$]'.format(self.SEARCH_SORT[self.sort])
            sort_urls = response.xpath(
                '//div[@id="stt__ps-sort-m"]/div/@data-url').extract()
            
            for sort_url in sort_urls:    
                m = re.search(pattern, sort_url)
                if m:
                    url = urlparse.urljoin(response.url,sort_url)
                    break
        
        request = response.request.replace(
            callback = self.parse,
            url = url)            
        yield request
                
    def parse_product(self, response):
        product = response.meta['product']
        desc = response.xpath('//div[@id="product-description-full"]/text()') \
                       .extract()
        if desc:  
            product['description'] = desc[0]

        related = response.css('#related li.rel-item .rel-title a')
        r = []
        for rel in related:
            title = rel.xpath('text()').extract()
            url = rel.xpath('@href').extract()
            if title and url:
                r.append(RelatedProduct(
                    title = title[0],
                    url = urlparse.urljoin(response.url,url[0])
                ))
        product['related_products'] = {'recommended':r}        
        
        return product
        
    def _scrape_total_matches(self, response):
        return None
        
    def _scrape_product_links(self, response):

        items = response.css('ol.product-results li.psli')
 
        if not items:
            self.log("Found no product links.", DEBUG)
        #try to get data from json    
        script = response.xpath('//div[@id="xjsi"]/script/text()').extract()    
        script = script[0] if script else ''
        pattern = r'"r":(\{"[^\}]*})'
        json_data = {}
        m = re.search(pattern, script)
        if m:
             json_data = json.loads(m.group(1))
            
        for item in items:
            url = title = description = price = image_url = None
            try:
                id = item.xpath('@data-docid').extract()[0]
                link = item.xpath('.//div[@class="pslmain"]/h3[@class="r"]/a')
                price = item.xpath('string(.//div[@class="pslmain"]//span[@class="price"]/b)'
                    ).extract()[0]
                title = link.xpath('string(.)').extract()[0]
                url = link.xpath('@href').extract()[0]                       
            except IndexError:
                self.log('Invalid HTML on {url}'.format(url=response.url), WARNING)
            
            #fill from json
            l = json_data.get(id)
            if l:
                try:
                    if not title:
                        title = Selector(text=l[1]).xpath('string(.)').extract()[0]
                    if not url:
                        url = l[2]
                    description = l[3]             
                    image_url = l[8][0][0]
                except IndexError:
                    self.log('Invalid JSON on {url}'.format(url=response.url), WARNING)
                    
            if url.startswith('http'):
                redirect = None
            else:    
                redirect = url
            url = urlparse.urljoin(response.url,url)

            yield redirect, SiteProductItem(
                url=url, 
                title=title, 
                price=price,
                image_url=image_url,
                description=description)

    def _scrape_next_results_page_link(self, response):

        next = response.css('table#nav td.cur') \
                       .xpath('following-sibling::td[1]/a/@href') \
                       .extract()
        
        if not next:
            link = None
            self.log('Next page link not found', ERROR)
        else:
            link = urlparse.urljoin(response.url, next[0])    
        return link
                                                  
