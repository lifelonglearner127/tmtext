# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import json
from nutrition_images.items import NutritionImagesItem
from detect_text_houghlines import is_text_image

class WalmartNutritionImagesSpider(scrapy.Spider):
    name = "walmart_nutrition_images"
    allowed_domains = ["walmart.com"]
    start_urls = (
        'http://www.walmart.com/browse/food/snacks-cookies-chips/976759_976787?cat_id=976759_976787',
    )

    def parse(self, response):
        urls = map(lambda u: "http://www.walmart.com" + u, response.xpath("//a[@class='js-product-title']/@href").extract())
        for url in urls:
            yield Request(url, callback=self.parse_url)

    def parse_url(self, response):
        # response.xpath("//title//text()").extract()
        def _fix_relative_url(relative_url):
            """Fixes relative image urls by prepending
            the domain. First checks if url is relative
            """

            if not relative_url.startswith("http"):
                return "http://www.walmart.com" + relative_url
            else:
                return relative_url

        # extract json from source
        page_raw_text = response.body
        start_index = page_raw_text.find('define("product/data",') + len('define("product/data",')
        end_index = page_raw_text.find('define("athena/analytics-data"', start_index)
        end_index = page_raw_text.rfind(");", 0, end_index) - 2
        body_dict = json.loads(page_raw_text[start_index:end_index])

        pinfo_dict = body_dict

        images_carousel = []

        for item in pinfo_dict['imageAssets']:
            images_carousel.append(item['versions']['hero'])

        for image in images_carousel:
            item = NutritionImagesItem()
            item['image'] = image
            (item['slope_average'], item['slope_median']) = is_text_image(image, is_url=True)
            item['is_likely_text'] = item['slope_median'] < 0.02

            yield item

