# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import json
import string
import re
from urllib import unquote
import urlparse

from scrapy.http import Request
from scrapy.http.request.form import FormRequest
from scrapy.log import msg, ERROR, WARNING, INFO, DEBUG

from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, \
    cond_set, cond_set_value, FLOATING_POINT_RGEX
from product_ranking.amazon_tests import AmazonTests

from product_ranking.amazon_bestsellers import amazon_parse_department
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.marketplace import Amazon_marketplace
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


class AmazonValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
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
        'nothing_found_1234654654': 0,
        'samsung t9500 battery 2600 li-ion warranty': [30, 250],
        'water pump bronze inch apollo': [2, 30],
        'ceiling fan industrial white system': [5, 50],
        'kaspersky total': [20, 100],
        'car navigator garmin maps 44LM': [1, 20],
        'yamaha drums midi': [50, 300],
        'black men shoes size 8  red stripes': [50, 300],
        'car audio equalizer pioneer mp3': [40, 150]
    }


class AmazonProductsSpider(AmazonTests, AmazonBaseClass):
    name = 'amazon_products'
    allowed_domains = ["amazon.com"]

    user_agent = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:35.0) Gecko'
                  '/20100101 Firefox/35.0')

    # String from html body that means there's no results
    total_match_not_found = 'did not match any products.'
    # Regexp for total matches to parse a number from html body
    total_matches_re = r'of\s?([\d,.\s?]+)'

    # Locale
    locale = 'en-US'

    SEARCH_URL = ('http://www.amazon.com/s/ref=nb_sb_noss_1?url=search-alias'
                  '%3Daps&field-keywords={search_term}')

    settings = AmazonValidatorSettings

    buyer_reviews_stars = ['one_star', 'two_star', 'three_star', 'four_star',
                           'five_star']

    def __init__(self, captcha_retries='10', *args, **kwargs):
        super(AmazonProductsSpider, self).__init__(*args, **kwargs)

        self.captcha_retries = int(captcha_retries)

        self.mtp_class = Amazon_marketplace(self)

        self._cbw = CaptchaBreakerWrapper()

    def parse_product(self, response):

        if not self._has_captcha(response):
            super(AmazonProductsSpider, self).parse_product(response)
            prod = response.meta['product']

            self._populate_from_html(response, prod)

            prod['buyer_reviews'] = self._build_buyer_reviews(response)

            mkt_place_link = urlparse.urljoin(
                response.url,
                is_empty(response.xpath(
                    "//div[contains(@class, 'a-box-inner')]" \
                    "//a[contains(@href, '/gp/offer-listing/')]/@href |" \
                    "//div[@id='secondaryUsedAndNew']" \
                    "//a[contains(@href, '/gp/offer-listing/')]/@href"
                ).extract()))

            new_meta = response.meta.copy()
            new_meta['product'] = prod
            if isinstance(prod["buyer_reviews"], Request):
                if mkt_place_link:
                    new_meta["mkt_place_link"] = mkt_place_link
                return prod["buyer_reviews"].replace(meta=new_meta, dont_filter=True)

            if mkt_place_link:
                return Request(
                    url=mkt_place_link, 
                    callback=self.parse_marketplace,
                    meta=new_meta,
                    dont_filter=True
                )

            result = prod

        elif response.meta.get('captch_solve_try', 0) >= self.captcha_retries:
            self.log("Giving up on trying to solve the captcha challenge after"
                     " %s tries for: %s" % (self.captcha_retries, prod['url']),
                     level=WARNING)
            result = None
        else:
            result = self._handle_captcha(response, self.parse_product)

        return result

    def _get_price(self, response, product):
        """ Parses and sets the product price, with all possible variations
        :param response: Scrapy's Response obj
        :param product: Scrapy's Item (dict, basically)
        :return: None
        """
        cond_set(
            product,
            'price',
            response.css(
                '#priceblock_ourprice ::text'
                ', #unqualifiedBuyBox .a-color-price ::text'
                ', #priceblock_saleprice ::text'
                ', #actualPriceValue ::text'
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
                    '/div/text()[normalize-space()]'
                ).extract()
            )
        if product.get('price', None):
            if not '$' in product['price']:
                if 'FREE' in product['price'] or ' ' in product['price']:
                    product['price'] = Price(
                        priceCurrency='USD',
                        price='0.00'
                    )
                else:
                    self.log('Currency symbol not recognized: %s' % response.url,
                             level=ERROR)
            else:
                price = re.findall('[\d ,.]+\d', product['price'])
                price = re.sub('[, ]', '', price[0])
                product['price'] = Price(
                    priceCurrency='USD',
                    price=price.replace('$', '').strip()\
                        .replace(',', '')
                )

    def populate_bestseller_rank(self, product, response):
        ranks = {' > '.join(map(unicode.strip,
                                itm.css('.zg_hrsr_ladder a::text').extract())):
                     int(re.sub('[ ,]', '',
                                itm.css('.zg_hrsr_rank::text').re(
                                    '([\d, ]+)')[0]))
                 for itm in response.css('.zg_hrsr_item')}
        prim = response.css('#SalesRank::text, #SalesRank .value'
                            '::text').re('#([\d ,]+) .*in (.+)\(')
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
        cond_set(product, 'brand', response.css('#brand ::text').extract())
        self._get_price(response, product)

        brand_name = is_empty(response.xpath('//a[@id="brand"]/text()').
            extract())
        cond_set(product, 'brand', brand_name)

        # parse Subscribe & Save
        price_ss = response.xpath('//*[contains(text(), "Subscribe & Save:")]/'
                                  '../..//*[@id="subscriptionPrice"]/text()').extract()
        if price_ss:
            price_ss = price_ss[0].strip()
            if price_ss.startswith('$'):
                price_ss = price_ss.replace(' ', '').replace(',', '').strip('$')
                try:
                    product['price_subscribe_save'] = float(str(price_ss))
                except Exception, _:
                    pass

        av = AmazonVariants()
        av.setupSC(response)
        product['variants'] = av._variants()

        brand_logo = is_empty(response.xpath('//a[@id="brand"]/@href')
            .extract())
        if brand_logo:
            brand = brand_logo.split('/')[1]
            cond_set_value(product, 'brand', brand)

        self.mtp_class.get_price_from_main_response(response, product)

        spans = response.xpath('//span[@class="a-text-bold"]')
        for span in spans:
            text = is_empty(span.xpath('text()').extract())
            if text and 'Item model number:' in text:
                possible_model = span.xpath('../span/text()').extract()
                if len(possible_model) > 1:
                    model = possible_model[1]
                    cond_set_value(product, 'model', model)

        description = response.css('.productDescriptionWrapper').extract()
        if not description:
            iframe_content = re.findall(
                r'var iframeContent = "(.*)"', response.body
            )
            if iframe_content:
                res = iframe_content[0]
                f = re.findall('body%3E%0A%20%20(.*)'
                    '%0A%20%20%3C%2Fbody%3E%0A%3C%2Fhtml%3E%0A', res)
                if f:
                    desc = unquote(f[0])
                    description = [desc]
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
        cond_set(product, 'model', model, conv=string.strip)
        self.populate_bestseller_rank(product, response)

    def _get_rating_by_star_by_individual_request(self, response):
        product = response.meta['product']
        mkt_place_link = response.meta.get("mkt_place_link")
        current_star = response.meta['_current_star']
        current_star_int = [
            i+1 for i, _star in enumerate(self.buyer_reviews_stars)
            if _star == current_star
        ][0]
        br = product.get('buyer_reviews')
        if br:
            rating_by_star = br.get('rating_by_star')
        else:
            if mkt_place_link:
                return self.mkt_request(mkt_place_link, {"product": product})
            return product
        if not rating_by_star:
            rating_by_star = {}
        num_of_reviews_for_star = re.search(
            r'Showing .+? of ([\d,\.]+) reviews', response.body)
        if num_of_reviews_for_star:
            num_of_reviews_for_star = num_of_reviews_for_star.group(1)
            num_of_reviews_for_star = num_of_reviews_for_star\
                .replace(',', '').replace('.', '')
            rating_by_star[str(current_star_int)] \
                = int(num_of_reviews_for_star)
        if not str(current_star_int) in rating_by_star.keys():
            rating_by_star[str(current_star_int)] = 0

        product['buyer_reviews']['rating_by_star'] = rating_by_star
        if len(product['buyer_reviews']['rating_by_star']) >= 5:
            product['buyer_reviews']['num_of_reviews'] \
                = int(product['buyer_reviews']['num_of_reviews'])
            product['buyer_reviews']['average_rating'] \
                = float(product['buyer_reviews']['average_rating'])
            # ok we collected all marks for all stars - can return the product
            product['buyer_reviews'] = BuyerReviews(**product['buyer_reviews'])
            if mkt_place_link:
                return self.mkt_request(mkt_place_link, {"product": product})
            return product

    def _get_asin_from_url(self, url):
        match = re.search(r'/([A-Z0-9]{4,15})/', url)
        if match:
            return match.group(1)

    def _create_post_requests(self, response, asin):
        url = ('http://www.amazon.com/ss/customer-reviews/ajax/reviews/get/'
               'ref=cm_cr_pr_viewopt_sr')
        meta = response.meta
        meta['_current_star'] = {}
        for star in self.buyer_reviews_stars:
            args = {
                'asin': asin, 'filterByStar': star,
                'filterByKeyword': '', 'formatType': 'all_formats',
                'pageNumber': '1', 'pageSize': '10', 'sortBy': 'helpful',
                'reftag': 'cm_cr_pr_viewopt_sr', 'reviewerType': 'all_reviews',
                'scope': 'reviewsAjax0',
            }
            meta['_current_star'] = star
            yield FormRequest(
                url=url, formdata=args, meta=meta,
                callback=self._get_rating_by_star_by_individual_request,
                dont_filter=True
            )

    def get_buyer_reviews_from_2nd_page(self, response):
        if self._has_captcha(response):
            return self._handle_captcha(
                response, 
                self.get_buyer_reviews_from_2nd_page
            )
        product = response.meta["product"]
        buyer_reviews = {}
        product["buyer_reviews"] = {}
        buyer_reviews["num_of_reviews"] = is_empty(response.xpath(
            '//span[contains(@class, "totalReviewCount")]/text()').extract(),
        '').replace(",", "")
        if not buyer_reviews['num_of_reviews']:
            buyer_reviews['num_of_reviews'] = ZERO_REVIEWS_VALUE
        average = is_empty(response.xpath(
            '//div[contains(@class, "averageStarRatingNumerical")]//span/text()'
        ).extract(), "")

        buyer_reviews["average_rating"] = \
            average.replace('out of 5 stars', '')

        buyer_reviews["rating_by_star"] = {}
        buyer_reviews = self.get_rating_by_star(response, buyer_reviews)[0]

        #print('*' * 20, 'parsing buyer reviews from', response.url)

        if not buyer_reviews.get('rating_by_star'):
            response.meta['product']['buyer_reviews'] = buyer_reviews
            # if still no rating_by_star (probably the rating is percent-based)
            # return self._create_post_requests(
            #     response, self._get_asin_from_url(response.url))
            #return

        product["buyer_reviews"] = BuyerReviews(**buyer_reviews)

        meta = {"product": product}
        mkt_place_link = response.meta.get("mkt_place_link", None)
        if mkt_place_link:
            return Request(
                url=mkt_place_link, 
                callback=self.parse_marketplace,
                meta=meta,
                dont_filter=True
            )

        return product

    def _build_buyer_reviews(self, response):
        buyer_reviews = {}

        total = response.xpath(
            'string(//*[@id="summaryStars"])').re(FLOATING_POINT_RGEX)
        if not total:
            total = response.xpath(
                'string(//div[@id="acr"]/div[@class="txtsmall"]'
                '/div[contains(@class, "acrCount")])'
            ).re(FLOATING_POINT_RGEX)
            if not total:
                return ZERO_REVIEWS_VALUE
        buyer_reviews['num_of_reviews'] = int(total[0].replace(',', ''))

        average = response.xpath(
            '//*[@id="summaryStars"]/a/@title')
        if not average:
            average = response.xpath(
                '//div[@id="acr"]/div[@class="txtsmall"]'
                '/div[contains(@class, "acrRating")]/text()'
            )
        average = average.extract()[0].replace('out of 5 stars','')
        buyer_reviews['average_rating'] = float(average)

        buyer_reviews['rating_by_star'] = {}
        buyer_reviews, table = self.get_rating_by_star(response, buyer_reviews)

        if not buyer_reviews.get('rating_by_star'):
            # scrape new buyer reviews request (that will lead to a new page)
            buyer_rev_link = is_empty(response.xpath(
                '//div[@id="revSum"]//a[contains(text(), "See all")' \
                ' or contains(text(), "See the customer review")' \
                ' or contains(text(), "See both customer reviews")]/@href'
            ).extract())
            buyer_rev_req = Request(
                url=buyer_rev_link,
                callback=self.get_buyer_reviews_from_2nd_page
            )
            # now we can safely return Request
            #  because it'll be re-crawled in the `parse_product` method
            return buyer_rev_req

        return BuyerReviews(**buyer_reviews)

    def get_rating_by_star(self, response, buyer_reviews):
        table = response.xpath(
            '//table[@id="histogramTable"]'
            '/tr[@class="a-histogram-row"]')
        if table:
            for tr in table: #td[last()]//text()').re('\d+')
                rating = is_empty(tr.xpath(
                    'string(.//td[1])').re(FLOATING_POINT_RGEX))
                number = is_empty(tr.xpath(
                    'string(.//td[last()])').re(FLOATING_POINT_RGEX))
                is_perc = is_empty(tr.xpath(
                    'string(.//td[last()])').extract())
                if "%" in is_perc:
                    break
                if number:
                    buyer_reviews['rating_by_star'][rating] = int(
                        number.replace(',', '')
                    )
        else:
            table = response.xpath(
                '//div[@id="revH"]/div/div[contains(@class, "fl")]'
            )
            for div in table:
                rating = div.xpath(
                    'string(.//div[contains(@class, "histoRating")])'
                ).re(FLOATING_POINT_RGEX)[0]
                number = div.xpath(
                    'string(.//div[contains(@class, "histoCount")])'
                ).re(FLOATING_POINT_RGEX)[0]
                buyer_reviews['rating_by_star'][rating] = int(
                    number.replace(',', '')
                )
        return buyer_reviews, table

    def _search_page_error(self, response):
        body = response.body_as_unicode()
        return "Your search" in body \
            and "did not match any products." in body

    def parse_marketplace(self, response):
        response.meta["called_class"] = self
        response.meta["next_req"] = None
        return self.mtp_class.parse_marketplace(response)

    def exit_point(self, product, next_req):
        if next_req:
            next_req.replace(meta={"product": product})
            return next_req
        return product

    def is_nothing_found(self, response):
        txt = response.xpath('//h1[@id="noResultsTitle"]/text()').extract()
        txt = ''.join(txt)
        return 'did not match any products' in txt

    def mkt_request(self, link, meta):
        return Request(
            url=link, 
            callback=self.parse_marketplace,
            meta=meta,
            dont_filter=True
        )