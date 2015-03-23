# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

from itertools import islice
import json
import re
import string
import urllib
import urllib2
import urlparse

from scrapy import Selector
from scrapy.http import FormRequest, Request
from scrapy.log import DEBUG, INFO

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set, FLOATING_POINT_RGEX
from product_ranking.spiders import cond_set_value, populate_from_open_graph


class FireboxProductSpider(BaseProductsSpider):
    name = 'firebox_products'
    allowed_domains = ["www.firebox.com"]
    start_urls = []

    SEARCH_URL = "http://www.firebox.com/firebox/search?searchstring={search_term}"

    product_link = "http://www.firebox.com"

    def __init__(self, *args, **kwargs):
        super(FireboxProductSpider, self).__init__(*args, **kwargs)

    def parse_product(self, response):
        prod = response.meta['product']
        reviews = response.xpath('//div[@id="review_loading"]/'
                                 'following::div[contains(@id, "review_")]')
        if reviews and len(reviews) > 0:
            total = len(reviews)
            stars = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            sum = 0

            for review in reviews:
                stars_count = len(review.xpath('./i[@class="icon-star"]'))
                stars[stars_count] += 1
                sum += stars_count
            avg = float(sum)/float(total)
            prod['buyer_reviews'] = BuyerReviews(total, avg, stars)

        title = response.xpath(
            '//h2[@class="product_name product_title"]/span[@itemprop="name"]/text()'
        ).extract()
        cond_set(prod, 'title', title)

        price = response.xpath(
            '//meta[@property="og:price:amount"]/@content'
        ).extract()
        priceCurrency = response.xpath(
            '//meta[@property="og:price:currency"]/@content'
        ).extract()
        if price and priceCurrency:
            if re.match("\d+(.\d+){0,1}", price[0]):
                prod["price"] = Price(priceCurrency=priceCurrency[0],
                                      price=price[0])

        des = response.xpath(
            '//div[@class="clearfix text_box margin_after bg_white"]'
            '| //div[@class="wide_page"]'
        ).extract()
        cond_set(prod, 'description', des)

        img_url = response.xpath(
            '//img[@id="product_image"]/@src'
        ).extract()
        cond_set(prod, 'image_url', img_url)

        cond_set(prod, 'locale', ['en-US'])

        prod['url'] = response.url

        items = response.xpath('//a[contains(@class,"g-med")] | //a[contains(@class,"g-large")]')
        related = []
        for item in items:
            name = item.xpath('.//img/@title').extract()
            link = item.xpath('.//@href').extract()
            if name and link:
                name = name[0]
                link = link[0]
                related.append(RelatedProduct(title=name, url=link))

        prod['related_products'] = related

        available = response.xpath(
            '//meta[@property="og:price:availability"]/@content'
        ).extract()
        if 'preorder' in available:
            prod['is_out_of_stock'] = True
        elif 'instock' in available:
            prod['is_out_of_stock'] = False

        return prod


    def _scrape_total_matches(self, response):
        total_matches = None
        if 'NO RESULTS'\
                in response.body_as_unicode():
            total_matches = 0
        total = response.xpath('//div[@class="searchtitle"]/text()').extract()
        if total:
            total = re.findall("(\d+)", total[0])
        total_matches = int(total[0])

        return total_matches

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[@class="block"]/div/a[1]/@href').extract()
        print 'LENGHT:', len(links)
        for link in links:
            yield self.product_link + link, SiteProductItem()
