# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import json
import re
import string
import urlparse
from datetime import datetime

from scrapy.http import Request
from scrapy.http.request.form import FormRequest
from scrapy.log import msg, ERROR, WARNING, INFO, DEBUG

from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.spiders import (BaseProductsSpider, cond_set,
                                     cond_set_value, FormatterWithDefaults,
                                     FLOATING_POINT_RGEX)
from product_ranking.amazon_tests import AmazonTests

from product_ranking.amazon_bestsellers import amazon_parse_department
from product_ranking.settings import ZERO_REVIEWS_VALUE

from product_ranking.amazon_base_class import AmazonBaseClass

is_empty = lambda x, y=None: x[0] if x else y


class AmazoncnValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = ['model', 'brand', 'price', 'bestseller_rank',
                       'buyer_reviews']
    ignore_fields = [
        'is_in_store_only', 'is_out_of_stock', 'related_products', 'upc',
        'google_source_site', 'description', 'special_pricing'
    ]
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = True  # ... duplicated requests?
    ignore_log_filtered = True  # ... filtered requests?
    test_requests = {
        'abrakadabrasdafsdfsdf': 0,  # should return 'no products' or just 0 products
        'adfhsadifgewrtgujoc2': 0,
        'iphone duos': [5, 175],
        'gold shell': [50, 200],
        'Led Tv screen': [20, 200],
        'told help': [5, 150],
        'crawl': [50, 400],
        'sony playstation 4': [50, 200],
        'store data all': [20, 300],
        'iphone stone': [40, 250]
    }

class AmazonProductsSpider(AmazonTests, AmazonBaseClass):
    name = 'amazoncn_products'
    allowed_domains = ["amazon.cn"]

    settings = AmazoncnValidatorSettings()

    SEARCH_URL = "http://www.amazon.cn/s/?field-keywords={search_term}"

    REVIEW_DATE_URL = 'http://www.amazon.cn/product-reviews/{product_id}/' \
                      'ref=cm_cr_pr_top_recent?ie=UTF8&showViewpoints=0&' \
                      'sortBy=bySubmissionDateDescending'
    SORT_MODES = {
        'default': 'relevancerank',
        'relevance': 'relevancerank',
        'best': 'popularity-rank',
        'new': 'date-desc-rank',
        'discount': 'discount-rank',
        'price_asc': 'price-asc-rank',
        'price_desc': 'price-desc-rank',
        'rating': 'review-rank'
    }

    def __init__(self, *args, **kwargs):
        super(AmazonProductsSpider, self).__init__(*args, **kwargs)

        # Variables for total matches method (_scrape_total_matches)
        self.total_match_not_found = '没有找到任何与'
        self.total_matches_re = r'共\s?([\d,.\s?]+)'

        # Price currency
        self.price_currency = 'CNY'
        self.price_currency_view = u'\uffe5'

    def parse_product(self, response):
        if self._has_captcha(response):
            result = self._handle_captcha(response, self.parse_product)

        if not self._has_captcha(response):
            return super(AmazonProductsSpider, self).parse_product(response)
            prod = response.meta['product']

            self._populate_from_html(response, prod)

            if isinstance(prod['buyer_reviews'], Request):
                meta = prod['buyer_reviews'].meta
                result = prod['buyer_reviews'].replace(meta=meta)
            else:
                result = prod

            prod_id = is_empty(re.findall('/dp/([a-zA-Z0-9]+)', response.url))
            meta = response.meta.copy()
            meta = {"product": prod, 'product_id': prod_id}
            return Request(
                url=self.REVIEW_DATE_URL.format(product_id=prod_id),
                callback=self.parse_last_buyer_review_date,
                meta=meta,
                dont_filter=True,
            )

        elif response.meta.get('captch_solve_try', 0) >= self.captcha_retries:
            product = response.meta['product']
            self.log("Giving up on trying to solve the captcha challenge after"
                     " %s tries for: %s" % (self.captcha_retries, product['url']),
                     level=WARNING)
            result = None
        else:
            result = self._handle_captcha(response, self.parse_product)
        return result

    def parse_last_buyer_review_date(self, response):
        product = response.meta['product']
        date = is_empty(response.xpath(
            '//table[@id="productReviews"]/tr/td/div/div/span/nobr/text()'
        ).extract())

        if date:
            d = datetime.strptime(
                date.replace(u'\u5e74', ' ').replace(u'\u6708', ' ').
                replace(u'\u65e5', ''), '%Y %m %d')
            date = d.strftime('%d/%m/%Y')
            product['last_buyer_review_date'] = date

        new_meta = response.meta.copy()
        new_meta['product'] = product
        return product

    def _populate_from_html(self, response, product):

        revs = self._buyer_reviews_from_html(response)
        if isinstance(revs, Request):
            meta = {"product": product}
            product['buyer_reviews'] = revs.replace(meta=meta)
        else:
            product['buyer_reviews'] = revs

    def _buyer_reviews_from_html(self, response):
        stars_regexp = r'.+(\d[\d, ]*)'
        total = ''.join(response.css('#summaryStars a::text').extract())
        total = re.search('\d[\d, ]*', total)
        total = total.group() if total else None
        total = int(re.sub('[ ,]+', '', total)) if total else None
        average = response.css('#avgRating span::text').extract()
        average = re.search('\d[\d ,.]*', average[0] if average else '')
        average = float(re.sub('[ ,]+', '',
                               average.group())) if average else None
        ratings = {}
        for row in response.css('.a-histogram-row .a-span10 ~ td a'):
            title = row.css('::attr(title)').extract()
            text = row.css('::text').extract()
            stars = re.search(stars_regexp, title[0], re.UNICODE) \
                if text and text[0].isdigit() and title else None
            if stars:
                stars = int(re.sub('[ ,]+', '', stars.group(1)))
                ratings[stars] = int(text[0])
        if not total:
            total = sum(ratings.itervalues()) if ratings else 0
        if not average:
            average = sum(k * v for k, v in
                          ratings.iteritems()) / total if ratings else 0

        if not total:
            ratings = {}
            average = float(is_empty(response.xpath(
                '//div[contains(@class, "a-fixed-left-grid")]'\
                '//span[contains(@class, "a-size-base")]/text()'
                ).re(FLOATING_POINT_RGEX), '0').replace(',', ''))
            total = 0
            for mark in response.xpath(
                '//div[contains(@class, "a-fixed-left-grid")]/div'
                '//table/tr[contains(@class, "a-histogram-row")]'):
                star = is_empty(mark.xpath(
                    'td[1]/span/text()').re(FLOATING_POINT_RGEX), 0)
                if star:
                    st = int(is_empty(mark.xpath(
                        'td[last()]/text()').re("\d+"), 0))
                    ratings[star] = st
                    total += st

        #For another HTML makeup
        if not total:
            ratings = {}
            average = 0
            total = is_empty(
                response.xpath(
                    "//span[contains(@class, 'tiny')]"
                    "/span[@class='crAvgStars']/a/text()"
                ).re("[\d\.\,]+"),
                0
            )
            if total:
                if isinstance(total, (str, unicode)):
                    total = int(total.replace(',', '').replace('.', '').strip())
            for rev in response.xpath(
                    '//span[contains(@class, "tiny")]'
                    '//div[contains(@class, "custRevHistogramPopId")]/table/tr'):
                star = is_empty(rev.xpath('td/a/text()').re("\d+"), None)
                if star:
                    ratings[star] = is_empty(
                        rev.xpath('td[last()]/text()').re("[\d\.\,]+"), 0)
                    if ratings[star]:
                        if isinstance(ratings[star], (str, unicode)):
                            ratings[star] = int(
                                ratings[star].replace(',', '').replace('.', '').strip()
                            )
            if ratings:
                average = sum(int(k) * int(v) for k, v in
                              ratings.iteritems()) / int(total) if ratings else 0
                average = float("%.2f" % round(average, 2))

        if not ratings:
            buyer_rev_link = response.xpath(
                '//div[@id="summaryContainer"]//table[@id="histogramTable"]'
                '/../a/@href'
            ).extract()
            if buyer_rev_link:
                buyer_rev_req = Request(
                    url=buyer_rev_link[0],
                    callback=self.get_buyer_reviews_from_2nd_page,
                    meta=response.meta.copy()
                )
                return buyer_rev_req
            else:
                return ZERO_REVIEWS_VALUE

        if int(total) == 0:
            buyer_reviews = ZERO_REVIEWS_VALUE
        else:
            buyer_reviews = BuyerReviews(num_of_reviews=total,
                                         average_rating=average,
                                         rating_by_star=ratings)
        return buyer_reviews

    def get_buyer_reviews_from_2nd_page(self, response):
        if self._has_captcha(response):
            result = self._handle_captcha(
                response, 
                self.get_buyer_reviews_from_2nd_page
            )
        product = response.meta["product"]
        prod_id = response.meta['product_id']
        buyer_reviews = {}
        product["buyer_reviews"] = {}
        total_revs = is_empty(response.xpath(
            '//table[@id="productSummary"]'
            '//span[@class="crAvgStars"]/a/text()').extract(), ''
        ).replace(",", "")
        buyer_reviews["num_of_reviews"] = is_empty(
                re.findall(FLOATING_POINT_RGEX, total_revs), 0
            )
        if int(buyer_reviews["num_of_reviews"]) == 0:
            product["buyer_reviews"] = ZERO_REVIEWS_VALUE
            return product

        buyer_reviews["rating_by_star"] = {}
        buyer_reviews = self.get_rating_by_star(response, buyer_reviews)


        product["buyer_reviews"] = BuyerReviews(**buyer_reviews)

        meta = response.meta.copy()
        meta['product'] = product
        if product['buyer_reviews'] != 0:
            return Request(url=self.REVIEW_DATE_URL.format(product_id=prod_id),
                           meta=meta,
                           dont_filter=True,
                           callback=self._parse_last_buyer_review_date)

        return product

        return product

    def get_rating_by_star(self, response, buyer_reviews):
        table = response.xpath(
                '//table[@id="productSummary"]//'
                'table[@cellspacing="1"]//tr'
            )
        total = 0
        if table:
            for tr in table[:5]:
                rating = is_empty(tr.xpath(
                    'string(.//td[1])').re(FLOATING_POINT_RGEX), '')
                number = is_empty(tr.xpath(
                    'string(.//td[last()])').re(FLOATING_POINT_RGEX), 0)
                is_perc = is_empty(tr.xpath(
                    'string(.//td[last()])').extract(), '')
                if "%" in is_perc:
                    break
                if number:
                    number = int(number.replace(',', ''))
                    buyer_reviews['rating_by_star'][rating] = number
                    total += number*int(rating)
        if total > 0:
            average = float(total)/ float(buyer_reviews['num_of_reviews'])
            buyer_reviews['average_rating'] = round(average, 1)
        return buyer_reviews