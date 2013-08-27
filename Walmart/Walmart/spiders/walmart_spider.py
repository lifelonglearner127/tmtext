from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Walmart.items import CategoryItem
from Walmart.items import ProductItem
from scrapy.http import Request
import sys
import re
import datetime

################################
# Run with 
#
# scrapy crawl walmart
#
################################

# scrape sitemap and extract categories
class WalmartSpider(BaseSpider):
    name = "walmart"
    allowed_domains = ["walmart.com"]
    start_urls = [
        "http://www.walmart.com/cp/All-Departments/121828",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//div[@class='MidContainer']/div[3]//a[@class='NavM']")
        parent_links = hxs.select("//div[@class='MidContainer']/div[3]//a[@class='NavXLBold']")

        root_url = "http://www.walmart.com"

        for link in links:
            item = CategoryItem()

            # search for the category's parent
            parents = []

            # select the preceding siblings that are a category title (have a child that is an a tag with a certain class)
            parents = link.select('parent::node()').select('preceding-sibling::node()').select('child::a[@class=\'NavXLBold\']')

            # if we found such siblings, get the last one to be the parent
            if parents:
                item['parent_text'] = parents[-1].select('text()').extract()[0]
                item['parent_url'] = parents[-1].select('@href').extract()[0]

                item['parent_url'] = Utils.add_domain(item['parent_url'], root_url)

            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]

            # add domain if relative URL
            item['url'] = Utils.add_domain(item['url'], root_url)

            item['level'] = 0

            #yield item

            # send category page to parseCategory function to extract description and number of products and add them to the item
            yield Request(item['url'], callback = self.parseCategory, meta = {'item' : item})

        for link in parent_links:
            item = CategoryItem()

            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]

            # add domain if relative URL
            item['url'] = Utils.add_domain(item['url'], root_url)

            item['level'] = 1

            #yield item

            # send category page to parseCategory function to extract description and number of products and add them to the item
            yield Request(item['url'], callback = self.parseCategory, meta = {'item' : item})

    # parse category page and extract description and number of products
    def parseCategory(self, response):
        hxs = HtmlXPathSelector(response)
        item = response.meta['item']

        description_holder = hxs.select("//div[@id='detailedPageDescriptionCopyBlock']")
        
        # try to find description title in <b> tag in the holder;
        # if it's not find, try to find it in the first <p> if the description
        # if fund there, exclude it from the description body
        description_title = description_holder.select(".//b/text()").extract()
        if description_title:
            item['description_title'] = description_title[0]

        description_texts = description_holder.select(".//text()[not(ancestor::b)]").extract()
        # if the list is not empty and contains at least one non-whitespace item
        if description_texts and reduce(lambda x,y: x or y, [line.strip() for line in description_texts]):
            item['description_text'] = " ".join(description_texts).strip()

        yield item


class Utils():

    # append domain name in front of relative URL if it's missing
    @staticmethod
    def add_domain(url, root_url):
        if not re.match("http:.*", url):
            url = root_url + url
        return url

# scrape bestsellers lists and extract products
class BestsellerSpider(BaseSpider):
    name = "bestseller"
    allowed_domains = ["walmart.com"]
    start_urls = [
        "http://www.walmart.com/cp/Best-Sellers/1095979",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        # select list of bestsellers departments
        dept_list = hxs.select("//div[@class='MainCopy']")[1]

        # select departments
        departments = dept_list.select("ul/li/a")

        for department in departments:

            # extract departments and pass them to parseDepartment function to parse list for each of them
            dept = department.select("text()").extract()[0]
            dept_url = department.select("@href").extract()[0]

            root_url = "http://www.walmart.com"
            url = root_url + dept_url
            request = Request(url, callback = self.parseDepartment)
            request.meta['department'] = dept

            yield request

    def parseDepartment(self, response):

        # some of the products are duplicates across departments, they will only appear once on the final list

        hxs = HtmlXPathSelector(response)

        department = response.meta['department']

        #TODO: what if there is pagination? haven't encountered it so far

        products = hxs.select("//div[@class='prodInfo']")
        root_url = "http://www.walmart.com"

        # counter to keep track of product's rank
        rank = 0

        for product in products:
            item = ProductItem()

            rank += 1
            item['rank'] = str(rank)

            product_link = product.select("div[@class='prodInfoBox']/a[@class='prodLink ListItemLink']")

            product_name = product_link.select("text()").extract()
            product_url = product_link.select("@href").extract()

            if product_name:
                item['list_name'] = product_name[0]

            if product_url:
                item['url'] = root_url + product_url[0]
            else:
                # if there's no url move on to the next product
                continue

            item['department'] = department

            #TODO: some of the products have the "From" prefix before the price, should I include that?
            price_div = product.select(".//div[@class='camelPrice'] | .//span[@class='camelPrice']")
            price1 = price_div.select("span[@class='bigPriceText2']/text()").extract()
            price2 = price_div.select("span[@class='smallPriceText2']/text()").extract()

            if price1 and price2:
                item['price'] = price1[0] + price2[0]

            #TODO: include out of stock products? :
            else:
                price1 = price_div.select("span[@class='bigPriceTextOutStock2']/text()").extract()
                price2 = price_div.select("span[@class='smallPriceTextOutStock2']/text()").extract()

                if price1 and price2:
                    item['price'] = price1[0] + price2[0]

            #TODO: are list prices always retrieved correctly?
            listprice = product.select(".//div[@class='PriceMLtgry']/text").extract()
            if listprice:
                item['listprice'] = listprice[0]

            item['bspage_url'] = response.url

            # pass the item to the parseProduct method
            request = Request(item['url'], callback = self.parseProduct)
            request.meta['item'] = item

            yield request

    def parseProduct(self, response):
        hxs = HtmlXPathSelector(response)

        item = response.meta['item']

        product_name = hxs.select("//h1[@class='productTitle']/text()").extract()[0]
        item['product_name'] = product_name

        page_title = hxs.select("//title/text()").extract()[0]

        # remove "Walmart.com" suffix from page title
        m = re.match("(.*) [:-] Walmart\.com", page_title, re.UNICODE)
        if m:
            page_title = m.group(1).strip()


        # there are other more complicated formul as as well, we're not removing them anymore, the product name is enough on this case
        # "Purchase the ... for a low price at Walmart.com"
        # m1 = re.match("(.*) for less at Walmart\.com\. Save money\. Live better\.", page_title, re.UNICODE)
        # if m1:
        #     page_title = m1.group(1).strip()

        # m2 = re.match("(.*) at an always low price from Walmart\.com\. Save money\. Live better\.", page_title, re.UNICODE)
        # if m2:
        #     page_title = m2.group(1).strip()

        # m3 = re.match("(.*) at Walmart\.com\. Save money\. Live better\.", page_title, re.UNICODE)
        # if m3:
        #     page_title = m3.group(1).strip()

        item['page_title'] = page_title

        # add date
        item['date'] = datetime.date.today().isoformat()

        yield item