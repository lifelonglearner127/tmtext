from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import TextResponse
from scrapy.http import Response
from scrapy.exceptions import CloseSpider
from search.items import SearchItem
from scrapy import log

from spiders_utils import Utils
#import urllib
import re
import itertools

import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet

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
#
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
	def __init__(self, product_name = None, product_url = None, product_urls_file = None, target_site = None, output = 1, threshold = 1.45, outfile = "search_results.txt", fast = 1):
		self.product_url = product_url
		self.product_name = product_name
		self.target_site = target_site
		self.output = int(output)
		self.product_urls_file = product_urls_file
		self.threshold = float(threshold)
		self.outfile = outfile
		self.fast = fast

		# (bloomingales scraper only works with this in the start_urls list)
		self.start_urls = ["http://www1.bloomingdales.com"]

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
				return
			product_model_holder = hxs.select("//td[contains(text(),'Model')]/following-sibling::*/text()").extract()
			if product_model_holder:
				product_model = product_model_holder[0]

		elif site == 'newegg':
			product_name_holder = hxs.select("//span[@itemprop='name']/text()").extract()
			if product_name_holder:
				product_name = product_name_holder[0].strip()
			else:
				sys.stderr.write("Broken product page link (can't find item title): " + response.url + "\n")
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

		#TODO: search by model number extracted from product name?

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
		#TODO: to make this faster, maybe gather all product urls from all queries results into a set, then parse them
		#there are probably many duplicates
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

			#product = hxs.select("//div[@id='result_0']/h3/a/span/text()").extract()[0]
			#TODO: refine this. get divs with id of the form result_<number>. not all of them have h3's (but this will exclude partial results?)
			# results = hxs.select("//h3[@class='newaps']/a")
			# for result in results:
			# 	item = SearchItem()
			# 	item['site'] = site

			# 	#TODO: some of these product names are truncated ("..."); even though less relevant ones (special offers or so)
			# this problem is solved by the direct extraction from the product page
			# 	item['product_name'] = result.select("span/text()").extract()[0]
			# 	product_url = result.select("@href").extract()[0]
				
			# 	# remove the part after "/ref" containing details about the search query
			# 	m = re.match("(.*)/ref=(.*)", product_url)
			# 	if m:
			# 		product_url = m.group(1)

			# 	item['product_url'] = Utils.add_domain(product_url, "http://www.amazon.com")

			# 	# extract product model
			# 	product_model = self.extract_model_amazon(str(item['product_url']))
			# 	if product_model:
			# 		item['product_model'] = product_model

			# 	if 'origin_url' in response.meta:
			# 		item['origin_url'] = response.meta['origin_url']

			# 	items.add(item)

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
					if self.output == 2:
						item = SearchItem()
						item['site'] = site
						#if 'origin_url' in response.meta:
						item['origin_url'] = response.meta['origin_url']
						return [item]

				return best_match

		else:
			
			if self.output == 2:
				item = SearchItem()
				item['site'] = site
				
				item['origin_url'] = response.meta['origin_url']


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

			brand_holder = hxs.select("//div[@id='brandByline_feature_div']//a/text()").extract()
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


		
# process text in product names, compute similarity between products
class ProcessText():
	# weight values
	MODEL_MATCH_WEIGHT = 10
	ALT_MODEL_MATCH_WEIGHT = 9
	BRAND_MATCH_WEIGHT = 6
	INCHES_MATCH_WEIGHT = 3
	NONWORD_MATCH_WEIGHT = 2
	DICTIONARY_WORD_MATCH_WEIGHT = 1

	#TODO: different weight if alt models match, not literal models?

	# exception brands - are brands names but are also found in the dictionary
	brand_exceptions = ['philips', 'sharp', 'sceptre', 'westinghouse', 'element', 'curtis', 'emerson']

	# normalize text to list of lowercase words (no punctuation except for inches sign (") or /)
	@staticmethod
	def normalize(orig_text):
		text = orig_text
		# other preprocessing: -Inch = " - fitting for staples->amazon search
		# TODO: suitable for all sites?
		text = re.sub("[- ][iI]nch", "\"", text)
		text = re.sub("(?<=[0-9])[iI][nN](?!=c)","\"", text)

		#! including ' as an exception keeps things like women's a single word. also doesn't find it as a word in wordnet -> too high a priority
		# excluding it leads to women's->women (s is a stopword)

		#TODO: what happens to non word characters like )? eg (Black)
		# replace 1/2 by .5 -> suitable for all sites?
		text = re.sub("[- ]1/2", ".5", text)
		# also split by "/" after replacing "1/2"
		text = re.sub("([^\w\"])|(u')", " ", text)
		stopset = set(stopwords.words('english'))#["and", "the", "&", "for", "of", "on", "as", "to", "in"]
		
		#TODO: maybe keep numbers like "50 1/2" together too somehow (originally they're "50-1/2")
		#TODO: maybe handle numbers separately. sometimes we want / to split (in words), and . not to (in numbers)
		# define a better regex above, or here at splitting
		tokens = text.split()
		clean = [token.lower() for token in tokens if token.lower() not in stopset and len(token) > 1]

		# TODO:
		# # add versions of the queries with different spelling
		# first add all the tokens but with some words replaced (version of original normalized)
		# extra = []
		# for word_comb in words:
		# 	for i in range(len(word_comb)):
		# 		# " -> -inch
		# 		m = re.match("", string, flags)
		#		# .5 ->  1/2


		return clean

	# get list of alternative model numbers

	# without the last letters, so as to match more possibilities
	# (there is are cases like this, for example un32eh5300f)

	# or split by dashes

	#TODO: add maybe multiple alternate model nrs - split by dash
	@staticmethod
	def alt_modelnrs(word):
		alt_models = []
		if not word:
			return []

		# remove last part of word
		m = re.match("(.*[0-9]+)([a-zA-Z\- ]+)", word)
		if m and float(len(m.group(1)))/len(m.group(2))>1:
			new_word = m.group(1)
			if len(new_word) > 2:
				alt_models.append(new_word)

		# split word by - or /
		if "-"  or "/" in word:
			sub_models = re.split(r"[-/]",word)
			for sub_model in sub_models:
				if ProcessText.is_model_number(sub_model.strip()):
					alt_models.append(sub_model.strip())

		return alt_models

	# normalize model numbers (remove dashes, lowercase)
	@staticmethod
	def normalize_modelnr(modelnr):
		return re.sub("[\- ]", "", modelnr.lower())

	# extract index of (first found) model number in list of words if any
	# return -1 if none found
	@staticmethod
	def extract_model_nr_index(words):
		for i in range(len(words)):
			if ProcessText.is_model_number(words[i]):
				return i
		return -1

	# check if model numbers of 2 products match
	# return 1 if they match, 2 if they match including alternative model numbers, and 0 if they don't
	@staticmethod
	def models_match(name1, name2, model1, model2):
		# add to the score if their model numbers match
		# check if the product models are the same, or if they are included in the other product's name
		# for the original product models, as well as for the alternative ones, and alternative product names

		alt_product_models = ProcessText.alt_modelnrs(model1)
		alt_product2_models = ProcessText.alt_modelnrs(model2)

		# get product models extracted from product name, if found
		model_index1 = ProcessText.extract_model_nr_index(name1)
		if model_index1 >= 0:
			product_model_fromname = name1[model_index1]
			alt_product_models_fromname = ProcessText.alt_modelnrs(product_model_fromname)
		else:
			product_model_fromname = None
			alt_product_models_fromname = []

		model_index2 = ProcessText.extract_model_nr_index(name2)
		if model_index2 >= 0:
			product2_model_fromname = name2[model_index2]
			alt_product2_models_fromname = ProcessText.alt_modelnrs(product2_model_fromname)
		else:
			product2_model_fromname = None
			alt_product2_models_fromname = []

		model_matched = 0
		# to see if models match, build 2 lists with each of the products' possible models, and check their intersection
		# actual models
		models1 = filter(None, [model1, product_model_fromname])
		models2 = filter(None, [model2, product2_model_fromname])

		# including alternate models
		alt_models1 = filter(None, [model1, product_model_fromname] + alt_product_models + alt_product_models_fromname)
		alt_models2 = filter(None, [model2, product2_model_fromname] + alt_product2_models + alt_product2_models_fromname)

		# normalize all product models
		models1 = map(lambda x: ProcessText.normalize_modelnr(x), models1)
		models2 = map(lambda x: ProcessText.normalize_modelnr(x), models2)
		alt_models1 = map(lambda x: ProcessText.normalize_modelnr(x), alt_models1)
		alt_models2 = map(lambda x: ProcessText.normalize_modelnr(x), alt_models2)

		# if models match
		if set(alt_models1).intersection(set(alt_models2)):
			# if actual models match (excluding alternate models)
			if set(models1).intersection(set(models2)):
				model_matched = 1
				log.msg("MATCHED: " + str(models1) + str(models2) + "\n", level=log.INFO)
			# if alternate models match
			else:
				model_matched = 2
				log.msg("ALT MATCHED: " + str(alt_models1) + str(alt_models2) + "\n", level=log.INFO)
		# if models not matched
		else:
			log.msg("NOT MATCHED: " + str(alt_models1) + str(alt_models2) + "\n", level=log.INFO)
		
		return model_matched


	# create combinations of comb_length words from original text (after normalization and tokenization and filtering out dictionary words)
	# return a list of all combinations
	@staticmethod
	def words_combinations(orig_text, comb_length = 3, fast = False):
		norm_text = ProcessText.normalize(orig_text)

		# exceptions to include even if they appear in wordnet
		exceptions = ['nt']

		# only keep non dictionary words
		# also keep Brands that are exceptions
		norm_text = [word for word in norm_text if (not wordnet.synsets(word) or word in exceptions or word in ProcessText.brand_exceptions) and len(word) > 1]

		# use fast option: use shorter length of combinations
		if fast:
			comb_length=2
		combs = itertools.combinations(range(len(norm_text)), comb_length)

		# use fast option: only select combinations that include first or second word
		if fast:
			#words=[map(lambda c: norm_text[c], x) for x in filter(lambda x: 0 in x or 1 in x, list(combs))]
			words=[map(lambda c: norm_text[c], x) for x in filter(lambda x: 0 in x or 1 in x, list(combs))]
		else:
			words=[map(lambda c: norm_text[c], x) for x in list(combs)]

		return words

	# return most similar product from a list to a target product (by their names)
	# if none is similar enough, return None
	# arguments:
	#			product_name - name of target product
	#			product_model - model number of target product, if available (as extracted from somewhere on the page other than its name)
	#			products2 - list of product items for products to search through
	#			param - threshold for accepting a product name as similar or not (float between 0-1)
	
	@staticmethod
	def similar(product_name, product_model, products2, param):
		result = None
		products_found = []
		for product2 in products2:

			words1 = ProcessText.normalize(product_name)
			words2 = ProcessText.normalize(product2['product_name'])
			if 'product_model' in product2:
				product2_model = product2['product_model']
			else:
				product2_model = None

			#TODO: currently only considering brand for target products
			# and only available for Amazon
			if 'product_brand' in product2:
				product2_brand = product2['product_brand']
			else:
				product2_brand = None

			# check if product names match (a similarity score)
			(score, threshold, brand_matched) = ProcessText.similar_names(words1, words2, product2_brand, param)
			
			# check if product models match (either from a "Model" field or extracted from their name)
			model_matched = ProcessText.models_match(words1, words2, product_model, product2_model)
			if model_matched:
				# if actual models matched
				if (model_matched == 1):
					score += ProcessText.MODEL_MATCH_WEIGHT
				# if alternate models matched
				elif (model_matched == 2):
					score += ProcessText.ALT_MODEL_MATCH_WEIGHT
			
			log.msg("\nPRODUCT: " + unicode(product_name) + " MODEL: " + unicode(product_model) + \
				"\nPRODUCT2: " + unicode(product2['product_name']) + " BRAND2: " + unicode(product2_brand) + " MODEL2: " + unicode(product2_model) + \
				"\nSCORE: " + str(score) + " THRESHOLD: " + str(threshold) + "\n", level=log.WARNING)

			if score >= threshold:
				# append product along with score and a third variable:
				# variable used for settling ties - aggregating product_matched and brand_matched
				tie_break_score = 0
				if model_matched:
					tie_break_score += 2
				if brand_matched:
					tie_break_score += 1
				products_found.append((product2, score, tie_break_score))


		products_found = sorted(products_found, key = lambda x: (x[1], x[2]), reverse = True)

		# return most similar product or None
		if products_found:
			result = products_found[0][0]

		return result


	# compute similarity between two products using their product names given as token lists
	# return score, threshold (dependent on names' length) and a boolean indicating if brands matched
	@staticmethod
	def similar_names(words1, words2, product2_brand, param):
		common_words = set(words1).intersection(set(words2))

		# assign weigths - 1 to normal words, 2 to nondictionary words
		# 6 to first word in text (assumed to be manufacturer)
		# or 10 if the word looks like a combination of letters and numbers (assumed to be model number)
		# (values stored in the static fields of the class)
		#TODO: update these if they're not relevant for a new category or site

		brand_matched = False
		weights_common = []
		for word in list(common_words):

			# if they share the first word (and it's a non-dictionary word) assume it's manufacturer and assign higher weight
			# this also eliminates high scores for matches like "Vizion TV"-"Cable for Vizio TV"
			#TODO: maybe also accept it if it's on first position in a name and second in another (ex: 50" Vizio)
			if word == words1[0] and word == words2[0] and (not wordnet.synsets(word) or word in ProcessText.brand_exceptions):
				weights_common.append(ProcessText.BRAND_MATCH_WEIGHT)
				brand_matched = True
			else:
				weights_common.append(ProcessText.weight(word))

			# if brand in product name doesn't match but it matches the one extracted from the page
			if not brand_matched and words1[0]==product_brand and (not wordnet.synsets(word) or word in ProcessText.brand_exceptions):
				weights_common.append(ProcessText.BRAND_MATCH_WEIGHT)
				brand_matched = True


			#sys.err.write("PRODUCT BRAND: " + str(product_brand) + "; " + str(words1) + "; " + str(words2) + "\n")

		weights1 = []
		for word in list(set(words1)):
			weights1.append(ProcessText.weight(word))

		weights2 = []
		for word in list(set(words2)):
			weights2.append(ProcessText.weight(word))

		#threshold = param*(sum(weights1) + sum(weights2))/2
		threshold = param*(len(weights1) + len(weights2))/2
		score = sum(weights_common)

		log.msg( "W1: " + str(words1), level=log.INFO)
		log.msg( "W2: " + str(words2), level=log.INFO)
		log.msg( "COMMON: " + str(common_words), level=log.INFO)
		log.msg( "WEIGHTS: " + str(weights1) + str(weights2) + str(weights_common), level=log.INFO)


		return (score, threshold, brand_matched)


	# compute weight to be used for a word for measuring similarity between two texts
	# assign lower weight to alternative product numbers (if they are, it's indicated by the boolean parameter altModels)
	@staticmethod
	def weight(word):

		if ProcessText.is_model_number(word):
			# model number matching is handled separately
			return 0

		# represents number of inches
		if word.endswith("\""):
			return ProcessText.INCHES_MATCH_WEIGHT

		# non dictionary word
		if not wordnet.synsets(word):
			return ProcessText.NONWORD_MATCH_WEIGHT

		# dictionary word
		return ProcessText.DICTIONARY_WORD_MATCH_WEIGHT

	# check if word is a likely candidate to represent a model number
	#Obs: currently finding years as model numbers (1951 will return True)
	@staticmethod
	def is_model_number(word):

		word = word.lower()

		# if there are more than 2 numbers and 2 letters and no non-word characters, 
		# assume this is the model number and assign it a higher weight
		letters = len(re.findall("[a-zA-Z]", word))
		numbers = len(re.findall("[0-9]", word))

		# some models on bestbuy have a - . but check (was not tested)
		# some models on bestbuy have . or /
		nonwords = len(re.findall("[^\w\-/\.]", word))
		
		if ((letters > 1 and numbers > 1) or numbers > 4) and nonwords==0 \
		and not word.endswith("in") and not word.endswith("inch") and not word.endswith("hz") and \
		not re.match("[0-9]{3,}[kmgt]b", word) and not re.match("[0-9]{3,}p", word) and not re.match("[0-9]{2,}hz", word):
		# word is not a memory size, frequency(Hz) or pixels description
			return True

		return False




