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

class BestbuySpider(SearchSpider):

	name = "bestbuy"

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


		results = hxs.select("//div[@class='hproduct']/div[@class='info-main']/h3/a")

		for result in results:
			item = SearchItem()
			item['site'] = site
			item['product_name'] = result.select("text()").extract()[0].strip()
			item['product_url'] = Utils.clean_url(Utils.add_domain(result.select("@href").extract()[0], "http://www.bestbuy.com"))

			if 'origin_url' in response.meta:
				item['origin_url'] = response.meta['origin_url']

			if 'origin_id' in response.meta:
				request.meta['origin_id'] = response.meta['origin_id']
				assert self.by_id
			else:
				assert not self.by_id


			model_holder = result.select("parent::node()/parent::node()//strong[@itemprop='model']/text()").extract()
			if model_holder:
				item['product_model'] = model_holder[0]

			items.add(item)