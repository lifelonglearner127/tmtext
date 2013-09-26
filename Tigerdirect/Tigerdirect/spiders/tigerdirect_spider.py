from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Tigerdirect.items import TigerdirectItem
from scrapy.http import Request
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
        links = hxs.select("//table//tr[1]/td//a[ancestor::h4]")

        for link in links:
            item = TigerdirectItem()
            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]
            yield Request(url = item['url'], callback = self.parseCategory, meta = {'item' : item})

    # receive one category url, add aditional info and return it; then extract its subcategories and parse them as well
    def parseCategory(self, response):
        hxs = HtmlXPathSelector(response)

        item = response.meta['item']

        # extract number of products if available
        nrproducts_holder = hxs.select("//div[@class='resultsfilterBottom']/div[@class='itemsShowresult']/strong[2]/text()").extract()
        if nrproducts_holder:
            item['nr_products'] = int(nrproducts_holder[0])

        # extract description if available
        desc_holder = hxs.select("//div[@class='textBlock']")


        yield item

        #TODO
        # extract subcategories
        parent = item