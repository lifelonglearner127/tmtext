from __future__ import division, absolute_import, unicode_literals

import re
import json

from scrapy.log import WARNING
from scrapy import Request

from product_ranking.items import SiteProductItem, RelatedProduct, \
    Price, BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    cond_set_value


class ShopNordstromProductsSpider(BaseProductsSpider):
    name = 'shopnordstrom_products'
    allowed_domains = ["shop.nordstrom.com",
                       "recs.richrelevance.com",
                       "nordstrom.ugc.bazaarvoice.com"]
    start_urls = []
    SEARCH_URL = "http://shop.nordstrom.com/sr?" \
        "origin=keywordsearch" \
        "&contextualcategoryid=0&keyword={search_term}"

    def __init__(self, site_name="shop.nordstrom.com", *args, **kwargs):
        super(ShopNordstromProductsSpider, self).__init__(*args,
                                                          site_name=site_name,
                                                          **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _request_buyer_reviews(self, response):
        upc = response.meta['upc']
        if not upc:
            return response.meta['product']
        url_reviews = "http://nordstrom.ugc.bazaarvoice.com" \
                      "/data/reviews.json?" \
                      "passkey=m55kapfgt0fr6f7rvwgw43cno" \
                      "&callback=jQuery20307092045104600421_1421850095549&apiversion=5.4" \
                      "&filter=rating:gte:1" \
                      "&filter=ProductId:%s" \
                      "&sort=Helpfulness:desc,TotalPositiveFeedbackCount:desc," \
                      "SubmissionTime:desc&limit=100" % (upc[0],)
        return Request(url_reviews, self._parse_buyer_reviews,
                       meta=response.meta, dont_filter=True)

    def _parse_buyer_reviews(self, response):
        product = response.meta['product']
        body = response.body
        if body:
            rp_ajax2 = re.findall("[^jQuery\d+\_\d+\(](.*)", body)
            rp_ajax2 = str("{") + rp_ajax2[0][0:-2]
            data = json.loads(rp_ajax2)
            num_of_reviews = data["TotalResults"]

            rating_by_star = {}
            count = 0
            sum_rat = 0
            for i in range(1, 6):
                rating_by_star[i] = 0
            for prod_rat in data["Results"]:
                rating_by_star[prod_rat["Rating"]] += 1
                sum_rat += prod_rat["Rating"]
                count += 1

            if count:
                average_rating = sum_rat / count
            else:
                average_rating = 0

            br = BuyerReviews(
                num_of_reviews,
                average_rating,
                rating_by_star
            )
            cond_set_value(product, 'buyer_reviews',
                           br if num_of_reviews else ZERO_REVIEWS_VALUE)
        else:
            cond_set_value(product, 'buyer_reviews', ZERO_REVIEWS_VALUE)
        return product

    def _request_related_products(self, response, item_num):
        if not item_num:
            return self._request_buyer_reviews(response)
        sessionId = re.findall("sessionId\"\:\"([^\"]*)", response.body)
        userId = re.findall("id\"\:\"([^\"]*)", response.body)

        url = "http://recs.richrelevance.com/rrserver/api/rrPlatform/recsForPlacements" \
              "?jcb=process" \
              "&apiClientKey=3c86c35d5f315680" \
              "&sessionId=%s" \
              "&userId=%s" \
              "&apiKey=469cc5818c1eb6ac" \
              "&chi=0" \
              "&productId=%s" \
              "&cts=http://shop.nordstrom.com/&categoryData=false" \
              "&excludeHtml=true" \
              "&pref=" \
              "&ts=1423746984929" \
              "&sgs=2M2:2M2" \
              "&placements=item_page.PP_4|item_page.PP_3|item_page.PP_2|item_page.FTR" \
              "&_=1423746984578" % (
                  sessionId[0],
                  userId[0],
                  re.findall("\d+", item_num[0])[0],
              )
        return Request(url, self._parse_related_products, meta=response.meta,
                       dont_filter=True)

    def _parse_related_products(self, response):
        data = json.loads(response.body_as_unicode())
        rp = []
        try:
            part = data["placements"][0]["strategyMessage"]
            related = ["People Also Purchased", "People Also Viewed",
                       "Similar Items", "People Also Bought"]
            if part in related:
                for li_prod in data["placements"][0][
                    "recommendedProducts"]:
                    title = li_prod.get("name", "")
                    url = li_prod.get("clickURL", "")
                    rp.append(RelatedProduct(title, url))
        except Exception:
            pass

        cond_set_value(response.meta['product'], 'related_products', rp)
        return self._request_buyer_reviews(response)

    def parse_product(self, response):

        product = response.meta['product']

        title = response.xpath(
            '//section[@id="product-title"]/h1/text()').extract()
        cond_set(product, 'title', title)

        brand = response.xpath(
            '//section[@id="brand-title"]/h2/a/text()').extract()
        cond_set(product, 'brand', brand)  

        upc = re.findall(
            "\"bazaarvoiceStyleId\"\:\"(\d+)\"",
            response.body_as_unicode()
        )

        item_num = response.xpath(
            '//td[@class="item-number"]/div/text()').extract()
        if upc:
            upc = re.findall("\d+", upc[0])
        response.meta['upc'] = upc

        des = response.xpath(
            '//section[@id="details-and-care"]').extract()
        cond_set(product, 'description', des) 

        price = response.xpath(
            '//td[contains(@class, "item-price")]/span[contains(@class, "sale-price")]/text()').extract()
        if not price:
            price = response.xpath(
                '//td[contains(@class, "item-price")]/span/text()').extract() 
        if price:
            price = re.findall("\d+\.{0,1}\d+", price[0].replace(',', ''))[0]
            product["price"] = Price(priceCurrency="USD", price=price)

        image_url = response.xpath(
            '//div[@id="product-image"]/img/@src').extract()
        cond_set(product, 'image_url', image_url)

        cond_set(product, 'locale', ("en_US",))

        return self._request_related_products(response, item_num)

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

