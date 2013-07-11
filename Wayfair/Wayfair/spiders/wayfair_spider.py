from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Wayfair.items import WayfairItem
import sys

################################
# Run with 
#
# scrapy crawl wayfair
#
################################


class WayfairSpider(BaseSpider):
    name = "wayfair"
    allowed_domains = ["wayfair.com"]
    start_urls = [
        "http://www.wayfair.com/site_map.php",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        # select category links on all 3 levels
        links = hxs.select("//div[@class='categories']/ul/li/ul/li/ul/li/a")
        parent_links = hxs.select("//div[@class='categories']/ul/li/ul/li/a")
        grandparent_links = hxs.select("//div[@class='categories']/ul/li/a")

        # select special section "browse by brand"
        special_links = hxs.select("//div[@class='brands']/ul/li/ul/li/a")
        special_parent_links = hxs.select("//div[@class='brands']/ul/li/a")
        items = []

        for link in links:
            # extracting parents
            parent = link.select('parent::node()/parent::node()/parent::node()/a')
            # extracting grandparents
            grandparent = parent.select('parent::node()/parent::node()/parent::node()/a')
            
            item = WayfairItem()
            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]

            item['parent_text'] = parent.select('text()').extract()[0]
            item['parent_url'] = parent.select('@href').extract()[0]

            grandparent_text = grandparent.select('text()').extract()
            grandparent_url = grandparent.select('@href').extract()
            if grandparent_text:
                item['grandparent_text'] = grandparent_text[0]
            if grandparent_url:
                item['grandparent_url'] = grandparent_text[0]

            # this is considered more detailed than the main category level (compared to other sitemaps)
            item['level'] = -1

            items.append(item)

        for link in parent_links:
            # extracting parents
            parent = link.select('parent::node()/parent::node()/parent::node()/a')
            
            item = WayfairItem()
            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]

            parent_text = parent.select('text()').extract()
            parent_url = parent.select('@href').extract()
            if (parent_text):
                item['parent_text'] = parent_text[0]
            if (parent_url):
                item['parent_url'] = parent_url[0]

            # this is considered the main category level
            item['level'] = 0

            items.append(item)

        for link in grandparent_links:
            item = WayfairItem()
            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]

            item['level'] = 1

            items.append(item)

        for link in special_links:
            # extracting parents
            parent = link.select('parent::node()/parent::node()/parent::node()/a')

            item = WayfairItem()
            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]

            parent_text = parent.select('text()').extract()
            parent_url = parent.select('@href').extract()
            if (parent_text):
                item['parent_text'] = parent_text[0]
            if (parent_url):
                item['parent_url'] = parent_url[0]

            # this is considered the main category level
            item['level'] = 0
            item['special'] = 1

            items.append(item)

        for link in special_parent_links:
            item = WayfairItem()
            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]

            item['level'] = 1
            item['special'] = 1

            items.append(item)

        return items
