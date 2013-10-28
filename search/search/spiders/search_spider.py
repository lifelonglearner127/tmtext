from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import TextResponse
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
					   "bjs.com", "sears.com", "staples.com", "newegg.com"]

	# pass product as argument to constructor - either product name or product URL
	# arguments:
	#				product_name - the product's name, for searching by product name
	#				product_url - the product's page url in the source site, for searching by product URL
	#				product_urls_file - file containing a list of product pages URLs
	#				target_site - the site to search on
	#				output - integer(1/2) option indicating output type (either result URL (1), or result URL and source product URL (2))
	#				threshold - parameter (0-1) for selecting results (the lower the value the more permissive the selection)
	def __init__(self, product_name = None, product_url = None, product_urls_file = None, target_site = None, output = 1, threshold = 1.0, outfile = "search_results.txt", fast = 0):
		self.product_url = product_url
		self.product_name = product_name
		self.target_site = target_site
		self.output = int(output)
		self.product_urls_file = product_urls_file
		self.threshold = float(threshold)
		self.outfile = outfile
		self.fast = fast
		# bloomingales scraper only works with this in the start_urls list
		# self.start_urls = ["http://www.amazon.com", "http://www.walmart.com", "http://www1.bloomingdales.com",\
		# 				   "http://www.overstock.com", "http://www.wayfair.com", "http://www.bestbuy.com", \
		# 				   "http://www.toysrus.com", "http://www.bjs.com", "http://www.sears.com", "http://www.staples.com"]

		self.start_urls = ["http://www1.bloomingdales.com"]

		#TODO start logging


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
					##print "MODEL: ", model_node.encode("utf-8")

		elif site == 'walmart':
			product_name = hxs.select("//h1[@class='productTitle']/text()").extract()[0]
			product_model_holder = hxs.select("//td[contains(text(),'Model')]/following-sibling::*/text()").extract()
			if product_model_holder:
				product_model = product_model_holder[0]

		elif site == 'newegg':
			product_name_holder = hxs.select("//span[@itemprop='name']/text()").extract()
			if product_name_holder:
				product_name = product_name_holder[0].strip()
			else:
				sys.stderr.write("Broken product page link (can't find item title): " + response.url)
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

		##print "PRODUCT: ", product_name.encode("utf-8")

		# 1) Search by model number
		if product_model:
			query1 = self.build_search_query(product_model)
			search_pages1 = self.build_search_pages(query1)
			page1 = search_pages1[self.target_site]
			request1 = Request(page1, callback = self.parseResults, cookies=cookies)

			#TODO: add query with model number and part of product name? that could narrow the results and make it faster. though it could also ommit some


			request1.meta['query'] = query1

			##print "QUERY (MODEL)", query1
			
			request = request1


		# 2) Search by product full name
		query2 = self.build_search_query(product_name)
		search_pages2 = self.build_search_pages(query2)
		page2 = search_pages2[self.target_site]
		request2 = Request(page2, callback = self.parseResults, cookies=cookies)


		request2.meta['query'] = query2

		##print "QUERY (PRODUCT)", query2

		pending_requests = []

		if not request:
			request = request2
		# else:
		# 	pending_requests.append(request2)

		# 3) Search by combinations of words in product's name
		# create queries

		for words in ProcessText.words_combinations(product_name, fast=self.fast):
			query3 = self.build_search_query(" ".join(words))
			search_pages3 = self.build_search_pages(query3)
			##print "QUERY", query3
			page3 = search_pages3[self.target_site]
			request3 = Request(page3, callback = self.parseResults, cookies=cookies)


			request3.meta['query'] = query3


			pending_requests.append(request3)


		request.meta['pending_requests'] = pending_requests
		request.meta['site'] = self.target_site
		# product page from source site
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

		##print "RESULTS URL", response.url
		
		hxs = HtmlXPathSelector(response)

		site = response.meta['site']
		origin_name = response.meta['origin_name']
		origin_model = response.meta['origin_model']

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

				item['product_url'] = Utils.add_domain(product_url, "http://www.amazon.com")

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
				product_name = result.select(".//text()").extract()[0]
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

		#TODO: currently only extracting first page - should I extract all pages?
		# bestbuy
		if (site == 'bestbuy'):
			results = hxs.select("//div[@class='hproduct']/div[@class='info-main']/h3/a")

			for result in results:
				item = SearchItem()
				item['site'] = site
				item['product_name'] = result.select("text()").extract()[0].strip()
				item['product_url'] = Utils.add_domain(result.select("@href").extract()[0], "http://www.bestbuy.com")

				if 'origin_url' in response.meta:
					item['origin_url'] = response.meta['origin_url']

				model_holder = result.select("parent::node()/parent::node()//strong[@itemprop='model']/text()").extract()
				if model_holder:
					item['product_model'] = model_holder[0]

				items.append(item)


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



		#print stuff
		self.log("PRODUCT: " + response.meta['origin_name'].encode("utf-8") + " MODEL: " + response.meta['origin_model'].encode("utf-8"), level="INFO")
		#print 
		self.log( "QUERY: " + response.meta['query'], level="INFO")
		self.log( "MATCHES: ", level="DEBUG")
		for item in items:
			self.log( item['product_name'].encode("utf-8"), level="DEBUG")
		self.log( '\n', level="DEBUG")


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
				request.meta['origin_model'] = response.meta['origin_model']

				return request


			# if there are no more pending requests, use cumulated items to find best match and send it as a result
			else:

				best_match = None

				if items:
					# from all results, select the product whose name is most similar with the original product's name
					best_match = ProcessText.similar(origin_name, origin_model, items, self.threshold)

					# #self.log( "ALL MATCHES: ", level="INFO")					
					# for item in items:
					# 	#print item['product_name'].encode("utf-8")
					# #print '\n'

					self.log( "FINAL: " + str(best_match), level="INFO")

				self.log( "\n----------------------------------------------\n", level="INFO")

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


				self.log( "FINAL: no items", level="INFO")

				return [item]


class ProcessText():
	# normalize text to list of lowercase words (no punctuation except for inches sign (") or /)

	@staticmethod
	def normalize(orig_text):
		text = orig_text
		# other preprocessing: -Inch = " - fitting for staples->amazon search
		# TODO: suitable for all sites?
		text = re.sub("[- ][iI]nch", "\"", text)
		text2 = re.sub("(?<=[0-9])[iI][nN](?!=c)","\"", text)

		
		#print "BEFORE:", text.encode("utf-8"), " AFTER:", text2.encode("utf-8")

		text=text2


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

	# get alternative model number

	# without the last letters, so as to match more possibilities
	# (there is are cases like this, for example un32eh5300f)
	@staticmethod
	def alt_modelnr(word):
		if not word:
			return None
		m = re.match("(.*[0-9]+)[a-zA-Z\-]+", word)
		if m:
			new_word = m.group(1)
			if len(new_word) > 2:
				return new_word
		return None

	# normalize model numbers (remove dashes, lowercase)
	@staticmethod
	def normalize_modelnr(modelnr):
		return re.sub("[\- ]", "", modelnr.lower())

	# build new tokenized list of words for a product name replacing (first found) the model number with the alternative one
	@staticmethod
	def name_with_alt_modelnr(words):
		new_words = list(words)
		# if there is a supposed model number among the words, replace it with its alternative
		i = ProcessText.extract_model_nr_index(words)
		if i >= 0:
			alt_model = ProcessText.alt_modelnr(words[i])
			if alt_model:
				new_word = alt_model
				new_words[i] = new_word
		return new_words

	# extract index of (first found) model number in list of words if any
	# return -1 if none found
	@staticmethod
	def extract_model_nr_index(words):
		for i in range(len(words)):
			if ProcessText.is_model_number(words[i]):
				log.msg("MODEL: " + words[i])
				return i
		return -1

	# create combinations of comb_length words from original text (after normalization and tokenization and filtering out dictionary words)
	# return a list of all combinations
	@staticmethod
	def words_combinations(orig_text, comb_length = 3, fast = False):
		norm_text = ProcessText.normalize(orig_text)

		# exceptions to include even if they appear in wordnet
		exceptions = ['nt']

		# if using fast option: don't look them up in wordnet
		if not fast:

			# only keep non dictionary words
			norm_text = [word for word in norm_text if (not wordnet.synsets(word) or word in exceptions) and len(word) > 1]

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
	#TODO: import this from match_product, as a library function
	@staticmethod
	def similar(product_name, product_model, products2, param):
		result = None
		products_found = []
		#print "PR2:", len(products2)
		for product2 in products2:

			words1 = ProcessText.normalize(product_name)
			words2 = ProcessText.normalize(product2['product_name'])
			if 'product_model' in product2:
				product2_model = product2['product_model']
			else:
				product2_model = None

			(score, threshold) = ProcessText.similar_names(words1, words2, param)

			# try it with alternative model numbers as well, and keep the one with highest score
			alt_words1 = ProcessText.name_with_alt_modelnr(words1)
			alt_words2 = ProcessText.name_with_alt_modelnr(words2)


			if alt_words1:
				# compute weights differently if we used alternative model numbers
				(score1, threshold1) = ProcessText.similar_names(alt_words1, words2, param, altModels=True)
				if score1 > score:
					(score, threshold) = (score1, threshold1)

			if (alt_words1 and alt_words2):
				(score2, threshold2) = ProcessText.similar_names(alt_words1, alt_words2, param, altModels=True)
				if score2 > score:
					(score, threshold) = (score2, threshold2)

			if alt_words2:
				(score3, threshold3) = ProcessText.similar_names(words1, alt_words2, param, altModels=True)
				if score3 > score:
					(score, threshold) = (score3, threshold3)
			

			MODEL_MATCH_WEIGHT = 7
			# add to the score if their model numbers match
			# check if the product models are the same, or if they are included in the other product's name
			# for the original product models, as well as for the alternative ones, and alternative product names

			alt_product_model = ProcessText.alt_modelnr(product_model)
			alt_product2_model = ProcessText.alt_modelnr(product2_model)

			# get product models extracted from product name, if found
			model_index1 = ProcessText.extract_model_nr_index(words1)
			if model_index1 >= 0:
				product_model_fromname = words1[model_index1]
				alt_product_model_fromname = ProcessText.alt_modelnr(product_model_fromname)
			else:
				product_model_fromname = None
				alt_product_model_fromname = None

			model_index2 = ProcessText.extract_model_nr_index(words2)
			if model_index2 >= 0:
				product2_model_fromname = words2[model_index2]
				alt_product2_model_fromname = ProcessText.alt_modelnr(product2_model_fromname)
			else:
				product2_model_fromname = None
				alt_product2_model_fromname = None

			product_matched = False
			# to see if models match, build 2 lists with each of the products' possible models, and check their intersection
			models1 = filter(None, [product_model, alt_product_model, product_model_fromname, alt_product_model_fromname])
			models2 = filter(None, [product2_model, alt_product2_model, product2_model_fromname, alt_product2_model_fromname])

			# normalize all product models
			models1 = map(lambda x: ProcessText.normalize_modelnr(x), models1)
			models2 = map(lambda x: ProcessText.normalize_modelnr(x), models2)

			if set(models1).intersection(set(models2)):
				product_matched = True

			matched = False
			if product_model and (product_model == product2_model):
				matched = True
				#sys.stderr.write("\nMATCHED1:" + " model1: " + str(product_model) + " product2_model: " + str(product2_model))
			elif (product2_model and alt_product_model == product2_model):
				matched = True
				#sys.stderr.write("\nMATCHED2:" + " model1: " + str(ProcessText.alt_modelnr(product_model)) + " product2_model: " + str(product2_model))
			elif (product_model and product_model == alt_product2_model):
				matched = True
				#sys.stderr.write("\nMATCHED3:" + " model1: " + str(product_model) + " product2_model: " + str(ProcessText.alt_modelnr(product2_model)))
			elif alt_product_model and (alt_product_model == alt_product2_model):
				matched = True
				#sys.stderr.write("\nMATCHED4:" + " model1: " + product_model + ", " + str(ProcessText.alt_modelnr(product_model)) + " product2_model: " + str(ProcessText.alt_modelnr(product2_model)))
			elif product_model in words2:
				matched = True
				#sys.stderr.write("\nMATCHED5:" + " model1: " + str(product_model) + " words2: " + str(words2))
			elif alt_product_model in words2:
				matched = True
				#sys.stderr.write("\nMATCHED6:" + " model1: " + str(ProcessText.alt_modelnr(product_model)) + " words2: " + str(words2))
			elif product_model in alt_words2:
				matched = True
				#sys.stderr.write("\nMATCHED7:" + " model1: " + str(product_model) + " words2: " + str(alt_words2))
			elif alt_product_model in alt_words2:
				matched = True
				#sys.stderr.write("\nMATCHED8:" + " model1: " + str(ProcessText.alt_modelnr(product_model)) + " words2: " + str(alt_words2))
			elif product2_model in words1:
				matched = True
				#sys.stderr.write("\nMATCHED9:" + " product2_model: " + str(product2_model) + " words1: " + str(words1))
			elif alt_product2_model in words1:
				matched = True
				#sys.stderr.write("\nMATCHED10:" + " product2_model: " + str(ProcessText.alt_modelnr(product2_model)) + " words1: " + str(words1))
			elif product2_model in alt_words1:
				matched = True
				#sys.stderr.write("\nMATCHED11:" + " product2_model: " + str(product2_model) + " words1: " + str(alt_words1))
			elif alt_product2_model in alt_words1:
				matched = True
				#sys.stderr.write("\nMATCHED12:" + " product2_model: " + str(ProcessText.alt_model(product2_model)) + " words1: " + str(alt_words1))

			else:
				pass
				#sys.stderr.write("\nNOT MATCHED:" + "model1: " + str(product_model) + " product2_model: " + str(product2_model) + " words1: " + str(words1) + " words2: " + str(words2))


			assert matched == product_matched
			if (matched == product_matched):
				log.msg("OK! " + str(matched) + str(set(models1)) + str(set(models2)), level="INFO")

			if matched:
				score += MODEL_MATCH_WEIGHT

			log.msg( "SCORE: " + str(score) + " THRESHOLD: " + str(threshold), level="INFO")

			if score >= threshold:
				products_found.append((product2, score))


		products_found = sorted(products_found, key = lambda x: x[1], reverse = True)

		#TODO: handle ties?

		# return most similar product or None
		if products_found:
			result = products_found[0][0]

		##print "FINAL", product_name.encode("utf-8"), products_found, "\n-----------------------------------------\n"

		return result


	# compute similarity between two products using their product names given as token lists
	@staticmethod
	def similar_names(words1, words2, param, altModels = False):
		common_words = set(words1).intersection(set(words2))

		# assign weigths - 1 to normal words, 2 to nondictionary words
		# 3 to first word in text (assumed to be manufacturer)
		# or if the word looks like a combination of letters and numbers (assumed to be model number)
		#TODO: update these if they're not relevant for a new category or site

		FIRSTWORD_WEIGHT = 4

		weights_common = []
		for word in list(common_words):

			# if they share the first word assume it's manufacturer and assign higher weight
			if word == words1[0] and word == words2[0]:
				weights_common.append(FIRSTWORD_WEIGHT)

			else:
				weights_common.append(ProcessText.weight(word, altModels))

		weights1 = []
		for word in list(set(words1)):
			weights1.append(ProcessText.weight(word, altModels))

		weights2 = []
		for word in list(set(words2)):
			weights2.append(ProcessText.weight(word, altModels))

		#threshold = param*(sum(weights1) + sum(weights2))/2
		threshold = param*(len(weights1) + len(weights2))/2
		score = sum(weights_common)

		#print "WORDS: ", product_name.encode("utf-8"), product2['product_name'].encode("utf-8")
		log.msg( "W1: " + str(words1), level="INFO")
		log.msg( "W2: " + str(words2), level="INFO")
		log.msg( "COMMON: " + str(common_words), level="INFO")
		log.msg( "WEIGHTS: " + str(weights1) + str(weights2) + str(weights_common), level="INFO")


		return (score, threshold)


	# compute weight to be used for a word for measuring similarity between two texts
	# assign lower weight to alternative product numbers (if they are, it's indicated by the boolean parameter altModels)
	@staticmethod
	def weight(word, altModels = False):

		if ProcessText.is_model_number(word):
			# return lower weight if this comes from words with alternative models (not original words as found on site)
			if not altModels:
				return 7
			else:
				return 6

		if not wordnet.synsets(word):
			return 2

		return 1

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
		
		if ((letters > 1 and numbers > 1) or numbers > 3) and nonwords==0 \
		and not word.endswith("in") and not word.endswith("inch") and not word.endswith("hz") and \
		not re.match("[0-9]{,3}[kmgt]b", word): # word is not a memory size description
			return True

		return False




