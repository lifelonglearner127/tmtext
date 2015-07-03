# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import splitquery
from urlparse import parse_qs
from generate_nutrition_from_text import screenshot_element

class WalmartGenerateImagesSpider(scrapy.Spider):
    name = "walmart_generate_images"
    allowed_domains = ["www.walmart.com"]
    start_urls = (
        'http://www.walmart.com/browse/food/976759?cat_id=976759',
    )

    # how many pages to parse
    MAX_PAGES = 15

    def parse(self, response):
        urls = map(lambda u: "http://www.walmart.com" + u, response.xpath("//a[@class='js-product-title']/@href").extract())
        screenshot_element(urls, 
            ("//div[@class='nutrition-section']", "//div[@class='NutFactsSIPT']"), 
            "nutrition", "/home/ana/code/tmtext/nutrition_info_images/nutrition_facts_screenshots/")

        # parse next page
        root_url, query = splitquery(response.url)
        # if we are on first page
        parsed_q = parse_qs(query)
        if 'page' not in parsed_q:
            for page in range(2, self.MAX_PAGES+1):
                next_page = root_url + "?" + query + "&page=%s" % str(page)
                yield Request(next_page, callback = self.parse)

