from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Amazon.items import AmazonItem
from Amazon.items import ProductItem
from scrapy.http import Request
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
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links_level0 = hxs.select("//div[@id='siteDirectory']//table//a")
        titles_level1 = hxs.select("//div//table//h2")
        items = []

        # add level 1 categories to items

        # first one is a special category ("Unlimited Instant Videos"), add it separately
        special_item = AmazonItem()
        special_item['text'] = titles_level1[0].select('text()').extract()[0]
        special_item['level'] = 2
        special_item['special'] = 1
        items.append(special_item)

        # the rest of the titles are not special
        for title in titles_level1[1:]:
            item = AmazonItem()
            item['text'] = title.select('text()').extract()[0]
            item['level'] = 2

            items.append(item)

        # add level 0 categories to items
        for link in links_level0:
            item = AmazonItem()
            item['text'] = link.select('text()').extract()[0]
            root_url = "http://www.amazon.com"
            item['url'] = root_url + link.select('@href').extract()[0]
            item['level'] = 1

            parent = link.select("parent::node()/parent::node()/preceding-sibling::node()")
            parent_text = parent.select('text()').extract()
            if parent_text:
                item['parent_text'] = parent_text[0]

                # if its parent is the special category, mark this one as special too
                if (item['parent_text'] == special_item['text']):
                    item['special'] = 1

            items.append(item)

        return items


class BestsellerSpider(BaseSpider):
    name = "bestseller"
    allowed_domains = ["amazon.com"]
    start_urls = [
        "http://www.amazon.com/Best-Sellers/zgbs/ref=zg_bs_unv_mas_0_mas_1",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        departments = hxs.select("//ul[@id='zg_browseRoot']/ul/li/a/@href").extract()
        
        for department in departments:
            yield Request(department, callback = self.parseDepartment)

    def parseDepartment(self, response):
        hxs = HtmlXPathSelector(response)
        products = hxs.select("//div[@class='zg_itemWrapper']")

        items = []

        for product in products:
            item = ProductItem()

            #TODO: this name will always be incomplete (ends in "..."), add name on product page
            item['name'] = product.select("div[@class='zg_title']/a/text()").extract()
            item['url'] = product.select("div[@class='zg_title']/a/@href").extract()

            #TODO: this needs to be refined, many prices etc
            item['price'] = product.select(".//strong[@class='price']/text()").extract()

            #TODO:
            #item['department'] = dep_name

            items.append(item)

            #TODO: implement next page (next 20 items)

        return items