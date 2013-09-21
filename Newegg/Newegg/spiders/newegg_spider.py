from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Newegg.items import CategoryItem
from Newegg.items import ProductItem
from scrapy.http import Request
import re
import sys
import datetime

from spiders_utils import Utils

################################
# Run with 
#
# scrapy crawl newegg
#
################################

# crawl sitemap and extract products and categories
class NeweggSpider(BaseSpider):
    name = "newegg"
    allowed_domains = ["newegg.com"]
    start_urls = ["http://www.newegg.com"]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        category_links = hxs.select("//div[@class='itmNav']//a")

        # unique ids for departments
        department_id = 0

        for category_link in category_links:

            item = CategoryItem()
            item['text'] = category_link.select("text()").extract()[0]
            item['url'] = category_link.select("@href").extract()[0]
            # mark as department
            item['level'] = 1

            # mark it as its own department, will be passed on to its subcategories
            item['department_text'] = item['text']
            item['department_url'] = item['url']
            item['department_id'] = department_id

            #items.append(item)
            yield Request(url = item['url'], callback = self.parseCategory, meta = {"item" : item, \
                'department_text' : item['department_text'], 'department_url' : item['department_url'], 'department_id' : item['department_id']})

        #return items

    def parseCategory(self, response):
        hxs = HtmlXPathSelector(response)

        item = response.meta['item']

        #TODO
        # extract number of products if available


        #TODO
        # extract description if available

        yield item

        parent = item

        #TODO
        # extract and parse subcategories
        subcats = hxs.select("//dl[@class='categoryList primaryNav']/dd/a")
        for subcat in subcats:
            item = CategoryItem()
            
            item['text'] = subcat.select("text()").extract()[0].strip()
            item['url'] = subcat.select("@href").extract()[0]

            item['parent_text'] = parent['text']
            item['parent_url'] = parent['url']
            item['level'] = parent['level'] - 1
            item['department_text'] = response.meta['department_text']
            item['department_url'] = response.meta['department_url']
            item['department_id'] = response.meta['department_id']

            yield Request(url = item['url'], callback = self.parseCategory, meta = {"item" : item, \
                "department_text" : response.meta['department_text'], "department_url" : response.meta['department_url'], "department_id" : response.meta['department_id']})
