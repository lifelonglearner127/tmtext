from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from Sears.items import SearsItem
import sys
import string

################################
# Run with 
#
# scrapy crawl sears
#
################################


class SearsSpider(BaseSpider):
    name = "sears"
    allowed_domains = ["sears.com"]

    start_urls = ['http://www.sears.com/shc/s/smv_10153_12605']

    
    def parse(self, response):

        hxs = HtmlXPathSelector(response)

        # get urls of pages for each category
        urls = hxs.select("//div[@class='siteMapSubCell']//ul/li/a/@href").extract()

        # parse each page in urls list with parsePage
        # build urls by adding the prefix of the main page url
        root_url = "http://www.sears.com/shc/s"
        for url in [urls[0]]:
            yield Request(root_url + "/" + url, callback = self.parsePage)

    # parse one page - extract items (categories)
    def parsePage(self, response):
        # currently selects only lowest level links, and their parents inside their fields
        hxs = HtmlXPathSelector(response)

        # select lowest level category and extract its parent
        links = hxs.select("//div[@class='siteMapSubCat']//ul//li")

        # extract page name by getting text in url after "=" symbol
        # example url: smv_10153_12605?vName=Appliances
        page_name = response.url.split("=")[1]

        items = []

        for link in links:
            item = SearsItem()
            item['page_text'] = page_name
            item['page_url'] = response.url

            # extract parent category element
            parent = link.select("parent::node()/preceding-sibling::node()[2]/a")
            item['parent_text'] = parent.select('text()').extract()
            item['parent_url'] = parent.select('@href').extract()
            
            item['text'] = link.select('text()').extract()
            item['url'] = link.select('a/@href').extract()
            items.append(item)

        return items
