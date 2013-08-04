from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import TextResponse
from Caturls.items import ProductItem

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time
import re

################################
# Run with 
#
# scrapy crawl producturls -a cat_page="<url>"
#
################################


# search for a product in all sites, using their search functions; give product as argument by its name or its page url
class CaturlsSpider(BaseSpider):

	name = "producturls"
	allowed_domains = ["staples.com", "bloomingdales.com", "walmart.com"]

	# store the cateory page url given as an argument into a field and add it to the start_urls list
	def __init__(self, cat_page):
		self.cat_page = cat_page
		self.start_urls = [cat_page]
		# staples televisions
		#self.start_urls = ["http://www.staples.com/Televisions/cat_CL142471"]
		# bloomingdales sneakers
		#self.start_urls = ["http://www1.bloomingdales.com/shop/shoes/sneakers?id=17400"]
		# walmart televisions
		#self.start_urls = ["http://www.walmart.com/cp/televisions-video/1060825?povid=P1171-C1110.2784+1455.2776+1115.2956-L13"]
		

	def parse(self, response):

		items = []

		# extract site domain
		m = re.match("http://www1?\.([^\.]+)\.com.*", response.url)
		if m:
			site = m.group(1)
		else:
			sys.stderr.write('Can\'t extract domain from URL.\n')
			return items

		# handle staples televisions
		if site == 'staples':
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
			items += self.parsePage(resp_for_scrapy)

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

				next_page = None
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

	# parse staples page and extract product URLs
	def parsePage_staples(self, response):

		hxs = HtmlXPathSelector(response)

		products = hxs.select("//a[@class='url']")
		items = []

		for product in products:

			item = ProductItem()
			root_url = "http://www.staples.com"
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
		
		items = []
		hxs = HtmlXPathSelector(response)
		root_url = "http://www.walmart.com"
		product_links = hxs.select("//a[@class='prodLink ListItemLink']/@href")

		for product_link in product_links:
			item = ProductItem()
			item['product_url'] = root_url + product_link.extract()
			print item['product_url']
			yield item
			#items.append(item)


		# select next page, if any, parse it too with this method
		next_page = hxs.select("//a[@class='link-pageNum' and text()=' Next ']/@href").extract()
		if next_page:
			page_url = root_url + next_page[0]
			yield Request(url = page_url, callback = self.parsePage_walmart)

		#return items
