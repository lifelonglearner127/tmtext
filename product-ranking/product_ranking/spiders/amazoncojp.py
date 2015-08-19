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
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    cond_set_value, FLOATING_POINT_RGEX
from product_ranking.amazon_tests import AmazonTests

from product_ranking.amazon_bestsellers import amazon_parse_department

from product_ranking.amazon_base_class import AmazonBaseClass

try:
    from captcha_solver import CaptchaBreakerWrapper
except ImportError as e:
    import sys
    print(
        "### Failed to import CaptchaBreaker.",
        "Will continue without solving captchas:",
        e,
        file=sys.stderr,
    )

    class FakeCaptchaBreaker(object):
        @staticmethod
        def solve_captcha(url):
            msg("No CaptchaBreaker to solve: %s" % url, level=WARNING)
            return None
    CaptchaBreakerWrapper = FakeCaptchaBreaker

is_empty = lambda x, y=None: x[0] if x else y

class AmazoncojpValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
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
        'alhpa beta vinigretto': 0,
        'dandy united': [30, 300],
        'magi yellow': [5, 150],
        'Led Tv screen': [40, 300],
        'red ship coat': [10, 150],
        'trash smash': [20, 250],
        'all for PC now': [15, 150],
        'iphone blast': [10, 200],
        'genius electronics black': [5, 120],
        'batteries 330v': [40, 270]
    }

class AmazonProductsSpider(AmazonTests, AmazonBaseClass):
    name = 'amazonjp_products'
    allowed_domains = ["amazon.co.jp"]

    settings = AmazoncojpValidatorSettings()

    # Variables for total matches method (_scrape_total_matches)
    total_match_not_found = '検索に一致する商品はありませんでした'
    total_matches_re = r'検索結果\s?([\d,.\s?]+)'

    # Locale
    locale = 'en-US'

    # Price currency
    price_currency = 'JPY'
    price_currency_view = '￥'

    SEARCH_URL = "http://www.amazon.co.jp/s/?field-keywords={search_term}"

    REVIEW_DATE_URL = 'http://www.amazon.co.jp/product-reviews/{product_id}/' \
                      'ref=cm_cr_pr_top_recent/376-5667359-8866511?ie=UTF8&' \
                      'showViewpoints=0&sortBy=bySubmissionDateDescending'

    def __init__(self, captcha_retries='10', *args, **kwargs):
        super(AmazonProductsSpider, self).__init__(*args, **kwargs)

        self.captcha_retries = int(captcha_retries)

        self._cbw = CaptchaBreakerWrapper()

    def parse_product(self, response):

        if not self._has_captcha(response):
            super(AmazonProductsSpider, self).parse_product(response)
            prod = response.meta['product']

            self._populate_from_html(response, prod)

            mkt_place_link = is_empty(response.xpath(
                    "//div[contains(@class, 'a-box-inner')]" \
                    "//a[contains(@href, '/gp/offer-listing/')]/@href |" \
                    "//div[@id='secondaryUsedAndNew']" \
                    "//a[contains(@href, '/gp/offer-listing/')]/@href"
            ).extract())

            meta = response.meta.copy()
            meta['product'] = prod
            prod_id = is_empty(re.findall('/dp/([a-zA-Z0-9]+)', response.url))
            meta['product_id'] = prod_id

            if mkt_place_link:
                mkt_place_link = urlparse.urljoin(response.url, mkt_place_link)
                meta["mkt_place_link"] = mkt_place_link

            if isinstance(prod['buyer_reviews'], Request):
                result = prod['buyer_reviews'].replace(meta=meta)
            else:
                if prod['buyer_reviews'] != 0:
                    return Request(url=self.REVIEW_DATE_URL.format(product_id=prod_id),
                                   meta=meta,
                                   dont_filter=True,
                                   callback=self.get_last_buyer_review_date)

            if mkt_place_link:
                result = Request(
                    url=meta['mkt_place_link'],
                    callback=self.parse_marketplace,
                    meta=meta,
                    dont_filter=True
                )
            else:
                cond_set_value(prod, 'marketplace', [])
                result = prod

        elif response.meta.get('captch_solve_try', 0) >= self.captcha_retries:
            product = response.meta['product']
            self.log("Giving up on trying to solve the captcha challenge after"
                     " %s tries for: %s" % (self.captcha_retries, product['url']),
                     level=WARNING)
            result = None
        else:
            result = self._handle_captcha(response, self.parse_product)
        return result

    def get_last_buyer_review_date(self, response):
        if self._has_captcha(response):
            return self._handle_captcha(
                response,
                self.get_last_buyer_review_date
            )

        product = response.meta['product']
        date = is_empty(response.xpath(
            '//table[@id="productReviews"]/tr/td/div/div/span/nobr/text()'
        ).extract())
        if date:
            d = datetime.strptime(date, '%Y/%m/%d')
            date = d.strftime('%d/%m/%Y')
            product['last_buyer_review_date'] = date

        else:
            date = is_empty(response.xpath(
                '//span[contains(@class, "review-date")]/text()'
            ).extract())
            if date:
                d = datetime.strptime(' '.join(re.findall('\d+', date)), '%Y %m %d')
                date = d.strftime('%d/%m/%Y')
                product['last_buyer_review_date'] = date

        new_meta = response.meta.copy()
        new_meta['product'] = product

        if 'mkt_place_link' in response.meta.keys():
            return Request(
                url=response.meta['mkt_place_link'],
                callback=self.parse_marketplace,
                meta=new_meta,
                dont_filter=True,
            )
        else:
            cond_set_value(product, 'marketplace', [])
        return product

    def _populate_from_html(self, response, product):

        # Some data is in a list (ul element).
        for li in response.css('td.bucket > .content > ul > li'):
            raw_keys = li.xpath('b/text()').extract()
            if not raw_keys:
                # This is something else, ignore.
                continue

            key = raw_keys[0].strip(' :').upper()
            if key == 'UPC':
                # Some products have several UPCs.
                raw_upc = li.xpath('text()').extract()[0]
                cond_set_value(
                    product,
                    'upc',
                    raw_upc.strip().replace(' ', ';'),
                )
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
        average = re.search(u'\u3061.*\d[\d ,.]*',
                            average[0] if average else '')
        average = float(
            re.sub('[ ,]+', '', average.group().replace(u'\u3061', ''))
        ) if average else None
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
                return 0

        buyer_reviews = BuyerReviews(num_of_reviews=total,
                                     average_rating=average,
                                     rating_by_star=ratings)
        return buyer_reviews

    def get_buyer_reviews_from_2nd_page(self, response):
        product = response.meta["product"]
        prod_id = response.meta["product_id"]
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
            product["buyer_reviews"] = 0
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
                           callback=self.get_last_buyer_review_date)

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

    def parse_marketplace(self, response):
        if self._has_captcha(response):
            result = self._handle_captcha(response, self.parse_marketplace)

        product = response.meta["product"]

        marketplaces = response.meta.get("marketplaces", [])

        for seller in response.xpath(
            '//div[contains(@class, "a-section")]/' \
            'div[contains(@class, "a-row a-spacing-mini olpOffer")]'):

            price = is_empty(seller.xpath(
                'div[contains(@class, "a-column")]' \
                '/span[contains(@class, "price")]/text()'
            ).re(FLOATING_POINT_RGEX), 0)

            name = is_empty(seller.xpath(
                'div/p[contains(@class, "Name")]/span/a/text()').extract())

            marketplaces.append({
                "price": Price(price=price, priceCurrency="USD"), 
                "name": name
            })

        next_link = is_empty(response.xpath(
            "//ul[contains(@class, 'a-pagination')]" \
            "/li[contains(@class, 'a-last')]/a/@href"
        ).extract())

        if next_link:
            meta = {"product": product, "marketplaces": marketplaces}
            return Request(
                url=urlparse.urljoin(response.url, next_link), 
                callback=self.parse_marketplace,
                meta=meta,
                dont_filter=True
            )

        product["marketplace"] = marketplaces

        return product
