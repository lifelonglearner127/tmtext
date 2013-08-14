from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import TextResponse
from search.items import SearchItem
import urllib
import re

import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet

# from selenium import webdriver
# import time

################################
# Run with 
#
# scrapy crawl search -a product_name="<name>" -a target_site="<site>" [-a output="<option(1/2)>"]
#      -- or --
# scrapy crawl search -a product_url="<url>" -a target_site="<site>" [-a output="<option(1/2)>"]
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
	def __init__(self, product_name = None, product_url = None, product_urls_file = None, target_site = None, output = 1, threshold = 0.65):
		self.product_url = product_url
		self.product_name = product_name
		self.target_site = target_site
		self.output = int(output)
		self.product_urls_file = product_urls_file
		self.threshold = float(threshold)
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
		search_query = "+".join(self.normalize(product_name))
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

		#print "DEBUG 1"

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
				#print "ZIPCODE", zipcode
			yield request

	# parse a product page (given its URL) and extract product's name
	def parseURL(self, response):
		#print "DEBUG 2"

		#TODO: !bug! some URLs from origin site don't get here

		site = response.meta['site']
		hxs = HtmlXPathSelector(response)
		if site == 'staples':

			product_name = hxs.select("//h1/text()").extract()[0]

			product_model = ""
			model_nodes = hxs.select("//p[@class='itemModel']/text()").extract()
			if model_nodes:
				model_node = model_nodes[0]
				m = re.match(".*Model:(.*)", model_node)
				if m:
					product_model = m.group(1)

			query = self.build_search_query(product_name)
			search_pages = self.build_search_pages(query)
			page = search_pages[self.target_site]
			#print "PAGE", page, "ORIGIN", response.url
			request = Request(page, callback = self.parseResults)
			request.meta['site'] = self.target_site
			# product page from source site
			request.meta['origin_url'] = response.url
			request.meta['origin_name'] = product_name
			zipcode = "12345"
			request.cookies = {"zipcode": zipcode}
			yield request


	# parse results page, handle each site separately
	def parseResults(self, response):

		#print "URL", response.url
		
		hxs = HtmlXPathSelector(response)

		site = response.meta['site']
		origin_name = response.meta['origin_name']

		# handle parsing separately for each site

		#TODO: parse multiple pages, can only parse first page so far

		#TODO: parse alternative results (if no results found for search query, but for similar ones)

		# amazon
		if (site == 'amazon'):
			# amazon returns partial results as well so we can just search for the entire product name and select from there
			items = []

			#product = hxs.select("//div[@id='result_0']/h3/a/span/text()").extract()[0]
			#TODO: refine this. get divs with id of the form result_<number>. not all of them have h3's (but this will exclude partial results?)
			results = hxs.select("//h3[@class='newaps']/a")
			for result in results:
				item = SearchItem()
				item['site'] = site
				item['product_name'] = result.select("span/text()").extract()[0]
				item['product_url'] = result.select("@href").extract()[0]
				if 'origin_url' in response.meta:
					item['origin_url'] = response.meta['origin_url']

				items.append(item)

			best_match = None

			if results:
				# from all results, select the product whose name is most similar with the original product's name
				best_match = self.similar(origin_name, items, self.threshold)
				# it's returned as a tuple so we need the first item
				if best_match:
					best_match = best_match[0]

			if not best_match:
				# if there are no results but the option was to include original product URL, create an item with just that
				if self.output == 2:
					item = SearchItem()
					item['site'] = site
					#if 'origin_url' in response.meta:
					item['origin_url'] = response.meta['origin_url']
					return [item]

			return [best_match]




			item = SearchItem()
			item['site'] = site
			#if 'origin_url' in response.meta:
			item['origin_url'] = response.meta['origin_url']
			return [item]


		# walmart
		if (site == 'walmart'):
			items = []

			results = hxs.select("//div[@class='prodInfo']/div[@class='prodInfoBox']/a[@class='prodLink ListItemLink']")
			for result in results:
				item = SearchItem()
				item['site'] = site
				item['product_name'] = result.select("text()").extract()[0]
				rel_url = result.select("@href").extract()[0]
				#TODO: maybe use urljoin
				root_url = "http://www.walmart.com"
				item['product_url'] = root_url + rel_url

				items.append(item)


		# bloomingdales

		#TODO: !! bloomingdales works sporadically
		if (site == 'bloomingdales'):
			items = []

			results = hxs.select("//div[@class='shortDescription']/a")
			for result in results:
				item = SearchItem()
				item['site'] = site
				item['product_name'] = result.select("text()").extract()[0]
				item['product_url'] = result.select("@href").extract()[0]

				items.append(item)


		# overstock
		if (site == 'overstock'):
			items = []

			results = hxs.select("//li[@class='product']/div[@class='product-content']/a[@class='pro-thumb']")
			for result in results:
				item = SearchItem()
				item['site'] = site
				item['product_name'] = result.select("span[@class='pro-name']/text()").extract()[0]
				item['product_url'] = result.select("@href").extract()[0]

				items.append(item)

		# wayfair
		if (site == 'wayfair'):
			items = []

			results = hxs.select("//li[@class='productbox']")

			for result in results:
				product_link = result.select(".//a[@class='toplink']")
				item = SearchItem()
				item['site'] = site
				item['product_url'] = product_link.select("@href").extract()[0]
				item['product_name'] = product_link.select("div[@class='prodname']/text()").extract()[0]
				#TODO: add brand?
				#item['brand'] = result.select("div[@class='prodname']/div[@class='prodbrandname emphasis]/text()").extract()[0]

				items.append(item)

		# bestbuy

		# toysrus
		if (site == 'toysrus'):
			results = hxs.select("//a[@class='prodtitle']")
			items = []

			for result in results:
				item = SearchItem()
				item['site'] = site
				item['product_name'] = result.select("text()").extract()[0]
				root_url = "http://www.toysrus.com"
				item['product_url'] = root_url + result.select("@href").extract()[0]

				items.append(item)


		# # bjs
		# if (site == 'bjs'):
		# 	results = hxs.select()

		# sears

		# # staples
		# if (site == 'staples')


	# normalize text to list of lowercase words (no punctuation except for inches sign (") or /)
	def normalize(self, orig_text):
		text = orig_text
		# other preprocessing: -Inch = " - fitting for staples->amazon search
		# TODO: suitable for all sites?
		#text = re.sub("\"", "-Inch", text)

		#! including ' as an exception keeps things like women's a single word. also doesn't find it as a word in wordnet -> too high a priority
		# excluding it leads to women's->women (s is a stopword)
		text = re.sub("([^\w\"/])|(u')", " ", text)
		stopset = set(stopwords.words('english'))#["and", "the", "&", "for", "of", "on", "as", "to", "in"]
		#tokens = nltk.WordPunctTokenizer().tokenize(text)
		# we need to keep 19" as one word for ex

		#TODO: maybe keep numbers like "50 1/2" together too somehow (originally they're "50-1/2")
		#TODO: maybe handle numbers separately. sometimes we want / to split (in words), and . not to (in numbers)
		# define a better regex above, or here at splitting
		tokens = text.split()
		clean = [token.lower() for token in tokens if token.lower() not in stopset and len(token) > 0]
		#print "clean", orig_text, clean

		return clean

	# return most similar product from a list to a target product (by their names)
	# if none is similar enough, return None
	# arguments:
	#			product_name - name of target product
	#			products2 - list of product items for products to search through
	#			param - threshold for accepting a product name as similar or not (float between 0-1)
	#TODO: import this from match_product, as a library function
	def similar(self, product_name, products2, param):
		result = None
		products_found = []
		for product2 in products2:
			words1 = set(self.normalize(product_name))
			words2 = set(self.normalize(product2['product_name']))
			common_words = words1.intersection(words2)

			weights_common = []
			for word in common_words:
				if not wordnet.synsets(word):
					weights_common.append(2)
				else:
					weights_common.append(1)
			#print common_words, weights_common

			weights1 = []
			for word in words1:
				if not wordnet.synsets(word):
					weights1.append(2)
				else:
					weights1.append(1)

			weights2 = []
			for word in words2:
				if not wordnet.synsets(word):
					weights2.append(2)
				else:
					weights2.append(1)

			#threshold = 0.5*(len(words1) + len(words2))/2

			#print "common words, weight:", common_words, sum(weights_common)

			threshold = param*(sum(weights1) + sum(weights2))/2

			if sum(weights_common) >= threshold:
				products_found.append((product2, sum(weights_common)))
				# product_name += " ".join(list(words1))
				# product_name2 += " ".join(list(words2))
				# print product_name, product_name2
			products_found = sorted(products_found, key = lambda x: x[1], reverse = True)

			# return most similar product or None
			if products_found:
				result = products_found[0]

			return result



