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
from product_ranking.guess_brand import guess_brand_from_first_words
from product_ranking.amazon_tests import AmazonTests

from product_ranking.amazon_bestsellers import amazon_parse_department
from product_ranking.settings import ZERO_REVIEWS_VALUE

try:
    from spiders_shared_code.amazon_variants import AmazonVariants
except ImportError:
    from amazon_variants import AmazonVariants

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

class AmazonProductsSpider(AmazonTests, BaseProductsSpider):
    name = 'amazoncn_products'
    allowed_domains = ["amazon.cn"]

    settings = AmazoncnValidatorSettings()

    SEARCH_URL = "http://www.amazon.cn/s/?field-keywords={search_term}"
    #SEARCH_URL = "http://www.amazon.cn/s/ref=sr_st_{sort_mode}" \
    #             "?keywords={search_term}&rh=k:{search_term},i:{sort_category}"

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

    def __init__(self, sort_category=None,
                 order='default', captcha_retries='10', *args, **kwargs):
        if sort_category is None and order != 'default':
            self.log('Category must be set for sort ordering')
            sort_mode = ''
        else:
            sort_mode = self.SORT_MODES.get(order)
            if sort_mode is None:
                self.log('No such sort mode defined: %s' % sort_mode)
        url_formatter = FormatterWithDefaults(
            sort_mode=sort_mode or self.SORT_MODES['default'],
            sort_category=sort_category or '')

        super(AmazonProductsSpider, self).__init__(url_formatter, *args,
                                                   **kwargs)

        self.captcha_retries = int(captcha_retries)

        self._cbw = CaptchaBreakerWrapper()

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse(self, response):
        if self._has_captcha(response):
            result = self._handle_captcha(response, self.parse)
        else:
            result = super(AmazonProductsSpider, self).parse(response)
        return result

    def _get_products(self, response):
        result = super(AmazonProductsSpider, self)._get_products(response)
        for r in result:
            if isinstance(r, Request):
                r = r.replace(dont_filter=True)
                yield r
            else:
                yield r

    def parse_product(self, response):
        if self._has_captcha(response):
            result = self._handle_captcha(response, self.parse_product)
        prod = response.meta['product']

        if not self._has_captcha(response):
            self._populate_from_js(response, prod)

            self._populate_from_html(response, prod)

            cond_set_value(prod, 'locale', 'en-US')  # Default locale.

            mkt_place_link = urlparse.urljoin(
                response.url,
                is_empty(response.xpath(
                    "//div[contains(@class, 'a-box-inner')]" \
                    "//a[contains(@href, '/gp/offer-listing/')]/@href |" \
                    "//div[@id='secondaryUsedAndNew']" \
                    "//a[contains(@href, '/gp/offer-listing/')]/@href"
                ).extract()))

            if isinstance(prod['buyer_reviews'], Request):
                meta = prod['buyer_reviews'].meta
                meta["mkt_place_link"] = mkt_place_link
                result =  prod['buyer_reviews'].replace(meta=meta)
            else:
                result = prod

            prod_id = is_empty(re.findall('/dp/([a-zA-Z0-9]+)', response.url))
            meta = response.meta.copy()
            meta = {"product": prod, 'product_id': prod_id}
            if mkt_place_link:
                meta['mkt_place_link'] = mkt_place_link
            return Request(
                url=self.REVIEW_DATE_URL.format(product_id=prod_id),
                callback=self.parse_last_buyer_review_date,
                meta=meta,
                dont_filter=True,
            )

        elif response.meta.get('captch_solve_try', 0) >= self.captcha_retries:
            self.log("Giving up on trying to solve the captcha challenge after"
                     " %s tries for: %s" % (self.captcha_retries, prod['url']),
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
        if 'mkt_place_link' in response.meta.keys():
                return Request(
                    url=response.meta['mkt_place_link'],
                    callback=self.parse_marketplace,
                    meta=new_meta,
                    dont_filter=True,
                )
        return product

    def _populate_bestseller_rank(self, product, response):
        # ranks = {' > '.join(map(unicode.strip,
        #                         itm.css('.zg_hrsr_ladder a::text').extract())):
        #              int(re.sub('[ ,]', '',
        #                         itm.css('.zg_hrsr_rank::text').re(
        #                             '([\d, ]+)')[0]))
        #          for itm in response.css('.zg_hrsr_item')}
        # prim = response.css('#SalesRank::text, #SalesRank .value'
        #                     '::text').re('([\d ,]+) .*in (.+)\(')
        # if prim:
        #     prim = {prim[1].strip(): int(re.sub('[ ,]', '', prim[0]))}
        #     ranks.update(prim)
        # ranks = [{'category': k, 'rank': v} for k, v in ranks.iteritems()]
        # cond_set_value(product, 'category', ranks)
        # # parse department
        # department = amazon_parse_department(ranks)
        # if department is None:
        #     product['department'] = None
        # else:
        #     product['department'], product['bestseller_rank'] \
        #         = department.items()[0]
        s = response.xpath(
            '//li[@id="SalesRank"]/text()[normalize-space()]'
        ).extract()
        if s:
            rank = is_empty(re.findall('\d+', s[0]))
            category = is_empty(s[0].split(rank)).replace('\n', '').strip()
            product['category'] = {category: rank}

        department = is_empty(response.xpath(
            '//div[@class="content"]/ul/li/a/text()').extract())

        if department:
            product['department'] = department.strip()

    def _populate_from_html(self, response, product):
        av = AmazonVariants()
        av.setupSC(response)
        product['variants'] = av._variants()

        cond_set(product, 'brand', response.css('#brand ::text').extract())
        price = response.css('#priceblock_ourprice ::text '
                         ', .price3P::text'
                         ', .priceLarge::text').extract()
        if not price:
            price = response.xpath(
                '//span[@id="priceblock_saleprice"]/text() |'
                '//div[@class="a-box-inner"]'
                '//span[@class="a-color-price"]/text() |'
                '//td/b[@class="priceLarge"]/text() |'
                '//div[contains(@data-reftag,"atv_dp_bb_est_hd_movie")]'
                '/button/text() |'
                '//li[@class="swatchElement selected"]'
                '//span[@class="a-color-price"]/text() |'
                '//span[@id="ags_price_local"]/text()'
            ).extract()

        cond_set(
            product,
            'price',
            price,
        )
        if product.get('price', None):
            if u'\uffe5' not in product.get('price', ''):
                self.log('Invalid price at: %s' % response.url, level=ERROR)
            else:
                price = re.findall(FLOATING_POINT_RGEX, product['price'])[0]
                product['price'] = Price(
                    price=price.replace(' ', '').replace(',', '').strip(),
                    priceCurrency='CNY'
                )

        description = response.css('.productDescriptionWrapper').extract()
        if not description:
            description = response.xpath(
                '//div[@id="bookDescription_feature_div"]/noscript |'
                '//div[@class="bucket"]/div[@class="content"] |'
                '//div[@id="featurebullets_feature_div"]'
            ).extract()

        cond_set(
            product,
            'description',
            description,
        )

        image_url = response.css(
                '#imgTagWrapperId > img ::attr(data-old-hires)').extract()
        if not image_url:
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
                    image_url = [image]
                except:
                    pass
        if not image_url:
            image_url = response.xpath(
                '//div[@id="img-canvas"]/img/@src |'
                '//div[@class="main-image-inner-wrapper"]/img/@src'
            ).extract()

        cond_set(
            product,
            'image_url',
            image_url
        )

        title = response.css('#productTitle ::text').extract()
        if not title:
            title = response.xpath(
                '//h1[@class="parseasinTitle"]'
                '/span[@id="btAsinTitle"]/span/text()'
            ).extract()
        cond_set(
            product, 'title', title)

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
                    cond_set(product, 'model', (model, ))
        if not product.get('brand') and product.get('title'):
            brand = guess_brand_from_first_words(product['title'])
            cond_set_value(product, 'brand', brand)
        cond_set(product, 'model', model, conv=string.strip)
        self._populate_bestseller_rank(product, response)
        revs = self._buyer_reviews_from_html(response)
        if isinstance(revs, Request):
            meta = {"product": product}
            product['buyer_reviews'] = revs.replace(meta=meta)
        else:
            product['buyer_reviews'] = revs


    def _populate_from_js(self, response, product):
        # Images are not always on the same spot...
        img_jsons = response.css(
            '#landingImage ::attr(data-a-dynamic-image)').extract()
        if img_jsons:
            img_data = json.loads(img_jsons[0])
            cond_set_value(
                product,
                'image_url',
                max(img_data.items(), key=lambda (_, size): size[0]),
                conv=lambda (url, _): url)

    def _scrape_total_matches(self, response):
        if len(response.css('h1#noResultsTitle')):
            total_matches = 0
        else:
            #count_matches = response.xpath(
            #    '//*[@id="resultCount"]/text()').re(u'共([\d, ]+)')
            count_matches = "".join(
                response.xpath("//h2[@id='s-result-count']/text()")
                .extract())
            count_matches = re.findall(r"[\d, ]+", count_matches)
            count_matches = [r for r in count_matches if len(r.strip()) > 0]
            if count_matches and count_matches[-1]:
                total_matches = int(
                    count_matches[-1].replace(',', '').strip())
            else:
                total_matches = None
        return total_matches

    def _scrape_product_links(self, response):
        lis = response.xpath("//ul/li[@class='s-result-item']")
        links = []
        for no, li in enumerate(lis):
            href = li.xpath(
                ".//a[contains(@class,'s-access-detail-page')]"
                "/@href").extract()
            if href:
                href = href[0]
                is_prime = li.xpath(
                    "*/descendant::i[contains(concat(' ',@class,' '),"
                    "' a-icon-prime ')]").extract()
                is_prime_pantry = li.xpath(
                    "*/descendant::i[contains(concat(' ',@class,' '),"
                    "' a-icon-prime-pantry ')]").extract()
                links.append((href, is_prime, is_prime_pantry))

        if not links:
            self.log("Found no product links.", WARNING)

        for link, is_prime, is_prime_pantry in links:
            prime = None
            if is_prime:
                prime = 'Prime'
            if is_prime_pantry:
                prime = 'PrimePantry'
            yield link, SiteProductItem(prime=prime)

    def _scrape_next_results_page_link(self, response):
        next_pages = response.css('#pagnNextLink ::attr(href)').extract()
        next_page_url = None
        if len(next_pages) == 1:
            next_page_url = next_pages[0]
        elif len(next_pages) > 1:
            self.log("Found more than one 'next page' link.", ERROR)
        return next_page_url

    # Captcha handling functions.

    def _has_captcha(self, response):
        return '.images-amazon.com/captcha/' in response.body_as_unicode()

    def _solve_captcha(self, response):
        forms = response.xpath('//form')
        assert len(forms) == 1, "More than one form found."

        captcha_img = forms[0].xpath(
            '//img[contains(@src, "/captcha/")]/@src').extract()[0]

        self.log("Extracted capcha url: %s" % captcha_img, level=DEBUG)
        return self._cbw.solve_captcha(captcha_img)

    def _handle_captcha(self, response, callback):
        # FIXME This is untested and wrong.
        captcha_solve_try = response.meta.get('captcha_solve_try', 0)
        url = response.url
        self.log("Captcha challenge for %s (try %d)."
                 % (url, captcha_solve_try),
                 level=INFO)

        captcha = self._solve_captcha(response)

        if captcha is None:
            self.log(
                "Failed to guess captcha for '%s' (try: %d)." % (
                    url, captcha_solve_try),
                level=ERROR
            )
            result = None
        else:
            self.log(
                "On try %d, submitting captcha '%s' for '%s'." % (
                    captcha_solve_try, captcha, url),
                level=INFO
            )
            meta = response.meta.copy()
            meta['captcha_solve_try'] = captcha_solve_try + 1
            result = FormRequest.from_response(
                response,
                formname='',
                formdata={'field-keywords': captcha},
                callback=callback,
                dont_filter=True,
                meta=meta)

        return result

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
                "price": Price(price=price, priceCurrency="CNY"),
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
                meta=meta
            )

        product["marketplace"] = marketplaces

        return product
