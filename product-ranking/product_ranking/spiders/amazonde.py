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
from product_ranking.spiders import BaseProductsSpider, cond_set,\
    cond_set_value, FLOATING_POINT_RGEX
from product_ranking.validation import BaseValidator
from product_ranking.amazon_bestsellers import amazon_parse_department
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.marketplace import Amazon_marketplace

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


class AmazonDeValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = ['model', 'brand', 'price', 'buyer_reviews', 'image_url']
    ignore_fields = [
        'is_in_store_only', 'is_out_of_stock', 'related_products', 'upc',
        'google_source_site', 'description', 'special_pricing', 'bestseller_rank'
    ]
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = False  # ... duplicated requests?
    ignore_log_filtered = False  # ... filtered requests?
    test_requests = {
        'abrakadabrasdafsdfsdf': 0,  # should return 'no products' or just 0 products
        'nothing_found_1234654654': 0,
        'dress code style all': [5, 70],
        'water pump bronze': [2, 70],
        'ceiling fan industrial': [15, 90],
        'kaspersky total': [30, 250],
        'car navigator garmin': [5, 100],
        'yamaha drums midi': [2, 50],
        'black men shoes size 8 red': [5, 70],
        'car audio equalizer pioneer': [5, 120]
    }


class AmazonProductsSpider(BaseValidator, AmazonBaseClass):

    name = 'amazonde_products'
    allowed_domains = ["amazon.de"]

    # Variables for total matches method (_scrape_total_matches)
    total_match_not_found = 'ergab leider keine Produkttreffer.'
    total_matches_re = r'von\s?([\d,.\s?]+)'

    # Locale
    locale = 'en-US'

    SEARCH_URL = "http://www.amazon.de/s/?field-keywords={search_term}"

    REVIEW_DATE_URL = "http://www.amazon.de/product-reviews/" \
                      "{product_id}/ref=cm_cr_dp_see_all_btm?ie=UTF8&" \
                      "showViewpoints=1&sortBy=bySubmissionDateDescending"

    settings = AmazonDeValidatorSettings

    use_proxies = True

    handle_httpstatus_list = [502, 503, 504]

    def __init__(self, captcha_retries='20', *args, **kwargs):
        super(AmazonProductsSpider, self).__init__(*args, **kwargs)

        self.captcha_retries = int(captcha_retries)

        self.mtp_class = Amazon_marketplace(self)

        self._cbw = CaptchaBreakerWrapper()

    def parse_product(self, response):

        if self._has_captcha(response):
            return self._handle_captcha(
                response,
                self.parse_product
            )

        if not self._has_captcha(response):

            super(AmazonProductsSpider, self).parse_product(response)
            prod = response.meta['product']

            self._populate_from_html(response, prod)

            #Get url for marketplace
            url = is_empty(response.xpath(
                    "//div[contains(@class, 'a-box-inner')]/span" \
                    "/a/@href |" \
                    "//div[contains(@class, 'a-box-inner')]" \
                    "//a[contains(@href, '/gp/offer-listing/')]/@href |" \
                    "//div[@id='secondaryUsedAndNew']" \
                    "//a[contains(@href, '/gp/offer-listing/')]/@href"
            ).extract())
            if url:
                mkt_place_link = urlparse.urljoin(
                    response.url,
                    url
                )
            else:
                asin = is_empty(response.xpath("//form[@id='addToCart']"
                    "/input[@name='ASIN']/@value").extract())
                if not asin:
                    asin = is_empty(re.findall(
                        "\"ASIN\"\:\"([^\"]*)", response.body_as_unicode()))
                if asin:
                    url = "/gp/offer-listing/%s/ref=dp_olp_all_mbc"\
                        "?ie=UTF8&amp;condition=new" % (asin,)
                    mkt_place_link = urlparse.urljoin(response.url, url)
                else:
                    mkt_place_link = None

            meta = response.meta.copy()
            meta['product'] = prod
            prod_id = is_empty(re.findall('/dp/([a-zA-Z0-9]+)', response.url))
            if not prod_id:
                prod_id = is_empty(re.findall('/d/([a-zA-Z0-9]+)', response.url))
            meta['product_id'] = prod_id
            if mkt_place_link:
                meta["mkt_place_link"] = mkt_place_link

            _avail = response.css('#availability ::text').extract()
            _avail = ''.join(_avail)
            if "nichtauflager" in _avail.lower().replace(' ', ''):
                prod['is_out_of_stock'] = True

            if isinstance(prod['buyer_reviews'], Request):
                result = prod['buyer_reviews'].replace(meta=meta)
            # else:
                # if prod['buyer_reviews'] != 0:
                #     return Request(url=self.REVIEW_DATE_URL.format(product_id=prod_id),
                #                    meta=meta,
                #                    dont_filter=True,
                #                    callback=self.get_last_buyer_review_date)
            result = prod
        elif response.meta.get('captch_solve_try', 0) >= self.captcha_retries:
            self.log("Giving up on trying to solve the captcha challenge after"
                     " %s tries for: %s" % (self.captcha_retries, response.meta['product']['url']),
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

        months = {'Januar': 'January',
                  'Februar': 'February',
                  u'M\xe4rz': 'March',
                  'Mai': 'May',
                  'Juni': 'June',
                  'Juli': 'July',
                  'Oktober': 'October',
                  'Dezember': 'December'
                  }

        if date:
            for key in months.keys():
                if key in date:
                    date = date.replace(key, months[key])
            d = datetime.strptime(date.replace('.', ''), '%d %B %Y')
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

    def _populate_bestseller_rank(self, product, response):
        ranks = {' > '.join(map(unicode.strip,
                                itm.css('.zg_hrsr_ladder a::text').extract())):
                     int(re.sub('[ ,]', '',
                                itm.css('.zg_hrsr_rank::text').re(
                                    '([\d, ]+)')[0]))
                 for itm in response.css('.zg_hrsr_item')}

        prim_a = response.css('#SalesRank::text, #SalesRank .value::text').re(
            '(\d+){0,1}\.{0,1}(\d+) .*en (.+)\(')
        prim = []
        if prim_a:
            if len(prim_a) > 1 and prim_a[0].isdigit() and prim_a[1].isdigit():
                prim.append(prim_a[0] + prim_a[1])
                prim.append(prim_a[2])
            elif len(prim_a) > 1 and prim_a[0].isdigit():
                prim[0].append(prim_a[0])
                prim[1].append(prim_a[1])
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
        cond_set(
            product,
            'price',
            response.css(
                '#priceblock_ourprice ::text'
                ', #unqualifiedBuyBox .a-color-price ::text'
                ', #priceblock_saleprice ::text'
                ', #buyNewSection .offer-price ::text'
            ).extract(),
        )
        if not product.get('price', None):
            cond_set(
                product,
                'price',
                response.xpath(
                    '//td/b[@class="priceLarge"]/text() |'
                    '//span[@class="olp-padding-right"]'
                    '/span[@class="a-color-price"]/text() |'
                    '//div[contains(@data-reftag,"atv_dp_bb_est_hd_movie")]'
                    '/button/text() |'
                    '//span[@id="priceblock_saleprice"]/text() |'
                    '//li[@class="swatchElement selected"]'
                    '//span[@class="a-color-price"]/text() |'
                    '//div[contains(@data-reftag,"atv_dp_bb_est_sd_movie")]'
                    '/button/text() |'
                    '//div[@id="mocaBBRegularPrice"]'
                    '/div/text()[normalize-space()] |'
                    '//span[@id="actualPriceValue"]/b/text()'
                    '[normalize-space()] |'
                    '//span[@id="actualPriceValue"]/text()[normalize-space()]|'
                    '//span[@class="price"]/text()'
                ).extract()
            )
        if not product.get('price', None):
            _price = re.search(
                r'a-color-price aw-nowrap&quot;&gt;EUR ([\d\.\,]+)&lt;/span&gt',
                response.body
            )
            if _price:
                _price = _price.group(1).strip().replace(' ', '')\
                    .replace('.', '').replace(',', '.')
                cond_set(product, 'price', ['EUR ' + _price])

        if not product.get('price', None):
            _price = response.xpath('//*[@id="product-price"]/text()').extract()
            cond_set(product, 'price', [_price])
        if not product.get('price', None):
            _price = response.xpath(
                '//*[contains(@class, "a-color-price")]/text()').extract()
            if _price:
                product['price'] = _price[0].strip()

        if isinstance(product.get('price', None), (list, tuple)):
            if product.get('price', None):
                product['price'] = product['price'][0]

        if product.get('price', None):
            if not u'EUR' in product.get('price', ''):
                self.log('Invalid price at: %s' % response.url, level=ERROR)
            else:
                price = re.findall(FLOATING_POINT_RGEX,
                    product['price'].replace(u'\xa0', '').strip())
                price = re.sub('[, ]', '.', price[0])
                product['price'] = Price(
                    price=price,
                    priceCurrency='EUR'
                )
        else:
            product.pop('price', '')  # remove the key completely

        if 'usverkauft' in response.body_as_unicode().lower().replace(' ', '') \
            or 'ergriffen' in response.body_as_unicode().lower().replace(' ', '') \
            or 'ichtauflager' in response.body_as_unicode().lower().replace(' ', '') \
            or 'ichtamlager' in response.body_as_unicode().lower().replace(' ', ''):
                with open('/tmp/_am_urls', 'a') as fh:
                    fh.write(str(response.url) + '\n')

        description = response.css('.productDescriptionWrapper').extract()
        if not description:
            description = response.xpath(
                '//div[@id="descriptionAndDetails"] |'
                '//div[@id="feature-bullets"] |'
                '//div[@id="ps-content"] |'
                '//div[@id="productDescription_feature_div"] |'
                '//div[contains(@class, "dv-simple-synopsis")] |'
                '//div[@class="bucket"]/div[@class="content"]'
            ).extract()
        cond_set(
            product,
            'description',
            description,
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
            elif key == 'ASIN' and model is None or key == 'ITEM MODEL NUMBER':
                model = li.xpath('text()').extract()
        if not product.get('model'):
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
                    cond_set(product, 'model', (model,))

        cond_set(product, 'model', model, conv=string.strip)
        self._populate_bestseller_rank(product, response)
        #revs = self._buyer_reviews_from_html(response)
        #if isinstance(revs, Request):
        #    meta = {"product": product}
        #    product['buyer_reviews'] = revs.replace(meta=meta)
        #else:
        #    product['buyer_reviews'] = revs
        product['buyer_reviews'] = ''

    def _buyer_reviews_from_html(self, response):
        stars_regexp = r'% .+ (\d[\d, ]*) '
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
            stars = re.search(stars_regexp, title[0]) \
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

        # if not ratings:
        #     buyer_rev_link = response.xpath(
        #         '//div[@id="summaryContainer"]//table[@id="histogramTable"]'
        #         '/../a/@href'
        #     ).extract()
        #     if buyer_rev_link:
        #         buyer_rev_req = Request(
        #             url=buyer_rev_link[0],
        #             callback=self.get_buyer_reviews_from_2nd_page,
        #             meta=response.meta.copy()
        #         )
        #         return buyer_rev_req
        #     else:
        #         return ZERO_REVIEWS_VALUE

        # add missing marks
        for mark in range(1, 6):
            if mark not in ratings:
                if str(mark) not in ratings:
                    if unicode(mark) not in ratings:
                        ratings[unicode(mark)] = 0

        buyer_reviews = BuyerReviews(num_of_reviews=total,
                                     average_rating=average,
                                     rating_by_star=ratings)
        return buyer_reviews

    def get_buyer_reviews_from_2nd_page(self, response):

        if self._has_captcha(response):
            return self._handle_captcha(
                response,
                self.get_buyer_reviews_from_2nd_page
            )

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
        response.meta["called_class"] = self
        response.meta["next_req"] = None
        return self.mtp_class.parse_marketplace(
            response, replace_comma_with_dot=True)

    def _validate_url(self, val):
        if not bool(val.strip()):  # empty
            return False
        if len(val.strip()) > 1500:  # too long
            if not 'redirect' in val:
                return False
            elif len(val.strip()) > 3000:
                return False
        if val.strip().count(u' ') > 5:  # too many spaces
            return False
        if not val.strip().lower().startswith('http'):
            return False
        return True

    def _validate_title(self, val):
        if not bool(val.strip()):  # empty
            return False
        if len(val.strip()) > 1500:  # too long
            return False
        if val.strip().count(u' ') > 300:  # too many spaces
            return False
        if '<' in val or '>' in val:  # no tags
            return False
        return True

    def exit_point(self, product, next_req):
        if next_req:
            next_req.replace(meta={"product": product})
            return next_req
        return product