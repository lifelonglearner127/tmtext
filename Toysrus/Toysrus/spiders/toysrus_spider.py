from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from Toysrus.items import CategoryItem
from Toysrus.items import ProductItem
import re
import sys
import string

################################
# Run with 
#
# scrapy crawl toysrus
#
################################

# scrape sitemap for departments and categories
class ToysrusSpider(BaseSpider):
    name = "toysrus"
    allowed_domains = ["toysrus.com"]

    start_urls = ['http://www.toysrus.com/sitemap/map.jsp']

    # build urls list containing each page of the sitemap, and pass them to parsePage to extract items (categories)
    # the output will not be organized by page by default
    def parse(self, response):

        # pages urls are of the form: http://www.toysrus.com/sitemap/map.jsp?p=<parameter>
        # initialize page names parameters
        pages = ['num']

        # add to page parameters only letters on even positions in the alphabet (they're the only ones that appear in the page names)
        for letter in [string.lowercase[i] for i in range(len(string.lowercase)) if i%2==0]:
            pages.append(letter)

        root_url = self.start_urls[0] + '?p='

        # build pages names and add them to urls list
        urls = []
        for page in pages:
            urls.append(root_url + page)

        # parse each page in urls list with parsePage
        for url in urls:
            yield Request(url, callback = self.parsePage)

    # parse one page - extract items (categories)
    def parsePage(self, response):
        hxs = HtmlXPathSelector(response)
        # selecting main level categories
        links = hxs.select("//div[@id='sitemapLinks']/ul/li/ul/li/a")

        # selecting low level categories
        low_links = hxs.select("//div[@id='sitemapLinks']/ul/li/ul/li/ul/li/a")

        # selecting lower level categories
        lower_links = hxs.select("//div[@id='sitemapLinks']/ul/li/ul/li/ul/li/ul/li/a")

        # selecting departments
        departments = hxs.select("//div[@id='sitemapLinks']/ul/li/a")

        items = []

        root_url = "http://www.toysrus.com"

        # add categories
        for link in links:

            # extract immediate parent
            parent = link.select("parent::node()/parent::node()/parent::node()/a")

            item = CategoryItem()

            # add the current page url as a field
            item['page'] = response.url

            item['text'] = link.select('text()').extract()[0]
            # build this into an absolute url by removing ".." prefix and adding domain
            item['url'] = root_url + link.select('@href').extract()[0][2:]

            item['parent_text'] = parent.select('text()').extract()[0]
            item['parent_url'] = root_url + parent.select('@href').extract()[0][2:]

            # this is the main level of categories
            item['level'] = 0

            items.append(item)


        # add subcategories
        for link in low_links:

            # extract immediate parent
            parent = link.select("parent::node()/parent::node()/parent::node()/a")

            item = CategoryItem()

            # add the current page url as a field
            item['page'] = response.url

            item['text'] = link.select('text()').extract()[0]
            # build this into an absolute url by removing ".." prefix and adding domain
            item['url'] = root_url + link.select('@href').extract()[0][2:]

            item['parent_text'] = parent.select('text()').extract()[0]
            item['parent_url'] = root_url + parent.select('@href').extract()[0][2:]

            # extract grandparent
            grandparent = parent.select("parent::node()/parent::node()/parent::node()/a")
            item['grandparent_text'] = grandparent.select('text()').extract()[0]
            item['grandparent_url'] = root_url + grandparent.select('@href').extract()[0][2:]

            # these are subcategories
            item['level'] = -1

            items.append(item)

        # add subsubcategories
        for link in lower_links:

            # extract immediate parent
            parent = link.select("parent::node()/parent::node()/parent::node()/a")

            item = CategoryItem()

            # add the current page url as a field
            item['page'] = response.url

            item['text'] = link.select('text()').extract()[0]
            # build this into an absolute url by removing ".." prefix and adding domain
            item['url'] = root_url + link.select('@href').extract()[0][2:]

            item['parent_text'] = parent.select('text()').extract()[0]
            item['parent_url'] = root_url + parent.select('@href').extract()[0][2:]

            # extract grandparent
            grandparent = parent.select("parent::node()/parent::node()/parent::node()/a")
            item['grandparent_text'] = grandparent.select('text()').extract()[0]
            item['grandparent_url'] = root_url + grandparent.select('@href').extract()[0][2:]

            # these are subsubcategories
            item['level'] = -2

            items.append(item)

        # add departments
        for link in departments:

            item = CategoryItem()

            # add the current page url as a field
            item['page'] = response.url

            item['text'] = link.select('text()').extract()[0]
            # build this into an absolute url by removing ".." prefix and adding domain
            item['url'] = root_url + link.select('@href').extract()[0][2:]

            # these are departments
            item['level'] = 1

            items.append(item)


        return items


################################
# Run with 
#
# scrapy crawl bestseller
#
################################

# scrape bestsellers list (from all categories)
class BestsellerSpider(BaseSpider):
    name = "bestseller"
    allowed_domains = ["toysrus.com"]

    start_urls = ['http://www.toysrus.com/family/index.jsp?categoryId=11049188&view=all']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select("//div[@class='prodloop_cont']")

        # keep counter to set rank of product
        rank = 0

        for product in products:
            item = ProductItem()
            rank += 1

            item['rank'] = str(rank)
            
            # get product name in bestsellers list page
            name = product.select("a[@class='prodtitle']/text()").extract()
            item['list_name'] = name[0]

            # get relative url of product page and add its root prefix
            root_url = "http://www.toysrus.com"
            url = product.select("a[@class='prodtitle']/@href").extract()
            if url:
                item['url'] = root_url + url[0]

            # if there's no url move on to the next product
            else:
                continue

            # get price ("our price")
            price = product.select("div[@class='prodPrice familyPrices']/span[@class='ourPrice2']/text()").extract()
            if price:
                item['price'] = price[0]

            # get list price
            listprice = product.select("div[@class='prodPrice familyPrices']/span[@class='listPrice2']/text()").extract()
            if listprice:
                item['listprice'] = listprice[0]

            # send the item to be parsed by parseProduct
            request = Request(item['url'], callback = self.parseProduct)
            request.meta['item'] = item

            yield request

    # extract info from product page: product name and page title
    def parseProduct(self, response):
        hxs = HtmlXPathSelector(response)
        title = hxs.select("//title/text()").extract()
        name = hxs.select("//h1/text()").extract()

        item = response.meta['item']

        page_title = title[0]

        # remove site name from page title
        m = re.match("(.*) - Toys ?\"?R\"? ?Us", page_title, re.UNICODE)
        if m:
            page_title = m.group(1).strip()

        item['page_title'] = page_title
        item['product_name'] = name[0]

        return item
