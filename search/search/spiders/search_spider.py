from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import TextResponse
from scrapy.http import Response
from scrapy.exceptions import CloseSpider
from search.items import SearchItem
from scrapy import log

from spiders_utils import Utils
from search.matching_utils import ProcessText

import re
import sys

# from selenium import webdriver
# import time

################################
# Run with 
#
# scrapy crawl search -a product_name="<name>" -a target_site="<site>" [-a output="<option(1/2)>"] [-a threshold=<value>] [a outfile="<filename>"] [-a fast=0]
#      -- or --
# scrapy crawl search -a product_url="<url>" -a target_site="<site>" [-a output="<option(1/2)>"] [-a threshold=<value>] [a outfile="<filename>""] [-a fast=0]
#      -- or --
# scrapy crawl search -a product_urls_file="<filename>" -a target_site="<site>" [-a output="<option(1/2)>"] [-a threshold=value] [a outfile="<filename>"] [-a fast=0]
#      -- or --
# scrapy crawl search -a walmart_ids_file="<filename>" -a target_site="<site>" [-a output="<option(1/2)>"] [-a threshold=value] [a outfile="<filename>"] [-a fast=0]
#
# Usage example:
#
# scrapy crawl search -a product_urls_file="../sample_output/walmart_televisions_urls.txt" -a target_site="bestbuy" -a output=2 -a outfile="search_results_1.4.txt" -a threshold=1.4 -s LOG_ENABLED=1 2>search_log_1.4.out
#
################################


# search for a product in all sites, using their search functions; give product as argument by its name or its page url
class SearchSpider(BaseSpider):

	name = "search"
	allowed_domains = ["amazon.com", "walmart.com", "bloomingdales.com", "overstock.com", "wayfair.com", "bestbuy.com", "toysrus.com",\
					   "bjs.com", "sears.com", "staples.com", "newegg.com"]

	# pass product as argument to constructor - either product name or product URL
	# arguments:
	#				product_name - the product's name, for searching by product name
	#				product_url - the product's page url in the source site, for searching by product URL
	#				product_urls_file - file containing a list of product pages URLs
	#				target_site - the site to search on
	#				output - integer(1/2) option indicating output type (either result URL (1), or result URL and source product URL (2))
	#				threshold - parameter (0-1) for selecting results (the lower the value the more permissive the selection)
	def __init__(self, product_name = None, product_url = None, product_urls_file = None, walmart_ids_file = None, target_site = None, \
		output = 1, threshold = 1.0, outfile = "search_results.txt", outfile2 = "not_matched.txt", fast = 0, use_proxy = False, by_id = False):
		self.product_url = product_url
		self.product_name = product_name
		self.target_site = target_site
		self.output = int(output)
		self.product_urls_file = product_urls_file
		self.walmart_ids_file = walmart_ids_file
		self.threshold = float(threshold)
		self.outfile = outfile
		self.outfile2 = outfile2
		self.fast = fast
		self.use_proxy = use_proxy
		self.by_id = by_id

		# (bloomingales scraper only works with this in the start_urls list)
		#self.start_urls = ["http://www1.bloomingdales.com"]
		self.start_urls = [ "http://www.walmart.com" ]

	def build_search_pages(self, search_query):
		# build list of urls = search pages for each site
		search_pages = {
						"amazon" : "http://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + search_query, \
						"walmart" : "http://www.walmart.com/search/search-ng.do?ic=16_0&Find=Find&search_query=%s&Find=Find&search_constraint=0" % search_query, \
						"bloomingdales" : "http://www1.bloomingdales.com/shop/search?keyword=%s" % search_query, \
						"overstock" : "http://www.overstock.com/search?keywords=%s" % search_query, \
						"wayfair" : "http://www.wayfair.com/keyword.php?keyword=%s" % search_query, \
						# #TODO: check this URL
						"bestbuy" : "http://www.bestbuy.com/site/searchpage.jsp?_dyncharset=ISO-8859-1&_dynSessConf=-26268873911681169&id=pcat17071&type=page&st=%s&sc=Global&cp=1&nrp=15&sp=&qp=&list=n&iht=y&fs=saas&usc=All+Categories&ks=960&saas=saas" % search_query, \
						"toysrus": "http://www.toysrus.com/search/index.jsp?kw=%s" % search_query, \
						# #TODO: check the keywords, they give it as caps
						# "bjs" : "http://www.bjs.com/webapp/wcs/stores/servlet/Search?catalogId=10201&storeId=10201&langId=-1&pageSize=40&currentPage=1&searchKeywords=%s&tASearch=&originalSearchKeywords=lg+life+is+good&x=-1041&y=-75" % search_query, \
						# #TODO: check this url
						# "sears" : "http://www.sears.com/search=%s" % search_query}
						# #TODO: staples?
						}

		return search_pages

	def build_search_query(self, product_name):
		# put + instead of spaces, lowercase all words
		search_query = "+".join(ProcessText.normalize(product_name))
		return search_query


	# parse input and build list of URLs to find matches for, send them to parseURL
	def parse(self, response):


		if not self.target_site:
			sys.stderr.write("You need to specify a target site.\nUsage:" + \
			" scrapy crawl search -a product_urls_file='<filename>' -a target_site='<site>' [-a output='<option(1/2)>'] [-a threshold=value] [a outfile='<filename>'] [-a fast=1]")
			raise CloseSpider("\n" + \
			"You need to specify a target site.\nUsage:" + \
			" scrapy crawl search -a product_urls_file='<filename>' -a target_site='<site>' [-a output='<option(1/2)>'] [-a threshold=value] [a outfile='<filename>'] [-a fast=1]")

		# if we have product names, pass them to parseResults
		if self.product_name:
			search_query = self.build_search_query(product_name)
			search_pages = build_search_pages(search_query)

			request = Request(search_pages[site], callback = self.parseResults)
			request.meta['site'] = self.target_site
			request.meta['origin_name'] = self.product_name
			
			yield request
		
		# if we have product URLs, pass them to parseURL to extract product names (which will pass them to parseResults)
		product_urls = []
		# if we have a single product URL, create a list of URLs containing it
		if self.product_url:
			product_urls.append(self.product_url)

		# if we have a file with a list of URLs, create a list with URLs found there
		if self.product_urls_file:
			f = open(self.product_urls_file, "r")
			for line in f:
				product_urls.append(line.strip())
			f.close()

		for product_url in product_urls:
			# extract site domain
			
			m = re.match("http://www1?\.([^\.]+)\.com.*", product_url)
			origin_site = ""
			if m:
				origin_site = m.group(1)
			else:
				sys.stderr.write('Can\'t extract domain from URL.\n')
			
			request = Request(product_url, callback = self.parseURL)
			request.meta['site'] = origin_site
			if origin_site == 'staples':
				zipcode = "12345"
				request.cookies = {"zipcode": zipcode}
				request.meta['dont_redirect'] = True
			yield request

		# if we have a file with Walmart ids, create a list of the ids there
		if self.walmart_ids_file:
			walmart_ids = []
			f = open(self.walmart_ids_file, "r")
			for line in f:
				if "," in line:
					id_string = line.strip().split(",")[0]
				else:
					id_string = line.strip()
				if re.match("[0-9]+", id_string):
					walmart_ids.append(id_string)
			f.close()		

			self.by_id = True	

			for walmart_id in walmart_ids:
				# create Walmart URLs based on these IDs
				walmart_url = Utils.add_domain(walmart_id, "http://www.walmart.com/ip/")
				request = Request(walmart_url, callback = self.parseURL)
				request.meta['site'] = 'walmart'
				yield request
		

	# parse a product page (given its URL) and extract product's name;
	# create queries to search by (use model name, model number, and combinations of words from model name), then send them to parseResults
	def parseURL(self, response):

		site = response.meta['site']
		hxs = HtmlXPathSelector(response)

		product_model = ""

		if site == 'staples':

			product_name = hxs.select("//h1/text()").extract()[0]

			model_nodes = hxs.select("//p[@class='itemModel']/text()").extract()
			if model_nodes:
				model_node = model_nodes[0]

				model_node = re.sub("\W", " ", model_node, re.UNICODE)
				m = re.match("(.*)Model:(.*)", model_node.encode("utf-8"), re.UNICODE)
				
				
				if m:
					product_model = m.group(2).strip()

		elif site == 'walmart':
			product_name_holder = hxs.select("//h1[@class='productTitle']/text()").extract()
			if product_name_holder:
				product_name = product_name_holder[0].strip()
			else:
				sys.stderr.write("Broken product page link (can't find item title): " + response.url + "\n")
				# return the item as a non-matched item
				item = SearchItem()
				item['site'] = site
				item['origin_url'] = response.url
				# remove unnecessary parameters
				m = re.match("(.*)\?enlargedSearch.*", item['origin_url'])
				if m:
					item['origin_url'] = m.group(1)
				item['origin_id'] = self.extract_walmart_id(item['origin_url'])
				yield item
				return

			#TODO: if it contains 2 words, first could be brand - also add it in similar_names function
			product_model_holder = hxs.select("//td[contains(text(),'Model')]/following-sibling::*/text()").extract()
			if product_model_holder:
				product_model = product_model_holder[0]

		elif site == 'newegg':
			product_name_holder = hxs.select("//span[@itemprop='name']/text()").extract()
			if product_name_holder:
				product_name = product_name_holder[0].strip()
			else:
				sys.stderr.write("Broken product page link (can't find item title): " + response.url + "\n")
				item = SearchItem()
				item['site'] = site
				item['origin_url'] = response.url
				yield item
				return
			product_model_holder = hxs.select("//dt[text()='Model']/following-sibling::*/text()").extract()
			if product_model_holder:
				product_model = product_model_holder[0]

		else:
			raise CloseSpider("Unsupported site: " + site)

		# create search queries and get the results using the target site's search function

		if site == 'staples':
			zipcode = "12345"
			cookies = {"zipcode": zipcode}
		else:
			cookies = {}

		request = None

		#TODO: search by alternative model numbers?

		#TODO: search by model number extracted from product name? Don't I do that implicitly? no, but in combinations

		# 1) Search by model number
		if product_model:
			query1 = self.build_search_query(product_model)
			search_pages1 = self.build_search_pages(query1)
			page1 = search_pages1[self.target_site]
			request1 = Request(page1, callback = self.parseResults, cookies=cookies)


			request1.meta['query'] = query1
			
			request = request1


		# 2) Search by product full name
		query2 = self.build_search_query(product_name)
		search_pages2 = self.build_search_pages(query2)
		page2 = search_pages2[self.target_site]
		request2 = Request(page2, callback = self.parseResults, cookies=cookies)

		request2.meta['query'] = query2

		pending_requests = []

		if not request:
			request = request2
		else:
			pending_requests.append(request2)

		# 3) Search by combinations of words in product's name
		# create queries

		for words in ProcessText.words_combinations(product_name, fast=self.fast):
			query3 = self.build_search_query(" ".join(words))
			search_pages3 = self.build_search_pages(query3)
			page3 = search_pages3[self.target_site]
			request3 = Request(page3, callback = self.parseResults, cookies=cookies)

			request3.meta['query'] = query3


			pending_requests.append(request3)

		request.meta['pending_requests'] = pending_requests
		request.meta['site'] = self.target_site
		# product page from source site
		#TODO: clean this URL? for walmart it added something with ?enlargedsearch=True
		request.meta['origin_url'] = response.url

		request.meta['origin_name'] = product_name
		request.meta['origin_model'] = product_model

		if self.by_id:
			request.meta['origin_id'] = self.extract_walmart_id(response.url)

		yield request


	# parse results page, handle each site separately

	# recieve requests for search pages with queries as:
	# 1) product model (if available)
	# 2) product name
	# 3) parts of product's name

	# accumulate results for each (sending the pending requests and the partial results as metadata),
	# and lastly select the best result by selecting the best match between the original product's name and the result products' names
	def parseResults(self, response):

		hxs = HtmlXPathSelector(response)

		site = response.meta['site']
		origin_name = response.meta['origin_name']
		origin_model = response.meta['origin_model']

		# if this comes from a previous request, get last request's items and add to them the results

		if 'items' in response.meta:
			items = response.meta['items']
		else:
			items = set()

		
		# handle parsing separately for each site

		# amazon
		if (site == 'amazon'):

			# amazon returns partial results as well so we can just search for the entire product name and select from there

			# for Amazon, extract product info from product page, that's the only place you can find the model
			# so send a request to the method that does this, with the same meta info as the request to this method,
			# then send it back here

			# check if we already did this, by checking if we have a key in meta indicating it
			# only proceed if we haven't
			if 'parsed' not in response.meta:
				request = Request(url = response.url, callback = self.parse_results_amazon, meta = response.meta)

				# add to meta url of current page being parsed
				request.meta['redirected_from'] = response.url

				request.meta['items'] = items

				return request

			else:
				del response.meta['parsed']


		# walmart
		if (site == 'walmart'):
			items = []

			results = hxs.select("//div[@class='prodInfo']/div[@class='prodInfoBox']/a[@class='prodLink ListItemLink']")
			for result in results:
				item = SearchItem()
				item['site'] = site
				product_name = result.select(".//text()").extract()[0]
				# append text that is in <span> if any
				span_text = result.select("./span/text()")

				#TODO: use span text differently, as it is more important/relevant (bold) ?
				for text in span_text:
					product_name += " " + text.extract()
				item['product_name'] = product_name
				rel_url = result.select("@href").extract()[0]
				
				root_url = "http://www.walmart.com"
				item['product_url'] = Utils.add_domain(rel_url, root_url)

				if 'origin_url' in response.meta:
					item['origin_url'] = response.meta['origin_url']

				if 'origin_id' in response.meta:
					request.meta['origin_id'] = response.meta['origin_id']
					assert self.by_id
				else:
					assert not self.by_id


				items.add(item)

		# bloomingdales

		#TODO: !! bloomingdales works sporadically
		if (site == 'bloomingdales'):

			results = hxs.select("//div[@class='shortDescription']/a")
			for result in results:
				item = SearchItem()
				item['site'] = site
				item['product_name'] = result.select("text()").extract()[0]
				item['product_url'] = result.select("@href").extract()[0]

				if 'origin_url' in response.meta:
					item['origin_url'] = response.meta['origin_url']

				if 'origin_id' in response.meta:
					request.meta['origin_id'] = response.meta['origin_id']
					assert self.by_id
				else:
					assert not self.by_id


				items.add(item)

		# overstock
		if (site == 'overstock'):

			results = hxs.select("//li[@class='product']/div[@class='product-content']/a[@class='pro-thumb']")
			for result in results:
				item = SearchItem()
				item['site'] = site
				item['product_name'] = result.select("span[@class='pro-name']/text()").extract()[0]
				item['product_url'] = result.select("@href").extract()[0]

				if 'origin_url' in response.meta:
					item['origin_url'] = response.meta['origin_url']

				if 'origin_id' in response.meta:
					request.meta['origin_id'] = response.meta['origin_id']
					assert self.by_id
				else:
					assert not self.by_id


				items.add(item)
		# wayfair
		if (site == 'wayfair'):

			results = hxs.select("//li[@class='productbox']")

			for result in results:
				product_link = result.select(".//a[@class='toplink']")
				item = SearchItem()
				item['site'] = site
				item['product_url'] = product_link.select("@href").extract()[0]
				item['product_name'] = product_link.select("div[@class='prodname']/text()").extract()[0]
				#TODO: add brand?
				#item['brand'] = result.select("div[@class='prodname']/div[@class='prodbrandname emphasis]/text()").extract()[0]

				if 'origin_url' in response.meta:
					item['origin_url'] = response.meta['origin_url']

				if 'origin_id' in response.meta:
					request.meta['origin_id'] = response.meta['origin_id']
					assert self.by_id
				else:
					assert not self.by_id


				items.add(item)
		#TODO: currently only extracting first page - should I extract all pages?
		# bestbuy
		if (site == 'bestbuy'):
			results = hxs.select("//div[@class='hproduct']/div[@class='info-main']/h3/a")

			for result in results:
				item = SearchItem()
				item['site'] = site
				item['product_name'] = result.select("text()").extract()[0].strip()
				item['product_url'] = Utils.clean_url(Utils.add_domain(result.select("@href").extract()[0], "http://www.bestbuy.com"))

				if 'origin_url' in response.meta:
					item['origin_url'] = response.meta['origin_url']

				if 'origin_id' in response.meta:
					request.meta['origin_id'] = response.meta['origin_id']
					assert self.by_id
				else:
					assert not self.by_id


				model_holder = result.select("parent::node()/parent::node()//strong[@itemprop='model']/text()").extract()
				if model_holder:
					item['product_model'] = model_holder[0]

				items.add(item)

		# toysrus
		if (site == 'toysrus'):
			results = hxs.select("//a[@class='prodtitle']")

			for result in results:
				item = SearchItem()
				item['site'] = site
				item['product_name'] = result.select("text()").extract()[0]
				root_url = "http://www.toysrus.com"
				item['product_url'] = root_url + result.select("@href").extract()[0]

				if 'origin_url' in response.meta:
					item['origin_url'] = response.meta['origin_url']

				if 'origin_id' in response.meta:
					request.meta['origin_id'] = response.meta['origin_id']
					assert self.by_id
				else:
					assert not self.by_id


				items.add(item)
		# # bjs
		# if (site == 'bjs'):
		# 	results = hxs.select()

		# sears

		# # staples
		# if (site == 'staples')



		#print stuff
		self.log("PRODUCT: " + response.meta['origin_name'].encode("utf-8") + " MODEL: " + response.meta['origin_model'].encode("utf-8"), level=log.DEBUG)
		self.log( "QUERY: " + response.meta['query'], level=log.DEBUG)
		self.log( "MATCHES: ", level=log.DEBUG)
		for item in items:
			self.log( item['product_name'].encode("utf-8"), level=log.DEBUG)
		self.log( '\n', level=log.DEBUG)


		# if there is a pending request (current request used product model, and pending request is to use product name),
		# continue with that one and send current results to it as metadata
		if 'pending_requests' in response.meta:
			# yield first request in queue and send the other ones as metadata
			pending_requests = response.meta['pending_requests']

			if pending_requests:
				request = pending_requests[0]

				# update pending requests
				request.meta['pending_requests'] = pending_requests[1:]

				request.meta['items'] = items

				request.meta['site'] = response.meta['site']
				# product page from source site
				request.meta['origin_url'] = response.meta['origin_url']
				request.meta['origin_name'] = response.meta['origin_name']
				request.meta['origin_model'] = response.meta['origin_model']

				if 'origin_id' in response.meta:
					request.meta['origin_id'] = response.meta['origin_id']
					assert self.by_id
				else:
					assert not self.by_id

				# used for amazon product URLs
				if 'search_results' in response.meta:
					request.meta['search_results'] = response.meta['search_results']

				return request


			# if there are no more pending requests, use cumulated items to find best match and send it as a result
			else:

				best_match = None

				if items:
					# from all results, select the product whose name is most similar with the original product's name
					best_match = ProcessText.similar(origin_name, origin_model, items, self.threshold)

					# #self.log( "ALL MATCHES: ", level=log.WARNING)					
					# for item in items:
					# 	#print item['product_name'].encode("utf-8")
					# #print '\n'

					self.log( "FINAL: " + str(best_match), level=log.WARNING)

				self.log( "\n----------------------------------------------\n", level=log.WARNING)

				if not best_match:
					# if there are no results but the option was to include original product URL, create an item with just that
					# output item if match not found for either output type
					#if self.output == 2:
					item = SearchItem()
					item['site'] = site
					
					item['origin_url'] = response.meta['origin_url']

					if 'origin_id' in response.meta:
						item['origin_id'] = response.meta['origin_id']
						assert self.by_id
					else:
						assert not self.by_id
					return [item]

				return best_match

		else:
			# output item if match not found for either output type
			#if self.output == 2:
			item = SearchItem()
			item['site'] = site
			
			item['origin_url'] = response.meta['origin_url']

			if 'origin_id' in response.meta:
				item['origin_id'] = response.meta['origin_id']
				assert self.by_id
			else:
				assert not self.by_id

				return [item]


	# parse results page for amazon, extract info for all products returned by search (keep them in "meta")
	def parse_results_amazon(self, response):
		hxs = HtmlXPathSelector(response)

		items = response.meta['items']

		# add product URLs to be parsed to this list
		if 'search_results' not in response.meta:
			product_urls = set()
		else:
			product_urls = response.meta['search_results']

		results = hxs.select("//h3[@class='newaps']/a")
		for result in results:
			product_url = result.select("@href").extract()[0]
				
			# remove the part after "/ref" containing details about the search query
			m = re.match("(.*)/ref=(.*)", product_url)
			if m:
				product_url = m.group(1)

			product_url = Utils.add_domain(product_url, "http://www.amazon.com")

			product_urls.add(product_url)

		# extract product info from product pages (send request to parse first URL in list)
		# add as meta all that was received as meta, will pass it on to parseResults function in the end
		# also send as meta the entire results list (the product pages URLs), will receive callback when they have all been parsed

		# send the request further to parse product pages only if we gathered all the product URLs from all the queries 
		# (there are no more pending requests)
		# otherwise send them back to parseResults and wait for the next query, save all product URLs in search_results
		# this way we avoid duplicates
		if product_urls and ('pending_requests' not in response.meta or not response.meta['pending_requests']):
			request = Request(product_urls.pop(), callback = self.parse_product_amazon, meta = response.meta)
			request.meta['items'] = items

			# this will be the new product_urls list with the first item popped
			request.meta['search_results'] = product_urls

			return request

		# if there were no results, the request will never get back to parseResults
		# so send it from here so it can parse the next queries
		else:
			request = Request(response.meta['redirected_from'], callback = self.parseResults, meta = response.meta)
			# remove unnecessary keys
			del request.meta['redirected_from']

			# add variable indicating results have been parsed
			request.meta['parsed'] = True

			# keep the search results in this variable until no more queries are added and we are ready to pass it to parse_product_amazon
			request.meta['search_results'] = product_urls

			return request

	# extract product info from a product page for amazon
	# keep product pages left to parse in 'search_results' meta key, send back to parse_results_amazon when done with all
	def parse_product_amazon(self, response):

		hxs = HtmlXPathSelector(response)
		items = response.meta['items']

		site = response.meta['site']
		origin_url = response.meta['origin_url']

		item = SearchItem()
		item['product_url'] = response.url
		item['site'] = site
		item['origin_url'] = origin_url

		if 'origin_id' in response.meta:
			item['origin_id'] = response.meta['origin_id']
			assert self.by_id
		else:
			assert not self.by_id


		# extract product name
		#TODO: id='title' doesn't work for all, should I use a 'contains' or something?
		# extract titles that are not empty (ignoring whitespace)
		# eliminate "Amazon Prime Free Trial"

		#TODO: to test this
		#product_name = filter(lambda x: not x.startswith("Amazon Prime"), hxs.select("//div[@id='title_feature_div']//h1//text()[normalize-space()!='']").extract())
		product_name = filter(lambda x: not x.startswith("Amazon Prime"), hxs.select("//h1//text()[normalize-space()!='']").extract())
		if not product_name:
			self.log("Error: No product name: " + str(response.url), level=log.INFO)

		else:
			item['product_name'] = product_name[0].strip()

			# extract product model number
			model_number_holder = hxs.select("//tr[@class='item-model-number']/td[@class='value']/text()").extract()
			if model_number_holder:
				item['product_model'] = model_number_holder[0]

			brand_holder = hxs.select("//div[@id='brandByline_feature_div']//a/text() | //a[@id='brand']/text()").extract()
			if brand_holder:
				item['product_brand'] = brand_holder[0]
			else:
				pass
				#sys.stderr.write("Didn't find product brand: " + response.url + "\n")

			# add result to items
			items.add(item)

		# if there are any more results to be parsed, send a request back to this method with the next product to be parsed
		product_urls = response.meta['search_results']

		if product_urls:
			request = Request(product_urls.pop(), callback = self.parse_product_amazon, meta = response.meta)
			request.meta['items'] = items
			# eliminate next product from pending list (this will be the new list with the first item popped)
			request.meta['search_results'] = product_urls

			return request
		else:
			# otherwise, we are done, send a request back to parseResults
			# add as meta all that was received as meta, add newly added items
			request = Request(response.meta['redirected_from'], callback = self.parseResults, meta = response.meta)
			# remove unnecessary keys
			del request.meta['redirected_from']
			del request.meta['search_results']
			request.meta['items'] = items

			# add variable indicating results have been parsed
			request.meta['parsed'] = True

			return request

	def extract_walmart_id(self, url):
		m = re.match(".*/ip/([0-9]+)", url)
		if m:
			return m.group(1)