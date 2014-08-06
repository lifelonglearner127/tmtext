from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
#from future_builtins import *

import re
import urlparse
import urllib

from scrapy.selector import Selector
from scrapy.log import ERROR

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set


class CvsProductsSpider(BaseProductsSpider):
    name = 'cvs_products'
    allowed_domains = ["cvs.com"]
    start_urls = []

    SEARCH_URL = "http://www.cvs.com/search/_/N-0?searchTerm={search_term}&pt=global&pageNum=1&sortBy=&navNum=20"

    def __init__(self, *args, **kwargs):
        super(CvsProductsSpider, self).__init__(
            #url_formatter=FormatterWithDefaults(pagenum=1, prods_per_page=32),
            *args, **kwargs)
        self.pagenum = 1

    def parse_product(self, response):
        print ("parse_product for", response.url)
        product = response.meta['product']
        sel = Selector(response)

        cond_set(product, 'title',
                 sel.xpath("//h1[@class='prodName']/text()").extract())

        image_url = sel.xpath("//div[@class='productImage']/img/@src").extract()[0]
        product['image_url'] = image_url

        size = sel.xpath("//form[@id='addCart']/table/tr/td[@class='col1']/text()[.='Size:']/../../td[2]/text()")
        size = size.extract()[0].strip()
        product['model'] = size

        addbasketbutton = sel.xpath('//a[@id="addBasketButton"]')
        if len(addbasketbutton) == 0:
            addbasketbutton = sel.xpath('//div[@class="addBasket"]/a')

        if len(addbasketbutton) >0:
            upc = addbasketbutton.xpath('@data-upcnumber').extract()[0]
            price = addbasketbutton.xpath('@data-listprice').extract()[0]
        else:
            upc = 0
            price = ""

        product['upc'] = int(upc)
        product['price'] = price

        desc = sel.xpath("//div[@id='prodDesc']/p/text()")
        desc = (" ".join(desc.extract())).strip()
        product['description'] = desc

        product['brand'] = ""
        product['locale'] = "en-US"
        product['related_products'] = {}

        print ("prod=", product)
        return product

    def _scrape_total_matches(self, sel):
        total = sel.xpath("//form[@id='topForm']/strong/text()").extract()
        if len(total) == 1:
            total = total[0].strip()
            re1 = r'Results.*of (\d+)'
            rg = re.compile(re1, re.IGNORECASE | re.DOTALL)
            m = rg.search(total)
            if m:
                n = m.group(1)
                return int(n)

    def _scrape_product_links(self, sel):
        """_scrape_product_links(sel:Selector)
                :iter<tuple<str, SiteProductItem>>

        Returns the products in the current results page and a SiteProductItem
        which may be partially initialized.
        """
        links = sel.xpath("//div[@class='product']/div[@class='innerBox']/div[@class='productSection1']/a/@href").extract()
        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            print ("debug. _scrape_product_links", no, link)
            # ovs DEBUG replace not pass url 
            yield link, SiteProductItem()
            #yield None, SiteProductItem()

    def _scrape_next_results_page_link(self, sel):
        """  I don't know how to transfer here search_page_no to make url for next search page.
        """
        response = sel.response
        max_page = int(self._scrape_total_matches(Selector(response))/20)

        url_parse = urlparse.urlsplit(response.url)
        query_string = urlparse.parse_qs(url_parse.query)
        current_page = int(query_string.get("pageNum", [1])[0])
        if current_page > max_page:
            return None
        query_string["pageNum"] = [current_page + 1]
        link = urlparse.urlunsplit((
            url_parse.scheme,
            url_parse.netloc,
            url_parse.path,
            urllib.urlencode(query_string, True),
            url_parse.fragment,
        ))
        return link

