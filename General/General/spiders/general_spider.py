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
    "amazon.com", "staples.com"] # to be added - check bitbucket
    start_urls = [
        # random url
        "http://www.staples.com",
    ]

    # store the cateory page url given as an argument into a field and add it to the start_urls list
    def __init__(self, prod_pages_file, outfile = "product_urls.txt", use_proxy = False):
        self.prod_pages_file = prod_pages_file
        self.outfile = outfile
        urlsfile = open(prod_pages_file, "r")
        self.prod_urls = []
        for line in urlsfile:
            self.prod_urls.append(line.strip())
        urlsfile.close()

    def parse(self, response):
        for url in self.prod_urls:
            domain =  Utils.extract_domain(url)
            if domain != 'staples':
                yield Request(url, callback = self.parseProdpage)
            # for staples we need extra cookies
            else:
                yield Request(url, callback = self.parseProdpage, cookies = {"zipcode" : "1234"}, \
            headers = {"Cookie" : "zipcode=" + "1234"}, meta = {"dont_redirect" : True, "dont_merge_cookies" : True})

    def parseProdpage(self, response):
        hxs = HtmlXPathSelector(response)

        item = ProductItem()
        item['url'] = response.url

        #########################
        # Works for:
        #
        #   macys
        #   amazon
        #   bloomingdales
        #   overstock
        #   newegg
        #
        # Doesn't work for:
        #   staples - a few exceptions
        #


        # select tags with "Title", then with "title" in their class or id
        # if none, select h1 tags, if there is only one assume that's the title
        # if more than one?
        # if none?
        # eliminate ones with just whitespace
        #TODO: idea: check similarity with page title
        product_name = hxs.select("//h1[contains(@id, 'Title') or contains(@class, 'Title')]//text()[normalize-space()!='']")
        # if there are more than 2, exclude them, it can't be right
        if product_name and len(product_name) < 2:
            # select ones that don't only contain whitespace
            item['product_name'] = product_name.extract()[0].strip()
        else:
            # find which sites need this
            #product_name = hxs.select("//*[contains(@id, 'Title') or contains(@class, 'Title')]//text()[normalize-space()!='']")
            if product_name and len(product_name) < 2:
                item['product_name'] = product_name.extract()[0].strip()
            else:
                product_name = hxs.select("//*[contains(@id, 'title') or contains(@class, 'title')\
                    or contains(@class, 'Title') or contains(@id, 'Title')]//text()[normalize-space()!='']")
                if product_name and len(product_name) < 2:
                    item['product_name'] = product_name.extract()[0].strip()
                else:
                    product_name = hxs.select("//*[contains(@id, 'name') or contains(@class, 'name')]//text()[normalize-space()!='']")
                    if product_name and len(product_name) < 2:
                        item['product_name'] = product_name.extract()[0].strip()
                    else:
                        h1s = hxs.select("//h1//text()[normalize-space()!='']")
                        if len(h1s) == 1:
                            item['product_name'] = h1s.extract()[0].strip()
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