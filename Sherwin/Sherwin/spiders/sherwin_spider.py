from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Sherwin.items import CategoryItem
from Sherwin.items import ProductItem
from scrapy.http import Request
from scrapy.http import Response
import re
import sys

from spiders_utils import Utils

################################
# Run with 
#
# scrapy crawl sherwin
#
################################

# crawls sitemap and extracts department and categories names and urls (as well as other info)
class SherwinSpider(BaseSpider):
	name = "sherwin"
	allowed_domains = ["sherwin-williams.com"]
	start_urls = [
		"https://www.sherwin-williams.com/sitemap/",
	]

	base_url = "http://www.sherwin-williams.com"

	def parse(self, response):
		hxs = HtmlXPathSelector(response)

		# extract departments
		departments = hxs.select("//h2")
		department_id = 0
		for department in departments:
			item = CategoryItem()
			department_text = department.select("text()").extract()[0]
			item['department_text'] = department_text

			#TODO: add department_url, from sherwin-williams.com ...? get department list from there and match with departments from here by seeing if names match

			item['department_id'] = department_id

			item['text'] = department_text

			#TODO
			#item['url'] = 
			item['level'] = 1

			# return item
			yield item

			# get categories in department
			#TODO: this is wrong, gets categories for all departments below this point
			categories = department.select("following-sibling::ul[1]/li")
			for category in categories:
				item = CategoryItem()
				#TODO: special if 'Services'? or Specifications, or Ads...
				category_text = category.select("a/text()").extract()[0]
				category_url =  Utils.add_domain(category.select("a/@href").extract()[0], self.base_url)
				item['text'] = category_text
				item['url'] = category_url

				item['department_id'] = department_id
				item['department_text'] = department_text
				#TODO
				# item['department_url'] = 

				item['parent_text'] = department_text
				#TODO
				# item['parent_url'] = 

				item['level'] = 0

				#TODO: do we need description_wc here as well?

				yield Request(item['url'], callback = self.parseCategory, meta = {'item' : item})

				# get subcategories in category
				subcategories = category.select("ul/li")
				for subcategory in subcategories:
					item = CategoryItem()

					item['text'] = subcategory.select("a/text()").extract()[0]
					item['url'] = Utils.add_domain(subcategory.select("a/@href").extract()[0], self.base_url)

					item['department_id'] = department_id
					item['department_text'] = department_text
					#TODO
					# item['department_url'] = 

					item['parent_text'] = category_text
					item['parent_url'] = category_url

					item['level'] = -1

					yield Request(item['url'], callback = self.parseSubcategory, meta = {'item' : item})

			department_id += 1

	def parseCategory(self, response):
		hxs = HtmlXPathSelector(response)

		item = response.meta['item']

		#TODO: test if this xpath should include other types of pages
		description_text_holder = hxs.select("//p[@class='subtitle grey']/text()").extract()
		description_title_holder = hxs.select("//h1/text()[normalize-space()!='']").extract()

		if description_text_holder:
			item['description_text'] = description_text_holder[0]
			item['description_title'] = description_title_holder[0]

			description_tokenized = Utils.normalize_text(item['description_text'])
			item['description_wc'] = len(description_tokenized)

			(item['keyword_count'], item['keyword_density']) = Utils.phrases_freq(item['description_title'], item['description_text'])
		else:
			item['description_wc'] = 0

		#TODO: add product count?

		yield item

	#TODO: check if pages on the same level always look the same, like I assumed. if not, do it recursively (not with 3 functions, but 1)

	def parseSubcategory(self, response):
		hxs = HtmlXPathSelector(response)

		subcategory = response.meta['item']

		# get its subcategories
		subsubcategories = hxs.select("//div[@class='product-category-expanded']//h3[@class='title']")
		for subsubcategory in subsubcategories:
			item = CategoryItem()
			item['text'] = subsubcategory.select("a/text()").extract()[0]
			item['url'] = Utils.add_domain(subsubcategory.select("a/@href").extract()[0], self.base_url)

			item['parent_text'] = subcategory['text']
			item['parent_url'] = subcategory['url']
			item['department_text'] = subcategory['department_text']
			# item['department_url'] = subcategory['department_url']
			item['department_id'] = subcategory['department_id']

			item['level'] = subcategory['level'] - 1

			description_text_holder = subsubcategory.select("following-sibling::p[@class='description'][1]/text()").extract()
			if description_text_holder:
				item['description_text'] = description_text_holder[0]
				item['description_title'] = item['text']
				description_tokenized = Utils.normalize_text(item['description_text'])
				item['description_wc'] = len(description_tokenized)

				(item['keyword_count'], item['keyword_density']) = Utils.phrases_freq(item['description_title'], item['description_text'])

			else:
				item['description_wc'] = 0

			# parse subsubcategory page to get product count
			yield Request(item['url'], callback = self.parseSubsubcategory, meta = {'item' : item})

	def parseSubsubcategory(self, response):
		hxs = HtmlXPathSelector(response)
		item = response.meta['item']

		#TODO: test
		product_count_holder = hxs.select("//li[@class='count']//text()[normalize-space()!='']").re("(?<=of )[0-9]+")

		if product_count_holder:
			item['nr_products'] = int(product_count_holder[0])

		#TODO: else - there must be another subcategory - parse it! example: http://www.sherwin-williams.com/home-builders/products/catalog/categories/exterior-paint-coatings/floor-coatings-exterior/

		yield item