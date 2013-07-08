from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from BJs.items import BjsItem
import sys

################################
# Run with 
#
# scrapy crawl bjs
#
################################


class BJsSpider(BaseSpider):
    name = "bjs"
    allowed_domains = ["bjs.com"]
    start_urls = [
        "http://www.bjs.com/webapp/wcs/stores/servlet/SiteMapView?langId=-1&storeId=10201&catalogId=10001",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//div[@class='links']//a")
        items = []

        #TODO: implement parents: right now it only selects lowest level links
        for link in links:
            item = BjsItem()
            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()
            items.append(item)

        return items
