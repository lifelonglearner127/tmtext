from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import TextResponse
from Staples.items import CategoryItem

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time
import re

################################
# Run with 
#
# scrapy crawl staples
#
################################


# search for a product in all sites, using their search functions; give product as argument by its name or its page url
class StaplesSpider(BaseSpider):

	name = "staples"
	allowed_domains = ["staples.com"]
	# use one random category page as the root page to extract departments
	start_urls = ["http://www.staples.com/Televisions/cat_CL142471"]


	def parse(self, response):

		
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

		driver.close()

		# parse department list
		items = self.parseList(resp_for_scrapy)

		return items

	def parseList(self, response):
		hxs = HtmlXPathSelector(response)
		
		items = []
		# add all department names
		departments = hxs.select("//div[@id='showallprods']/ul/li/a")

		root_url = "http://www.staples.com"

		for department in departments:
			item = CategoryItem()

			item['text'] = department.select("text()").extract()[0]
			item['url'] = root_url + department.select("@href").extract()[0]
			item['level'] = 1


			# parse each department page for its categories, pass the department item too so that it's added to the list in parseDept
			yield Request(item['url'], callback = self.parseDept, meta = {"department": item})


	def parseDept(self, response):

		# for "copy & print" there's an exception, we don't need zipcode

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


		hxs = HtmlXPathSelector(resp_for_scrapy)
		categories = hxs.select("//h2/a")

		root_url = "http://www.staples.com"

		items = []
		items.append(response.meta['department'])

		for category in categories:
			# there are pages that don't have categories
			item = CategoryItem()
			text = category.select("text()").extract()
			if text:
				item['text'] = text[0]
			url = category.select("@href").extract()
			if url:
				item['url'] = root_url + url[0]
			item['level'] = 0
			item['parent_text'] = response.meta['department']['text']
			item['parent_url'] = response.url

			items.append(item)

		driver.close()

		return items