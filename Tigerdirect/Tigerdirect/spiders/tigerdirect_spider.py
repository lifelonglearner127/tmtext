from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Tigerdirect.items import TigerdirectItem
from scrapy.http import Request
import sys
import re
from spiders_utils import Utils

################################
# Run with 
#
# scrapy crawl tigerdirect
#
################################


class TigerdirectSpider(BaseSpider):
    name = "tigerdirect"
    allowed_domains = ["tigerdirect.com"]
    start_urls = [
        "http://www.tigerdirect.com/computerproducts.asp",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//table//tr[1]/td//a[ancestor::h4]")

        for link in links:
            item = TigerdirectItem()
            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]
            item['level'] = 1
            yield Request(url = item['url'], callback = self.parseCategory, meta = {'item' : item})

    # receive one category url, add aditional info and return it; then extract its subcategories and parse them as well
    def parseCategory(self, response):
        hxs = HtmlXPathSelector(response)

        item = response.meta['item']

        # extract number of products if available
        nrproducts_holder = hxs.select("//div[@class='resultsfilterBottom']/div[@class='itemsShowresult']/strong[2]/text()").extract()
        if nrproducts_holder:
            item['nr_products'] = int(nrproducts_holder[0])

        # extract description if available
        description_holders = hxs.select("//div[@class='textBlock']")
        # if the list is not empty and contains at least one non-whitespace item
        if description_holders:
            description_texts = description_holders.select(".//text()[not(ancestor::h2)]").extract()

            # replace all whitespace with one space, strip, and remove empty texts; then join them
            item['description_text'] = " ".join([re.sub("\s+"," ", description_text.strip()) for description_text in description_texts if description_text.strip()])

            tokenized = Utils.normalize_text(item['description_text'])
            item['description_wc'] = len(tokenized)

            description_title = description_holders.select(".//h2/text()").extract()
            if description_title:
                item['description_title'] = description_title[0].strip()

                (item['keyword_count'], item['keyword_density']) = Utils.phrases_freq(item['description_title'], item['description_text'])
        else:
            item['description_wc'] = 0



        yield item

        #TODO
        # extract subcategories
        parent = item