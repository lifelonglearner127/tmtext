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
    "amazon.com", "staples.com", "williams-sonoma.com"] # to be added - check bitbucket
    start_urls = [
        # random url
        "http://www.walmart.com",
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
            #TODO: pass some cookie with country value for sites where price for example is displayed in local currency
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
        #   amazon              //span[@id='btAsinTitle']/text(), //h1[@id='title']/text(), //h1[@class='parseasinTitle, //h1[@class='parseasintitle']/text()
        #   bloomingdales       //h1[@id='productTitle']/text()
        #   overstock           "//h1/text()"
        #   newegg
        #   tigerdirect
        #   walmart             //h1[@class='productTitle']/text()
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
                product_name = hxs.select("//h1[contains(@*, 'title') or contains(@*, 'Title') or contains (@*, 'name')]//text()[normalize-space()!='']")
                if product_name and len(product_name) < 2:
                    item['product_name'] = product_name.extract()[0].strip()
                else:
                    product_name = hxs.select("//*[contains(@*, 'Title') or contains(@*,'title')]//text()[normalize-space()!='']")
                    if product_name and len(product_name) < 2:
                        item['product_name'] = product_name.extract()[0].strip()
                    else:
                        h1s = hxs.select("//h1//text()[normalize-space()!='']")
                        if len(h1s) == 1:
                            item['product_name'] = h1s.extract()[0].strip()
                        else:
                            print 'Error: no product name: ', response.url


        #TODO: needs improvement
        # extract price
        price_holder = hxs.select("//text()[normalize-space()='$' or normalize-space()='USD' or normalize-space()='usd']/parent::*/parent::*")
        # look for number regular expressions
        price = price_holder.select(".//text()").re("[0-9\s]+")
        # assume first value is dollars and second is cents (if they are different)
        if len(price) > 1 and price[0] != price[1]:
            #TODO: errors for tigerdirect when price is > 1000 => 1.999
            price_string = "$" + price[0] + "." + price[1]
        else:
            price_string = price[0]
        if price:
            item['price'] = price_string
            #TODO: what if there are more prices on the page, like for other products? see tigerdirect


        # # bestbuy
        # item['product_name'] = hxs.select("//h1/text()").extract()[0].strip()

        # # overstock
        # product_name = hxs.select("//h1/text()").extract()[0]

        # # bloomingdales
        # product_name = hxs.select("//h1[@id='productTitle']/text()").extract()[0]

        # # macys


        yield item