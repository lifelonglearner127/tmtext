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
        # currently extracting bottom level categories, and their parents and grandparents in their fields
        links = hxs.select("//div[@class='categories']/ul/li/ul/li/ul/li/a")
        items = []

        for link in links:
            #TODO: add grandparent extraction (broadest categories)

            # extracting parents and parents of parents ("grandparents")
            parent = link.select('parent::node()/parent::node()/parent::node()/a')
            
            item = WayfairItem()
            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()

            item['parent_text'] = parent.select('text()').extract()
            item['parent_url'] = parent.select('@href').extract()

            items.append(item)

        return items
