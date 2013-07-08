from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from Toysrus.items import ToysrusItem
import sys
import string

################################
# Run with 
#
# scrapy crawl toysrus
#
################################


class ToysrusSpider(BaseSpider):
    name = "toysrus"
    allowed_domains = ["toysrus.com"]

    #TODO: should this be empty to avoid redundancy or is it not visited?
    start_urls = ['http://www.toysrus.com/sitemap/map.jsp']

    #TODO: it seems to work but the order of adding the categories to the output is chaotic (not respecting page order), does it really work well?
    def parse(self, response):

        # build urls list containing each page of the sitemap

        # initialize page names
        pages = ['num']

        # add only letters on even positions (they're the only ones that appear in the page names)
        for letter in [string.lowercase[i] for i in range(len(string.lowercase)) if i%2==0]:
            pages.append(letter)

        root_url = self.start_urls[0] + '?p='

        # build pages names and add them to urls list
        urls = []
        for page in pages:
            urls.append(root_url + page)

        for url in urls:
            yield Request(url, callback = self.parsePage)

    def parsePage(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//div[@id='sitemapLinks']//ul//a")
        items = []

        #TODO: implement parents
        for link in links:
            item = ToysrusItem()
            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()
            items.append(item)

        return items
