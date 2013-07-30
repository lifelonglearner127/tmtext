from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import TextResponse
from Caturls.items import ProductItem

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time

################################
# Run with 
#
# scrapy crawl producturls -a cat_page="<url>"
#
################################


# search for a product in all sites, using their search functions; give product as argument by its name or its page url
class SearchSpider(BaseSpider):

	name = "producturls"
	allowed_domains = ["staples.com"]

	# store the cateory page url given as an argument into a field and add it to the start_urls list
	def __init__(self, cat_page):
		self.cat_page = cat_page
		#self.start_urls = [cat_page]
		self.start_urls = ["http://www.staples.com/Televisions/cat_CL142471"]
		

	def parse(self, response):

		items = []

		# use selenium to complete the zipcode form and get the first results page
		driver = webdriver.Firefox()
		driver.get("http://www.staples.com/Televisions/cat_CL142471")

		textbox = driver.find_element_by_name("zipCode")
		textbox.send_keys("12345")

		button = driver.find_element_by_id("submitLink")
		button.click()

		cookie = {"zipcode": "12345"}
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
		#while (next_page):
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
		items += self.parsePage(resp_for_scrapy)

			#next_page = driver.find_element_by_xpath("//li[@class='pageNext']/a")

		driver.close()

		return items

		#print "HTML_STR:", html_str


	def parsePage(self, response):

		hxs = HtmlXPathSelector(response)

		#print "URL:", response.url, resp_for_scrapy.url
		#products = hxs.select("//ul[@class='productDetail']//div[@class='name']/h3/a[@class='url']")
		products = hxs.select("//a[@class='url']")
		#products = hxs.select("//body")
		if not products:
			print "NO PRODUCTS"

		items = []

		for product in products:

			item = ProductItem()
			root_url = "http://www.staples.com"
			item['product_url'] = root_url + product.select("@href").extract()[0]
			#item['product_url'] = product.select["@id"].extract()

			#TODO implement pages
			items.append(item)

		return items