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


################################
# Run with 
#
# scrapy crawl tesco -a cat_page="<url>" [-a outfile="<filename>" -a brands_file="<brands_filename>"]
# 
# (if specified, brands_filename contains list of brands that should be considered - one brand on each line. other brands will be ignored)
#
################################


class TescoSpider(CaturlsSpider):

	name = "tesco"
	allowed_domains = ["tesco.com"]

	# tesco haircare
	#self.start_urls = ["http://www.tesco.com/direct/health-beauty/hair-care/cat3376671.cat?catId=4294961777"]

	# add brand option
	def __init__(self, cat_page, outfile = "product_urls.txt", use_proxy = False, brands_file=None):
		super(TescoSpider, self).__init__(cat_page=cat_page, outfile=outfile, use_proxy=use_proxy)

		self.base_url = "http://www.tesco.com"

		self.brands = []
		self.brands_normalized = []
		# if a file with a list of specific brands is specified, add them to a class field
		if brands_file:
			brands_file_h = open(brands_file, "r")
			for line in brands_file_h:
				self.brands.append(line.strip())
			brands_file_h.close()

			self.brands_normalized = reduce(lambda x, y: x+y, map(lambda x: self.brand_versions_fuzzy(x), self.brands))

	# parse category page - extract subcategories, send their url to be further parsed (to parseSubcategory)
	def parse(self, response):
		hxs = HtmlXPathSelector(response)

		subcats_links = hxs.select("//h2[contains(text(),'categories')]/following-sibling::ul[1]/li/a/@href").extract()
		# add domain
		subcats_urls = map(lambda x: Utils.add_domain(x, self.base_url), subcats_links)

		# send subcategories to be further parsed
		for subcat in subcats_urls:
			yield Request(url = subcat, callback = self.parseSubcategory)

	# parse subcategory page - extract urls to brands menu page; or directly to brands pages (if all available on the page)
	def parseSubcategory(self, response):
		hxs = HtmlXPathSelector(response)

		#print "SUBCATEGORY:", response.url

		# extract link to page containing brands (look for link to 'more')
		brands_menu_page = hxs.select("//h4[contains(text(),'Brand')]/following-sibling::ul[1]/li[@class='more']/a/@data-overlay-url").extract()

		if brands_menu_page:
			# send request for brands pages to be extracted
			yield Request(url = Utils.add_domain(brands_menu_page[0], self.base_url), callback = self.parseBrandsMenu)
		else:

			# if no 'more' link, extract brand pages directly from this page (it means they are all here)
			brands_pages = hxs.select("//h4[contains(text(),'Brand')]/following-sibling::ul[1]/li/a")

			for brand_page in brands_pages:
				brand_name = brand_page.select("span[@class='facet-str-name']/text()").extract()[0]
				brand_url = Utils.add_domain(brand_page.select("@href").extract()[0], self.base_url)

				# filter brands if it applies
				if self.brands and not self.name_matches_brands(brand_name):
					self.log("Omitting brand " + brand_name, level=log.INFO)
					continue

				# send request for brands page to be parsed and its products extracted
				yield Request(url = brand_url, callback = self.parseBrandPage)



	# extract each brand page, apply brand filter if option set; send page urls to be further prsed for product urls
	def parseBrandsMenu(self, response):
		hxs = HtmlXPathSelector(response)

		# extract links to brands pages
		brands_links = hxs.select("//ul/li/a")
		for brand_link in brands_links:
			brand_name = brand_link.select("@data-facet-option-value").extract()[0]

			# filter brands if it applies
			if self.brands and not self.name_matches_brands(brand_name):
				self.log("Omitting brand " + brand_name, level=log.INFO)
				continue

			# build brand url
			try:

				# extract brand id
				brand_id = brand_link.select("@data-facet-option-id").extract()[0]
				# extract base url for brand page
				brand_base_url = Utils.add_domain(hxs.select("//form/@action").extract()[0], self.base_url)
				# extract relative url parameters for brand page
				brand_relative_url_params = hxs.select("//input/@value").extract()[0]
				# extract catId parameter
				cat_id_param = re.findall("catId=[0-9]+(?=&|$)", brand_relative_url_params)[0]
				# build brand page
				brand_page_url = brand_base_url + "?" + cat_id_param + "+" + str(brand_id)

				#print brand_page_url

				yield Request(url = brand_page_url, callback = self.parseBrandPage)

			except Exception, e:
				self.log("Couldn't extract brand page from menu: " + e, level=log.ERROR)


	# parse a brand's page and extract product urls
	def parseBrandPage(self, response):
		hxs = HtmlXPathSelector(response)

		# extract product holder. not extracting <a> element directly because each product holder has many a elements (all just as good, but we only want one)
		product_holders = hxs.select("//div[@class='product ']")
		for product_holder in product_holders:
			# extract first link in product holder
			product_link = product_holder.select(".//a/@href").extract()[0]
			product_url = Utils.add_domain(product_link, self.base_url)

			item = ProductItem()
			item['product_url'] = product_url

			yield item

			#TODO: pagination support?

