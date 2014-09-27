from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse
import urllib

from scrapy.log import ERROR, DEBUG, INFO
from scrapy.http import Request

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
     cond_set, cond_set_value, _extract_open_graph_metadata

class Category:
    sort_orders = None
    def __init__(self, url, sort_orders = None):
        self.url = url
        if sort_orders:
            self.sort_orders = sort_orders

class Grocery(Category):
    sort_orders = {
        'default' : 'RELEVANCE',
        'low_price': 'PRICE_ASC',
        'high_price': 'PRICE_DESC',
        'name_asc' : 'NAME_ASC',
        'name_desc':'NAME_DESC',
        'best_sellers':'TOP_SELLERS',
        'rating': 'RATINGS_DESC',
    }        
class Products(Category):
    sort_orders = {
        'default' : 'default',
        'newest': 'newest_first',
        'rating': 'avg_rating',
        'name_asc' : ' price_asc',
        'high_price': 'price_desc',
        'offers':'great_offers'
    } 

def clear_text(l):
    """
    usefull for  clearing sel.xpath('.//text()').explode() expressions
    """
    return " ".join(
        [it for it in map(string.strip, l) if it])
        
class SainsburysUkProductsSpider(BaseProductsSpider):
    name = 'sainsburys_uk_products'
    allowed_domains = ["sainsburys.co.uk"]
    start_urls = []

    SEARCH_URL = "http://www.sainsburys.co.uk/sol/global_search/global_result.jsp?" \
        "bmForm=global_search&GLOBAL_DATA._search_term1={search_term}&" \
        "GLOBAL_DATA._searchType=0"
        
    CATEGORIES = {
        'Groceries' : Grocery("http://www.sainsburys.co.uk/"
            "webapp/wcs/stores/servlet/SearchDisplayView?" 
            "langId=44&storeId=10151&catalogId=10122&pageSize=30&"
            "orderBy={sort_order}&searchTerm={search_term}&beginIndex=0"),
        'Home & garden' : Products("http://www.sainsburys.co.uk/"
            "sol/shop/home_and_garden/list.html?search={search_term}"
            "&sort={sort_order}"),
        'Appliances' : Products("http://www.sainsburys.co.uk/"
            "sol/shop/appliances/list.html?search={search_term}"
            "&sort={sort_order}"),
        'Technology' : Products("http://www.sainsburys.co.uk/"
            "sol/shop/technology/list.html?search={search_term}"
            "&sort={sort_order}"), 
        'Toys' : Products("http://www.sainsburys.co.uk/"
            "sol/shop/toys_and_nursery/list.html?search={search_term}"
            "&sort={sort_order}"), 
        'Sport & leisure' : Products("http://www.sainsburys.co.uk/"
            "sol/shop/sport_and_leisure/list.html?search={search_term}"
            "&sort={sort_order}"),
        'Baby' : Products("http://www.sainsburys.co.uk/"
            "sol/shop/baby/list.html?search={search_term}"
            "&sort={sort_order}"),
        'Events' : Products("http://www.sainsburys.co.uk/"
            "sol/shop/events/list.html?search={search_term}"
            "&sort={sort_order}"),            
    }    
    
    def __init__(self, search_sort='default', *args, **kwargs):
        super(SainsburysUkProductsSpider, self).__init__(*args, **kwargs)
        self.search_sort = search_sort
        
    def start_requests(self):

        for request in super(SainsburysUkProductsSpider, self).start_requests():
            request.callback = self.parse_global_search
            yield request           
            
    def parse_global_search(self, response):
        total_matches = self._scrape_total_matches(response)
        if total_matches is not None:
            response.meta['total_matches'] = total_matches
            self.log("Found %d total matches." % total_matches, INFO)

            categories = []
            
            groceries = response.xpath(
                '//div[@class="sectionResult foodnDrink"]'
                '//div[@class="sectionResult groceries"]')
            if groceries:
                categories.append('Groceries')
                self.log("Groceries found.", INFO)
            products = response.xpath(  
                '//div[@class="sectionResult gmproductcatagory"]'
                '/div[@class="containerBoxHeader"]/h4/text()') \
                .extract()     
            for product in products:
                self.log("{} found.".format(product), INFO)
                if product in self.CATEGORIES:
                    categories.append(product)
                    
            if categories:
                response.meta['categories'] = categories
                return self._request_category(0, response)
        else:
            self.log("No products found.", INFO)
    def _request_category(self, cat, response):
        st = response.meta['search_term']
        cat_obj = self.CATEGORIES[response.meta['categories'][cat]]
        
        sort = cat_obj.sort_orders.get(
            self.search_sort, 
            cat_obj.sort_orders['default'])
            
        url = cat_obj.url.format(
            search_term=urllib.quote_plus(st),
            sort_order=sort    
            )
        new_meta = response.meta.copy()
        new_meta['cat'] = cat    
        new_meta['products_per_page'] = None
        return Request(
            url,
            meta=new_meta)
                
                 
    def parse_product(self, response):
        product = response.meta['product']
    

        return product
            

    def _scrape_total_matches(self, response):
        total = None
        
        totals = response.css('.panelContentHeader strong::text').extract()
        
        if totals:
            total = int(totals[0].strip())
                      
        else:
            self.log(
                "Failed to find 'total matches' for %s" % response.url,
                ERROR
            )
    
        return total    
        
    def _scrape_product_links(self, response):
        cat = response.meta['categories'][response.meta['cat']]
        if cat == 'Groceries':
        
            items = response.css(
                '#productLister ul.productLister .productNameAndPromotions h3 a'
            )
        else:
            items = response.xpath(
                '(//ul[@class="itemList"])[1]'
                '//h3[@class="listItemDesc"]//a'
            )
                
        if not items:
            self.log("Found no product links.", DEBUG)
        self.log("Found {} links.".format(len(items)), DEBUG)
        for item in items:
            title = item.xpath('text()').extract()
            link = item.xpath('@href').extract()
            
            if link and title:
                title = title[0].strip()
                yield None, SiteProductItem(
                    title=title,
                    url=link[0])
            
    def _scrape_next_results_page_link(self, response):
        cat_index = response.meta['cat']
        cat = response.meta['categories'][cat_index]
        if cat == 'Groceries':
        
            next = response.css(
                '#productLister .pagination li.next a::attr(href)'
            ).extract()
            
        else:
            next = response.css(
                '.paging li.next a::attr(href)'
            ).extract()
        link = None
        if next:
            link = urlparse.urljoin(response.url, next[0])    
        else:
            cat_index += 1
            
            if cat_index < len(response.meta['categories']):
                link = self._request_category(cat_index, response)
        return link
                              
