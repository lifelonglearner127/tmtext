from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from general_spider.items import CategoryItem
from general_spider.items import ProductItem
from scrapy.http import Request
import sys
import re
import datetime

from spiders_utils import Utils


################################
# Run with 
#
# scrapy crawl general
#
################################

# scrape sitemap and extract categories
class WalmartSpider(BaseSpider):
    name = "walmart"
    allowed_domains = ["walmart.com"]
    start_urls = [
        "http://www.walmart.com/cp/All-Departments/121828",
    ]
    root_url = "http://www.walmart.com"

    # keep crawled items represented by (url, parent_url) pairs
    # to eliminate duplicates
    crawled = []

    def parse(self, response):