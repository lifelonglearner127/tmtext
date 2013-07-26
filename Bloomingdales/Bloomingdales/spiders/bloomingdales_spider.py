from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Bloomingdales.items import CategoryItem
from Bloomingdales.items import ProductItem
from scrapy.http import Request
import re
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
        pages = [
                    # handbags
                "http://www1.bloomingdales.com/shop/handbags/best-sellers?id=23173#fn=sortBy%3DBEST_SELLERS%26productsPerPage%3D96",\
                    # shoes
                "http://www1.bloomingdales.com/shop/shoes/best-sellers?id=23268#fn=sortBy%3DBEST_SELLERS%26productsPerPage%3D96", \
                    # shoes page 2
                "http://www1.bloomingdales.com/shop/shoes/best-sellers?id=23268#fn=pageIndex%3D2%26sortBy%3DBEST_SELLERS%26productsPerPage%3D96"
                 
        ]

        # call parsePage for each of these pages
        for page_i in range(len(pages)):
            request = Request(pages[page_i], callback = self.parsePage)
            if page_i == 0:
                department = "Handbags"
            else:
                department = "Shoes"
            #print "+++++++++++++++++" + pages[page_i]
            request.meta['department'] = department
            yield request

    def parsePage(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select("//div[@class='productThumbnail showQuickView']")




        #sys.stderr.write("---------------------------------------------------" + response.url)

        if not products:
            return
        
        # counter to hold rank of product
        rank = 0

        for product in products:
            item = ProductItem()

            rank += 1
            item['rank'] = str(rank)

            # get item department from response's meta
            item['department'] = response.meta['department']

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
