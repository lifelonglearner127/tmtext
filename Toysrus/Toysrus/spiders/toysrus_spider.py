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

    start_urls = ['http://www.toysrus.com/sitemap/map.jsp']

    # build urls list containing each page of the sitemap, and pass them to parsePage to extract items (categories)
    # the output will not be organized by page by default
    def parse(self, response):

        # pages urls are of the form: http://www.toysrus.com/sitemap/map.jsp?p=<parameter>
        # initialize page names parameters
        pages = ['num']

        # add to page parameters only letters on even positions in the alphabet (they're the only ones that appear in the page names)
        for letter in [string.lowercase[i] for i in range(len(string.lowercase)) if i%2==0]:
            pages.append(letter)

        root_url = self.start_urls[0] + '?p='

        # build pages names and add them to urls list
        urls = []
        for page in pages:
            urls.append(root_url + page)

        # parse each page in urls list with parsePage
        for url in urls:
            yield Request(url, callback = self.parsePage)

    # parse one page - extract items (categories)
    def parsePage(self, response):
        hxs = HtmlXPathSelector(response)
        # currently selecting categories on all levels (both children and parents)
        links = hxs.select("//div[@id='sitemapLinks']//ul//a")
        items = []

        #TODO: implement parents
        for link in links:
            item = ToysrusItem()
            item['page'] = response.url
            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()
            items.append(item)

        return items
