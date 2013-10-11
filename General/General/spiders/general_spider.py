from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from General.items import CategoryItem
from General.items import ProductItem
from scrapy.http import Request
import sys
import re
import datetime

from spiders_utils import Utils


################################
# Run with 
#
# scrapy crawl products -a prod_pages_file="<urls_file>" [-a outfile="<filename>"]
#
################################

# scrape product page and extract info on it
class ProductsSpider(BaseSpider):
    name = "products"
    allowed_domains = ["walmart.com", "bestbuy.com", "newegg.com", "tigerdirect.com", "overstock.com", "bloomingdales.com", "macys.com",\
    "amazon.com"] # to be added - check bitbucket
    start_urls = [
        # random url
        "http://www.walmart.com/cp/All-Departments/121828",
    ]

    # store the cateory page url given as an argument into a field and add it to the start_urls list
    def __init__(self, prod_pages_file, outfile = "product_urls.txt", use_proxy = False):
        self.prod_pages_file = prod_pages_file
        self.outfile = outfile
        urlsfile = open(prod_pages_file, "r")
        self.prod_urls = []
        for line in urlsfile:
            self.prod_urls.append(line.strip())
        print self.prod_urls
        urlsfile.close()

    def parse(self, response):
        #print self.prod_urls
        for url in self.prod_urls:
            print url
            yield Request(url, callback = self.parseProdpage)

    def parseProdpage(self, response):
        hxs = HtmlXPathSelector(response)

        item = ProductItem()
        item['url'] = response.url

        # select h1 tags. if there are more than one, select those with "Title" or "title" in their class or id
        # if more than one?
        # if none?
        h1s = hxs.select("//h1/text()")
        if len(h1s) == 1:
            item['product_name'] = h1s.extract()[0]
        else:
            product_name = hxs.select("//*[contains(id, 'Title') or contains(class, 'Title')\
                or contains(id, 'title') or contains(class, 'title')]/text()")
            if product_name:
                item['product_name'] = product_name.extract()[0]
            else:
                print 'Error: no product name: ', response.url

        # # walmart
        # product_name = hxs.select("//h1[@class='productTitle']/text()").extract()[0]
        # item['product_name'] = product_name

        # # bestbuy
        # item['product_name'] = hxs.select("//h1/text()").extract()[0].strip()

        # # newegg

        # # tigerdirect

        # # overstock
        # product_name = hxs.select("//h1/text()").extract()[0]

        # # bloomingdales
        # product_name = hxs.select("//h1[@id='productTitle']/text()").extract()[0]

        # # macys

        # # amazon
        # product_name = hxs.select("//span[@id='btAsinTitle']/text()").extract()
        # if not product_name:
        #     product_name = hxs.select("//h1[@id='title']/text()").extract()
        # if not product_name:
        #     product_name = hxs.select("//h1[@class='parseasinTitle']/text()").extract()
        # if not product_name:
        #     product_name = hxs.select("//h1[@class='parseasintitle']/text()").extract()

        yield item