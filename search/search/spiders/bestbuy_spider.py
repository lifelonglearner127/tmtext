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

    # initialize fields specific to this derived spider
    def init_sub(self):
        self.target_site = "bestbuy"
        self.start_urls = [ "http://www.bestbuy.com" ]

    def parseResults(self, response):

        hxs = HtmlXPathSelector(response)

        #site = response.meta['origin_site']
        origin_name = response.meta['origin_name']
        origin_model = response.meta['origin_model']
        origin_url = response.meta['origin_url']

        # if this comes from a previous request, get last request's items and add to them the results

        if 'items' in response.meta:
            items = response.meta['items']
        else:
            items = set()


        results = hxs.select("//div[@class='list-item-info']/div[@class='sku-title']/h4/a")

        for result in results:
            item = SearchItem()
            #item['origin_site'] = site
            product_name_holder = result.select("text()").extract()
            if product_name_holder:
                item['product_name'] = product_name_holder[0].strip()
            else:
                self.log("Error: No product name: " + str(response.url) + " from product: " + origin_url, level=log.ERROR)

            item['product_url'] = Utils.clean_url(Utils.add_domain(result.select("@href").extract()[0], "http://www.bestbuy.com"))

            if 'origin_url' in response.meta:
                item['origin_url'] = response.meta['origin_url']

            if 'origin_name' in response.meta:
                item['origin_name'] = response.meta['origin_name']

            if 'origin_model' in response.meta:
                item['origin_model'] = response.meta['origin_model']                

            model_holder = result.select("../../../div[@class='sku-model']/ul/li[@class='model-number']/span[@id='model-value']/text()").extract()
            if model_holder:
                item['product_model'] = model_holder[0]

            price_holder = result.select("../../../../div[@class='list-item-price']//div[@class='price-block']//div[@class='medium-item-price']/text()[normalize-space()]").extract()
            if price_holder:
                price = price_holder[0].strip()
                price = re.sub(",", "", price)
                price = float(price)
                item['product_target_price'] = price

            items.add(item)

        response.meta['items'] = items
        response.meta['parsed'] = items
        return self.reduceResults(response)