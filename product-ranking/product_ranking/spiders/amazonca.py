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

from product_ranking.items import SiteProductItem, Price, BuyerReviews, \
    MarketplaceSeller
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import (BaseProductsSpider, cond_set,
                                     cond_set_value, FLOATING_POINT_RGEX)

from product_ranking.amazon_bestsellers import amazon_parse_department
from product_ranking.marketplace import Amazon_marketplace
from product_ranking.amazon_tests import AmazonTests
from spiders_shared_code.amazon_variants import AmazonVariants

from product_ranking.amazon_base_class import AmazonBaseClass

is_empty = lambda x, y=None: x[0] if x else y

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


class AmazoncaValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = ['model', 'brand', 'description', 'price', 'bestseller_rank']
    ignore_fields = [
        'is_in_store_only', 'is_out_of_stock', 'related_products', 'upc',
        'buyer_reviews', 'google_source_site', 'special_pricing',
    ]
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = False  # ... duplicated requests?
    ignore_log_filtered = False  # ... filtered requests?
    test_requests = {
        'abrakadabrasdafsdfsdf': 0,  # should return 'no products' or just 0 products
        'nothing_found_1234654654': 0,
        'transformator': [50, 300],
        'kaspersky total': [3, 50],
        'gold sold fold': [5, 200],  # spider should return from 5 to 200 products
        'yamaha drums midi': [5, 100],
        'black men shoes size 8 red': [5, 100],
        'antoshka': [5, 150],
        'apple ipod nano gold': [50, 300],
        'programming product best': [5, 100],
    }


class AmazonProductsSpider(AmazonTests, AmazonBaseClass):
    name = 'amazonca_products'
    allowed_domains = ["amazon.ca"]

    # String from html body that means there's no results
    total_match_not_found = 'did not match any products.'
    # Regexp for total matches to parse a number from html body
    total_matches_re = r'of\s?([\d,.\s?]+)'

    # Locale
    locale = 'en-US'

    SEARCH_URL = "http://www.amazon.ca/s/?field-keywords={search_term}"

    REVIEW_DATE_URL = 'http://www.amazon.ca/product-reviews/{product_id}/' \
                      'ref=cm_cr_pr_top_recent?ie=UTF8&showViewpoints=0&' \
                      'sortBy=bySubmissionDateDescending'

    settings = AmazoncaValidatorSettings

    def __init__(self, captcha_retries='10', *args, **kwargs):
        super(AmazonProductsSpider, self).__init__(*args, **kwargs)

        self.captcha_retries = int(captcha_retries)

        self._cbw = CaptchaBreakerWrapper()

        self.mtp_class = Amazon_marketplace(self)

    def parse_product(self, response):

        if not self._has_captcha(response):
            super(AmazonProductsSpider, self).parse_product(response)
            prod = response.meta['product']

            self._populate_from_html(response, prod)

            mkt_place_link = urlparse.urljoin(
                response.url,
                is_empty(response.xpath(
                    "//div[contains(@class, 'a-box-inner')]" \
                    "//a[contains(@href, '/gp/offer-listing/')]/@href |" \
                    "//div[@id='secondaryUsedAndNew']" \
                    "//a[contains(@href, '/gp/offer-listing/')]/@href"
                ).extract()))
            prod_id = is_empty(re.findall('/dp/([a-zA-Z0-9]+)', response.url))
            meta = response.meta.copy()
            meta = {"product": prod}
            if mkt_place_link:
                meta['mkt_place_link'] = mkt_place_link
            return Request(
                url=self.REVIEW_DATE_URL.format(product_id=prod_id),
                callback=self.parse_last_buyer_review_date,
                meta=meta,
                dont_filter=True,
            )
        elif response.meta.get('captch_solve_try', 0) >= self.captcha_retries:
            self.log(
                "Giving up on trying to solve the captcha challenge after"
                " %s tries for: %s" % (self.captcha_retries, prod['url']),
                level=WARNING
            )
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
            try:
                d = datetime.strptime(date.replace('.', ''), '%B %d %Y')
            except:
                d = datetime.strptime(date.replace('.', ''), '%b %d %Y')
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
        return product

    def populate_bestseller_rank(self, product, response):
        ranks = {' > '.join(map(unicode.strip,
                                itm.css('.zg_hrsr_ladder a::text').extract())):
                     int(re.sub('[ ,]', '',
                                itm.css('.zg_hrsr_rank::text').re(
                                    '([\d, ]+)')[0]))
                 for itm in response.css('.zg_hrsr_item')}
        prim = response.css('#SalesRank::text, #SalesRank .value'
                            '::text').re('([\d ,]+) .*in (.+)\(')
        if prim:
            prim = {prim[1].strip(): int(re.sub('[ ,]', '', prim[0]))}
            ranks.update(prim)
        ranks = [{'category': k, 'rank': v} for k, v in ranks.iteritems()]
        cond_set_value(product, 'category', ranks)
        # parse department
        department = amazon_parse_department(ranks)
        if department is None:
            product['department'] = None
        else:
            product['department'], product['bestseller_rank'] \
                = department.items()[0]

    def _populate_from_html(self, response, product):
        ### Populate variants with CH/SC class
        av = AmazonVariants()
        av.setupSC(response)
        product['variants'] = av._variants()

        price = response.xpath(
            '//span[@id="priceblock_saleprice"]/text()'
        ).extract()
        if not price:
            price = response.css('#priceblock_ourprice ::text').extract()
        if not price:
            price = response.xpath(
                '//div[contains(@class, "a-box")]//div[@class="a-row"]'
                '//span[contains(@class, "a-color-price")]/text() |'
                '//b[@class="priceLarge"]/text() |'
                '//span[@class="olp-padding-right"]'
                '/span[@class="a-color-price"]/text() |'
                '//div[@class="a-box-inner"]/div/'
                'span[@class="a-color-price"]/text() |'
                '//span[@id="priceblock_dealprice"]/text()'
            ).extract()

        cond_set(
            product,
            'price',
            price,
        )
        if product.get('price', None):
            price = product.get('price', '')
            if not u'CDN$' in price:
                if 'FREE' in price or ' ' in price:
                    product['price'] = Price(
                        priceCurrency='CAD',
                        price='0.00'
                    )
                else:
                    self.log('Invalid price at: %s' % response.url,
                             level=ERROR)
            else:
                price = re.findall('[\d ,.]+\d', product['price'])
                price = re.sub('[, ]', '', price[0])
                product['price'] = Price(
                    price=price.replace(u'CDN$', '').replace(
                        ' ', '').replace(',', '').strip(),
                    priceCurrency='CAD'
                )

        self.mtp_class.get_price_from_main_response(response, product)

        description = response.css('.productDescriptionWrapper').extract()
        if not description:
            description = response.xpath(
                '//div[@id="feature-bullets"] |'
                '//div[@class="bucket"]/div[@class="content"]'
            ).extract()
        cond_set(
            product,
            'description',
            description,
        )
        image = response.css(
                '#imgTagWrapperId > img ::attr(data-old-hires)').extract()
        if not image:
            j = re.findall(r"'colorImages': { 'initial': (.*)},",
                           response.body)
            if not j:
                j = re.findall(r'colorImages = {"initial":(.*)}',
                               response.body)
            if j:
                try:
                    res = json.loads(j[0])
                    try:
                        image = res[0]['large']
                    except:
                        image = res[1]['large']
                    image = [image]
                except:
                    pass
        if not image:
            image = response.xpath(
                '//div[@id="img-canvas"]/img/@src |'
                '//img[@id="main-image"]/@src |'
                '//div[@class="main-image-inner-wrapper"]/img/@src'
            ).extract()

        cond_set(
            product,
            'image_url',
            image
        )

        # Some data is in a list (ul element).
        model = None
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
            elif (key == 'ASIN' and model is None
                    or key == 'ITEM MODEL NUMBER'):
                model = li.xpath('text()').extract()
        cond_set(product, 'model', model, conv=string.strip)
        if not product.get('model', "").strip():
            model = is_empty(response.xpath(
                '//div[contains(@class, "content")]/ul/'
                'li/b[contains(text(), "ASIN")]/../text() |'
                '//table/tbody/tr/'
                'td[contains(@class, "label") and contains(text(), "ASIN")]'
                '/../td[contains(@class, "value")]/text() |'
                '//div[contains(@class, "content")]/ul/'
                'li/b[contains(text(), "ISBN-10")]/../text()'
            ).extract())
            if model:
                cond_set(product, 'model', (model.strip(),))
        self._buyer_reviews_from_html(response, product)
        self.populate_bestseller_rank(product, response)

    def _buyer_reviews_from_html(self, response, product):
        stars_regexp = r'.+(\d[\d, ]*)'
        total = response.css('#summaryStars a::text')
        total = total or response.css('#revSum a::text')
        total = total.re('(\d[\d, ]*) reviews')
        total = total[0] if total else None
        total = int(re.sub('[ ,]+', '', total)) if total else None
        average = response.css('#avgRating span::text')
        average = average or response.css('acrRating')
        average = average.re('\d[\d ,.]*')
        average = float(average[0]) if average else None
        ratings = {1: 0, 2: 0, 3: 0, 4: 0,5: 0}
        for row in response.css('.a-histogram-row .a-span10 ~ td a'):
            title = row.css('::attr(title)').extract()
            text = row.css('::text').extract()
            stars = re.search(stars_regexp, title[0], re.UNICODE) \
                if text and text[0].isdigit() and title else None
            if stars:
                stars = int(re.sub('[ ,]+', '', stars.group(1)))
                ratings[stars] = int(text[0])
        if not sum(ratings.values()):
            ratings = response.css('.histoCount::text').re('\d[\d ,]*')
            ratings = [re.sub(', ', '', rating) for rating in ratings]
            ratings = {star + 1: int(num)
                       for star, num in enumerate(reversed(ratings))}
        if not total:
            total = sum(ratings.itervalues()) if ratings else 0
        buyer_reviews = BuyerReviews(num_of_reviews=total,
                                     average_rating=average,
                                     rating_by_star=ratings)
        cond_set_value(product, 'buyer_reviews',
                       buyer_reviews if total else ZERO_REVIEWS_VALUE)

    def parse_marketplace(self, response):
        response.meta["called_class"] = self
        response.meta["next_req"] = None
        return self.mtp_class.parse_marketplace(response)

    def exit_point(self, product, next_req):
        if next_req:
            next_req.replace(meta={"product": product})
            return next_req
        return product

    def _validate_title(self, val):
        if not bool(val.strip()):  # empty
            return False
        if len(val.strip()) > 2500:  # too long
            return False
        if val.strip().count(u' ') > 600:  # too many spaces
            return False
        if '<' in val or '>' in val:  # no tags
            if not re.search("(\<\s?\d)|(\>\s?\d)", val):
                return False
        return True
