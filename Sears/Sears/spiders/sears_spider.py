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

    
    def parsep(self, response):

        hxs = HtmlXPathSelector(response)

        # get urls of pages for each category
        urls = hxs.select("//div[@class='siteMapSubCell']//ul/li/a/@href").extract()

        # parse each page in urls list with parsePage
        # build urls by adding the prefix of the main page url
        root_url = "http://www.sears.com/shc/s"
        for url in urls:
            yield Request(root_url + "/" + url, callback = self.parsePage)

    # parse one page - extract items (categories)
    def parse(self, response):
        # currently selects only lowest level links, and their parents inside their fields
        hxs = HtmlXPathSelector(response)

        #TODO: add pages as separate categories as well?
        #TODO: add special categories if any

        # select lowest level categories
        links = hxs.select("//div[@class='siteMapSubCat']//ul//li")
        # select parent categories
        parent_links = hxs.select("//div[@class='siteMapSubCat']//h4//a")

        # extract page name by getting text in url after "=" symbol
        # example url: smv_10153_12605?vName=Appliances
        page_name = response.url.split("=")[1]

        items = []

        for link in links:
            item = SearsItem()
            item['page_text'] = page_name
            item['page_url'] = response.url
            # add the page as the grandparent category
            item['grandparent_text'] = page_name
            item['grandparent_url'] = response.url

            # extract parent category element
            parent = link.select("parent::node()/preceding-sibling::node()[2]/a")
            item['parent_text'] = parent.select('text()').extract()
            item['parent_url'] = parent.select('@href').extract()

            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('a/@href').extract()[0]

            # the bottom level categories are considered to be below the main level category as they are very detailed
            item['level'] = -1
            items.append(item)

        for link in parent_links:
            item = SearsItem()
            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]

            item['page_text'] = page_name
            item['page_url'] = response.url
            # add the page as the parent category
            item['parent_text'] = page_name
            item['parent_url'] = response.url
            # this is considered to be the main category level
            item['level'] = 0

            items.append(item)

        return items
