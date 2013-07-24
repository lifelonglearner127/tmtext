from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Amazon.items import AmazonItem
from Amazon.items import ProductItem
from scrapy.http import Request
from scrapy.http import Response
import re
import sys

################################
# Run with 
#
# scrapy crawl amazon
#
################################

# crawls sitemap and extracts department and categories names and urls (as well as other info)
class AmazonSpider(BaseSpider):
    name = "amazon"
    allowed_domains = ["amazon.com"]
    start_urls = [
        "http://www.amazon.com/gp/site-directory/ref=sa_menu_top_fullstore",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links_level0 = hxs.select("//div[@id='siteDirectory']//table//a")
        titles_level1 = hxs.select("//div//table//h2")
        items = []

        # add level 1 categories to items

        # first one is a special category ("Unlimited Instant Videos"), add it separately
        special_item = AmazonItem()
        special_item['text'] = titles_level1[0].select('text()').extract()[0]
        special_item['level'] = 2
        special_item['special'] = 1
        items.append(special_item)

        # the rest of the titles are not special
        for title in titles_level1[1:]:
            item = AmazonItem()
            item['text'] = title.select('text()').extract()[0]
            item['level'] = 2

            items.append(item)

        # add level 0 categories to items
        for link in links_level0:
            item = AmazonItem()
            item['text'] = link.select('text()').extract()[0]
            root_url = "http://www.amazon.com"
            item['url'] = root_url + link.select('@href').extract()[0]
            item['level'] = 1

            parent = link.select("parent::node()/parent::node()/preceding-sibling::node()")
            parent_text = parent.select('text()').extract()
            if parent_text:
                item['parent_text'] = parent_text[0]

                # if its parent is the special category, mark this one as special too
                if (item['parent_text'] == special_item['text']):
                    item['special'] = 1

            items.append(item)

        return items

# crawl bestsellers lists and extract product name, price, department etc
class BestsellerSpider(BaseSpider):
    name = "bestseller"
    allowed_domains = ["amazon.com"]
    start_urls = [
        "http://www.amazon.com/Best-Sellers/zgbs/ref=zg_bs_unv_mas_0_mas_1",
    ]

    # get main pages for department bestseller pages and pass them to the parsePage function
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        department_links = hxs.select("//ul[@id='zg_browseRoot']/ul/li/a")

        departments = []

        # extract department name and url for each department in menu
        #TODO: add info about availability
        #TODO: manage exceptions: MP3
        #                         lawn and garden is missing page 3
        for department_link in department_links:
            department = {"url" : department_link.select("@href").extract()[0], "text" : department_link.select("text()").extract()[0]}
            departments.append(department)
        
        # pass department urls to parsePage (35 departments)
        for department in departments:
            request = Request(department['url'], callback = self.parsePage)
            request.meta['dept_name'] = department['text']
            yield request

    # extract each page url for a department's bestseller list and pass it to parseDepartment
    def parsePage(self, response):
        hxs = HtmlXPathSelector(response)
        
        # for MP3 Downloads, rerun this method with its subcategories (MP3 Songs and MP3 Albums). also split it into paid and free?
        if response.meta['dept_name'] == "MP3 Downloads":
            subcategories = hxs.select("//ul[@id='zg_browseRoot']/ul/ul/li/a")
            for subcategory in subcategories:
                request = Request(subcategory.select("@href").extract()[0], callback = self.parsePage)
                request.meta['dept_name'] = subcategory.select("text()").extract()[0]
                yield request

        else:
            page_urls = hxs.select("//div[@id='zg_paginationWrapper']//a/@href").extract()

            for page_url in page_urls:
                request = Request(page_url, callback = self.parseDepartment)
                request.meta['dept_name'] = response.meta['dept_name']
                yield request

    # take a page of a department's bestsellers list and extract products
    def parseDepartment(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select("//div[@class='zg_itemImmersion']")

        items = []

        for product in products:
            item = ProductItem()

            #TODO: the index for the title is sometimes out of range - sometimes it can't find that tag (remove the [0] to debug)
            list_name = product.select("div[@class='zg_itemWrapper']//div[@class='zg_title']/a/text()").extract()
            if list_name:
                item['list_name'] = list_name[0]
            else:
                # if there's no product name don't include this product in the list, move on to the next
                continue

            url = product.select("div[@class='zg_itemWrapper']//div[@class='zg_title']/a/@href").extract()
            if url:
                item['url'] = url[0].strip()
            else:
                # if there's no product url don't include this product in the list, move on to the next
                # one of the products in Lawn & Garden is missing a name and url, also in Sports & Outdoors
                continue
            
            #TODO: this needs to be refined, many prices etc. extract all prices? new, used etc
            prices = product.select("div[@class='zg_itemWrapper']//div[@class='zg_price']")

            price = prices.select("strong[@class='price']/text()").extract()
            listprice = prices.select("span[@class='listprice']/text()").extract()

            # some of the items don't have a price
            if price:
                item['price'] = price[0]

            # some items don't have a "list price"
            if listprice:
                item['listprice'] = listprice[0]

            # extract rank and ignore last character of the string (it's .)
            item['rank'] = product.select(".//span[@class='zg_rankNumber']/text()").extract()[0][:-1]

            #dept_name = hxs.select("//ul[@id='zg_browseRoot']//span[@class='zg_selected']/text()").extract()[0].strip()
            item['department'] = response.meta['dept_name']#dept_name

            # pass the item to the parseProduct function to extract info from product page
            request = Request(item['url'], callback = self.parseProduct)
            request.meta['item'] = item

            yield request


    # extract info from product page
    def parseProduct(self, response):
        hxs = HtmlXPathSelector(response)

        item = response.meta['item']

        # find title of product page
        page_title = hxs.select("//title/text()").extract()[0]

        # Remove "Amazon.com" from title, to leave only the prouct's name

        # handle all cases (titles come in different formats)
        
        # format 1
        m1 = re.match("(.*)[-:] Amazon\.com(.*)", page_title, re.UNICODE)
        if m1:
            page_title = m1.group(1).strip() + m1.group(2)

        # format 2
        m2 = re.match("Amazon\.com ?: (.*)", page_title, re.UNICODE)
        if m2:
            page_title = m2.group(1)

        # Remove department name from page title if found

        # there are some other suffixes after : , that are not always the same department's name (like ": Kitchen & Dining" in an Appliances product)
        
        # m = re.match("(.*): " + item['department'], page_title, re.UNICODE)
        # if m:
        #     page_title = m.group(1)

        #TODO: handle special characters, like trademark symbol; also output them as unicode strings in the output file
        
        item['page_title'] = page_title


        # find product name on product page (5 possible formats)
        product_name = hxs.select("//span[@id='btAsinTitle']/text()").extract()
        if not product_name:
            product_name = hxs.select("//h1[@id='title']/text()").extract()
        if not product_name:
            product_name = hxs.select("//h1[@class='parseasinTitle']/text()").extract()
        if not product_name:
            product_name = hxs.select("//h1[@class='parseasintitle']/text()").extract()

        # for the movies department it's only a h1
        if not product_name:
            product_name = hxs.select("//h1/text()").extract()
        # if not product_name:
        #     product_name = "nume"
        # else:
        item['product_name'] = product_name[0].strip()

        return item
