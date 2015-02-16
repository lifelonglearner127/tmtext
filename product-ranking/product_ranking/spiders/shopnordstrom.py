from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re
import json
import urllib2
import urlparse
import string

from scrapy.log import WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, \
    Price, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    cond_set_value


class ShopNordstromProductsSpider(BaseProductsSpider):
    name = 'shopnordstrom_products'
    allowed_domains = ["shop.nordstrom.com"]
    start_urls = []
    SEARCH_URL = "http://shop.nordstrom.com/sr?" \
        "origin=keywordsearch" \
        "&contextualcategoryid=0&keyword={search_term}"

    def parse_product(self, response):

        product = response.meta['product']

        title = response.xpath(
            '//section[@id="product-title"]/h1/text()').extract()
        cond_set(product, 'title', title)

        brand = response.xpath(
            '//section[@id="brand-title"]/h2/a/text()').extract()
        cond_set(product, 'brand', brand)  

        upc = re.findall(
            "\"bazaarvoiceStyleId\"\: \"(\d+)\"",
            response.body_as_unicode()
        )

        item_num = response.xpath(
            '//td[@class="item-number"]/div/text()').extract()
        if upc:
            upc = re.findall("\d+", upc[0])
            cond_set(product, 'upc', upc)

        des = response.xpath(
            '//section[@id="details-and-care"]').extract()
        cond_set(product, 'description', des) 

        price = response.xpath(
            '//td[contains(@class, "item-price")]/span/text()').extract() 
        if price:
            price = re.findall("\d+", price[0])[0]
            product["price"] = Price(priceCurrency="USD", price=price)

        image_url = response.xpath(
            '//div[@id="product-image"]/img/@src').extract()
        cond_set(product, 'image_url', image_url)

        if item_num:  # RelatedProduct
            rp = []
            url = "http://recs.richrelevance.com/rrserver/api/" \
                "rrPlatform/recsForPlacements?jcb=process" \
                "&apiClientKey=3c86c35d5f315680" \
                "&apiKey=469cc5818c1eb6ac&productId=%s" \
                "&placements=item_page.PP_4|item_page.PP_3|" \
                "item_page.FTR&_=1421842916059" % (
                    re.findall("\d+", item_num[0])[0],)

            ajax = urllib2.urlopen(url)
            rp_ajax = ajax.read()
            ajax.close()
            data = json.loads(rp_ajax)
            
            try:
                for li_prod in data["placements"][0]["recommendedProducts"]:
                    title = li_prod.get("name", "")
                    url = li_prod.get("clickURL", "")
                    rp.append(RelatedProduct(title, url))
            except Exception:
                pass

            cond_set_value(product, 'related_products', rp)

        if upc:#Reviews
            url_reviews = "http://nordstrom.ugc.bazaarvoice.com" \
                "/data/reviews.json?" \
                "passkey=m55kapfgt0fr6f7rvwgw43cno" \
                "&callback=jQuery20307092045104600421_1421850095549&apiversion=5.4" \
                "&filter=rating:gte:1" \
                "&filter=ProductId:%s" \
                "&sort=Helpfulness:desc,TotalPositiveFeedbackCount:desc," \
                "SubmissionTime:desc&limit=100" % (upc[0],)

            ajax = urllib2.urlopen(url_reviews)
            rp_ajax = ajax.read()
            ajax.close()
            if rp_ajax:
                rp_ajax2 = re.findall("[^jQuery\d+\_\d+\(](.*)", rp_ajax)
                rp_ajax2 = str("{") + rp_ajax2[0][0:-2]
                data = json.loads(rp_ajax2)
                num_of_reviews = data["TotalResults"]

                rating_by_star = {}
                count = 0
                sum_rat = 0
                for i in range(1,6):
                    rating_by_star[i] = 0
                for prod_rat in data["Results"]:
                    rating_by_star[prod_rat["Rating"]] += 1
                    sum_rat += prod_rat["Rating"] 
                    count += 1

                if count:
                    average_rating = sum_rat / count
                else:
                    average_rating = 0

                if num_of_reviews > count:
                   average_rating = 0
                   rating_by_star = {}

                br = BuyerReviews(
                    num_of_reviews,
                    average_rating,
                    rating_by_star
                )
                cond_set_value(product, 'buyer_reviews', br)

        cond_set(product, 'locale', ("en_US",))

        return product

    def _scrape_total_matches(self, response):
        total_matches = response.xpath(
            '//div[contains(@class, "fashion-results-count")]' \
            '/span[@class="count"]/text()'
        ).extract()
        if total_matches:
            total_matches = int(total_matches[0].replace(',', ''))
        else:
           return 0
        return total_matches

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[contains(@class, "fashion-item")]' \
            '/div[contains(@class, "info")]' \
            '/a[1]/@href'
        ).extract()

        if not links:
            self.log("Found no product links.", WARNING)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        url = response.url
        next_num = response.xpath(
            '//li[@class="page-arrow page-next"]/a/@href').extract()
        if next_num:
            next_num = next_num[0]
            return "http://shop.nordstrom.com/sr" + next_num
        return None
