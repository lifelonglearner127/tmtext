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
		self.threshold = 0.5
		self.fast = 0



	# # parse results page, extract info for all products returned by search (keep them in "meta")
	# def parseResults(self, response):
	# 	if site == 'sony':
	# 		yield self.parseResults_sony(response)


	# parse results page, extract info for all products returned by search (keep them in "meta")
	def parseResults(self, response):
		hxs = HtmlXPathSelector(response)

		if 'items' in response.meta:
			items = response.meta['items']
		else:
			items = set()

		# # add product URLs to be parsed to this list
		# if 'search_results' not in response.meta:
		# 	product_urls = set()
		# else:
		# 	product_urls = response.meta['search_results']

		results = hxs.select("//h2[@class='ws-product-title fn']//text()")

		# if we were redirected to a product page, it means it's an exact match so stop search here
		if results:
			response.meta['pending_requests'] = []
			for result in results:
				# we are already on the product page
				#product_urls.add(product_url)
				item = SearchItem()
				item['product_url'] = response.url
				item['product_name'] = result.extract()
				# hard code brand as 'sony'
				item['product_brand'] = 'sony'
				item['origin_url'] = response.meta['origin_url']
				items.add(item)

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


		# extract product info from product pages (send request to parse first URL in list)
		# add as meta all that was received as meta, will pass it on to reduceResults function in the end
		# also send as meta the entire results list (the product pages URLs), will receive callback when they have all been parsed

		# send the request further to parse product pages only if we gathered all the product URLs from all the queries 
		# (there are no more pending requests)
		# otherwise send them back to parseResults and wait for the next query, save all product URLs in search_results
		# this way we avoid duplicates
		# if product_urls and ('pending_requests' not in response.meta or not response.meta['pending_requests']):
		# 	request = Request(product_urls.pop(), callback = self.parse_product_sony, meta = response.meta)
		# 	request.meta['items'] = items

		# 	# this will be the new product_urls list with the first item popped
		# 	request.meta['search_results'] = product_urls

		# 	return request

		# # if there were no results, the request will never get back to reduceResults
		# # so send it from here so it can parse the next queries
		# # add to the response the URLs of the products to crawl we have so far, items (handles case when it was not created yet)
		# # and field 'parsed' to indicate that the call was received from this method (was not the initial one)
		# else:
		response.meta['items'] = items
		response.meta['parsed'] = True
		#response.meta['search_results'] = product_urls
		# only send the response we have as an argument, no need to make a new request
		return self.reduceResults(response)

	# # extract product info from a product page for sony
	# # keep product pages left to parse in 'search_results' meta key, send back to parseResults_new when done with all
	# def parse_product_sony(self, response):

	# 	hxs = HtmlXPathSelector(response)

	# 	items = response.meta['items']

	# 	site = response.meta['site']
	# 	origin_url = response.meta['origin_url']

	# 	item = SearchItem()
	# 	item['product_url'] = response.url
	# 	item['site'] = site
	# 	item['origin_url'] = origin_url

	# 	if 'origin_id' in response.meta:
	# 		item['origin_id'] = response.meta['origin_id']
	# 		assert self.by_id
	# 	else:
	# 		assert not self.by_id


		
	# 	product_name = hxs.select("//h2[@class='ws-product-title fn//text()")
	# 	if not product_name:
	# 		self.log("Error: No product name: " + str(response.url), level=log.INFO)

	# 	else:
	# 		item['product_name'] = product_name[0].strip()

	# 	# 	# extract product model number
	# 	# 	model_number_holder = 
	# 	# 	if model_number_holder:
	# 	# 		item['product_model'] = model_number_holder[0]

	# 	# hardcode brand as sony, no need to extract it
	# 	item['product_brand'] = 'sony'

	# 	# add result to items
	# 	items.add(item)

	# 	# if there are any more results to be parsed, send a request back to this method with the next product to be parsed
	# 	product_urls = response.meta['search_results']

	# 	if product_urls:
	# 		request = Request(product_urls.pop(), callback = self.parse_product_amazon, meta = response.meta)
	# 		request.meta['items'] = items
	# 		# eliminate next product from pending list (this will be the new list with the first item popped)
	# 		request.meta['search_results'] = product_urls

	# 		return request
	# 	else:
	# 		# otherwise, we are done, send a the response back to reduceResults (no need to make a new request)
	# 		# add as meta newly added items
	# 		# also add 'parsed' field to indicate that the parsing of all products was completed and they cand be further used
	# 		# (actually that the call was made from this method and was not the initial one, so it has to move on to the next request)

	# 		response.meta['parsed'] = True
	# 		response.meta['items'] = items

	# 		return self.reduceResults(response)