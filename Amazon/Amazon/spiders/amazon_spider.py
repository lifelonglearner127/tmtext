from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Amazon.items import AmazonItem
import sys

################################
# Run with 
#
# scrapy crawl amazon
#
################################


class AmazonSpider(BaseSpider):
    name = "amazon"
    allowed_domains = ["amazon.com"]
    start_urls = [
        "http://www.amazon.com/gp/site-directory/ref=sa_menu_top_fullstore",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//div[@id='siteDirectory']//table//a")
        items = []

        for link in links:
            item = AmazonItem()
            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()

            parent = link.select("parent::node()/parent::node()/preceding-sibling::node()")
            item['parent_text'] = parent.select('text()').extract()

            items.append(item)

        return items
