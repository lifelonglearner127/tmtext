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
#   scrapy crawl <site> -a product_name="<name>" [-a output="<option(1/2)>"] [-a threshold=<value>] [a outfile="<filename>"] [-a fast=0]
#      -- or --
#   scrapy crawl <site> -a product_url="<url>" [-a output="<option(1/2)>"] [-a threshold=<value>] [a outfile="<filename>""] [-a fast=0]
#      -- or --
#   scrapy crawl <site> -a product_urls_file="<filename>" [-a output="<option(1/2)>"] [-a threshold=value] [a outfile="<filename>"] [-a fast=0]
#      -- or --
#   scrapy crawl <site> -a walmart_ids_file="<filename>" [-a output="<option(1/2)>"] [-a threshold=value] [a outfile="<filename>"] [-a fast=0]
# 
# where <site> is the derived spider corresponding to the site to search on 
#
# Usage example:
#
# scrapy crawl amazon -a product_urls_file="../sample_output/walmart_televisions_urls.txt" -a output=2 -a outfile="search_results_1.4.txt" -a threshold=1.4 -s LOG_ENABLED=1 2>search_log_1.4.out
#
################################


# search for a product in all sites, using their search functions; give product as argument by its name or its page url
class SearchSpider(BaseSpider):

	name = "search"
	allowed_domains = ["amazon.com", "walmart.com", "bloomingdales.com", "overstock.com", "wayfair.com", "bestbuy.com", "toysrus.com",\
					   "bjs.com", "sears.com", "staples.com", "newegg.com", "ebay.com", "sony.com", "samsung.com"]

	# pass product as argument to constructor - either product name or product URL
	# arguments:
	#				product_name - the product's name, for searching by product name
	#				product_url - the product's page url in the source site, for searching by product URL
	#				product_urls_file - file containing a list of product pages URLs
	#				output - integer(1/2) option indicating output type (either result URL (1), or result URL and source product URL (2))
	#				threshold - parameter for selecting results (the lower the value the more permissive the selection)
	def __init__(self, product_name = None, product_url = None, product_urls_file = None, walmart_ids_file = None, \
		output = 1, threshold = 1.0, outfile = "search_results.txt", outfile2 = "not_matched.txt", fast = 0, use_proxy = False, by_id = False):

		# call specific init for each derived class
		self.init_sub()

		self.product_url = product_url
		self.product_name = product_name
		self.output = int(output)
		self.product_urls_file = product_urls_file
		self.walmart_ids_file = walmart_ids_file
		self.threshold = float(threshold)
		self.outfile = outfile
		self.outfile2 = outfile2
		self.fast = fast
		self.use_proxy = use_proxy
		self.by_id = by_id

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
						"ebay": "http://www.ebay.com/sch/i.html?_trksid=p2050601.m570.l1313&_nkw=%s" % search_query, \
						"sony": "http://store.sony.com/search?SearchTerm=%s" % search_query, \
						"samsung": "http://www.samsung.com/us/function/search/espsearchResult.do?input_keyword=%s" % search_query
						}

		return search_pages

	def build_search_query(self, product_name):
		# put + instead of spaces, lowercase all words
		search_query = "+".join(ProcessText.normalize(product_name, stem=False, exclude_stopwords=False))
		return search_query


	# parse input and build list of URLs to find matches for, send them to parseURL
	def parse(self, response):

		if self.product_name:

			# can inly use this option if self.target_site has been initialized (usually true for spiders for retailers sites, not true for manufacturer's sites)
			if not self.target_site:
				self.log("You can't use the product_name option without setting the target site to search on\n", level=log.ERROR)
				raise CloseSpider("\nYou can't use the product_name option without setting the target site to search on\n")

			search_query = self.build_search_query(self.product_name)
			search_pages = self.build_search_pages(search_query)

			request = Request(search_pages[self.target_site], callback = self.parseResults)
			request.meta['origin_name'] = self.product_name
			request.meta['query'] = search_query

			# just use empty product model and url, for compatibility, also pending_requests
			request.meta['origin_model']  = ''
			request.meta['origin_url'] = ''
			request.meta['pending_requests'] = []

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
			request.meta['origin_site'] = origin_site
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
				#request.meta['origin_site'] = 'walmart'
				yield request
		

	# parse a product page (given its URL) and extract product's name;
	# create queries to search by (use model name, model number, and combinations of words from model name), then send them to parseResults
	def parseURL(self, response):

		site = response.meta['origin_site']
		hxs = HtmlXPathSelector(response)

		product_model = ""

		product_brand = ""

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
				#item['origin_site'] = site
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
				#item['origin_site'] = site
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

		# if there is no product model, try to extract it
		if not product_model:
			product_model_index = ProcessText.extract_model_nr_index(product_name)
			if product_model_index >= 0:
				product_model = product_name[product_model_index]

		# if there is no product brand, get first word in name, assume it's the brand
		product_brand_extracted = ""
		#product_name_tokenized = ProcessText.normalize(product_name)
		product_name_tokenized = [word.lower() for word in product_name.split(" ")]
		#TODO: maybe extract brand as word after 'by', if 'by' is somewhere in the product name
		if len(product_name_tokenized) > 0 and re.match("[a-z]*", product_name_tokenized[0]):
			product_brand_extracted = product_name_tokenized[0].lower()

		# if we are in manufacturer spider, set target_site to manufacturer site
		if self.name == 'manufacturer':

			#TODO: restore commented code; if brand not found, try to search for it on every manufacturer site (build queries fo every supported site)
			# hardcode target site to sony
			#self.target_site = 'sony'
			self.target_site = product_brand_extracted

			# can only go on if site is supported
			# (use dummy query)
			if self.target_site not in self.build_search_pages("").keys():

				product_brands_extracted = set(self.build_search_pages("").keys()).intersection(set(product_name_tokenized))
				
				if product_brands_extracted:
					self.target_site = product_brands_extracted.pop()
				else:
					self.log("Manufacturer site not supported (" + self.target_site + ") or not able to extract brand from product name (" + product_name + ")\n", level=log.ERROR)
					#raise CloseSpider("Manufacturer site not supported (" + self.target_site + ") or not able to extract brand from product name (" + product_name + ")\n")
					item = SearchItem()
					item['origin_url'] = response.url
					item['product_name'] = product_name
					if product_model:
						item['product_model'] = product_model
					yield item
					return


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
		#request.meta['origin_site'] = 
		# product page from source site
		#TODO: clean this URL? for walmart it added something with ?enlargedsearch=True
		request.meta['origin_url'] = response.url

		request.meta['origin_name'] = product_name
		request.meta['origin_model'] = product_model

		# origin product brand as extracted from name (basically the first word in the name)
		request.meta['origin_brand_extracted'] = product_brand_extracted

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
	def reduceResults(self, response):

		items = response.meta['items']
		#site = response.meta['origin_site']

		if 'parsed' not in response.meta:

			# pass to specific prase results function (in derived class)
			return self.parseResults(response)

		else:
			del response.meta['parsed']


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

				#request.meta['origin_site'] = response.meta['origin_site']
				# product page from source site
				request.meta['origin_url'] = response.meta['origin_url']
				request.meta['origin_name'] = response.meta['origin_name']
				request.meta['origin_model'] = response.meta['origin_model']
				request.meta['origin_brand_extracted'] = response.meta['origin_brand_extracted']

				if 'origin_id' in response.meta:
					request.meta['origin_id'] = response.meta['origin_id']
					assert self.by_id
				else:
					assert not self.by_id

				# used for result product URLs
				if 'search_results' in response.meta:
					request.meta['search_results'] = response.meta['search_results']

				return request


			# if there are no more pending requests, use cumulated items to find best match and send it as a result
			else:

				best_match = None

				if items:

					# from all results, select the product whose name is most similar with the original product's name
					best_match = ProcessText.similar(response.meta['origin_name'], response.meta['origin_model'], items, self.threshold)

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
					#item['origin_site'] = site
					
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
			#item['origin_site'] = site
			
			item['origin_url'] = response.meta['origin_url']

			if 'origin_id' in response.meta:
				item['origin_id'] = response.meta['origin_id']
				assert self.by_id
			else:
				assert not self.by_id

				return [item]

	def extract_walmart_id(self, url):
		m = re.match(".*/ip/([0-9]+)", url)
		if m:
			return m.group(1)