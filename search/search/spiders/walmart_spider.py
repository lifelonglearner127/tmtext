from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
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

class WalmartSpider(SearchSpider):

	name = "walmart"

	# initialize fields specific to this derived spider
	def init_sub(self):
		self.target_site = "walmart"
		self.start_urls = [ "http://www.walmart.com" ]

	def parseResults(self, response):


		hxs = HtmlXPathSelector(response)

		site = response.meta['site']
		origin_name = response.meta['origin_name']
		origin_model = response.meta['origin_model']

		# if this comes from a previous request, get last request's items and add to them the results

		if 'items' in response.meta:
			items = response.meta['items']
		else:
			items = set()



		results = hxs.select("//div[@class='prodInfo']/div[@class='prodInfoBox']/a[@class='prodLink ListItemLink']")
		for result in results:
			item = SearchItem()
			item['site'] = site
			product_name = result.select(".//text()").extract()[0]
			# append text that is in <span> if any
			span_text = result.select("./span/text()")

			#TODO: use span text differently, as it is more important/relevant (bold) ?
			for text in span_text:
				product_name += " " + text.extract()
			item['product_name'] = product_name
			rel_url = result.select("@href").extract()[0]
			
			root_url = "http://www.walmart.com"
			item['product_url'] = Utils.add_domain(rel_url, root_url)

			if 'origin_url' in response.meta:
				item['origin_url'] = response.meta['origin_url']

			if 'origin_id' in response.meta:
				request.meta['origin_id'] = response.meta['origin_id']
				assert self.by_id
			else:
				assert not self.by_id


			items.add(item)

		response.meta['items'] = items
		response.meta['parsed'] = items
		return self.reduceResults(response)