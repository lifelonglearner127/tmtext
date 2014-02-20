from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import FormRequest
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
import os

import captcha_solver
import urllib


class AmazonSpider(SearchSpider):

	name = "amazon"
	# cookie_header = "x-wl-uid=1Y9x3Q0Db5VX3Xvh1wKV9kdGsDEeLDkceSgPK5Hq+AhrYZKCWSHWq6CeCiAwA7BsYZQ58tkG8c3c=; session-token=JPU0C93JOc0DMIZwsQTlpZFJAADURltK2s5Cm22nmFGmaGRwiOPKdvd+ALLsrWay07GVVQtBquy/KpNSTFb5e0HfWeHAq92jFhXz5nQouwyqMLtEC3MUu2TWkIRGps4ppDXQfMP/r96gq0QfRR8EdPogbQ9RzEXoIKf3tj3klxeO2mT6xVQBTfpMPbQHQtv8uyFjWgkLtp6upe4eWorbpd/KyWlBSQXD4eiyfQLIC480TxbOvCBmDhGBOqf6Hk0Nprh2OO2EfrI=; x-amz-captcha-1=1391100438353490; x-amz-captcha-2=+EDhq9rcotSRn783vYMxdQ==; csm-hit=337.71|1391093239619; ubid-main=188-7820618-3817319; session-id-time=2082787201l; session-id=177-0028713-4113141"
	# cookies = {"x-wl-uid" : "1Y9x3Q0Db5VX3Xvh1wKV9kdGsDEeLDkceSgPK5Hq+AhrYZKCWSHWq6CeCiAwA7BsYZQ58tkG8c3c=", \
	# "session-token" : "JPU0C93JOc0DMIZwsQTlpZFJAADURltK2s5Cm22nmFGmaGRwiOPKdvd+ALLsrWay07GVVQtBquy/KpNSTFb5e0HfWeHAq92jFhXz5nQouwyqMLtEC3MUu2TWkIRGps4ppDXQfMP/r96gq0QfRR8EdPogbQ9RzEXoIKf3tj3klxeO2mT6xVQBTfpMPbQHQtv8uyFjWgkLtp6upe4eWorbpd/KyWlBSQXD4eiyfQLIC480TxbOvCBmDhGBOqf6Hk0Nprh2OO2EfrI=",\
	# "x-amz-captcha-1" : "1391100438353490" , "x-amz-captcha-2" : "+EDhq9rcotSRn783vYMxdQ==", "csm-hit" : "337.71|1391093239619", "ubid-main" : "188-7820618-3817319",\
	# "session-id-time" : "2082787201l", "session-id" : "177-0028713-4113141"}

	# initialize fields specific to this derived spider
	def init_sub(self):
		self.target_site = "amazon"
		self.start_urls = [ "http://www.amazon.com" ]

		# captcha classifier. initialize to null and train the first time we encounter a captcha
		self.CB = None

		# paths for data necessary for captcha solving
		self.CAPTCHAS_DIR = "captchas"
		self.SOLVED_CAPTCHAS_DIR = "solved_captchas"
		self.TRAIN_DATA_PATH = "train_captchas_data"

	# given an image URL of the captcha, download the image and solve the captcha, return the result as text
	def solve_captcha(self, image_URL):

		# create necessary directories
		if not os.path.exists(self.CAPTCHAS_DIR):
			os.makedirs(self.CAPTCHAS_DIR)
		if not os.path.exists(self.SOLVED_CAPTCHAS_DIR):
			os.makedirs(self.SOLVED_CAPTCHAS_DIR)

		# solve captcha
		# get image name
		m = re.match(".*/(Captcha_.*)",image_URL)
		if not m:
			return None

		else:
			image_name = m.group(1)

			# download image
			urllib.urlretrieve(image_URL, self.CAPTCHAS_DIR + "/" + image_name)

			captcha_text = None

			try:
				# solve captcha

				# train the classifier the first time it's used.
				# so if it's not been initialized, train it now
				if not self.CB:
					self.CB = captcha_solver.CaptchaBreaker(self.TRAIN_DATA_PATH)
					self.log("Training captcha classifier...", level=log.INFO)


				captcha_text = self.CB.test_captcha(self.CAPTCHAS_DIR + "/" + image_name)

				# save it again with solved captcha text as name
				urllib.urlretrieve(image_URL, self.SOLVED_CAPTCHAS_DIR + "/" + captcha_text + ".jpg")
				self.log("Solving captcha: " + image_URL + " with result " + captcha_text, level=log.WARNING)

			except Exception, e:
				self.log("Exception from captcha solving, for captcha " + self.CAPTCHAS_DIR + "/" + image_name + "\nException message: " + str(e), level=log.ERROR)

			return captcha_text

	# parse results page for amazon, extract info for all products returned by search (keep them in "meta")
	def parseResults(self, response):
		hxs = HtmlXPathSelector(response)

		if 'items' in response.meta:
			items = response.meta['items']
		else:
			items = set()

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
		# add as meta all that was received as meta, will pass it on to reduceResults function in the end
		# also send as meta the entire results list (the product pages URLs), will receive callback when they have all been parsed

		# send the request further to parse product pages only if we gathered all the product URLs from all the queries 
		# (there are no more pending requests)
		# otherwise send them back to parseResults and wait for the next query, save all product URLs in search_results
		# this way we avoid duplicates
		if product_urls and ('pending_requests' not in response.meta or not response.meta['pending_requests']):
			request = Request(product_urls.pop(), callback = self.parse_product_amazon, meta = response.meta)
			if self.cookies_file:
				request.cookies = self.amazon_cookies
				request.headers['Cookies'] = self.amazon_cookie_header
				#request.meta['dont_merge_cookies'] = True
			request.meta['items'] = items

			# this will be the new product_urls list with the first item popped
			request.meta['search_results'] = product_urls

			return request

		# if there were no results, the request will never get back to reduceResults
		# so send it from here so it can parse the next queries
		# add to the response the URLs of the products to crawl we have so far, items (handles case when it was not created yet)
		# and field 'parsed' to indicate that the call was received from this method (was not the initial one)
		else:
			response.meta['items'] = items
			response.meta['parsed'] = True
			response.meta['search_results'] = product_urls
			# only send the response we have as an argument, no need to make a new request
			return self.reduceResults(response)

	# extract product info from a product page for amazon
	# keep product pages left to parse in 'search_results' meta key, send back to parseResults_new when done with all
	def parse_product_amazon(self, response):

		hxs = HtmlXPathSelector(response)

		items = response.meta['items']

		#site = response.meta['origin_site']
		origin_url = response.meta['origin_url']

		item = SearchItem()
		item['product_url'] = response.url
		#item['origin_site'] = site
		item['origin_url'] = origin_url
		item['origin_name'] = response.meta['origin_name']

		if 'origin_model' in response.meta:
			item['origin_model'] = response.meta['origin_model']

		# if 'origin_id' in response.meta:
		# 	item['origin_id'] = response.meta['origin_id']
		# 	assert self.by_id
		# else:
		# 	assert not self.by_id


		# extract product name
		#TODO: id='title' doesn't work for all, should I use a 'contains' or something?
		# extract titles that are not empty (ignoring whitespace)
		# eliminate "Amazon Prime Free Trial"

		#TODO: to test this
		#product_name = filter(lambda x: not x.startswith("Amazon Prime"), hxs.select("//div[@id='title_feature_div']//h1//text()[normalize-space()!='']").extract())
		product_name = filter(lambda x: not x.startswith("Amazon Prime"), hxs.select("//h1//text()[normalize-space()!='']").extract())
		if not product_name:
			self.log("Error: No product name: " + str(response.url) + " for walmart product " + origin_url, level=log.ERROR)

			# assume there is a captcha to crack
			
			# solve captcha
			captcha_text = None
			image = hxs.select(".//img/@src").extract()
			if image:
				captcha_text = self.solve_captcha(image[0])

			# value to use if there was an exception
			if not captcha_text:
				captcha_text = ''


			#TODO: if there is no product name but no captcha either, so let's say it just outputs to log that there was an error, does that also mean all meta info is lost? (request is not passed on)
			#No, it just doesn't get added to items, the request is made anyway
			#TODO: don't return this request if page is not form? (it generates en exception)
			
			# create a FormRequest to this same URL, with everything needed in meta
			# items, cookies and search_urls not changed from previous response so no need to set them again
	
			return [FormRequest.from_response(response, callback = self.parse_product_amazon, formdata={'field-keywords' : captcha_text}, meta = response.meta)]

		else:
			item['product_name'] = product_name[0].strip()

			# extract product model number
			model_number_holder = hxs.select("//tr[@class='item-model-number']/td[@class='value']/text() | //li/b/text()[normalize-space()='Item model number:']/parent::node()/parent::node()/text()").extract()
			if model_number_holder:
				item['product_model'] = model_number_holder[0].strip()
			# if no product model explicitly on the page, try to extract it from name
			else:
				product_model_extracted = ProcessText.extract_model_from_name(item['product_name'])
				if product_model_extracted:
					item['product_model'] = product_model_extracted
				#print "MODEL EXTRACTED: ", product_model_extracted, " FROM NAME ", item['product_name'].encode("utf-8")


			brand_holder = hxs.select("//div[@id='brandByline_feature_div']//a/text() | //a[@id='brand']/text()").extract()
			if brand_holder:
				item['product_brand'] = brand_holder[0]
			else:
				pass
				#sys.stderr.write("Didn't find product brand: " + response.url + "\n")

			# extract price
			#! extracting list price and not discount price when discounts available?
			price_holder = hxs.select("//span[contains(@id,'priceblock')]/text() | //span[@class='a-color-price']/text() " + \
				"| //span[@class='listprice']/text() | //span[@id='actualPriceValue']/text() | //b[@class='priceLarge']/text() | //span[@class='price']/text()").extract()

			# if we can't find it like above try other things:
			if not price_holder:
				# prefer new prices to used ones
				price_holder = hxs.select("//span[contains(@class, 'olp-new')]//text()[contains(.,'$')]").extract()
			if price_holder:
				product_target_price = price_holder[0].strip()
				# remove commas separating orders of magnitude (ex 2,000)
				product_target_price = re.sub(",","",product_target_price)
				m = re.match("\$([0-9]+\.?[0-9]*)", product_target_price)
				if m:
					item['product_target_price'] = float(m.group(1))
				else:
					self.log("Didn't match product price: " + product_target_price + " " + response.url + "\n", level=log.WARNING)

			else:
				self.log("Didn't find product price: " + response.url + "\n", level=log.INFO)


			# add result to items
			items.add(item)

		# if there are any more results to be parsed, send a request back to this method with the next product to be parsed
		product_urls = response.meta['search_results']

		if product_urls:
			request = Request(product_urls.pop(), callback = self.parse_product_amazon, meta = response.meta)
			if self.cookies_file:
				request.cookies = self.amazon_cookies
				request.headers['Cookies'] = self.amazon_cookie_header
				#request.meta['dont_merge_cookies'] = True
			request.meta['items'] = items
			# eliminate next product from pending list (this will be the new list with the first item popped)
			request.meta['search_results'] = product_urls

			return request
		else:
			# otherwise, we are done, send a the response back to reduceResults (no need to make a new request)
			# add as meta newly added items
			# also add 'parsed' field to indicate that the parsing of all products was completed and they cand be further used
			# (actually that the call was made from this method and was not the initial one, so it has to move on to the next request)

			response.meta['parsed'] = True
			response.meta['items'] = items

			return self.reduceResults(response)