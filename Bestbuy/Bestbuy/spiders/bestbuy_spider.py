from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Bestbuy.items import BestbuyItem
import sys

################################
# Run with 
#
# scrapy crawl bestbuy
#
################################


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
            item = BestbuyItem()

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
            item = BestbuyItem()

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
