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
        links = hxs.select("//div[@class='MidContainer']/div[3]//a")
        items = []

        for link in links:
            item = WalmartItem()

            # if it's a bottom level category search for its parent
            parents = []

            # check class of a tag and use it to determine if the category has a parent
            cat_type = link.select('@class').extract()[0]
            if cat_type.decode('utf-8') == 'NavM':
            # select the preceding siblings that are a category title (have a child that is an a tag with a certain class)
                parents = link.select('parent::node()').select('preceding-sibling::node()').select('child::a[@class=\'NavXLBold\']')

            # if we found such siblings, get the last one to be the parent
            if parents:
                item['parent_text'] = parents[-1].select('text()').extract()
                item['parent_url'] = parents[-1].select('@href').extract()

            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()
            items.append(item)

        return items
