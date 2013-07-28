from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from search.items import SearchItem
import re

class SearchSpider(BaseSpider):

	name = "search"

	# pass product as argument to constructor - either product name or product url
	def __init__(self, product_name = None, product_url = None):
		if product_name:
			self.search_query = "+".join(product_name.split())
		if product_url:
			self.search_query = self.get_name(product_url)
		self.start_urls = ["http://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + search_query]

	def parse(self, response):
		hxs = HtmlXPathSelector(response)
		product = hxs.select("//div[@id='result_0']/h3/a/span/text()").extract()[0]
		item = SearchItem()
		item['name'] = product

		yield item


	# get the name of a product from the URL of its page
	# the URL can be from various sites
	def get_name(product_url):

		# extract domain
		#TODO: under construction



