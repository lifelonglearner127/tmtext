from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Sherwin.items import CategoryItem
from Sherwin.items import ProductItem
from scrapy.http import Request
from scrapy.http import Response
import re
import sys

from spiders_utils import Utils

################################
# Run with 
#
# scrapy crawl sherwin
#
################################

# crawls sitemap and extracts department and categories names and urls (as well as other info)
class SherwinSpider(BaseSpider):
    name = "sherwin"
    allowed_domains = ["sherwin-williams.com"]
    start_urls = [
        "https://www.sherwin-williams.com/sitemap/",
    ]

    base_url = "http://www.sherwin-williams.com"

    def parse(self, response):
    	hxs = HtmlXPathSelector(response)

    	# extract departments
    	departments = hxs.select("//h2")
    	department_id = 0
    	for department in departments:
    		item = CategoryItem()
    		department_text = department.select("text()").extract()[0]
    		item['department_text'] = department_text

    		#TODO: add department_url, from sherwin-williams.com ...? get department list from there and match with departments from here by seeing if names match

    		item['department_id'] = department_id

    		item['text'] = department_text

    		#TODO
    		#item['url'] = 
    		item['level'] = 1

    		# return item
    		yield item

    		# get categories in department
    		#TODO: this is wrong, gets categories for all departments below this point
    		categories = department.select("following-sibling::ul[1]/li")
    		for category in categories:
    			item = CategoryItem()
    			#TODO: special if 'Services'? or Specifications, or Ads...
    			category_text = category.select("a/text()").extract()[0]
    			category_url =  Utils.add_domain(category.select("a/@href").extract()[0], self.base_url)
    			item['text'] = category_text
    			item['url'] = category_url

    			item['department_id'] = department_id
    			item['department_text'] = department_text
    			#TODO
    			# item['department_url'] = 

    			item['parent_text'] = department_text
    			#TODO
    			# item['parent_url'] = 

    			item['level'] = 0

    			yield item
    			#TODO: or yield request? to add description and products count

    			# get subcategories in category
    			subcategories = category.select("ul/li")
    			for subcategory in subcategories:
    				item = CategoryItem()

    				item['text'] = subcategory.select("a/text()").extract()[0]
    				item['url'] = Utils.add_domain(subcategory.select("a/@href").extract()[0], self.base_url)

    				item['department_id'] = department_id
    				item['department_text'] = department_text
    				#TODO
    				# item['department_url'] = 

    				item['parent_text'] = category_text
    				item['parent_url'] = category_url

    				item['level'] = -1

    				#TODO: yield request instead
    				yield item

    		department_id += 1