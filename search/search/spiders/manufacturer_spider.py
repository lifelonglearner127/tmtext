from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import TextResponse
from scrapy.http import Response
from scrapy.exceptions import CloseSpider
from search.items import SearchItem
from search.spiders.search_spider import SearchSpider
from scrapy import log

from spiders_utils import Utils
from search.matching_utils import ProcessText

import re
import sys


class ManufacturerSpider(SearchSpider):

	name = "manufacturer"

	# arbitrary start url
	start_urls = ['http://www.sony.com']

	# initialize fields specific to this derived spider
	def init_sub(self):
		#TODO: find a better way for this
		self.threshold = 0.8
		self.fast = 0

	# parse results page, extract info for all products returned by search (keep them in "meta")
	def parseResults(self, response):
		hxs = HtmlXPathSelector(response)

		if 'items' in response.meta:
			items = response.meta['items']
		else:
			items = set()

		#TODO: implement support for multiple results pages?
		results = hxs.select("//h2[@class='ws-product-title fn']//text()")

		# if we were redirected to a product page, it means it's an exact match so stop search here
		if results:
			# temporarily set threshold to lower value
			oldthreshold = self.threshold
			self.threshold = 0.2
			response.meta['pending_requests'] = []
			for result in results:
				# we are already on the product page
				item = SearchItem()
				item['product_url'] = response.url
				item['product_name'] = result.extract()
				# hard code brand as 'sony'
				item['product_brand'] = 'sony'
				item['origin_url'] = response.meta['origin_url']

				item['product_images'] = len(hxs.select("//a[@class='ws-alternate-views-list-link']/img").extract())
				#TODO: to check
				item['product_videos'] = len(hxs.select("//li[@class='ws-video']//img").extract())

				items.add(item)

			self.threshold = oldthreshold

		else:
			# try to see if this is a results page then
			results = hxs.select("//h5[@class='ws-product-title fn']")
			for result in results:
				item = SearchItem()
				item['product_url'] = result.select("parent::node()//@href").extract()[0]
				item['product_name'] = result.select("text()").extract()[0]
				item['product_brand'] = 'sony'
				item['origin_url'] = response.meta['origin_url']
				items.add(item)


		response.meta['items'] = items
		response.meta['parsed'] = True
		
		return self.reduceResults(response)

