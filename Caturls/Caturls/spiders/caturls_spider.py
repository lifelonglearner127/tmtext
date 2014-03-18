from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import TextResponse
from Caturls.items import ProductItem
from pprint import pprint
from scrapy import log

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from spiders_utils import Utils

import time
import re
import sys
import json



################################
# 
#
# Abstract spider class
#
################################


# search for a product in all sites, using their search functions; give product as argument by its name or its page url
class CaturlsSpider(BaseSpider):

	name = "producturls"
	allowed_domains = ["staples.com", "bloomingdales.com", "walmart.com", "amazon.com", "bestbuy.com", \
	"nordstrom.com", "macys.com", "williams-sonoma.com", "overstock.com", "newegg.com", "tigerdirect.com"]

	# store the cateory page url given as an argument into a field and add it to the start_urls list
	def __init__(self, cat_page, outfile = "product_urls.txt", use_proxy = False):
		self.cat_page = cat_page
		self.start_urls = [cat_page]
		self.outfile = outfile
		self.use_proxy = use_proxy

		# keep track of parsed pages to avoid duplicates
		# used for newegg motherboards
		self.parsed_pages = []
