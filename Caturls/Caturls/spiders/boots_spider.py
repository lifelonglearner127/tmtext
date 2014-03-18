from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import TextResponse
from Caturls.items import ProductItem
from Caturls.spiders.caturls_spider import CaturlsSpider
from pprint import pprint
from scrapy import log

from spiders_utils import Utils

import re
import sys
import urllib
import urlparse

################################
# Run with 
#
# scrapy crawl boots -a cat_page="<url>" [-a outfile="<filename>" -a brands_file="<brands_filename>"]
# 
# (if specified, brands_filename contains list of brands that should be considered - one brand on each line. other brands will be ignored)
#
################################


class BootsSpider(CaturlsSpider):

	name = "boots"
	allowed_domains = ["boots.com"]

	# boots haircare
	#self.start_urls = ["http://www.boots.com/en/Beauty/Hair/"]

	# add brand option
	def __init__(self, cat_page, outfile = "product_urls.txt", use_proxy = False, brands_file=None):
		super(BootsSpider, self).__init__(cat_page=cat_page, outfile=outfile, use_proxy=use_proxy)
		self.brands = []
		# if a file with a list of specific brands is specified, add them to a class field
		if brands_file:
			brands_file_h = open(brands_file, "r")
			for line in brands_file_h:
				self.brands.append(line.strip())
			brands_file_h.close()

	
	def parse(self, response):
		hxs = HtmlXPathSelector(response)
		# get link to results by brand ('More' link in the left side menu under 'Brand')
		brands_result_link = hxs.select("//h3[.//text()='Brand']/following-sibling::ul[1]/li[last()]/a/@href").extract()

		if brands_result_link:
			return Request(brands_result_link[0], callback=self.parsePage)
		else:
			self.log("No link to search results by brand; aborting crawling", level=log.ERROR)

	# extract query parameters from a URL, return them as a dict
	# uses regex, no url libraries (alternative to urlparse)
	def extract_parameters(self, query_string):
		# extract parameters with urlparse
		# q = urlparse.parse_qs(query_string)
		# q = {p : q[p][0] for p in q}
		# return q

		# parse url into parameters
		parameters_strings = re.findall("[^\?&]+=[^\?&#]*", query_string)
		# extract parameter and value for each
		parameters = dict(map(lambda x: x.split("="), parameters_strings))

		return parameters		

	# split url into base url and query string. to be passed to urlparse and urlencode
	# returns 3 strings: base url, query string, and trailing string if any
	def parse_url(self, url):
		# extract everything between ? and # or end of the url
		#print "URL:", url
		m = re.match("(http://[^\?]+\?)([^#]+)(.*)", url)
		base = m.group(1)
		# unconcode these - otherwise urlencode will encode them again (in build_boots_param_url)
		query_string = urllib.unquote(m.group(2))
		trailing = m.group(3)
		return (base, query_string, trailing)

	# using given url with parameters and parameters to be changed, return a new query string with parameters changed according to the site's javascript function used to filter results
	# used to build a url displaying filtered results (by brand)

	# see applyN and applyNe and setPageNumber here http://www.boots.com/wcsstore/ConsumerDirectStorefrontAssetStore/javascript/boots.search.tabs.js
	# value is either new_endeca_value for applyN and applyNe, or page value for setPageNumber

	# max_page is special argument passed for js_function value of setPageNumber. if set, only sets page number if it's below max_page. used to avoid infinite pagination loops
	def build_boots_param_url(self, url, js_function, t_param, value, max_page=None):

		# parse url and extract query string
		base, qs, trailing = self.parse_url(url)

		# get query parameters
		params = self.extract_parameters(qs)

		# decide parameter to be changed depending on javascript function name
		changed_param = None
		if js_function == 'applyN':
			changed_param = 'N'
		if js_function == 'applyNe':
			changed_param = 'Ne'
		if js_function == 'setPageNumber':
			changed_param = 'page'
			# if page value is higher than max_page, abort
			if max_page and int(value) > max_page:
				print "REACHED MAX PAGE", value, max_page
				return None
		# if it was none of these, there was a problem
		if not changed_param:
			self.log("Couldn't match js function name to any known functions: " + js_function + " \n", level=log.ERROR)
			return None

		# add new parameters, remove unnecessary ones
		for t_param_ in ['t1', 't2', 't3', 't4']:
			# add t values if there were none
			if 'N' in params:
				params[t_param_ + "_N"] = params['N']
			if 'Ne' in params:
				params[t_param_ + "_Ne"] = params['Ne']

			if t_param_ == t_param:
				params[t_param_ + "_" + changed_param] = value

		if 'Ne' in params:
			del params['Ne']
		if 'N' in params:
			del params['N']

		params['searchTerm'] = ''


		# build new url with updated params dict
		new_url = base + urllib.urlencode(params) + trailing

		return new_url

	# from javascript attribute of element, extract arguments representing query string parameters to be changed
	# return tuple of (js_function, t_param, new_endeca_value)
	def extract_boots_js_args(self, js_call_string):
		m = re.match("javascript:(applyNe?|setPageNumber)\('(t[0-9])', '([0-9 ]+)'(, .*)?\);", js_call_string)
		return (m.group(1), m.group(2), m.group(3))

	# get name of brand as appears in menu and return actual brand name
	def clean_brand_name(self, brand):
		m = re.match("\s*(.+)\s*\([0-9]+\).*", brand, flags=re.DOTALL|re.MULTILINE)
		return m.group(1).strip()

	# get link to results page containg brands menu (from parse) and extract link for each brand, pass it to parseBrandPage
	def parsePage(self, response):
		hxs = HtmlXPathSelector(response)

		url = response.url
		#url = "http://www.boots.com/webapp/wcs/stores/servlet/EndecaSearchListerView?storeId=10052&searchTerm=&catalogId=11051&langId=-1&t1_N=4294962961%204294957806&t1_Ne=1&t2_N=4294962961&t2_Ne=1&t3_N=4294962961&t3_Ne=1&t4_N=4294962961&t4_Ne=1&searchv2=true&categoryId=4712#container"
		
		# extract page url for each brand
		brand_links = hxs.select("//h3[.//text()='By brand:']/following-sibling::ul[1]/li//a")

		for brand_link in brand_links:
			brand_url = brand_link.select("@href").extract()[0]
			brand_name = self.clean_brand_name(brand_link.select("text()").extract()[0])

			# if we have a whitelist of brands and current brand is not on it, move on
			if self.brands and brand_name not in self.brands:
				self.log("Omitting brand " + brand_name + "\n", level=log.INFO)
				continue

			# extract js call in href of brand element
			js_call_string = self.extract_boots_js_args(brand_url)
			# build url
			brand_page = self.build_boots_param_url(url, *(js_call_string))

			print "CRAWLING BRAND", brand_name, brand_page

			yield Request(url = brand_page, callback = self.parseBrandPage)

	# parse results page for one brand and extract product urls, handle pagination
	def parseBrandPage(self, response):
		hxs = HtmlXPathSelector(response)

		# extract product urls
		product_urls = hxs.select("//div[@class='pl_productName']/a/@href")
		for url in product_urls:
			item = ProductItem()
			item['product_url'] = url.extract().encode("utf-8")
			yield item


		# crawl next pages if any
		# find if there is a next page
		# select maximum page number on the page
		available_pages = map(lambda x: int(x), hxs.select("//div[@class='pagination']/ul/li/a/text()").re("[0-9]+"))
		print "PAGES", available_pages, response.url
		max_page = max(available_pages)
		# extract 'next page' link
		next_page_link = hxs.select("//li[@class='next']/a")
		if next_page_link:
			# extract js call to next page, use it to build the next page url
			js_call_string = self.extract_boots_js_args(next_page_link.select("@href").extract()[0].encode("utf-8"))
			print "MAX_PAGE", max_page
			next_page = self.build_boots_param_url(response.url, *(js_call_string), max_page=max_page)

			# if there is no next page, function will return None
			if next_page:
				print "Crawling page", next_page
				yield Request(url = next_page, callback = self.parseBrandPage)
			else:
				print "Omitting page " + next_page

		else:
			print "NO NEXT PAGE", response.url



