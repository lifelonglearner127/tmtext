# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals

import string
import json
import urllib
import urllib2
import re

from scrapy import Request
from product_ranking.items import SiteProductItem, Price, BuyerReviews, RelatedProduct
from product_ranking.spiders import cond_set_value
from product_ranking.spiders.contrib.product_spider import ProductsSpider
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.guess_brand import guess_brand_from_first_words


def _populate(item, key, value, first=False):
    if not value:
        return
    value = filter(None, map(string.strip, value))
    if value:
        if first:
            item[key] = value[0]
        else:
            item[key] = value


class PetsmartProductsSpider(ProductsSpider):
    name = 'petsmart_products'
    allowed_domains = ['petsmart.com']

    SEARCH_URL = 'http://www.petsmart.com/search?SearchTerm={search_term}'

    XPATH = {
        'product': {
            'title': '//h1[contains(@class, "product-name")]/text()',
            'categories': '//div[@class="breadcrumb-wrapper"]/a/@href',
            'description': '//div[@itemprop="description"]/text()',
            'currency': '//meta[@property="og:price:currency"]/@content',
            'price': '//meta[@property="og:price:amount"]/@content',
            'out_of_stock_button': '//meta[@property="og:availability"]/@content',
            'id': '//input[@id="parentSKU"]/@value',
            'sku': '//input[@id="productID"]/@value',
            'size': '//ul[@class="swatches size"]//a/@data-variant-value',
            'color': '//ul[@class="swatches color"]//a/@data-variant-value',
            'variants': '//li[contains(@class, "ws-variation-list-item")]/@data-sku',
        },
        'search': {
            'total_matches': '//div[@class="results-hits"]',
            'next_page': '//li[@class="current-page"]/following-sibling::li/a/@href',
            'prod_links': '//ul[contains(@class,"search-result-items")]/li/a/@href',
        },
    }

    IMAGE_URL = 'http://s7d2.scene7.com/is/image/PetSmart/{sku}_Imageset'

    def __init__(self, *args, **kwargs):
        self.br = BuyerReviewsBazaarApi(called_class=self)
        super(PetsmartProductsSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        product = response.meta['product']

        # locale
        product['locale'] = 'en_US'

        # title
        title = response.xpath(self.XPATH['product']['title']).extract()
        _populate(product, 'title', title, first=True)

        # categories
        categories = response.xpath(self.XPATH['product']['categories']).extract()
        if categories:
            if categories[0][-1] == '/':
                categories = categories[0][:-1].replace('http://www.petsmart.com/', '').split('/')
            else:
                categories = categories[0].replace('http://www.petsmart.com/', '').split('/')
        _populate(product, 'categories', categories)
        if product.get('categories'):
            product['category'] = product['categories'][-1]

        # description
        description = response.xpath(self.XPATH['product']['description']).extract()
        _populate(product, 'description', description, first=True)

        # buyer reviews

        product_id = re.findall(r'configData.productId = \"(.+)\";', response.body_as_unicode())

        if product_id:
            rating_url = "http://api.bazaarvoice.com/data/batch.json?" \
                "passkey=208e3foy6upqbk7glk4e3edpv&apiversion=5.5" \
                "&displaycode=4830-en_us&resource.q0=products" \
                "&stats.q0=reviews&filteredstats.q0=reviews" \
                "&filter_reviews.q0=contentlocale%3Aeq%3Aen%2Cen_US" \
                "&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen%2Cen_US" \
                "&resource.q1=reviews" \
                "&filter.q1=isratingsonly%3Aeq%3Afalse" \
                "&filter.q1=contentlocale%3Aeq%3Aen%2Cen_US" \
                "&sort.q1=helpfulness%3Adesc%2Ctotalpositivefeedbackcount%3Adesc&stats.q1=reviews" \
                "&filteredstats.q1=reviews" \
                "&include.q1=authors%2Cproducts%2Ccomments" \
                "&filter_reviews.q1=contentlocale%3Aeq%3Aen%2Cen_US" \
                "&filter_reviewcomments.q1=contentlocale%3Aeq%3Aen%2Cen_US" \
                "&filter_comments.q1=contentlocale%3Aeq%3Aen%2Cen_US" \
                "&limit.q1=1&offset.q1=0&limit_comments.q1=3"
            rating_url += "&filter.q0=id%3Aeq%3A" + str(product_id[0])
            rating_url += "&filter.q1=productid%3Aeq%3A" + str(product_id[0])

            ajax = urllib2.urlopen(rating_url)
            resp = ajax.read()
            ajax.close()

            data = json.loads(resp)
            try:
                num_of_reviews = data["BatchedResults"]["q1"] \
                    ["Includes"]["Products"][product_id[0]] \
                    ["ReviewStatistics"]["TotalReviewCount"]
            except KeyError:
                num_of_reviews = None

            try:
                average_rating = round(data["BatchedResults"]["q1"] \
                    ["Includes"]["Products"][product_id[0]] \
                    ["ReviewStatistics"]["AverageOverallRating"], 2)
            except KeyError:
                average_rating = None

            try:
                rating_by_star = { 1:0, 2:0, 3:0, 4:0, 5:0 }
                rbs = data["BatchedResults"]["q1"] \
                    ["Includes"]["Products"][product_id[0]] \
                    ["ReviewStatistics"]["RatingDistribution"]
                for mark in rbs:
                    rating_by_star[mark["RatingValue"]] = mark["Count"]
            except KeyError:
                rating_by_star = None

            if average_rating or num_of_reviews:
                product["buyer_reviews"] = BuyerReviews(
                    average_rating=average_rating,
                    num_of_reviews=num_of_reviews,
                    rating_by_star=rating_by_star,
                )
            else:
                product['buyer_reviews'] = ZERO_REVIEWS_VALUE

        # variants
        variants = set(response.xpath(self.XPATH['product']['variants']).extract())

        if len(variants) > 1:
            product['variants'] = []
            response.meta['product'] = product
            variant_sku = variants.pop()
            response.meta['variants'] = variants
            return Request(
                response.url.split('?')[0].split(';')[0] + '?var_id=' + variant_sku,
                meta=response.meta,
                callback=self._parse_variants,
                # dont_filter=True
            ) 
        else:
            product['variants'] = [self._parse_variant_data(response)]
            return product

    def _parse_variants(self, response):
        response.meta['product']['variants'].append(
            self._parse_variant_data(response)
        )
        if response.meta.get('variants'):
            variant_sku = response.meta['variants'].pop()
            return Request(
                response.url.split('?')[0] + '?var_id=' + variant_sku,
                meta=response.meta,
                callback=self._parse_variants,
                # dont_filter=True
            )
        else:
            return response.meta['product'] 

    def _parse_variant_data(self, response):
        data = {}
        # id
        id = response.xpath(self.XPATH['product']['id']).extract()
        _populate(data, 'id', id, first=True)

        # sku
        sku = response.xpath(self.XPATH['product']['sku']).extract()
        _populate(data, 'sku', sku, first=True)

        # image url
        if data.get('sku'):
            image_url = [self.IMAGE_URL.format(sku=data['sku'])]
        else:
            image_url = [""]
        _populate(data, 'image_url', image_url, first=True)

        # in stock?
        stock = response.xpath(self.XPATH['product']['out_of_stock_button']).extract()
        data['is_out_of_stock'] = True
        if stock:
            if re.search('in stock', stock[0], re.IGNORECASE):
                data['is_out_of_stock'] = False
            else:
                data['is_out_of_stock'] = True

        if data['is_out_of_stock']:
            data['available_online'] = False
            data['available_store'] = False
        else:
            available_online = re.search('this item is not available for in-store pickup', response.body_as_unicode(), re.IGNORECASE)
            available_store = re.search('your items will be available', response.body_as_unicode(), re.IGNORECASE)
            data['available_online'] = False
            data['available_store'] = False
            data['is_in_store_only'] = False
            if available_store:
                data['is_in_store_only'] = True
                data['available_online'] = False
                data['available_store'] = True
            elif available_online:
                data['available_online'] = True
                data['available_store'] = False
                data['is_in_store_only'] = False

        # currency
        currency = response.xpath(self.XPATH['product']['currency']).extract()
        _populate(data, 'currency', currency, first=True)

        # price
        price = response.xpath(self.XPATH['product']['price']).extract()
        if price:
            price = price[0].strip(currency[0])
            data['price'] = float(price)

        # size
        size = response.xpath(self.XPATH['product']['size']).extract()
        _populate(data, 'size', size)

        # color
        color = response.xpath(self.XPATH['product']['color']).extract()
        _populate(data, 'color', color)

        return data

    def _total_matches_from_html(self, response):
        total_matches = response.xpath(self.XPATH['search']['total_matches']).re(r'\d+')
        if total_matches:
            return int(total_matches[0])

    def _scrape_next_results_page_link(self, response):
        next_page = response.xpath(self.XPATH['search']['next_page']).extract()
        if next_page:
            return next_page[0]

    def _scrape_product_links(self, response):
        for link in response.xpath(self.XPATH['search']['prod_links']).extract():
            yield link.split('?')[0].split(';')[0], SiteProductItem()
