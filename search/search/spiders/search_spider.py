from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from search.items import SearchItem
import urllib
import re

################################
# Run with 
#
# scrapy crawl search -a product_name="<name>"
#      -- or --
# scrapy crawl search -a product_url="<url>"
#
################################


# search for a product in all sites, using their search functions; give product as argument by its name or its page url
class SearchSpider(BaseSpider):

	name = "search"

	# pass product as argument to constructor - either product name or product url
	def __init__(self, product_name = None, product_url = None):
		self.search_query = ""
		if product_name:
			self.search_query = "+".join(product_name.split())
		# if product_url:
		# 	self.search_query = self.get_name(product_url)
		self.start_urls = ["http://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + self.search_query]

	def parse(self, response):

		# build list of urls = search pages for each site
		search_pages = {"amazon" : ("http://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + self.search_query), \
						"walmart" : "http://www.walmart.com/search/search-ng.do?ic=16_0&Find=Find&search_query=%s&Find=Find&search_constraint=0" % self.search_query, \
						# "bloomingdales" : "http://www1.bloomingdales.com/shop/search?keyword=%s" % self.search_query, \
						# "overstock" : "http://www.overstock.com/search?keywords=%s" % self.search_query, \
						# "wayfair" : "http://www.wayfair.com/keyword.php?keyword=%s" % self.search_query, \
						# #TODO: check this URL
						# "bestbuy" : "http://www.bestbuy.com/site/searchpage.jsp?_dyncharset=ISO-8859-1&_dynSessConf=-26268873911681169&id=pcat17071&type=page&st=%s&sc=Global&cp=1&nrp=15&sp=&qp=&list=n&iht=y&fs=saas&usc=All+Categories&ks=960&saas=saas" % self.search_query, \
						# "toysrus": "http://www.toysrus.com/search/noResults.jsp?kw=%s" % self.search_query, \
						# #TODO: check the keywords, they give it as caps
						# "bjs" : "http://www.bjs.com/webapp/wcs/stores/servlet/Search?catalogId=10201&storeId=10201&langId=-1&pageSize=40&currentPage=1&searchKeywords=%s&tASearch=&originalSearchKeywords=lg+life+is+good&x=-1041&y=-75" % self.search_query, \
						# #TODO: check this url
						# "sears" : "http://www.sears.com/search=%s" % self.search_query}
						}

		# pass them to parseResults
		for site in search_pages:
			print "URRLLLLLLLL", search_pages[site]
			request = Request(search_pages[site], callback = self.parseResults)
			request.meta['site'] = site
			yield request

	# parse results page, handle each site separately
	def parseResults(self, response):
		hxs = HtmlXPathSelector(response)

		site = response.meta['site']

		# handle parsing separately for each site

		# amazon
		if (site == 'amazon'):

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

		# overstock

		# wayfair

		# bestbuy

		# toysrus

		# bjs

		# sears


	# get the name of a product from the URL of its page
	# the URL can be from various sites
	#def get_name(product_url):

		# extract domain
		#TODO: under construction



