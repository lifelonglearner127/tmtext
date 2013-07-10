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
        # currently selecting bottom level categories, and their parents and parents of parents ("grandparents") in their fields
        links = hxs.select("//div[@id='sitemap']//li[@class='bullet3']//a")
        items = []

        #TODO: implement grandparents
        for link in links:

            # extract immediate parent of this link (first preceding sibling (of the parent) with class='bullet2')
            parent = link.select("parent::node()/preceding-sibling::*[@class='bullet2'][1]/a")

            item = OverstockItem()
            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()

            item['parent_text'] = parent.select('text()').extract()
            item['parent_url'] = parent.select('@href').extract()

            items.append(item)

        return items
