from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Macys.items import CategoryItem
from scrapy.http import Request
from scrapy.http import TextResponse
import re
import sys

################################
# Run with 
#
# scrapy crawl macys
#
################################

# scrape sitemap list and retrieve categories
class MacysSpider(BaseSpider):
    name = "macys"
    allowed_domains = ["macys.com"]
    start_urls = [
        "http://www1.macys.com/cms/slp/2/Site-Index",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//div[@id='sitemap_header']/a")
        root_url = "http://www1.macys.com"

        for link in links:
            item = CategoryItem()

            text = link.select('text()').extract()[0]
            item['text'] = text
            item['url'] = link.select('@href').extract()[0]
            item['level'] = 1
            yield item

            # create request to extract subcategories for this category
            yield Request(item['url'], callback = self.parseCategory, meta = {'parent' : item['text']})

    # extract subcategories from each category
    def parseCategory(self, response):
        hxs = HtmlXPathSelector(response)
        chapters = hxs.select("//li[@class='nav_cat_item_bold']")
        
        for chapter in chapters:

            #TODO: still includes some special categories (like "Coming Soon" in men)
            # exclude "Brands" chapter
            chapter_name = chapter.select("span/text()").extract()
            if not chapter_name or "brands" in chapter_name[0]:
                continue

            subcats = chapter.select("ul/li/a")
            for subcat in subcats:
                item = CategoryItem()
                text = subcat.select('text()').extract()[0]
                # if it starts with "Shop all", ignore it
                if re.match("Shop [aA]ll.*", text):
                    continue
                else:
                    item['text'] = text
                item['url'] = subcat.select('@href').extract()[0]
                item['level'] = 0
                item['parent_text'] = response.meta['parent']
                item['parent_url'] = response.url

                yield item
