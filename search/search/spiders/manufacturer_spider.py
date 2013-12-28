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

THRESHOLD_LOW = 0.2

class ManufacturerSpider(SearchSpider):

	name = "manufacturer"

	# arbitrary start url
	start_urls = ['http://www.sony.com']

	threshold = 0.8

	# initialize fields specific to this derived spider
	def init_sub(self):
		#TODO: find a better way for this
		#self.threshold = 0.8
		self.fast = 0
		#self.output = 2

		self.sites_to_parse_methods = {"sony" : self.parseResults_sony, \
										"samsung" : self.parseResults_samsung}

	# pass to site-specific parseResults method
	def parseResults(self, response):
		target_site = response.meta['target_site']
		if target_site in self.sites_to_parse_methods:
			return self.sites_to_parse_methods[target_site](response)

	# parse samsung results page
	def parseResults_samsung(self, response):
		hxs = HtmlXPathSelector(response)

		if 'items' in response.meta:
			items = response.meta['items']
		else:
			items = set()

		# add product URLs to be parsed to this list
		if 'search_results' not in response.meta:
			product_urls = set()
		else:
			product_urls = response.meta['search_results']


		#TODO: implement support for multiple results pages?
		results = hxs.select("//ul[@class='product-info']")

		# if we find any results to this it means we are already on a product page
		if results:
			product_urls.add(response.url)
			# it also means it's an exact match, so stop search here
			response.meta['pending_requests'] = []
			# # also temporarily lower threshold
			# self.threshold = 0.2

		else:
			# # try to see if this is a results page then
			# results = 
			# for result in results:
			# 	product_url = result.select("parent::node()//@href").extract()[0]
			# 	product_urls.add(product_url)
			pass

		if product_urls and ('pending_requests' not in response.meta or not response.meta['pending_requests']):
			request = Request(product_urls.pop(), callback = self.parse_product_samsung, meta = response.meta)
			request.meta['items'] = items

			# this will be the new product_urls list with the first item popped
			request.meta['search_results'] = product_urls

			return request

		# if there were no results, the request will never get back to reduceResults
		else:
			response.meta['items'] = items
			response.meta['parsed'] = True
			response.meta['search_results'] = product_urls
			# only send the response we have as an argument, no need to make a new request
			return self.reduceResults(response)

		

	# parse sony results page, extract info for all products returned by search (keep them in "meta")
	def parseResults_sony(self, response):
		hxs = HtmlXPathSelector(response)

		if 'items' in response.meta:
			items = response.meta['items']
		else:
			items = set()

		# add product URLs to be parsed to this list
		if 'search_results' not in response.meta:
			product_urls = set()
		else:
			product_urls = response.meta['search_results']


		#TODO: implement support for multiple results pages?
		results = hxs.select("//h2[@class='ws-product-title fn']//text()")

		# if we find any results to this it means we are already on a product page
		if results:
			#TODO: only works when queries with product model, but in original form, that is, with caps
			product_urls.add(response.url)
			# it also means it's an exact match, so stop search here
			response.meta['pending_requests'] = []
			# also set threshold to lower value
			response.meta['threshold'] = THRESHOLD_LOW

		else:
			#TODO
			# try to see if this is a results page then
			results = hxs.select("//h5[@class='ws-product-title fn']")
			for result in results:
				product_url = result.select("parent::node()//@href").extract()[0]
				product_urls.add(product_url)

		if product_urls and ('pending_requests' not in response.meta or not response.meta['pending_requests']):
			request = Request(product_urls.pop(), callback = self.parse_product_sony, meta = response.meta)
			request.meta['items'] = items

			# this will be the new product_urls list with the first item popped
			request.meta['search_results'] = product_urls

			return request

		# if there were no results, the request will never get back to reduceResults
		else:
			response.meta['items'] = items
			response.meta['parsed'] = True
			response.meta['search_results'] = product_urls
			# only send the response we have as an argument, no need to make a new request
			return self.reduceResults(response)


		# parse product page on samsung.com
	def parse_product_samsung(self, response):

		hxs = HtmlXPathSelector(response)

		items = response.meta['items']

		#site = response.meta['origin_site']
		origin_url = response.meta['origin_url']

		# create item
		item = SearchItem()
		item['product_url'] = response.url
		item['origin_url'] = origin_url
		# hardcode brand to sony
		item['product_brand'] = 'samsung'

		# extract product name, brand, model, etc; add to items
		product_info = hxs.select("//ul[@class='product-info']")
		product_name = product_info.select("/meta[@itemprop='name']/@content")
		if not product_name:
			self.log("Error: No product name: " + str(response.url), level=log.INFO)
		else:
			item['product_name'] = product_name.extract()[0]
		product_model = product_info.select("/meta[@itemprop='model']/@content")
		if product_model:
			item['product_model'] = product_model.extract()[0]

		#TODO
		# item['product_images'] = 
		# #TODO: to check
		# item['product_videos'] = l

		items.add(item)


		# if there are any more results to be parsed, send a request back to this method with the next product to be parsed
		product_urls = response.meta['search_results']

		if product_urls:
			request = Request(product_urls.pop(), callback = self.parse_product_samsung, meta = response.meta)
			request.meta['items'] = items
			# eliminate next product from pending list (this will be the new list with the first item popped)
			request.meta['search_results'] = product_urls

			return request
		else:
			# otherwise, we are done, send a the response back to reduceResults (no need to make a new request)

			response.meta['parsed'] = True
			response.meta['items'] = items

			return self.reduceResults(response)


	# parse product page on sony.com
	def parse_product_sony(self, response):
		hxs = HtmlXPathSelector(response)

		items = response.meta['items']

		#site = response.meta['origin_site']
		origin_url = response.meta['origin_url']

		# create item
		item = SearchItem()
		item['product_url'] = response.url
		item['origin_url'] = origin_url
		# hardcode brand to sony
		item['product_brand'] = 'sony'

		# extract product name, brand, model, etc; add to items
		product_name = hxs.select("//h2[@class='ws-product-title fn']//text()")
		if not product_name:
			self.log("Error: No product name: " + str(response.url), level=log.INFO)
		else:
			item['product_name'] = product_name.extract()[0]
		product_model = hxs.select("//span[@class='ws-product-item-number-value item-number']/text()")
		if product_model:
			item['product_model'] = product_model.extract()[0]

		item['product_images'] = len(hxs.select("//a[@class='ws-alternate-views-list-link']/img").extract())
		item['product_videos'] = len(hxs.select("//li[@class='ws-video']//img").extract())

		items.add(item)


		# if there are any more results to be parsed, send a request back to this method with the next product to be parsed
		product_urls = response.meta['search_results']

		if product_urls:
			request = Request(product_urls.pop(), callback = self.parse_product_sony, meta = response.meta)
			request.meta['items'] = items
			# eliminate next product from pending list (this will be the new list with the first item popped)
			request.meta['search_results'] = product_urls

			return request
		else:
			# otherwise, we are done, send a the response back to reduceResults (no need to make a new request)

			response.meta['parsed'] = True
			response.meta['items'] = items

			return self.reduceResults(response)

