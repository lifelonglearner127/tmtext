from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Amazon.items import AmazonItem
import sys

################################
# Run with 
#
# scrapy crawl amazon
#
################################


class AmazonSpider(BaseSpider):
    name = "amazon"
    allowed_domains = ["amazon.com"]
    start_urls = [
        "http://www.amazon.com/gp/site-directory/ref=sa_menu_top_fullstore",
        #"file:///home/ana/code/nlp_reviews/misc/the_pages/Amazon.com--Earth's%20Biggest%20Selection.html"
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links_level0 = hxs.select("//div[@id='siteDirectory']//table//a")
        titles_level1 = hxs.select("//div//table//h2")
        items = []

        # add level 0 categories to items
        for link in links_level0:
            item = AmazonItem()
            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]
            item['level'] = 0

            parent = link.select("parent::node()/parent::node()/preceding-sibling::node()")
            item['parent_text'] = parent.select('text()').extract()[0]

            items.append(item)

        # add level 1 categories to items
        for title in titles_level1:
            item = AmazonItem()
            item['text'] = title.select('text()').extract()[0]
            item['level'] = 1

            items.append(item)

        return items
