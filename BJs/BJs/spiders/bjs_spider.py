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

        for link in links:

            # extract parent category
            parent = link.select("parent::node()/parent::node()/parent::node()/div/div[position()=1]/a")

            item = BjsItem()
            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()

            item['parent_text'] = parent.select('h2/text()').extract()
            item['parent_url'] = parent.select('@href').extract()

            items.append(item)

        return items
