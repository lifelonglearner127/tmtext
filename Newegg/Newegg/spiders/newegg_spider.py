from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Newegg.items import CategoryItem
from Newegg.items import ProductItem
from scrapy.http import Request
import re
import sys
import datetime

from spiders_utils import Utils

################################
# Run with 
#
# scrapy crawl newegg
#
################################

# crawl sitemap and extract products and categories
class NeweggSpider(BaseSpider):
    name = "newegg"
    allowed_domains = ["newegg.com"]
    start_urls = ["http://www.newegg.com"]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        items = []
        category_links = hxs.select("//div[@class='itmNav']//a")
        for category_link in category_links:

            item = CategoryItem()
            item['text'] = category_link.select("text()").extract()[0]
            item['url'] = category_link.select("@href").extract()[0]
            # mark as department
            item['level'] = 1
            items.append(item)

        return items