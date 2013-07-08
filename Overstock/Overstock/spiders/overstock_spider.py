from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Overstock.items import OverstockItem
import sys

################################
# Run with 
#
# scrapy crawl overstock
#
################################


class OverstockSpider(BaseSpider):
    name = "overstock"
    allowed_domains = ["overstock.com"]
    start_urls = [
        "http://www.overstock.com/sitemap",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//div[@id='sitemap']//li[@class='bullet3']//a")
        items = []

        #TODO: implement parents: we are only selecting lowest level links for now
        for link in links:
            item = OverstockItem()
            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()
            items.append(item)

        return items
