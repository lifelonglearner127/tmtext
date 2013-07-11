from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Walmart.items import WalmartItem
import sys

################################
# Run with 
#
# scrapy crawl walmart
#
################################


class WalmartSpider(BaseSpider):
    name = "walmart"
    allowed_domains = ["walmart.com"]
    start_urls = [
        "http://www.walmart.com/cp/All-Departments/121828",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//div[@class='MidContainer']/div[3]//a[@class='NavM']")
        parent_links = hxs.select("//div[@class='MidContainer']/div[3]//a[@class='NavXLBold']")
        items = []

        for link in links:
            item = WalmartItem()

            # search for the category's parent
            parents = []

            # select the preceding siblings that are a category title (have a child that is an a tag with a certain class)
            parents = link.select('parent::node()').select('preceding-sibling::node()').select('child::a[@class=\'NavXLBold\']')

            # if we found such siblings, get the last one to be the parent
            if parents:
                item['parent_text'] = parents[-1].select('text()').extract()[0]
                item['parent_url'] = parents[-1].select('@href').extract()[0]

            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()

            item['level'] = 0

            items.append(item)

        for link in parent_links:
            item = WalmartItem()

            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()

            item['level'] = 1

            items.append(item)

        return items
