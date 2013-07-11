from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Overstock.items import OverstockItem
import sys

################################
# Run with 
#
# scrapy crawl overstock
#
################################


class OverstockSpider(BaseSpider):
    name = "overstock"
    allowed_domains = ["overstock.com"]
    start_urls = [
        "http://www.overstock.com/sitemap",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        # currently selecting bottom level categories, and their parents and parents of parents ("grandparents") in their fields
        links = hxs.select("//div[@id='sitemap']//li[@class='bullet3']//a")
        parent_links = hxs.select("//div[@id='sitemap']//li[@class='bullet2']//a")
        grandparent_links = hxs.select("//div[@id='sitemap']//li[@class='bullet1']//a")
        items = []

        #TODO: mark special categories (if appropriate for any)

        for link in links:

            # extract immediate parent of this link (first preceding sibling (of the parent node) with class='bullet2')
            parent = link.select("parent::node()/preceding-sibling::*[@class='bullet2'][1]/a")
            # extract grandparent of this link (first preceding sibling of the parent's parent node witch class='bullet1')
            grandparent = parent.select("parent::node()/preceding-sibling::*[@class='bullet1'][1]/a")

            item = OverstockItem()
            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]

            item['parent_text'] = parent.select('text()').extract()[0]
            item['parent_url'] = parent.select('@href').extract()[0]

            item['grandparent_text'] = grandparent.select('text()').extract()[0]
            item['grandparent_url'] = grandparent.select('@href').extract()[0]

            # this will be considered lower than the main level, because these categories are very detailed
            item['level'] = -1

            items.append(item)

        for link in parent_links:

            # extract immediate parent of this link (first preceding sibling (of the parent node) with class='bullet2')
            parent = link.select("parent::node()/preceding-sibling::*[@class='bullet1'][1]/a")

            item = OverstockItem()
            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]

            item['parent_text'] = parent.select('text()').extract()[0]
            item['parent_url'] = parent.select('@href').extract()[0]

            # this will be considered the main level of the nested list (it's comparable with the main level of the other sitemaps)
            item['level'] = 0

            items.append(item)

        for link in grandparent_links:

            item = OverstockItem()
            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]

            item['level'] = 1

            items.append(item)

        return items
