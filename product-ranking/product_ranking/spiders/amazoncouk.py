# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
import re
import json
import urlparse
from datetime import datetime

from scrapy.http import Request
from scrapy.http.request.form import FormRequest
from scrapy.log import msg, ERROR, WARNING, INFO, DEBUG
from scrapy.selector import Selector

from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    cond_set_value, FLOATING_POINT_RGEX, dump_url_to_file

from product_ranking.amazon_bestsellers import amazon_parse_department
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.marketplace import Amazon_marketplace
from product_ranking.amazon_tests import AmazonTests
from spiders_shared_code.amazon_variants import AmazonVariants

from product_ranking.amazon_base_class import AmazonBaseClass

# scrapy crawl amazoncouk_products -a searchterms_str="iPhone"

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


    class FakeCaptchaBreaker(object):
        @staticmethod
        def solve_captcha(url):
            msg("No CaptchaBreaker to solve: %s" % url, level=WARNING)
            return None
    CaptchaBreakerWrapper = FakeCaptchaBreaker


class AmazoncoukValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
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
        'nothing_fou': [5, 50],
        'kaspersky total': [5, 70],
        'gold sold fold': [5, 200],  # spider should return from 5 to 200 products
        'yamaha drums midi': [5, 100],
        'black men shoes size 8 red stripes': [5, 80],
        'antoshka': [5, 200],
        'apple ipod nano sold': [100, 300],
        'avira 2': [20, 300],
    }


class AmazonCoUkProductsSpider(AmazonTests, AmazonBaseClass):
    name = "amazoncouk_products"
    allowed_domains = ["www.amazon.co.uk"]
    start_urls = []

    # String from html body that means there's no results
    total_match_not_found = 'did not match any products.'
    # Regexp for total matches to parse a number from html body
    total_matches_re = r'of\s?([\d,.\s?]+)'

    # Locale
    locale = 'en-US'

    # Price currency
    price_currency = 'GBP'
    price_currency_view = '£'
    
    SEARCH_URL = ("http://www.amazon.co.uk/s/ref=nb_sb_noss?"
                  "url=search-alias=aps&field-keywords={search_term}&rh=i:aps,"
                  "k:{search_term}&ajr=0")

    REVIEW_DATE_URL = 'http://www.amazon.co.uk/product-reviews/{product_id}' \
                      '/ref=cm_cr_dp_see_all_btm?ie=UTF8&' \
                      'showViewpoints=1&sortBy=bySubmissionDateDescending'

    _cbw = CaptchaBreakerWrapper()

    settings = AmazoncoukValidatorSettings

    use_proxies = True

    handle_httpstatus_list = [502, 503, 504]

    def __init__(self, captcha_retries='20', *args, **kwargs):
        # locations = settings.get('AMAZONFRESH_LOCATION')
        # loc = locations.get(location, '')
        super(AmazonCoUkProductsSpider, self).__init__(*args, **kwargs)

        self.captcha_retries = int(captcha_retries)

        self.mtp_class = Amazon_marketplace(self)

    def parse_product(self, response):

        if self._has_captcha(response):
            return self._handle_captcha(
                response,
                self.parse_product
            )

        super(AmazonCoUkProductsSpider, self).parse_product(response)
        prod = response.meta['product']

        ### Populate variants with CH/SC class
        av = AmazonVariants()
        av.setupSC(response)
        prod['variants'] = av._variants()

        title = response.xpath(
            '//span[@id="productTitle"]/text()[normalize-space()] |'
            '//div[@class="buying"]/h1/span[@id="btAsinTitle"]'
            '/text()[normalize-space()] |'
            '//div[@id="title_feature_div"]/h1/text()[normalize-space()] |'
            '//div[@id="title_row"]/span/h1/text()[normalize-space()] |'
            '//h1[@id="aiv-content-title"]/text()[normalize-space()] |'
            '//div[@id="item_name"]/text()[normalize-space()] |'
            '//h1[@class="parseasinTitle"]/span[@id="btAsinTitle"]'
            '/span/text()[normalize-space()]'
        ).extract()
        cond_set(prod, 'title', title)

        brand = response.xpath('//a[@id="brand"]/text()').extract()
        cond_set(prod, 'brand', brand)

        if not prod.get('brand', None):
            dump_url_to_file(response.url)

        self.mtp_class.get_price_from_main_response(response, prod)

        prod['url'] = response.url

        mkt_place_link = urlparse.urljoin(
                response.url,
                is_empty(response.xpath(
                    "//a[contains(@href, '/gp/offer-listing/')]/@href |" \
                    "//div[contains(@class, 'a-box-inner')]" \
                    "//div[@id='secondaryUsedAndNew']" \
                    "//a[contains(@href, '/gp/offer-listing/')]/@href"
                ).extract()))

        new_meta = response.meta.copy()
        new_meta['product'] = prod
        prod_id = is_empty(re.findall('/dp/([a-zA-Z0-9]+)', response.url))
        new_meta['product_id'] = prod_id

        if mkt_place_link and "condition=" in mkt_place_link:
            mkt_place_link = re.sub("condition=([^\&]*)", "", mkt_place_link)
            new_meta['mkt_place_link'] = mkt_place_link

        revs = self._buyer_reviews_from_html(response)
        if isinstance(revs, Request):
            if mkt_place_link:
                new_meta["mkt_place_link"] = mkt_place_link
            return revs.replace(meta=new_meta)
        else:
            prod['buyer_reviews'] = revs

        if prod['buyer_reviews'] != 0:
            return Request(url=self.REVIEW_DATE_URL.format(product_id=prod_id),
                           meta=new_meta,
                           dont_filter=True,
                           callback=self._parse_last_buyer_review_date)

        return prod

    def _search_page_error(self, response):
        sel = Selector(response)

        try:
            found1 = sel.xpath('//div[@class="warning"]/p/text()').extract()[0]
            found2 = sel.xpath(
                '//div[@class="warning"]/p/strong/text()'
            ).extract()[0]
            found = found1 + " " + found2
            if 'did not match any products' in found:
                self.log(found, ERROR)
                return True
            return False
        except IndexError:
            return False

    def get_buyer_reviews_from_2nd_page(self, response):

        if self._has_captcha(response):
            result = self._handle_captcha(response,
                                          self.get_buyer_reviews_from_2nd_page)
            print('handle captcha')
        else:
            product = response.meta["product"]
            buyer_reviews = {}
            product["buyer_reviews"] = {}
            prod_id = response.meta["product_id"]
            total_revs = is_empty(response.xpath(
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

    def get_rating_by_star(self, response, buyer_reviews):
        table = response.xpath(
                '//table[@id="productSummary"]//'
                'table[@cellspacing="1"]//tr'
            )
        total = 0
        print(response)
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
        else:
            stars = response.xpath(
                '//div[@class="histoRating"]/text()'
            ).re('(\d)+ star')

            rating = response.xpath(
                '//div[@class="histoCount"]/text()'
            ).extract()

            rating_by_star = {}
            for i in range(0, len(stars)):
                rating_by_star[stars[i]] = int(rating[i])
                total += int(stars[i]) * int(rating[i])
            if len(rating_by_star) > 0:
                buyer_reviews['rating_by_star'] = rating_by_star

        if total > 0:
            average = float(total)/float(buyer_reviews['num_of_reviews'])
            buyer_reviews['average_rating'] = round(average, 1)
        return buyer_reviews

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
            stars = re.search(stars_regexp, title[0])
            if stars:
                stars = int(re.sub('[ ,]+', '', stars.group(1)))
                ratings[stars] = int(text[0].replace(",", ""))
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
        if int(total) == 0:
            buyer_reviews = ZERO_REVIEWS_VALUE
        else:
            buyer_reviews = BuyerReviews(num_of_reviews=total,
                                         average_rating=average,
                                         rating_by_star=ratings)
        if not ratings:
            buyer_rev_link = response.xpath(
                '//div[@id="revSum"]//a[contains(text(), "See all")' \
                ' or contains(text(), "See the customer review")' \
                ' or contains(text(), "See both customer reviews")]/@href'
            ).extract()
            if buyer_rev_link:
                buyer_rev_req = Request(
                    url=buyer_rev_link[0],
                    callback=self.get_buyer_reviews_from_2nd_page,
                    meta=response.meta.copy()
                )
                buyer_reviews = buyer_rev_req

        return buyer_reviews
        # cond_set_value(product, 'buyer_reviews', buyer_reviews)

    def _parse_last_buyer_review_date(self, response):
        product = response.meta['product']
        date = is_empty(response.xpath(
            '//table[@id="productReviews"]/tr/td/div/div/span/nobr/text()'
        ).extract())
        # TODO: fix the code below (fails on dates like '11 Sept 2014') - test on many URLs!
        """
        if date:
            try:
                d = datetime.strptime(date.replace('.', ''), '%d %b %Y')
            except Exception as e:
                d = datetime.strptime(date.replace('.', ''), '%d %B %Y')
            date = d.strftime('%d/%m/%Y')
            product['last_buyer_review_date'] = date
        """
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

    def parse_marketplace(self, response):
        response.meta["called_class"] = self
        response.meta["next_req"] = None
        return self.mtp_class.parse_marketplace(response)

    def exit_point(self, product, next_req):
        if next_req:
            next_req.replace(meta={"product": product})
            return next_req
        return product

    def parse_502(self, response):
        parts = urlparse.urlparse(response.url)
        if parts.port and parts.port != 80:
            self.log('Got status %s - retrying without port' % response.status)
            return Request(response.url.replace(':'+str(parts.port)+'/', '/'))

    def parse_503(self, response):
        return self.parse_502(response)

    def parse_504(self, response):
        return self.parse_502(response)
