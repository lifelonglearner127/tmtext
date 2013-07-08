from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Wayfair.items import WayfairItem
import sys

################################
# Run with 
#
# scrapy crawl wayfair
#
################################


class WayfairSpider(BaseSpider):
    name = "wayfair"
    allowed_domains = ["wayfair.com"]
    start_urls = [
        "http://www.wayfair.com/site_map.php",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//div[@id='yui-main']//a")
        items = []

        #TODO: implement parents
        for link in links:
            item = WayfairItem()
            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()
            items.append(item)

        return items
