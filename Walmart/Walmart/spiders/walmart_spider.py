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
        "http://www.amazon.com/gp/site-directory/ref=sa_menu_top_fullstore",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//div[@class='MidContainer']/div[3]//a")
        items = []

        for link in links:
            item = WalmartItem()
            # select the preceding siblings that are a category title (have a child that is an a tag with a certain class)
            #TODO: right now it selects them for parents node too, to be fixed
            parent = link.select('parent::node()').select('preceding-sibling::node()').select('child::a[@class=\'NavXLBold\']')
            # if we found such siblings, get the last one to be the parent
            if parent:
                item['parent_text'] = parent[-1].select('text()').extract()
                item['parent_url'] = parent[-1].select('@href').extract()
            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()
            items.append(item)

        return items
