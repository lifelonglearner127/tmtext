from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import TextResponse
from Caturls.items import ProductItem
from pprint import pprint


from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time
import re
import sys
import json

################################
# Run with 
#
# scrapy crawl producturls -a cat_page="<url>" [-a outfile="<filename>"]
#
################################


# search for a product in all sites, using their search functions; give product as argument by its name or its page url
class CaturlsSpider(BaseSpider):

	name = "producturls"
	allowed_domains = ["staples.com", "bloomingdales.com", "walmart.com", "amazon.com", "bestbuy.com", "nordstrom.com", "macys.com", "williams-sonoma.com"]

	# store the cateory page url given as an argument into a field and add it to the start_urls list
	def __init__(self, cat_page, outfile = "product_urls.txt"):
		self.cat_page = cat_page
		self.start_urls = [cat_page]
		self.outfile = outfile
		# staples televisions
		#self.start_urls = ["http://www.staples.com/Televisions/cat_CL142471"]
		# bloomingdales sneakers
		#self.start_urls = ["http://www1.bloomingdales.com/shop/shoes/sneakers?id=17400"]
		# walmart televisions
		#self.start_urls = ["http://www.walmart.com/cp/televisions-video/1060825?povid=P1171-C1110.2784+1455.2776+1115.2956-L13"]
		# amazon televisions
		#self.start_urls = ["http://www.amazon.com/Televisions-Video/b/ref=sa_menu_tv?ie=UTF8&node=1266092011"]
		# bestbuy televisions
		#self.start_urls = ["http://www.bestbuy.com/site/Electronics/Televisions/pcmcat307800050023.c?id=pcmcat307800050023&abtest=tv_cat_page_redirect"]
		# nordstrom sneakers
		#self.start_urls = ["http://shop.nordstrom.com/c/womens-sneakers?dept=8000001&origin=topnav"]
		# macy's sneakers
		#self.start_urls = ["http://www1.macys.com/shop/shoes/sneakers?id=26499&edge=hybrid"]
		# macy's blenders
		#self.start_urls = ["http://www1.macys.com/shop/kitchen/blenders?id=46710&edge=hybrid"]
		# macy's coffee makers
		#self.start_urls = ["http://www1.macys.com/shop/kitchen/coffee-makers?id=24733&edge=hybrid"]
		# macy's mixers
		#self.start_urls = ["http://www1.macys.com/shop/kitchen/mixers-accessories?id=46705&edge=hybrid"]
		# williams-sonoma blenders
		#self.start_urls = ["http://www.williams-sonoma.com/products/cuisinart-soup-maker-blender-sbc-1000/?pkey=cblenders&"]
		# williams-sonoma mixers
		#self.start_urls = ["http://www.williams-sonoma.com/shop/electrics/mixers-attachments/?cm_type=gnav"]
		# williams-sonoma coffee makers
		#self.start_urls = ["http://www.williams-sonoma.com/shop/electrics/coffee-makers/?cm_type=gnav"]

		

	def parse(self, response):

		items = []

		# extract site domain
		m = re.match("http://((www1?)|(shop))\.([^\.]+)\.com.*", response.url)
		if m:
			site = m.group(4)
		else:
			sys.stderr.write('Can\'t extract domain from URL.\n')
			return items

		# handle staples televisions
		if site == 'staples':
			# zipcode = "12345"

			# hxs = HtmlXPathSelector(response)
			# return Request(self.cat_page, callback = self.parsePage_staples, cookies = {"zipcode" : zipcode}, meta = {"dont_redirect" : False})
			# use selenium to complete the zipcode form and get the first results page
			driver = webdriver.Firefox()
			driver.get(response.url)

			# set a hardcoded value for zipcode
			zipcode = "12345"

			textbox = driver.find_element_by_name("zipCode")
			textbox.send_keys(zipcode)

			button = driver.find_element_by_id("submitLink")
			button.click()

			cookie = {"zipcode": zipcode}
			driver.add_cookie(cookie)

			time.sleep(5)

			# convert html to "nice format"
			text_html = driver.page_source.encode('utf-8')
			#print "TEXT_HTML", text_html
			html_str = str(text_html)

			# this is a hack that initiates a "TextResponse" object (taken from the Scrapy module)
			resp_for_scrapy = TextResponse('none',200,{},html_str,[],None)
			#resp_for_scrapy = TextResponse(html_str)

			# pass first page to parsePage function to extract products
			items += self.parsePage_staples(resp_for_scrapy)

			# use selenium to get next page, while there is a next page
			next_page = driver.find_element_by_xpath("//li[@class='pageNext']/a")
			while (next_page):
				next_page.click()
				time.sleep(5)

				# convert html to "nice format"
				text_html = driver.page_source.encode('utf-8')
				#print "TEXT_HTML", text_html
				html_str = str(text_html)

				# this is a hack that initiates a "TextResponse" object (taken from the Scrapy module)
				resp_for_scrapy = TextResponse('none',200,{},html_str,[],None)
				#resp_for_scrapy = TextResponse(html_str)

				# pass first page to parsePage function to extract products
				items += self.parsePage_staples(resp_for_scrapy)

				hxs = HtmlXPathSelector(resp_for_scrapy)
				next = hxs.select("//li[@class='pageNext']/a")
				next_page = None
				if next:
					next_page = driver.find_element_by_xpath("//li[@class='pageNext']/a")

				#TODO: this doesn't work
				# try:
				# 	next_page = driver.find_element_by_xpath("//li[@class='pageNext']/a")
				# 	break
				# except NoSuchElementException:
				# 	# if there are no more pages exit the loop
				# 	driver.close()
				# 	return items

			driver.close()

			return items

		# handle bloomingdales sneakers
		if site == 'bloomingdales':
			driver = webdriver.Firefox()
			driver.get(response.url)
			
			# use selenium to select USD currency
			link = driver.find_element_by_xpath("//li[@id='bl_nav_account_flag']//a")
			link.click()
			time.sleep(5)
			button = driver.find_element_by_id("iShip_shipToUS")
			button.click()
			time.sleep(10)

			# convert html to "nice format"
			text_html = driver.page_source.encode('utf-8')
			html_str = str(text_html)

			# this is a hack that initiates a "TextResponse" object (taken from the Scrapy module)
			resp_for_scrapy = TextResponse('none',200,{},html_str,[],None)

			# parse first page with parsePage_bloomingdales function
			items += self.parsePage_bloomingdales(resp_for_scrapy)
			hxs = HtmlXPathSelector(resp_for_scrapy)

			# while there is a next page get it and pass it to parsePage_bloomingdales
			next_page_url = hxs.select("//li[@class='nextArrow']//a")
			
			while next_page_url:

			# use selenium to click on next page arrow and retrieve the resulted page if any
				next = driver.find_element_by_xpath("//li[@class='nextArrow']//a")
				next.click()

				time.sleep(5)

				# convert html to "nice format"
				text_html = driver.page_source.encode('utf-8')
				html_str = str(text_html)

				# this is a hack that initiates a "TextResponse" object (taken from the Scrapy module)
				resp_for_scrapy = TextResponse('none',200,{},html_str,[],None)

				# pass the page to parsePage function to extract products
				items += self.parsePage_bloomingdales(resp_for_scrapy)

				hxs = HtmlXPathSelector(resp_for_scrapy)
				next_page_url = hxs.select("//li[@class='nextArrow']//a")

			driver.close()

			return items

		# works for both product list pages and higher level pages with links in the left side menu to the product links page
		if site == 'walmart':
			hxs = HtmlXPathSelector(response)

			# try to see if it's not a product page but branches into further subcategories, select "See all..." page URL
			#! this has a space after the div class, maybe in other pages it doesn't
			seeall = hxs.select("//div[@class='CustomSecondaryNav ']//li[last()]/a/@href").extract()
			if seeall:
				root_url = "http://www.walmart.com"
				page_url = root_url + seeall[0]
				# send the page to parsePage and extract product URLs
				request = Request(page_url, callback = self.parsePage_walmart)
				return request
			# if you can't find the link to the product list page, try to parse this as the product list page
			else:
				return Request(response.url, callback = self.parsePage_walmart)


		# works for both product list pages and higher level pages with links in the left side menu to the product links page
		if site == 'amazon':
			hxs = HtmlXPathSelector(response)
			# select first see more list ("All Televisions")
			seeall = hxs.select("//p[@class='seeMore'][1]/a/@href").extract()
			root_url = "http://www.amazon.com"

			# if we can find see all link, follow it and pass it to parsePage to extract product URLs
			if seeall:
				page_url = root_url + seeall[0]
				return Request(page_url, callback = self.parsePage_amazon)

			# otherwise, try to parse current page as product list page
			else:
				return Request(response.url, callback = self.parsePage_amazon)

		# works for both product list pages and higher level pages with links in the left side menu to the product links page
		if site == 'bestbuy':
			hxs = HtmlXPathSelector(response)

			# try to see if it's not a product page but branches into further subcategories, select "See all..." page URL
			seeall_list = hxs.select("//ul[@class='search']")
			if seeall_list:
				seeall = seeall_list[0].select("li[1]/a/@href").extract()
				if seeall:
					root_url = "http://www.bestbuy.com"
					page_url = root_url + seeall[0]

					# send the page to parsePage and extract product URLs
					return Request(page_url, callback = self.parsePage_bestbuy)

			# if you can't find the link to the product list page, try to parse this as the product list page
			else:
				return Request(response.url, callback = self.parsePage_bestbuy)


		if site == 'nordstrom':
			hxs = HtmlXPathSelector(response)

			return Request(response.url, callback = self.parsePage_nordstrom)

		if site == 'macys':

			hxs = HtmlXPathSelector(response)

			m = re.match("http://www1.macys.com/shop(.*)\?id=([0-9]+).*", self.cat_page)
			cat_id = 0
			if m:
				cat_id = int(m.group(2))
			productids_request = "http://www1.macys.com/catalog/category/facetedmeta?edge=hybrid&categoryId=%d&pageIndex=1&sortBy=ORIGINAL&productsPerPage=40&" % cat_id
			return Request(productids_request, callback = self.parse_macys, headers = {"Cookie" : "shippingCountry=US"}, meta={'dont_merge_cookies': True, "cat_id" : cat_id, "page_nr" : 1})

		if site == 'williams-sonoma':

			return Request(url = self.cat_page, callback = self.parsePage_sonoma)

	# parse macy's category
	def parse_macys(self, response):
		
		json_response = json.loads(unicode(response.body, errors='replace'))
		product_ids = json_response['productIds']

		# if there are any product ids parse them and go to the next page
		# (if there are no product ids it means the current page is empty and we stop)
		if product_ids:
			cat_id = response.meta['cat_id']

			product_ids2 = [str(cat_id) + "_" + str(product_id) for product_id in product_ids]
			product_ids_string = ",".join(product_ids2)

			products_page = "http://www1.macys.com/shop/catalog/product/thumbnail/1?edge=hybrid&limit=none&suppressColorSwatches=false&categoryId=%d&ids=%s" % (cat_id, product_ids_string)
			# parse products from this page
			request = Request(products_page, callback = self.parsePage_macys, headers = {"Cookie" : "shippingCountry=US"}, meta={'dont_merge_cookies': True, "cat_id" : cat_id})
			yield request

			# send a new request for the next page
			page = int(response.meta['page_nr']) + 1
			next_page = re.sub("pageIndex=[0-9]+", "pageIndex=" + str(page), response.url)
			request = Request(next_page, callback = self.parse_macys, headers = {"Cookie" : "shippingCountry=US"}, meta={'dont_merge_cookies': True, "cat_id" : cat_id, "page_nr" : page})
			yield request

	# parse macy's page and extract product URLs
	def parsePage_macys(self, response):
		hxs = HtmlXPathSelector(response)

		products = hxs.select("//div[@class='shortDescription']/a")

		items = []
		root_url = "http://www1.macys.com"
		for product in products:
			item = ProductItem()
			item['product_url'] = root_url + product.select("@href").extract()[0]
			items.append(item)

		return items


	# parse williams-sonoma page and extract product URLs
	def parsePage_sonoma(self, response):
		hxs = HtmlXPathSelector(response)
		products = hxs.select("//li[@class='product-cell ']/a")
		items = []

		for product in products:
			item = ProductItem()
			item['product_url'] = product.select("@href").extract()[0]
			items.append(item)

		return items

	# parse staples page and extract product URLs
	def parsePage_staples(self, response):

		hxs = HtmlXPathSelector(response)

		products = hxs.select("//a[@class='url']")
		root_url = "http://www.staples.com"
		items = []

		for product in products:

			item = ProductItem()
			item['product_url'] = root_url + product.select("@href").extract()[0]
			items.append(item)

		return items

	# parse bloomingdales page and extract product URLs
	def parsePage_bloomingdales(self, response):
		hxs = HtmlXPathSelector(response)
		items = []
		products = hxs.select("//div[@class='shortDescription']")
		for product in products:
			item = ProductItem()
			item['product_url'] = product.select("a/@href").extract()[0]
			items.append(item)
		return items

	# parse walmart page and extract product URLs
	def parsePage_walmart(self, response):
		hxs = HtmlXPathSelector(response)
		root_url = "http://www.walmart.com"
		product_links = hxs.select("//a[@class='prodLink ListItemLink']/@href")

		for product_link in product_links:
			item = ProductItem()
			item['product_url'] = root_url + product_link.extract()
			yield item

		# select next page, if any, parse it too with this method
		next_page = hxs.select("//a[@class='link-pageNum' and text()=' Next ']/@href").extract()
		if next_page:
			page_url = root_url + next_page[0]
			yield Request(url = page_url, callback = self.parsePage_walmart)

	# parse walmart page and extract product URLs
	def parsePage_amazon(self, response):
		hxs = HtmlXPathSelector(response)
		product_links = hxs.select("//h3[@class='newaps']/a/@href")
		for product_link in product_links:
			item = ProductItem()
			item['product_url'] = product_link.extract()
			yield item

		# select next page, if any, parse it too with this method
		root_url = "http://www.amazon.com"
		next_page = hxs.select("//a[@title='Next Page']/@href").extract()
		if next_page:
			page_url = root_url + next_page[0]
			yield Request(url = page_url, callback = self.parsePage_amazon)

	# parse bestbuy page and extract product URLs
	def parsePage_bestbuy(self, response):
		hxs = HtmlXPathSelector(response)
		root_url = "http://www.bestbuy.com"

		# extract product URLs
		product_links = hxs.select("//div[@class='info-main']/h3/a/@href")
		for product_link in product_links:
			item = ProductItem()
			item['product_url'] = root_url + product_link.extract()
			yield item

		# select next page, if any, parse it too with this method
		next_page = hxs.select("//ul[@class='pagination']/li/a[@class='next']/@href").extract()
		if next_page:
			page_url = root_url + next_page[0]
			yield Request(url = page_url, callback = self.parsePage_bestbuy)

	# parse nordstrom page and extract URLs
	def parsePage_nordstrom(self, response):
		hxs = HtmlXPathSelector(response)
		root_url = "http://shop.nordstrom.com"

		# extract product URLs
		product_links = hxs.select("//div/a[@class='title']/@href")
		for product_link in product_links:
			item = ProductItem()
			item['product_url'] = root_url + product_link.extract()
			yield item

		# select next page, if any, parse it too with this method
		next_page = hxs.select("//ul[@class='arrows']/li[@class='next']/a/@href").extract()
		if next_page:
			page_url = next_page[0]
			yield Request(url = page_url, callback = self.parsePage_nordstrom)


	# parse macys page and extract URLs
	def parsePage_macys(self, response):
		hxs = HtmlXPathSelector(response)
		root_url = "http://www1.macys.com"

		# extract product URLs
		product_links = hxs.select("//div[@class='shortDescription']/a/@href")
		for product_link in product_links:
			item = ProductItem()
			item['product_url'] = root_url + product_link.extract()
			yield item


