from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Sherwin.items import CategoryItem
from Sherwin.items import ProductItem
from scrapy.http import Request
from scrapy.http import Response
import re
import sys

from spiders_utils import Utils

################################
# Run with 
#
# scrapy crawl sherwin
#
################################

# crawls sitemap and extracts department and categories names and urls (as well as other info)
class SherwinSpider(BaseSpider):
    name = "sherwin"
    allowed_domains = ["sherwin-williams.com"]
    start_urls = [
        "https://www.sherwin-williams.com/sitemap/",
    ]

    def parse(self, response):
    	pass
