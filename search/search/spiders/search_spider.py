from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import TextResponse
from search.items import SearchItem
import urllib
import re

# from selenium import webdriver
# import time

################################
# Run with 
#
# scrapy crawl search -a product_name="<name>" -a target_site="<site>"
#      -- or --
# scrapy crawl search -a product_url="<url>" -a target_site="<site>"
#
################################


# search for a product in all sites, using their search functions; give product as argument by its name or its page url
class SearchSpider(BaseSpider):

	name = "search"
	allowed_domains = ["amazon.com", "walmart.com", "bloomingdales.com", "overstock.com", "wayfair.com", "bestbuy.com", "toysrus.com",\
					   "bjs.com", "sears.com", "staples.com"]

	# pass product as argument to constructor - either product name or product url
	def __init__(self, product_name = None, product_url = None, target_site = None):
		self.product_url = product_url
		self.product_name = product_name
		self.target_site = target_site
		# bloomingales scraper only works with this in the start_urls list
		self.start_urls = ["http://www.amazon.com", "http://www.walmart.com", "http://www1.bloomingdales.com",\
						   "http://www.overstock.com", "http://www.wayfair.com", "http://www.bestbuy.com", \
						   "http://www.toysrus.com", "http://www.bjs.com", "http://www.sears.com", "http://www.staples.com"]

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
						}

		return search_pages

	def build_search_query(self, product_name):
		# put + instead of spaces, lowercase all words
		search_query = "+".join([name.lower() for name in product_name.split()])
		return search_query

	def parse(self, response):

		# if we have product names, pass them to parseResults
		if self.product_name:
			search_query = self.build_search_query(product_name)
			search_pages = build_search_pages(search_query)

			request = Request(search_pages[site], callback = self.parseResults)
			request.meta['site'] = self.target_site
			yield request
		
		# if we have product URLs, pass them to parseURL to extract product names (which will pass them to parseResults)
		if self.product_url:
			# extract site domain
			m = re.match("http://www1?\.([^\.]+)\.com.*", self.product_url)
			origin_site = ""
			if m:
				origin_site = m.group(1)
			else:
				sys.stderr.write('Can\'t extract domain from URL.\n')
			request = Request(self.product_url, callback = self.parseURL)
			request.meta['site'] = origin_site
			if origin_site == 'staples':
				zipcode = "12345"
				request.cookies = {"zipcode": zipcode}
			yield request

	# parse a product page (given its URL) and extract product's name
	def parseURL(self, response):
		site = response.meta['site']
		hxs = HtmlXPathSelector(response)
		if site == 'staples':

			product_name = hxs.select("//h1/text()").extract()[0]

			product_model = ""
			model_node = hxs.select("//p[@class='itemModel']/text()").extract()[0]
			m = re.match(".*Model:(.*)", model_node)
			if m:
				product_model = m.group(1)

			query = self.build_search_query(product_name)
			search_pages = self.build_search_pages(query)
			page = search_pages[self.target_site]
			print "SEARCH_PAGE", page
			request = Request(page, callback = self.parseResults)
			request.meta['site'] = self.target_site
			yield request


	# parse results page, handle each site separately
	def parseResults(self, response):
		
		hxs = HtmlXPathSelector(response)

		site = response.meta['site']

		# handle parsing separately for each site

		#TODO: parse multiple pages, can only parse first page so far

		#TODO: parse alternative results (if no results found for search query, but for similar ones)

		# amazon
		if (site == 'amazon'):
			# amazon returns partial results as well so we can just search for the entire product name and select from there
			items = []

			#product = hxs.select("//div[@id='result_0']/h3/a/span/text()").extract()[0]
			#TODO: refine this. get divs with id of the form result_<number>. not all of them have h3's
			results = hxs.select("//h3[@class='newaps']/a")
			for result in results:
				item = SearchItem()
				item['site'] = site
				item['product_name'] = result.select("span/text()").extract()[0]
				item['product_url'] = result.select("@href").extract()[0]

				yield item

		# walmart
		if (site == 'walmart'):

			results = hxs.select("//div[@class='prodInfo']/div[@class='prodInfoBox']/a[@class='prodLink ListItemLink']")
			for result in results:
				item = SearchItem()
				item['site'] = site
				item['product_name'] = result.select("text()").extract()[0]
				rel_url = result.select("@href").extract()[0]
				#TODO: maybe use urljoin
				root_url = "http://www.walmart.com"
				item['product_url'] = root_url + rel_url

				yield item


		# bloomingdales

		#TODO: !! bloomingdales works sporadically
		if (site == 'bloomingdales'):

			results = hxs.select("//div[@class='shortDescription']/a")
			for result in results:
				item = SearchItem()
				item['site'] = site
				item['product_name'] = result.select("text()").extract()[0]
				item['product_url'] = result.select("@href").extract()[0]

				yield item


		# overstock
		if (site == 'overstock'):

			results = hxs.select("//li[@class='product']/div[@class='product-content']/a[@class='pro-thumb']")
			for result in results:
				item = SearchItem()
				item['site'] = site
				item['product_name'] = result.select("span[@class='pro-name']/text()").extract()[0]
				item['product_url'] = result.select("@href").extract()[0]

				yield item

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

				yield item

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

				yield item


		# # bjs
		# if (site == 'bjs'):
		# 	results = hxs.select()

		# sears

		# # staples
		# if (site == 'staples')



