from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import TextResponse
from scrapy.exceptions import CloseSpider
from search.items import SearchItem
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
# scrapy crawl search -a product_name="<name>" -a target_site="<site>" [-a output="<option(1/2)>"] [-a threshold=<value>] [a outfile="<filename>"]
#      -- or --
# scrapy crawl search -a product_url="<url>" -a target_site="<site>" [-a output="<option(1/2)>"] [-a threshold=<value>] [a outfile="<filename>""]
#      -- or --
# scrapy crawl search -a product_urls_file="<filename>" -a target_site="<site>" [-a output="<option(1/2)>"] [-a threshold=value] [a outfile="<filename>"]
#
################################


# search for a product in all sites, using their search functions; give product as argument by its name or its page url
class SearchSpider(BaseSpider):

	name = "search"
	allowed_domains = ["amazon.com", "walmart.com", "bloomingdales.com", "overstock.com", "wayfair.com", "bestbuy.com", "toysrus.com",\
					   "bjs.com", "sears.com", "staples.com"]

	# pass product as argument to constructor - either product name or product URL
	# arguments:
	#				product_name - the product's name, for searching by product name
	#				product_url - the product's page url in the source site, for searching by product URL
	#				product_urls_file - file containing a list of product pages URLs
	#				target_site - the site to search on
	#				output - integer(1/2) option indicating output type (either result URL (1), or result URL and source product URL (2))
	#				threshold - parameter (0-1) for selecting results (the lower the value the more permissive the selection)
	def __init__(self, product_name = None, product_url = None, product_urls_file = None, target_site = None, output = 1, threshold = 0.4, outfile = "search_results.txt"):
		self.product_url = product_url
		self.product_name = product_name
		self.target_site = target_site
		self.output = int(output)
		self.product_urls_file = product_urls_file
		self.threshold = float(threshold)
		self.outfile = outfile
		# bloomingales scraper only works with this in the start_urls list
		# self.start_urls = ["http://www.amazon.com", "http://www.walmart.com", "http://www1.bloomingdales.com",\
		# 				   "http://www.overstock.com", "http://www.wayfair.com", "http://www.bestbuy.com", \
		# 				   "http://www.toysrus.com", "http://www.bjs.com", "http://www.sears.com", "http://www.staples.com"]

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
						# "bestbuy" : "http://www.bestbuy.com/site/searchpage.jsp?_dyncharset=ISO-8859-1&_dynSessConf=-26268873911681169&id=pcat17071&type=page&st=%s&sc=Global&cp=1&nrp=15&sp=&qp=&list=n&iht=y&fs=saas&usc=All+Categories&ks=960&saas=saas" % search_query, \
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
			#print "PRODUCT_URL", product_url
			request = Request(product_url, callback = self.parseURL)
			request.meta['site'] = origin_site
			if origin_site == 'staples':
				zipcode = "12345"
				request.cookies = {"zipcode": zipcode}
				request.meta['dont_redirect'] = True
			yield request

	# parse a product page (given its URL) and extract product's name
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
					##print "MODEL: ", model_node.encode("utf-8")

		else:
			raise CloseSpider("Unsupported site: " + site)

		# create search queries and get the results using the target site's search function

		if site == 'staples':
			zipcode = "12345"
			cookies = {"zipcode": zipcode}
		else:
			cookies = {}

		request = None

		##print "PRODUCT: ", product_name.encode("utf-8")

		# 1) Search by model number
		if product_model:
			query1 = self.build_search_query(product_model)
			search_pages1 = self.build_search_pages(query1)
			page1 = search_pages1[self.target_site]
			request1 = Request(page1, callback = self.parseResults, cookies=cookies)


			#DEBUG
			request1.meta['query'] = query1

			##print "QUERY (MODEL)", query1
			
			request = request1


		# 2) Search by product full name
		query2 = self.build_search_query(product_name)
		search_pages2 = self.build_search_pages(query2)
		page2 = search_pages2[self.target_site]
		request2 = Request(page2, callback = self.parseResults, cookies=cookies)


		#DEBUG
		request2.meta['query'] = query2

		##print "QUERY (PRODUCT)", query2

		pending_requests = []

		if not request:
			request = request2
		# else:
		# 	pending_requests.append(request2)

		# 3) Search by combinations of words in product's name
		# create queries

		for words in ProcessText.words_combinations(product_name):
			query3 = self.build_search_query(" ".join(words))
			search_pages3 = self.build_search_pages(query3)
			##print "QUERY", query3
			page3 = search_pages3[self.target_site]
			request3 = Request(page3, callback = self.parseResults, cookies=cookies)


			#DEBUG
			request3.meta['query'] = query3


			pending_requests.append(request3)


		request.meta['pending_requests'] = pending_requests
		request.meta['site'] = self.target_site
		# product page from source site
		request.meta['origin_url'] = response.url

		# include model in product name (if it was not there)
		request.meta['origin_name'] = product_name + " " + product_model

		yield request


	# parse results page, handle each site separately

	# recieve requests for search pages with queries as:
	# 1) product model (if available)
	# 2) product name
	# 3) parts of product's name

	# accumulate results for each (sending the pending requests and the partial results as metadata),
	# and lastly select the best result by selecting the best match between the original product's name and the result products' names
	def parseResults(self, response):

		##print "RESULTS URL", response.url
		
		hxs = HtmlXPathSelector(response)

		site = response.meta['site']
		origin_name = response.meta['origin_name']

		# if this comes from a previous request, get last request's items and add to them the results

		if 'items' in response.meta:
			items = response.meta['items']
			##print "INITIAL ITEMS: ", items
		else:
			items = []

		
		# handle parsing separately for each site

		# amazon
		if (site == 'amazon'):
			# amazon returns partial results as well so we can just search for the entire product name and select from there

			#product = hxs.select("//div[@id='result_0']/h3/a/span/text()").extract()[0]
			#TODO: refine this. get divs with id of the form result_<number>. not all of them have h3's (but this will exclude partial results?)
			results = hxs.select("//h3[@class='newaps']/a")
			for result in results:
				item = SearchItem()
				item['site'] = site

				#TODO: some of these product names are truncated ("..."); even though less relevant ones (special offers or so)
				item['product_name'] = result.select("span/text()").extract()[0]
				product_url = result.select("@href").extract()[0]
				
				# remove the part after "/ref" containing details about the search query
				m = re.match("(.*)/ref=(.*)", product_url)
				if m:
					product_url = m.group(1)

				item['product_url'] = product_url

				if 'origin_url' in response.meta:
					item['origin_url'] = response.meta['origin_url']

				items.append(item)


		# walmart
		if (site == 'walmart'):
			items = []

			results = hxs.select("//div[@class='prodInfo']/div[@class='prodInfoBox']/a[@class='prodLink ListItemLink']")
			for result in results:
				item = SearchItem()
				item['site'] = site
				product_name = result.select("text()").extract()[0]
				# append text that is in <span> if any
				span_text = result.select("./span/text()")

				#TODO: use span text differently, as it is more important/relevant (bold) ?
				for text in span_text:
					product_name += " " + text.extract()
				item['product_name'] = product_name
				rel_url = result.select("@href").extract()[0]
				#TODO: maybe use urljoin
				root_url = "http://www.walmart.com"
				item['product_url'] = root_url + rel_url

				if 'origin_url' in response.meta:
					item['origin_url'] = response.meta['origin_url']

				items.append(item)


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

				items.append(item)


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

				items.append(item)

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

				items.append(item)

		# bestbuy

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

				items.append(item)

		# # bjs
		# if (site == 'bjs'):
		# 	results = hxs.select()

		# sears

		# # staples
		# if (site == 'staples')



		# #print stuff
		# print "PRODUCT: ", response.meta['origin_name'].encode("utf-8")
		# print "QUERY: ", response.meta['query']
		# print "MATCHES: "
		# for item in items:
		# 	print item['product_name'].encode("utf-8")
		# print '\n'


		# if there is a pending request (current request used product model, and pending request is to use product name),
		# continue with that one and send current results to it as metadata
		if 'pending_requests' in response.meta:
			# yield first request in queue and send the other ones as metadata
			pending_requests = response.meta['pending_requests']

			if pending_requests:
				request = pending_requests[0]
				request.meta['pending_requests'] = pending_requests[1:]
				request.meta['items'] = items

				request.meta['site'] = response.meta['site']
				# product page from source site
				request.meta['origin_url'] = response.meta['origin_url']
				request.meta['origin_name'] = response.meta['origin_name']

				return request


			# if there are no more pending requests, use cumulated items to find best match and send it as a result
			else:

				best_match = None

				if items:
					# from all results, select the product whose name is most similar with the original product's name
					best_match = ProcessText.similar(origin_name, items, self.threshold)

					# #print "ALL MATCHES: "
					# for item in items:
					# 	#print item['product_name'].encode("utf-8")
					# #print '\n'

					#print "FINAL: ", best_match

				#print "\n----------------------------------------------\n"

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
				#if 'origin_url' in response.meta:
				item['origin_url'] = response.meta['origin_url']
				return [item]


class ProcessText():
	# normalize text to list of lowercase words (no punctuation except for inches sign (") or /)

	@staticmethod
	def normalize(orig_text):
		text = orig_text
		# other preprocessing: -Inch = " - fitting for staples->amazon search
		# TODO: suitable for all sites?
		text = re.sub("[- ][iI]nch", "\"", text)
		text = re.sub("(?<=[0-9])in","\"", text)

		#! including ' as an exception keeps things like women's a single word. also doesn't find it as a word in wordnet -> too high a priority
		# excluding it leads to women's->women (s is a stopword)

		# replace 1/2 by .5 -> suitable for all sites?
		text = re.sub(" 1/2", "\.5", text)
		# also split by "/" after replacing "1/2"
		text = re.sub("([^\w\"])|(u')", " ", text)
		stopset = set(stopwords.words('english'))#["and", "the", "&", "for", "of", "on", "as", "to", "in"]
		
		#TODO: maybe keep numbers like "50 1/2" together too somehow (originally they're "50-1/2")
		#TODO: maybe handle numbers separately. sometimes we want / to split (in words), and . not to (in numbers)
		# define a better regex above, or here at splitting
		tokens = text.split()
		clean = [token.lower() for token in tokens if token.lower() not in stopset and len(token) > 0]

		return clean

	# create combinations of comb_length words from original text (after normalization and tokenization and filtering out dictionary words)
	# return a list of all combinations
	@staticmethod
	def words_combinations(orig_text, comb_length = 3):
		norm_text = ProcessText.normalize(orig_text)

		# exceptions to include even if they appear in wordnet
		exceptions = ['nt']

		# only keep non dictionary words
		norm_text_nondict = [word for word in norm_text if (not wordnet.synsets(word) or word in exceptions) and len(word) > 1]

		combs = itertools.combinations(range(len(norm_text_nondict)), comb_length)
		words=[map(lambda c: norm_text_nondict[c], x) for x in list(combs)]

		# TODO:
		# # add versions of the queries with different spelling
		# first add all the tokens but with some words replaced (version of original normalized)
		# extra = []
		# for word_comb in words:
		# 	for i in range(len(word_comb)):
		# 		# " -> -inch
		# 		m = re.match("", string, flags)
		#		# .5 ->  1/2


		return words

	# return most similar product from a list to a target product (by their names)
	# if none is similar enough, return None
	# arguments:
	#			product_name - name of target product
	#			products2 - list of product items for products to search through
	#			param - threshold for accepting a product name as similar or not (float between 0-1)
	#TODO: import this from match_product, as a library function
	@staticmethod
	def similar(product_name, products2, param):
		result = None
		products_found = []
		#print "PR2:", len(products2)
		for product2 in products2:
			words1 = ProcessText.normalize(product_name)
			words2 = ProcessText.normalize(product2['product_name'])
			common_words = set(words1).intersection(set(words2))

			# assign weigths - 1 to normal words, 2 to nondictionary words
			# 3 to first word in text (assumed to be manufacturer)
			# or if the word looks like a combination of letters and numbers (assumed to be model number)
			#TODO: update these if they're not relevant for a new category or site

			weights_common = []
			for word in list(common_words):

				# if they share the first word assume it's manufacturer and assign higher weight
				if word == words1[0] and word == words2[0]:
					weights_common.append(5)

				else:
					weights_common.append(ProcessText.weight(word))

			weights1 = []
			for word in list(words1):
				weights1.append(ProcessText.weight(word))

			weights2 = []
			for word in list(words2):
				weights2.append(ProcessText.weight(word))

			#threshold = param*(sum(weights1) + sum(weights2))/2
			threshold = param*(len(weights1) + len(weights2))/2
			score = sum(weights_common)

			# print "W1: ", words1
			# print "W2: ", words2
			# print "COMMON: ", common_words
			# print "WEIGHTS: ", weights1, weights2, weights_common

			# print "SCORE: ", score, "THRESHOLD: ", threshold

			if score >= threshold:
				products_found.append((product2, sum(weights_common)))

		products_found = sorted(products_found, key = lambda x: x[1], reverse = True)

		# return most similar product or None
		if products_found:
			result = products_found[0][0]

		##print "FINAL", product_name.encode("utf-8"), products_found, "\n-----------------------------------------\n"

		return result

	# compute weight to be used for a word for measuring similarity between two texts
	@staticmethod
	def weight(word):

		# if there are more than 2 numbers and 2 letters and no non-word characters, 
		# assume this is the model number and assign it a higher weight
		letters = len(re.findall("[a-zA-Z]", word))
		numbers = len(re.findall("[0-9]", word))
		nonwords = len(re.findall("\W", word))
		
		if letters > 1 and numbers > 1 and nonwords==0:
			return 5

		if not wordnet.synsets(word):
			return 2

		return 1




