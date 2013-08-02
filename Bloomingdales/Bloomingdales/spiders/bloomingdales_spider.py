from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Bloomingdales.items import CategoryItem
from Bloomingdales.items import ProductItem
from scrapy.http import Request
from scrapy.http import TextResponse
from selenium import webdriver
import re
import time
import sys

################################
# Run with 
#
# scrapy crawl bloomingdales
#
################################

# scrape sitemap list and retrieve categories
class BloomingdalesSpider(BaseSpider):
    name = "bloomingdales"
    allowed_domains = ["bloomingdales.com"]
    start_urls = [
        "http://www1.bloomingdales.com/service/sitemap/index.ognc?cm_sp=NAVIGATION-_-BOTTOM_LINKS-_-SITE_MAP",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//div[@class='sr_siteMap_container']/div[position()>2 and position()<5]//a")
        items = []

        #TODO: add registry as special category?

        for link in links:
            item = CategoryItem()
            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]
            item['level'] = 0
            items.append(item)

        return items


################################
# Run with 
#
# scrapy crawl bestseller
#
################################

# scrape bestsellers list and retrieve products
class BloomingdalesSpider(BaseSpider):
    name = "bestseller"
    allowed_domains = ["bloomingdales.com"]
    start_urls = [
        "http://www1.bloomingdales.com/service/sitemap/index.ognc?cm_sp=NAVIGATION-_-BOTTOM_LINKS-_-SITE_MAP",
    ]

    def parse(self, response):

        # list of bestsellers pages, product ordered by bestseller

        #TODO: can't parse page 2 pf shoes
        #TODO: they're not ordered by bestseller
        #TODO: add date
        pages = [
                    # handbags
                "http://www1.bloomingdales.com/shop/handbags/best-sellers?id=23173",\
                    # shoes
                "http://www1.bloomingdales.com/shop/shoes/best-sellers?id=23268", \
                #     # shoes page 2
                # #"http://www1.bloomingdales.com/shop/shoes/best-sellers?id=23268#fn=pageIndex%3D2%26sortBy%3DBEST_SELLERS%26productsPerPage%3D96"
                # "http://www1.bloomingdales.com/shop/shoes/best-sellers?id=23268&pageIndex=2"
                 
        ]

        # call parsePage for each of these pages
        for page_i in range(len(pages)):
            request = Request(pages[page_i], callback = self.parseDept)
            if page_i == 0:
                department = "Handbags"
            else:
                department = "Shoes"
            #print "+++++++++++++++++" + pages[page_i]
            request.meta['department'] = department
            yield request

    def parseDept(self, response):
        department = response.meta['department']
        hxs = HtmlXPathSelector(response)
        items = []

        # # use selenium to select the sorting option
        driver = webdriver.Firefox()
        driver.get(response.url)

        # use selenium to select USD currency
       
        link = driver.find_element_by_xpath("//li[@id='bl_nav_account_flag']//a")
        link.click()
        time.sleep(5)
        button = driver.find_element_by_id("iShip_shipToUS")
        button.click()
        time.sleep(10)

        dropdown = driver.find_element_by_id("sortBy")
        for option in dropdown.find_elements_by_tag_name("option"):
            if option.text == 'Best Sellers':
                option.click()

        time.sleep(5)

        # convert html to "nice format"
        text_html = driver.page_source.encode('utf-8')
        html_str = str(text_html)

        # this is a hack that initiates a "TextResponse" object (taken from the Scrapy module)
        resp_for_scrapy = TextResponse('none',200,{},html_str,[],None)
       
        # pass first page to parsePage function to extract products
        items += self.parsePage(resp_for_scrapy, department)


        next_page_url = hxs.select("//li[@class='nextArrow']/div/a")
        while next_page_url:
            # use selenium to click on next page arrow and retrieve the resulted page if any
            next = driver.find_element_by_xpath("//li[@class='nextArrow']/div/a")
            next.click()

            time.sleep(5)

            # convert html to "nice format"
            text_html = driver.page_source.encode('utf-8')
            html_str = str(text_html)

            # this is a hack that initiates a "TextResponse" object (taken from the Scrapy module)
            resp_for_scrapy = TextResponse('none',200,{},html_str,[],None)

            # pass the page to parsePage function to extract products
            items += self.parsePage(resp_for_scrapy, department)

            hxs = HtmlXPathSelector(resp_for_scrapy)
            next_page_url = hxs.select("//li[@class='nextArrow']/div/a")
            if next_page_url:
                print "NEXT_PAGE_URL", next_page_url

        driver.close()

        return items

    def parsePage(self, response, department):
        hxs = HtmlXPathSelector(response)
        products = hxs.select("//div[@class='productThumbnail showQuickView']")

        if not products:
            return
        
        # counter to hold rank of product
        rank = 0

        for product in products:
            item = ProductItem()

            rank += 1
            item['rank'] = str(rank)

            # get item department from response's meta
            item['department'] = department

            # extract name and url from bestsellers list
            product_link = product.select("div[@class='shortDescription']/a")
            name = product_link.select("text()").extract()
            if name:
                item['list_name'] = name[0]
            url = product_link.select("@href").extract()
            if url:
                item['url'] = url[0]

            # if there's no url move on to next product
            else:
                continue

            #TODO: add net price?

            #TODO: parse price to leave only int value? (eliminate "USD")
            price = product.select(".//div[@class='prices']//span[@class='priceBig']/text()").extract()
            if price:
                item['price'] = price[0]

            # call parseProduct method on each product]
            request = Request(item['url'], callback = self.parseProduct)
            request.meta['item'] = item

            yield request

    def parseProduct(self, response):
        hxs = HtmlXPathSelector(response)
        product_name = hxs.select("//h1[@id='productTitle']/text()").extract()[0]

        page_title = hxs.select("//title/text()").extract()[0]

        item = response.meta['item']

        # remove page suffix " | Bloomingdales"
        m = re.match("(.*) \| Bloomingdale's", page_title, re.UNICODE)
        if m:
            page_title = m.group(1).strip()

        item['page_title'] = page_title
        item['product_name'] = product_name

        return item
