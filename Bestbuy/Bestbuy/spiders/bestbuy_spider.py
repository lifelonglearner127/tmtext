from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Bestbuy.items import BestbuyItem
import sys

################################
# Run with 
#
# scrapy crawl bestbuy
#
################################


class BestbuySpider(BaseSpider):
    name = "bestbuy"
    allowed_domains = ["bestbuy.com"]
    start_urls = [
        "http://www.bestbuy.com/site/sitemap.jsp",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//div[@id='container']/div/header//nav/ul[@id='nav']//a")
        items = []

        #TODO: implement parents
        for link in links:
            item = BestbuyItem()
            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()
            items.append(item)

        return items
