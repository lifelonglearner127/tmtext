from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Tigerdirect.items import TigerdirectItem
import sys

################################
# Run with 
#
# scrapy crawl tigerdirect
#
################################


class TigerdirectSpider(BaseSpider):
    name = "tigerdirect"
    allowed_domains = ["tigerdirect.com"]
    start_urls = [
        "http://www.tigerdirect.com/computerproducts.asp",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//table//tr[1]/td//a[ancestor::h4 | ancestor::ul]")
        items = []

        #TODO: implement parents
        for link in links:
            item = TigerdirectItem()
            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()
            items.append(item)

        return items
