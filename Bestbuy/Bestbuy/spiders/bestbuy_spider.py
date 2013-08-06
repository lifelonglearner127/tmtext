from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Bestbuy.items import CategoryItem
from Bestbuy.items import ProductItem
from scrapy.http import Request
import re
import sys
import datetime

################################
# Run with 
#
# scrapy crawl bestbuy
#
################################

# crawl sitemap and extract products and categories
class BestbuySpider(BaseSpider):
    name = "bestbuy"
    allowed_domains = ["bestbuy.com"]
    start_urls = [
        "http://www.bestbuy.com/site/sitemap.jsp",
    ]

    def parse(self, response):
        # currently not extracting parents that are non-links (smaller parent categories like "resources" and "shops")
        hxs = HtmlXPathSelector(response)

        # select all categories (bottom level)
        product_links = hxs.select("//div[@id='container']/div/header//nav/ul[@id='nav']//li/a")

        # select all parent categories
        parent_links = hxs.select("//div[@id='container']/div/header//nav/ul[@id='nav']//h4/a")

        #TODO: add extraction of level 3 categories (broadest: products, services,...)
        
        items = []

        for link in product_links:

            # retrieve parent category for this link
            parent = link.select("parent::node()/parent::node()/preceding-sibling::node()/a")
            item = CategoryItem()

            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]

            
            parent_text = parent.select('text()').extract()
            parent_url = parent.select('@href').extract()
            if parent_text:
                item['parent_text'] = parent_text[0]
            if parent_url:
                item['parent_url'] = parent_url[0]


            # mark it as special if a certain condition is checked
            if (link.select("parent::node()/parent::*[@class='nav-res']")):
                item['special'] = 1
            #TODO: add its direct parent if it's special (not among the categories). ex: shops, resources...

            # get grandparent of the category, mark item as special if grandparent is special
            grandparent = parent.select("parent::node()/parent::node()/parent::node()/parent::node()")
            if not grandparent.select('@class') or grandparent.select('@class').extract()[0] != 'nav-pro':
                item['special'] = 1

            
            grandparent_text = grandparent.select('a/text()').extract()
            grandparent_url = grandparent.select('a/@href').extract()
            if grandparent_text:
                item['grandparent_text'] = grandparent_text[0]
            if grandparent_url:
                item['grandparent_url'] = grandparent_url[0]

            item['level'] = 0

            items.append(item)

        for link in parent_links:
            item = CategoryItem()

            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]

            item['level'] = 1
            parent = link.select("parent::node()/parent::node()/parent::node()/parent::node()")

            # mark item as special if its parent is special
            if not parent.select('@class').extract() or parent.select('@class').extract()[0] != "nav-pro":
                item['special'] = 1

            parent_text = parent.select('a/text()').extract()
            parent_url = parent.select('a/@href').extract()
            if parent_text:
                item['parent_text'] = parent_text[0]
            if parent_url:
                item['parent_url'] = parent_url[0]

            items.append(item)

        return items


################################
# Run with 
#
# scrapy crawl bestbuy [-a max_products=<number>]
#
################################

# crawl bestsellers pages and extract products info
class BestsellerSpider(BaseSpider):
    name = "bestseller"
    allowed_domains = ["bestbuy.com"]
    start_urls = [
        "http://www.bestbuy.com/site/Electronics/Top-Rated-Products/pcmcat140900050011.c?id=pcmcat140900050011"
    ]

    def __init__(self, max_products = 100):
        # maximum number of bestseller products per category (54 categories)
        self.max_products = int(max_products)

    def parse(self, response):
        # extract departments then pass them to be parsed for categories
        hxs = HtmlXPathSelector(response)
        department_links = hxs.select("//div[@class='narrowcontent']/ul[@class='search']/li/a")
        root_url = "http://www.bestbuy.com"

        for department_link in department_links:
            department_name = department_link.select("text()").extract()[0].strip()
            department_url = root_url + department_link.select("@href").extract()[0]

            # pass department page to be parsed by parseDepartment
            request = Request(department_url, callback = self.parseDepartment)
            request.meta['department'] = department_name
            yield request

    def parseDepartment(self, response):
        # extract categories then pass them to be parsed for categories
        hxs = HtmlXPathSelector(response)

        # select last list in menu
        categories_list = hxs.select("//div[@class='narrowcontent']")[-1]
        category_links = categories_list.select("ul[@class='search']/li/a")
        
        root_url = "http://www.bestbuy.com"

        for category_link in category_links:
            category_name = category_link.select("text()").extract()[0].strip()
            category_url = root_url + category_link.select("@href").extract()[0]

            # pass category page to be parsed by parsePage
            request = Request(category_url, callback = self.parsePage)
            request.meta['department'] = response.meta['department']
            request.meta['category'] = category_name
            yield request


    # parse product list page and extract products info
    def parsePage(self, response):
        hxs = HtmlXPathSelector(response)
        root_url = "http://www.bestbuy.com"
        products_per_page = 15

        max_products = self.max_products
        root_url = "http://www.bestbuy.com"

        # find page number by adding 1 to the previous one
        if 'page_nr' not in response.meta:
            page_nr = 1
        else:
            page_nr = response.meta['page_nr'] + 1

        # find product rank using page number and number of items per page
        rank = (page_nr - 1) * 15

        products = hxs.select("//div[@class='hproduct']")
        for product in products:
            item = ProductItem()
            rank += 1
            item['rank'] = str(rank)
            product_link = product.select("div[@class='info-main']/h3/a")
            item['list_name'] = product_link.select("text()").extract()[0].strip()
            url = product_link.select("@href").extract()
            if url:
                item['url'] = root_url + url[0]
            item['department'] = response.meta['department']
            item['category'] = response.meta['category']
            item['bspage_url'] = response.url
            item['date'] = datetime.date.today().isoformat()

            item['SKU'] = product.select(".//strong[@class='sku']/text()").extract()[0]

            #TODO: extract product model?

            saleprice = product.select("div[@class='info-side']/div/h4[@class='price sale']/span/text()").extract()
            if saleprice:
                item['price'] = saleprice[0]

            # regular price
            regprice = product.select("div[@class='info-side']/h4[@class='price regular']/span/text()").extract()
            if regprice:
                item['regprice'] = regprice[0]

            if rank > max_products:
                break

            if not url:
                yield item
            else:
                # send this product page to be parsed by parseProduct
                # ! duplicates are removed: products that are in more than one category will appear in only one of them
                #TODO: include duplicates if they are from different categories?
                yield Request(item['url'], callback = self.parseProduct, meta = {"item":item})


        # select next page, if any, parse it too with this method
        if rank < max_products:
            next_page = hxs.select("//ul[@class='pagination']/li/a[@class='next']/@href").extract()
            if next_page:
                page_url = root_url + next_page[0]
                request = Request(url = page_url, callback = self.parsePage)
                request.meta['department'] = response.meta['department']
                request.meta['category'] = response.meta['category']
                request.meta['page_nr'] = page_nr
                yield request


    # parse product page and extract product info
    def parseProduct(self, response):
        hxs = HtmlXPathSelector(response)
        item = response.meta['item']

        page_title = hxs.select("//title/text()").extract()[0].strip()
        # remove "- Best Buy" suffix from page title
        m = re.match("(.*) - Best Buy", page_title, re.UNICODE)
        if m:
            page_title = m.group(1)
        item['product_name'] = hxs.select("//h1/text()").extract()[0].strip()

        yield item

