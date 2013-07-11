from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Bestbuy.items import BestbuyItem
import sys

################################
# Run with 
#
# scrapy crawl bestbuy
#
################################


class BestbuySpider(BaseSpider):
    name = "bestbuy"
    allowed_domains = ["bestbuy.com"]
    start_urls = [
        #"http://www.bestbuy.com/site/sitemap.jsp",
        "file:///home/ana/code/nlp_reviews/misc/the_pages/BestBuy.com%20-%20Site%20Map.html"
    ]

    def parse(self, response):
        # currently not extracting parents that are non-links (smaller parent categories like "resources" and "shops")
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//div[@id='container']/div/header//nav/ul[@id='nav']/a")
        items = []

        for link in links:

            # retrieve parent category for this link
            #TODO: for links that don't have a parent this output should be omitted, to fix
            parent = link.select("parent::node()/parent::node()/preceding-sibling::node()/a")
            item = BestbuyItem()

            item['text'] = link.select('text()').extract()
            item['url'] = link.select('@href').extract()

            item['parent_text'] = parent.select('text()').extract()
            item['parent_url'] = parent.select('@href').extract()

            items.append(item)

        return items
