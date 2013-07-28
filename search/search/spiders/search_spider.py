from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from search.items import SearchItem

class SearchSpider(BaseSpider):

	name = "search"

	def __init__(self, product_name):
		search_query = "+".join(product_name.split())
		self.start_urls = ["http://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + search_query]

	def parse(self, response):
		hxs = HtmlXPathSelector(response)
		product = hxs.select("//div[@id='result_0']/h3/a/span/text()").extract()[0]
		item = SearchItem()
		item['name'] = product

		yield item


