from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Bloomingdales.items import BloomingdalesItem
import sys

################################
# Run with 
#
# scrapy crawl bloomingdales
#
################################


class BloomingdalesSpider(BaseSpider):
    name = "bloomingdales"
    allowed_domains = ["bloomingdales.com"]
    start_urls = [
        "http://www1.bloomingdales.com/service/sitemap/index.ognc?cm_sp=NAVIGATION-_-BOTTOM_LINKS-_-SITE_MAP",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//div[@class='sr_siteMap_container']/div[position()>2 and position()<5]//a")
        items = []

        for link in links:
            item = BloomingdalesItem()
            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()
            items.append(item)

        return items
