# ~~coding=utf-8~~
from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
import re
import urlparse
from urllib import unquote
import json
import string
import random

from scrapy.http import Request
from scrapy.http.request.form import FormRequest
from scrapy.log import msg, ERROR, WARNING, INFO, DEBUG
import lxml.html
import requests

from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, \
    cond_set_value, FLOATING_POINT_RGEX, FormatterWithDefaults
from product_ranking.guess_brand import guess_brand_from_first_words
from product_ranking.marketplace import Amazon_marketplace
from spiders_shared_code.amazon_variants import AmazonVariants
from product_ranking.amazon_bestsellers import amazon_parse_department
from product_ranking.settings import ZERO_REVIEWS_VALUE
from scrapy.conf import settings

is_empty = lambda x, y="": x[0] if x else y

try:
    from captcha_solver import CaptchaBreakerWrapper
except ImportError as e:
    import sys

    print(
        "### Failed to import CaptchaBreaker.",
        "Will continue without solving captchas:",
        e,
        file=sys.stderr
    )


    class FakeCaptchaBreaker(object):
        @staticmethod
        def solve_captcha(url):
            msg("No CaptchaBreaker to solve: %s" % url, level=WARNING)
            return None


    CaptchaBreakerWrapper = FakeCaptchaBreaker


class AmazonBaseClass(BaseProductsSpider):
    buyer_reviews_stars = ['one_star', 'two_star', 'three_star', 'four_star',
                           'five_star']

    SEARCH_URL = 'https://{domain}/s/ref=nb_sb_noss_1?url=search-alias' \
                 '%3Daps&field-keywords={search_term}'

    REVIEW_DATE_URL = 'https://{domain}/product-reviews/{product_id}/' \
                      'ref=cm_cr_pr_top_recent?ie=UTF8&showViewpoints=0&' \
                      'sortBy=bySubmissionDateDescending&reviewerType=all_reviews'
    REVIEW_URL_1 = 'https://{domain}/ss/customer-reviews/ajax/reviews/get/' \
                   'ref=cm_cr_pr_viewopt_sr'
    REVIEW_URL_2 = 'https://{domain}/product-reviews/{product_id}/' \
                   'ref=acr_dpx_see_all?ie=UTF8&showViewpoints=1'

    handle_httpstatus_list = [404]


    AMAZON_PRIME_URL = 'https://www.amazon.com/gp/product/du' \
                       '/bbop-ms3-ajax-endpoint.html?ASIN={0}&merchantID={1}' \
                       '&bbopruleID=Acquisition_AddToCart_PrimeBasicFreeTrial' \
                       'UpsellEligible&sbbopruleID=Acquisition_AddToCart_' \
                       'PrimeBasicFreeTrialUpsellEligible&deliveryOptions=' \
                       '%5Bsame-us%2Cnext%2Csecond%2Cstd-n-us%2Csss-us%5D' \
                       '&preorder=false&releaseDateDeliveryEligible=false'

    MKTP_USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/601.4.4 (KHTML, like Gecko) Version/9.0.3 Safari/601.4.4',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
    ]

    def __init__(self, captcha_retries='10', *args, **kwargs):
        middlewares = settings.get('DOWNLOADER_MIDDLEWARES')
        middlewares['product_ranking.custom_middlewares.AmazonProxyMiddleware'] = 750
        middlewares['product_ranking.randomproxy.RandomProxy'] = None
        settings.overrides['DOWNLOADER_MIDDLEWARES'] = middlewares
        settings.overrides['RETRY_HTTP_CODES'] = [500, 502, 504, 400, 403, 404, 408]
        # this turns off crawlera per-request
        # settings.overrides['CRAWLERA_ENABLED'] = True
        super(AmazonBaseClass, self).__init__(
            site_name=self.allowed_domains[0],
            url_formatter=FormatterWithDefaults(
                domain=self.allowed_domains[0]
            ),
            *args, **kwargs)
        self.mtp_class = Amazon_marketplace(self)
        self.captcha_retries = int(captcha_retries)
        self._cbw = CaptchaBreakerWrapper()
        self.ignore_variant_data = kwargs.get('ignore_variant_data', None)
        if self.ignore_variant_data in ('1', True, 'true', 'True'):
            self.ignore_variant_data = True
        else:
            self.ignore_variant_data = False
        # Turned on by default
        self.ignore_color_variants = kwargs.get('ignore_color_variants', True)
        if self.ignore_color_variants in ('0', False, 'false', 'False'):
            self.ignore_color_variants = False
        else:
            self.ignore_color_variants = True

    def _is_empty(self, x, y=None):
        return x[0] if x else y

    def _get_int_from_string(self, num):
        if num:
            num = re.findall(
                r'(\d+)',
                num
            )

            try:
                num = int(''.join(num))
                return num
            except ValueError as exc:
                self.log("Error to parse string value to int: {exc}".format(
                    exc=exc
                ), ERROR)

        return 0

    def _get_float_from_string(self, num):
        if num:
            num = self._is_empty(
                re.findall(
                    FLOATING_POINT_RGEX,
                    num
                ), 0.00
            )
            try:
                num = float(num.replace(',', '.'))
            except ValueError as exc:
                self.log("Error to parse string value to int: {exc}".format(
                    exc=exc
                ), ERROR)

        return num

    def _scrape_total_matches(self, response):
        """
        Overrides BaseProductsSpider method to scrape total result matches. total_matches_str
        and total_matches_re need to be set for every concrete amazon spider.
        :param response:
        :return: Number of total matches (int)
        """
        total_match_not_found_re = getattr(self, 'total_match_not_found_re', None)
        total_matches_re = getattr(self, 'total_matches_re', None)

        if not total_match_not_found_re and not total_matches_re:
            self.log('Either total_match_not_found_re or total_matches_re '
                     'is not defined. Or both.', ERROR)
            return None

        if unicode(total_match_not_found_re) in response.body_as_unicode():
            return 0

        count_matches = self._is_empty(
            response.xpath(
                '//h2[@id="s-result-count"]/text()'
            ).re(unicode(self.total_matches_re))
        )

        total_matches = self._get_int_from_string(count_matches)

        return total_matches

    def _scrape_results_per_page(self, response):
        num = response.xpath(
            '//*[@id="s-result-count"]/text()').re('1-(\d+) of')

        if num:
            return int(num[0])
        else:
            num = response.xpath(
                '//*[@id="s-result-count"]/text()').re('(\d+) results')
            if num:
                return int(num[0])

        return None

    def _scrape_next_results_page_link(self, response):
        """
        Overrides BaseProductsSpider method to get link on next page of products.
        """
        next_pages = response.xpath('//*[@id="pagnNextLink"]/@href |'
                                    '//ul[contains(@class, "a-pagination")]'
                                    '/a[contains(text(), "eiter")]/@href').extract()
        next_page_url = None

        if len(next_pages) == 1:
            next_page_url = next_pages[0]
        elif len(next_pages) > 1:
            self.log("Found more than one 'next page' link.", ERROR)

        return next_page_url

    def _scrape_product_links(self, response):
        """
        Overrides BaseProductsSpider method to scrape product links.
        """
        lis = response.xpath(
            "//div[@id='resultsCol']/./ul/li |"
            "//div[@id='mainResults']/.//ul/li [contains(@id, 'result')] |"
            "//div[@id='atfResults']/.//ul/li[contains(@id, 'result')] |"
            "//div[@id='mainResults']/.//div[contains(@id, 'result')] |"
            "//div[@id='btfResults']//ul/li[contains(@id, 'result')]")
        links = []
        last_idx = -1

        for li in lis:
            is_prime = li.xpath(
                "*/descendant::i[contains(concat(' ', @class, ' '),"
                "' a-icon-prime ')] |"
                ".//span[contains(@class, 'sprPrime')]"
            )
            is_prime_pantry = li.xpath(
                "*/descendant::i[contains(concat(' ',@class,' '),'"
                "a-icon-prime-pantry ')]"
            )
            data_asin = self._is_empty(
                li.xpath('@id').extract()
            )

            is_sponsored = bool(li.xpath('.//h5[contains(text(), "ponsored")]').extract())

            try:
                idx = int(self._is_empty(
                    re.findall(r'\d+', data_asin)
                ))
            except ValueError:
                continue

            if idx > last_idx:
                link = self._is_empty(
                    li.xpath(
                        ".//a[contains(@class,'s-access-detail-page')]/@href |"
                        ".//h3[@class='newaps']/a/@href"
                    ).extract()
                )
                if not link:
                    continue

                if 'slredirect' in link:
                    link = 'http://' + self.allowed_domains[0] + '/' + link

                links.append((link, is_prime, is_prime_pantry, is_sponsored))
            else:
                break

            last_idx = idx

        if not links:
            self.log("Found no product links.", WARNING)

        if links:
            for link, is_prime, is_prime_pantry, is_sponsored in links:
                prime = None
                if is_prime:
                    prime = 'Prime'
                if is_prime_pantry:
                    prime = 'PrimePantry'
                prod = SiteProductItem(prime=prime, is_sponsored_product=is_sponsored)
                yield Request(link, callback=self.parse_product,
                              headers={'Referer': None},
                              meta={'product': prod}), prod

    def _parse_single_product(self, response):
        """
        Method from BaseProductsSpider. Enables single url mode.
        """
        return self.parse_product(response)

    def _get_products(self, response):
        """
        Method from BaseProductsSpider.
        """
        result = super(AmazonBaseClass, self)._get_products(response)

        for r in result:
            if isinstance(r, Request):
                r = r.replace(dont_filter=True)
            yield r

    def parse(self, response):
        """
        Main parsing method from BaseProductsSpider.
        """
        if self._has_captcha(response):
            result = self._handle_captcha(response, self.parse)
        else:
            result = super(AmazonBaseClass, self).parse(response)

        return result

    def parse_product(self, response):
        meta = response.meta.copy()
        product = meta['product']
        reqs = []

        if response.status == 404:
            product['response_code'] = 404
            product['not_found'] = True
            return product

        if 'the Web address you entered is not a functioning page on our site' \
                in response.body_as_unicode().lower():
            product['not_found'] = True
            return product

        if self._has_captcha(response):
            return self._handle_captcha(
                response,
                self.parse_product
            )
        elif response.meta.get('captch_solve_try', 0) >= self.captcha_retries:
            product = response.meta['product']
            self.log("Giving up on trying to solve the captcha challenge after"
                     " %s tries for: %s" % (self.captcha_retries, product['url']),
                     level=WARNING)
            return None

        # Set product ID
        product_id = self._parse_product_id(response.url)
        cond_set_value(response.meta, 'product_id', product_id)

        # Set locale
        if getattr(self, 'locale', None):
            product['locale'] = self.locale
        else:
            self.log('Variable for locale is not defined.', ERROR)

        # Parse title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title)

        # Parse image url
        image_url = self._parse_image_url(response)
        cond_set_value(product, 'image_url', image_url, conv=string.strip)

        # Parse brand
        brand = self._parse_brand(response)
        cond_set_value(product, 'brand', brand)

        # Parse price Subscribe & Save
        price_subscribe_save = self._parse_price_subscribe_save(response)
        cond_set_value(product, 'price_subscribe_save', price_subscribe_save, conv=string.strip)

        # Parse model
        model = self._parse_model(response)
        cond_set_value(product, 'model', model, conv=string.strip)

        # Parse price
        price = self._parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse original price
        price_original = self._parse_price_original(response)
        cond_set_value(product, 'price_original', price_original)

        # Parse description
        description = self._parse_description(response)
        cond_set_value(product, 'description', description)

        # Parse upc
        upc = self._parse_upc(response)
        cond_set_value(product, 'upc', upc)

        # No longer available
        no_longer_avail = self._parse_no_longer_available(response)
        cond_set_value(product, 'no_longer_available', no_longer_avail)
        if product.get('no_longer_available', None):
            product['is_out_of_stock'] = True

        # Prime & PrimePantry
        if not product.get('prime', None) and self._parse_prime_pantry(response):
            product['prime'] = self._parse_prime_pantry(response)

        if not product.get('prime', None):
            data_body = response.xpath('//script[contains(text(), '
                                       '"merchantID")]/text()').extract()
            if data_body:
                asin = is_empty(re.findall(r'"ASIN" : "(\w+)"', data_body[0]),
                                None)
                merchantID = is_empty(re.findall(r'"merchantID" : "(\w+)"',
                                                 data_body[0]), None)

                if asin and merchantID:
                    reqs.append(
                        Request(url=self.AMAZON_PRIME_URL.format(asin, merchantID),
                                meta=meta, callback=self._amazon_prime_check)
                    )

        # Parse ASIN
        asin = response.xpath(
            './/*[contains(text(), "ASIN")]/following-sibling::td/text()|.//*[contains(text(), "ASIN")]'
            '/following-sibling::text()[1]').extract()
        asin = [a.strip() for a in asin if a.strip()]
        asin = asin[0] if asin else None
        cond_set_value(product, 'asin', asin)
        # See bugzilla #11492
        cond_set_value(product, 'reseller_id', asin)

        # Parse variants
        if not self.ignore_variant_data:
            variants = self._parse_variants(response)
            product['variants'] = variants
            # Nothing to parse here, move along
            if variants:
                if self.ignore_color_variants:
                    # Get default selected color and get prices only for default color
                    # Getting all variants prices raise performance concerns because of huge amount of added requests
                    # See bz #11443
                    try:
                        default_color = [c['properties'].get('color') for c in variants if c.get('selected')]
                        default_color = default_color[0] if default_color else None
                        prc_variants = [v for v in variants if v['properties'].get('color') == default_color]
                    except Exception as e:
                        self.log('Error ignoring color variants, getting price for all variants: {}'.format(e), WARNING)
                        prc_variants = variants
                else:
                    prc_variants = variants
                # Parse variants prices
                # Turn on only for amazon.com for now
                if prc_variants and 'amazon.com/' in response.url:
                    js_text = response.xpath('.//script[contains(text(),"immutableURLPrefix")]/text()').extract()
                    js_text = js_text[0] if js_text else None
                    if not js_text:
                        self.log('js block not found for url'.format(response.url), WARNING)
                    else:
                        url_regex = """immutableURLPrefix['"]:['"](.+?)['"]"""
                        base_url = re.findall(url_regex, js_text)
                        # print base_url
                        base_url = base_url[0] if base_url else None
                        for variant in prc_variants:
                            # Set default price value
                            variant['price'] = None
                            # print(variant)
                            child_asin = variant.get('asin')
                            if child_asin:
                                # Build child variants urls based on parent url
                                child_url = base_url + "&psc=1&asinList={}&isFlushing=2&dpEnvironment=softlines&id={}&mType=full".format(
                                    child_asin, child_asin)
                                req_url = urlparse.urljoin(response.url, child_url)
                                if req_url:
                                    req = Request(req_url, meta=meta, callback=self._parse_variants_price)
                                    reqs.append(req)


        # Parse buyer reviews
        buyer_reviews = self._parse_buyer_reviews(response)
        if isinstance(buyer_reviews, Request):
            reqs.append(
                buyer_reviews.replace(dont_filter=True)
            )
        else:
            product['buyer_reviews'] = buyer_reviews
        reqs.append(
            Request(
                url=self.REVIEW_DATE_URL.format(
                    product_id=product_id,
                    domain=self.allowed_domains[0]
                ),
                callback=self._parse_last_buyer_review_date,
                meta=meta,
                dont_filter=True,
            )
        )

        # Parse marketplaces
        _prod = self._parse_marketplace_from_top_block(response)
        if _prod:
            product = _prod

        _prod, req = self._parse_marketplace_from_static_right_block(response)
        if _prod:
            product = _prod

        # There are more sellers to extract
        if req:
            reqs.append(req)

        # TODO: fix the block below - it removes previously scraped marketplaces
        # marketplace_req = self._parse_marketplace(response)
        # if marketplace_req:
        #    reqs.append(marketplace_req)

        # Parse category
        categories_full_info = self._parse_category(response)
        # cond_set_value(product, 'category', category)
        cond_set_value(product, 'categories_full_info', categories_full_info)
        # Left old simple format just in case
        categories = [c.get('name') for c in categories_full_info] if categories_full_info else None
        cond_set_value(product, 'categories', categories)

        # build_categories(product)
        category_rank = self._parse_category_rank(response)
        if category_rank:
            # Parse departments and bestseller rank
            department = amazon_parse_department(category_rank)

            if department is None:
                product['department'] = None
            else:
                department, bestseller_rank = department.items()[0]

                cond_set_value(product, 'department', department)
                cond_set_value(product, 'bestseller_rank', bestseller_rank)

        _avail = response.css('#availability ::text').extract()
        _avail = ''.join(_avail)
        _avail_lower = _avail.lower().replace(' ', '')
        # Check if any of the keywords for oos is in the _avail text
        if any(map((lambda x: x in _avail_lower), ['nichtauflager', 'currentlyunavailable'])):
            product['is_out_of_stock'] = True

        req = self._parse_questions(response)
        if req:
            reqs.append(req)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_variants_price(self, response):
        meta = response.meta
        reqs = meta.get('reqs')
        product = meta['product']
        child_asin = re.findall(r'asinList=(.+?)&', response.url)
        child_asin = child_asin[0] if child_asin else None
        price_regex = """price_feature_div.+?priceblock_ourprice[^_].+?">\$([\d\.]+)"""
        price = re.findall(price_regex, response.body)
        # Trying alternative regex
        if not price:
            price_regex = """buybox_feature_div.+?a-color-price['"]>\s?.+?([\d\.]+)"""
            price = re.findall(price_regex, response.body)
        if not price:
            fail_var_url = [v.get('url') for v in product["variants"] if v.get('asin')==child_asin]
            self.log('Unable to find price for variant: {} ASIN {} url {}'.format(
                response.url, child_asin, fail_var_url), WARNING)
        else:
            try:
                price = float(price[0]) if price else None
                for variant in product["variants"]:
                    var_asin = variant.get('asin')
                    # print(var_asin, child_asin)
                    if var_asin and var_asin == child_asin:
                        variant['price'] = price
                        break
            except BaseException as e:
                self.log('Unable to convert price for variant: {}, {}'.format(response.url, e), WARNING)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    @staticmethod
    def _parse_product_id(url):
        prod_id = re.findall(r'/dp?/(\w+)|product/(\w+)/', url)
        if not prod_id:
            prod_id = re.findall(r'/dp?/(\w+)|product/(\w+)', url)
        if not prod_id:
            prod_id = re.findall(r'([A-Z0-9]{4,20})', url)
        if isinstance(prod_id, (list, tuple)):
            prod_id = [s for s in prod_id if s][0]
        if isinstance(prod_id, (list, tuple)):
            prod_id = [s for s in prod_id if s][0]
        return prod_id

    def _parse_questions(self, response):
        None

    def _parse_category(self, response):
        cat = response.xpath(
            '//span[@class="a-list-item"]/'
            'a[@class="a-link-normal a-color-tertiary"]')
        if not cat:
            cat = response.xpath('//li[@class="breadcrumb"]/a[@class="breadcrumb-link"]')
        if not cat:
            cat = response.xpath('.//*[@id="nav-subnav"]/a[@class="nav-a nav-b"]')

        categories_full_info = []
        for cat_sel in cat:
            c_url = cat_sel.xpath("./@href").extract()
            c_url = urlparse.urljoin(response.url, c_url[0]) if c_url else None
            c_text = cat_sel.xpath(".//text()").extract()
            c_text = c_text[0].strip() if c_text else None
            categories_full_info.append({"url": c_url,
                                         "name": c_text})

        if categories_full_info:
            return categories_full_info

    def _parse_title(self, response, add_xpath=None):
        """
        Parses product title.
        :param response:
        :param add_xpath: Additional xpathes, so you don't need to change base class
        :return: Number of total matches (int)
        """
        xpathes = '//span[@id="productTitle"]/text()[normalize-space()] |' \
                  '//div[@class="buying"]/h1/span[@id="btAsinTitle"]/text()[normalize-space()] |' \
                  '//div[@id="title_feature_div"]/h1/text()[normalize-space()] |' \
                  '//div[@id="title_row"]/span/h1/text()[normalize-space()] |' \
                  '//h1[@id="aiv-content-title"]/text()[normalize-space()] |' \
                  '//div[@id="item_name"]/text()[normalize-space()] |' \
                  '//h1[@class="parseasinTitle"]/span[@id="btAsinTitle"]' \
                  '/span/text()[normalize-space()] |' \
                  '//*[@id="title"]/text()[normalize-space()] |' \
                  '//*[@id="product-title"]/text()[normalize-space()]'
        if add_xpath:
            xpathes += ' |' + add_xpath
            xpathes += ' |' + add_xpath

        title = self._is_empty(
            response.xpath(xpathes).extract(), ''
        ).strip()

        if not title:
            # Create title from parts
            parts = response.xpath(
                '//div[@id="mnbaProductTitleAndYear"]/span/text()'
            ).extract()
            if parts:
                title = ''
                for part in parts:
                    title += part
                title = [title]

        if not title:
            title = self._is_empty(response.css('#ebooksProductTitle ::text').extract(), '').strip()

        return title

    def _parse_image_url(self, response, add_xpath=None):
        """
        Parses product image.
        :param add_xpath: Additional xpathes, so you don't need to change base class
        """
        xpathes = '//div[@class="main-image-inner-wrapper"]/img/@src |' \
                  '//div[@id="coverArt_feature_div"]//img/@src |' \
                  '//div[@id="img-canvas"]/img/@src |' \
                  '//div[@class="dp-meta-icon-container"]/img/@src |' \
                  '//input[@id="mocaGlamorImageUrl"]/@value |' \
                  '//div[@class="egcProdImageContainer"]' \
                  '/img[@class="egcDesignPreviewBG"]/@src |' \
                  '//img[@id="main-image"]/@src |' \
                  '//*[@id="imgTagWrapperId"]/.//img/@data-old-hires |' \
                  '//img[@id="imgBlkFront"]/@src |' \
                  '//img[@class="masrw-main-image"]/@src'
        if add_xpath:
            xpathes += ' |' + add_xpath

        image = self._is_empty(
            response.xpath(xpathes).extract(), ''
        )

        if not image:
            # Another try to parse img_url: from html body as JS data
            img_re = self._is_empty(
                re.findall(
                    r"'colorImages':\s*\{\s*'initial':\s*(.*)\},|colorImages\s*=\s*\{\s*\"initial\":\s*(.*)\}",
                    response.body), ''
            )

            img_re = self._is_empty(list(img_re))

            if img_re:
                try:
                    res = json.loads(img_re)
                    image = res[0]['large']
                except Exception as exc:
                    self.log('Unable to parse image url from JS on {url}: {exc}'.format(
                        url=response.url, exc=exc), WARNING)

        if not image:
            # Images are not always on the same spot...
            img_jsons = response.xpath(
                '//*[@id="landingImage"]/@data-a-dynamic-image'
            ).extract()

            if img_jsons:
                img_data = json.loads(img_jsons[0])
                image = max(img_data.items(), key=lambda (_, size): size[0])

        if not image:
            image = response.xpath('//*[contains(@id, "ebooks-img-canvas")]//@src').extract()
            if image:
                image = image[0]
            else:
                image = None

        if image and 'base64' in image:
            img_jsons = response.xpath(
                '//*[@id="imgBlkFront"]/@data-a-dynamic-image | '
                '//*[@id="landingImage"]/@data-a-dynamic-image'
            ).extract()

            if img_jsons:
                img_data = json.loads(img_jsons[0])

                image = max(img_data.items(), key=lambda (_, size): size[0])[0]

        return image

    def _parse_no_longer_available(self, response):
        if response.xpath('//*[contains(@id, "availability")]'
                          '//*[contains(text(), "navailable")]'):  # Unavailable or unavailable
            return True
        if response.xpath('//*[contains(@id, "outOfStock")]'
                          '//*[contains(text(), "navailable")]'):  # Unavailable or unavailable
            return True

    def _parse_brand(self, response, add_xpath=None):
        """
        Parses product brand.
        :param add_xpath: Additional xpathes, so you don't need to change base class
        """
        xpathes = '//*[@id="brand"]/text() |' \
                  '//*[contains(@class, "contributorNameID")]/text() |' \
                  '//*[contains(@id, "contributorName")]/text() |' \
                  '//*[@id="bylineContributor"]/text() |' \
                  '//*[@id="contributorLink"]/text() |' \
                  '//*[@id="by-line"]/.//a/text() |' \
                  '//*[@id="artist-container"]/.//a/text() |' \
                  '//div[@class="buying"]/.//a[contains(@href, "search-type=ss")]/text() |' \
                  '//a[@id="ProductInfoArtistLink"]/text() |' \
                  '//a[contains(@href, "field-author")]/text()'
        if add_xpath:
            xpathes += ' |' + add_xpath

        product = response.meta['product']
        title = product.get('title', '')

        brand = response.xpath(xpathes).extract()
        brand = self._is_empty([b for b in brand if b.strip()])

        if brand and (u'®' in brand):
            brand = brand.replace(u'®', '')

        if not brand:
            brand = self._is_empty(
                response.xpath('//a[@id="brand"]/@href').re("\/([A-Z].+?)\/b")
            )

        if not brand and title:
            try:
                brand = guess_brand_from_first_words(title)
            except:
                brand = guess_brand_from_first_words(title[0])
            if brand:
                brand = [brand]

        if isinstance(brand, list):
            brand = [br.strip() for br in brand if brand and 'search result' not in br.lower()]

        brand = brand or ['NO BRAND']

        while isinstance(brand, (list, tuple)):
            if brand:
                brand = brand[0]
            else:
                brand = None
                break

        # remove authors
        if response.xpath('//*[contains(@id, "byline")]//*[contains(@class, "author")]'):
            brand = None

        if isinstance(brand, (str, unicode)):
            brand = brand.strip()

        return brand

    def _parse_price_subscribe_save(self, response, add_xpath=None):
        """
        Parses product price subscribe and save.
        :param add_xpath: Additional xpathes, so you don't need to change base class
        """
        xpathes = '//*[contains(text(), "Subscribe & Save:")]/' \
                  '../..//*[@id="subscriptionPrice"]/text()'
        if add_xpath:
            xpathes += ' |' + add_xpath

        price_ss = self._is_empty(
            response.xpath(xpathes).extract(), None
        )
        if not price_ss:
            price_ss = response.xpath(
                '//*[contains(text(), "Subscribe & Save")]/'
                '../../span[contains(@class, "a-label")]/span[contains(@class, "-price")]/text()'
            ).extract()
            if price_ss:
                price_ss = price_ss[0]
        if not price_ss:
            price_ss = None
        if price_ss and price_ss.startswith('$'):
            price_ss = self._is_empty(
                re.findall(
                    FLOATING_POINT_RGEX,
                    price_ss
                )
            )
            try:
                price_ss = float(price_ss)
            except ValueError as exc:
                self.log(
                    "Unable to extract price Subscribe&Save on {url}: {exc}".format(
                        url=response.url, exc=exc
                    ), WARNING
                )

        if price_ss:
            price_ss = self._is_empty(
                re.findall(
                    FLOATING_POINT_RGEX,
                    price_ss
                )
            )

        return price_ss

    def _parse_marketplace(self, response):
        """
        Parses product marketplaces
        :param response:
        :return: Request to parse marketplace if url exists
        """
        meta = response.meta.copy()
        product = meta['product']

        self.mtp_class.get_price_from_main_response(response, product)

        mkt_place_link = urlparse.urljoin(
            response.url,
            self._is_empty(response.xpath(
                "//a[contains(@href, '/gp/offer-listing/')]/@href |"
                "//div[contains(@class, 'a-box-inner')]/span/a/@href |"
                "//*[@id='universal-marketplace-glance-features']/.//a/@href"
            ).extract())
        )

        if mkt_place_link:
            new_meta = response.meta.copy()
            new_meta['product'] = product
            new_meta["mkt_place_link"] = mkt_place_link
            return Request(
                url=mkt_place_link,
                callback=self._parse_mkt,
                meta=new_meta,
                dont_filter=True
            )

        return None

    def _parse_mkt(self, response):
        if self._has_captcha(response):
            return self._handle_captcha(
                response,
                self._parse_mkt
            )

        response.meta["called_class"] = self
        response.meta["next_req"] = None

        return self.mtp_class.parse_marketplace(response)

    def _parse_model(self, response, add_xpath=None):
        """
        Parses product model.
        :param add_xpath: Additional xpathes, so you don't need to change base class
        """
        xpathes = '//div[contains(@class, "content")]/ul/li/' \
                  'b[contains(text(), "Item model number")]/../text() |' \
                  '//table/tbody/tr/' \
                  'td[contains(@class, "label") and contains(text(), "ASIN")]/' \
                  '../td[contains(@class, "value")]/text() |' \
                  '//div[contains(@class, "content")]/ul/li/' \
                  'b[contains(text(), "ISBN-10")]/../text()'

        if add_xpath:
            xpathes += ' |' + add_xpath

        model = self._is_empty(
            response.xpath(xpathes).extract(), ''
        )

        if not model:
            model = self._is_empty(response.xpath('//div[contains(@class, "content")]/ul/li/'
                                                  'b[contains(text(), "ASIN")]/../text()').extract())

        if not model:
            spans = response.xpath('//span[@class="a-text-bold"]')
            for span in spans:
                text = self._is_empty(span.xpath('text()').extract())
                if text and 'Item model number:' in text:
                    possible_model = span.xpath('../span/text()').extract()
                    if len(possible_model) > 1:
                        model = possible_model[1]

        if not model:
            for li in response.css('td.bucket > .content > ul > li'):
                raw_keys = li.xpath('b/text()').extract()
                if not raw_keys:
                    # This is something else, ignore.
                    continue

                key = raw_keys[0].strip(' :').upper()
                if key == 'ASIN' and model is None or key == 'ITEM MODEL NUMBER':
                    model = li.xpath('text()').extract()

        return model

    def _parse_price(self, response, add_xpath=None):
        """
        Parses product price.
        :param add_xpath: Additional xpathes, so you don't need to change base class
        """
        xpathes = '//b[@class="priceLarge"]/text()[normalize-space()] |' \
                  '//div[contains(@data-reftag,"atv_dp_bb_est_hd_movie")]' \
                  '/button/text()[normalize-space()] |' \
                  '//span[@id="priceblock_saleprice"]/text()[normalize-space()] |' \
                  '//div[@id="mocaBBRegularPrice"]/div/text()[normalize-space()] |' \
                  '//*[@id="priceblock_ourprice"][contains(@class, "a-color-price")]' \
                  '/text()[normalize-space()] |' \
                  '//*[@id="priceBlock"]/.//span[@class="priceLarge"]' \
                  '/text()[normalize-space()] |' \
                  '//*[@id="actualPriceValue"]/*[@class="priceLarge"]' \
                  '/text()[normalize-space()] |' \
                  '//*[@id="actualPriceValue"]/text()[normalize-space()] |' \
                  '//*[@id="buyNewSection"]/.//*[contains(@class, "offer-price")]' \
                  '/text()[normalize-space()] |' \
                  '//div[contains(@class, "a-box")]/div[@class="a-row"]' \
                  '/text()[normalize-space()] |' \
                  '//span[@id="priceblock_dealprice"]/text()[normalize-space()] |' \
                  '//*[contains(@class, "price3P")]/text()[normalize-space()] |' \
                  '//span[@id="ags_price_local"]/text()[normalize-space()] |' \
                  '//div[@id="olpDivId"]/.//span[@class="price"]' \
                  '/text()[normalize-space()] |' \
                  '//div[@id="buybox"]/.//span[@class="a-color-price"]' \
                  '/text()[normalize-space()] |' \
                  '//div[@id="unqualifiedBuyBox"]/.//span[@class="a-color-price"]/text() |' \
                  '//div[@id="tmmSwatches"]/.//li[contains(@class,"selected")]/./' \
                  '/span[@class="a-color-price"] |' \
                  '//div[contains(@data-reftag,"atv_dp_bb_est_sd_movie")]/button/text() |' \
                  '//span[contains(@class, "header-price")]/text()'

        if add_xpath:
            xpathes += ' |' + add_xpath

        price_currency_view = getattr(self, 'price_currency_view', None)
        price_currency = getattr(self, 'price_currency', None)

        if not price_currency and not price_currency_view:
            self.log('Either price_currency or price_currency_view '
                     'is not defined. Or both.', ERROR)
            return None

        price_currency_view = unicode(self.price_currency_view)
        price = response.xpath(xpathes).extract()
        price = self._is_empty([p for p in price if p.strip()], '')

        if price:
            if price_currency_view not in price:
                price = '0.00'
                if 'FREE' not in price:
                    self.log('Currency symbol not recognized: %s' % response.url,
                             level=WARNING)
            else:
                price = self._is_empty(
                    re.findall(
                        FLOATING_POINT_RGEX,
                        price), '0.00'
                )
        else:
            price = '0.00'

        price = self._fix_dots_commas(price)

        # Price is parsed in different format:
        # 1,235.00 --> 1235.00
        # 2,99 --> 2.99
        price = (price[:-3] + price[-3:].replace(',', '.')).replace(',', '')
        price = round(float(price), 2)

        # try to scrape the price from another place
        if price == 0.0:
            price2 = re.search('\|([\d\.]+)\|baseItem"}', response.body)
            if price2:
                price2 = price2.group(1)
                try:
                    price2 = float(price2)
                    price = price2
                except:
                    pass

        if price == 0.0:
            _price = response.css('#alohaPricingWidget .a-color-price ::text').extract()
            if _price:
                _price = ''.join([c for c in _price[0].strip() if c.isdigit() or c == '.'])
                try:
                    price = float(_price)
                except:
                    pass

        if price == 0.0:
            # "add to cart first" price?
            _price = re.search(r'asin\-metadata.{3,100}?price.{3,100}?([\d\.]+)',
                               response.body_as_unicode())
            if _price:
                _price = _price.group(1)
                try:
                    _price = float(_price)
                    price = _price
                except ValueError:
                    pass

        return Price(price=price, priceCurrency=self.price_currency)

    def _parse_price_original(self, response, add_xpath=None):
        """
        Parses product's original price.
        :param add_xpath: Additional xpathes, so you don't need to change base class
        """
        xpathes = '//*[@id="price"]/.//*[contains(@class, "a-text-strike")]' \
                  '/text()'

        if add_xpath:
            xpathes += ' |' + add_xpath

        price_original = self._is_empty(
            response.xpath(xpathes).extract()
        )

        if price_original:
            price_original = self._is_empty(
                re.findall(
                    FLOATING_POINT_RGEX,
                    price_original
                ), 0.00
            )
            try:
                price_original = float(price_original)
            except ValueError:
                price_original = None

        return price_original

    def _parse_category_rank(self, response):
        """
        Parses product categories.
        """
        ranks = {
            ' > '.join(map(
                unicode.strip, itm.css('.zg_hrsr_ladder a::text').extract())
            ): int(re.sub('[ ,]', '', itm.css('.zg_hrsr_rank::text').re(
                '([\d, ]+)'
            )[0]))
            for itm in response.css('.zg_hrsr_item')
            }

        prim = response.css('#SalesRank::text, #SalesRank .value'
                            '::text').re('#?([\d ,]+) .*in (.+)\(')

        if prim:
            prim = {prim[1].strip(): int(re.sub('[ ,]', '', prim[0]))}
            ranks.update(prim)

        category_rank = [{'category': k, 'rank': v} for k, v in ranks.iteritems()]

        return category_rank

    def _parse_description(self, response, add_xpath=None):
        """
        Parses product description.
        :param add_xpath: Additional xpathes, so you don't need to change base class
        """
        xpathes = '//*[contains(@class, "productDescriptionWrapper")] |' \
                  '//div[@id="descriptionAndDetails"] |' \
                  '//div[@id="feature-bullets"] |' \
                  '//div[@id="ps-content"] |' \
                  '//div[@id="productDescription_feature_div"] |' \
                  '//div[contains(@class, "dv-simple-synopsis")] |' \
                  '//div[@class="bucket"]/div[@class="content"] |' \
                  '//div[@id="bookDescription_feature_div"]/noscript'

        if add_xpath:
            xpathes += ' |' + add_xpath

        description = self._is_empty(response.xpath(xpathes).extract())
        if not description:
            description = self._is_empty(
                response.css('#featurebullets_feature_div').extract())
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
                    description = desc

        if isinstance(description, (list, tuple)):
            description = description[0]
        return description.strip() if description else None

    def _parse_upc(self, response):
        """
        Parses product upc.
        """
        upc = None
        for li in response.css('td.bucket > .content > ul > li'):
            raw_keys = li.xpath('b/text()').extract()

            if not raw_keys:
                # This is something else, ignore.
                continue

            key = raw_keys[0].strip(' :').upper()
            if key == 'UPC':
                # Some products have several UPCs.
                raw_upc = li.xpath('text()').extract()[0]
                upc = raw_upc.strip().replace(' ', ';')

        return upc

    def _parse_variants(self, response):
        """
        Parses product variants.
        """
        av = AmazonVariants()
        av.setupSC(response)
        variants = av._variants()

        return variants

    def _parse_prime_pantry(self, response):
        if response.css('#price img#pantry-badge').extract():
            return 'PrimePantry'
        if response.css('.feature i.a-icon-prime').extract():
            return 'Prime'

    def _amazon_prime_check(self, response):
        product = response.meta['product']
        reqs = response.meta.get('reqs')

        if response.xpath('//p[contains(text(), "Yes, I want FREE Two-Day '
                          'Shipping with Amazon Prime")]'):
            product['prime'] = 'Prime'

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_last_buyer_review_date(self, response):
        if self._has_captcha(response):
            return self._handle_captcha(
                response,
                self._parse_last_buyer_review_date
            )
        meta = response.meta.copy()
        product = meta['product']
        reqs = meta.get('reqs')

        date = self._is_empty(
            response.xpath(
                '//table[@id="productReviews"]/tr/td/div/div/span/nobr/text() |'
                '//div[contains(@class, "reviews-content")]/./'
                '/span[contains(@class, "review-date")]/text()'
            ).extract()
        )

        if date:
            date = self._format_last_br_date(date)
            if date:
                cond_set_value(product, 'last_buyer_review_date',
                               date.strftime('%d-%m-%Y'))

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _format_last_br_date(self, data):
        """
        Parses date to normal format.
        """
        raise NotImplementedError

    def _parse_buyer_reviews(self, response):
        buyer_reviews = {}

        total = response.xpath(
            'string(//*[@id="summaryStars"])').re(FLOATING_POINT_RGEX)
        if not total:
            total = response.xpath(
                'string(//div[@id="acr"]/div[@class="txtsmall"]'
                '/div[contains(@class, "acrCount")])'
            ).re(FLOATING_POINT_RGEX)
        if not total:
            total = response.xpath('.//*[contains(@class, "totalReviewCount")]/text()').re(FLOATING_POINT_RGEX)
            if not total:
                return ZERO_REVIEWS_VALUE
        # For cases when total looks like: [u'4.2', u'5', u'51']
        if len(total) == 3:
            buyer_reviews['num_of_reviews'] = int(total[-1].replace(',', '').
                                                  replace('.', ''))
        else:
            buyer_reviews['num_of_reviews'] = int(total[0].replace(',', '').
                                                  replace('.', ''))

        average = response.xpath(
            '//*[@id="summaryStars"]/a/@title')
        if not average:
            average = response.xpath(
                '//div[@id="acr"]/div[@class="txtsmall"]'
                '/div[contains(@class, "acrRating")]/text()'
            )
        if not average:
            average = response.xpath(
                ".//*[@id='reviewStarsLinkedCustomerReviews']//span/text()"
            )
        average = average.extract()[0].replace('out of 5 stars', '') if average else 0.0
        average = average.replace('von 5 Sternen', '').replace('5つ星のうち', '') \
            .replace('平均', '').replace(' 星', '').replace('étoiles sur 5', '') \
            .strip()
        buyer_reviews['average_rating'] = float(average)

        buyer_reviews['rating_by_star'] = {}
        buyer_reviews, table = self.get_rating_by_star(response, buyer_reviews)

        if not buyer_reviews.get('rating_by_star'):
            # scrape new buyer reviews request (that will lead to a new page)
            buyer_rev_link = is_empty(response.xpath(
                '//div[@id="revSum" or @id="reviewSummary"]//a[contains(text(), "See all")' \
                ' or contains(text(), "See the customer review")' \
                ' or contains(text(), "See both customer reviews")]/@href'
            ).extract())
            buyer_rev_link = urlparse.urljoin(response.url, buyer_rev_link)
            # Amazon started to display broken (404) link - fix
            if buyer_rev_link:
                buyer_rev_link = re.search(r'.*product-reviews/[a-zA-Z0-9]+/',
                                           buyer_rev_link)
                if buyer_rev_link:
                    buyer_rev_link = buyer_rev_link.group(0)
            buyer_rev_req = Request(
                url=buyer_rev_link,
                callback=self.get_buyer_reviews_from_2nd_page
            )
            # now we can safely return Request
            #  because it'll be re-crawled in the `parse_product` method
            return buyer_rev_req

        return BuyerReviews(**buyer_reviews)

    def get_buyer_reviews_from_2nd_page(self, response):
        if self._has_captcha(response):
            return self._handle_captcha(
                response,
                self.get_buyer_reviews_from_2nd_page
            )
        product = response.meta["product"]
        reqs = response.meta.get('reqs', [])
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
        # buyer_reviews = self.get_rating_by_star(response, buyer_reviews)[0]

        # print('*' * 20, 'parsing buyer reviews from', response.url)

        if not buyer_reviews.get('rating_by_star'):
            response.meta['product']['buyer_reviews'] = buyer_reviews
            # if still no rating_by_star (probably the rating is percent-based)
            return self._create_get_requests(response)

        if not buyer_reviews.get('rating_by_star'):
            response.meta['product']['buyer_reviews'] = buyer_reviews
            # if still no rating_by_star (probably the rating is percent-based)
            return self._create_post_requests(response)

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
        elif reqs:
            return self.send_next_request(reqs, response)

        return product

    def get_rating_by_star(self, response, buyer_reviews):
        table = response.xpath(
            '//table[@id="histogramTable"]'
            '/tr[@class="a-histogram-row"]')
        if table:
            for tr in table:  # td[last()]//text()').re('\d+')
                rating = is_empty(tr.xpath(
                    'string(.//td[1])').re(FLOATING_POINT_RGEX))
                number = is_empty(tr.xpath(
                    'string(.//td[last()])').re(FLOATING_POINT_RGEX))
                is_perc = is_empty(tr.xpath(
                    'string(.//td[last()])').extract())
                if "%" in is_perc:
                    break
                if number:
                    number = number.replace('.', '')
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

    def _create_get_requests(self, response):
        """
        Method to create request for every star count.
        """
        meta = response.meta.copy()
        meta['_current_star'] = {}
        asin = meta['product_id']
        for star in self.buyer_reviews_stars:
            args = 'ref=cm_cr_arp_d_viewopt_sr?' \
                   'ie=UTF8&' \
                   'reviewerType=all_reviews&' \
                   'showViewpoints=1&' \
                   'sortBy=recent&' \
                   'pageNumber=1&' \
                   'filterByStar={star} ' \
                   'formatType=all_formats'.format(star=star)
            url = response.url + args
            meta['_current_star'] = star
            yield Request(
                url,
                meta=meta,
                callback=self._get_rating_by_star_by_individual_request,
                dont_filter=True
            )

    def _create_post_requests(self, response):
        """
        Method to create request for every star count.
        """
        meta = response.meta.copy()
        meta['_current_star'] = {}
        asin = meta['product_id']

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
                url=self.REVIEW_URL_1.format(domain=self.allowed_domains[0]),
                formdata=args, meta=meta,
                callback=self._get_rating_by_star_by_individual_request,
                dont_filter=True
            )



    def _get_rating_by_star_by_individual_request(self, response):
        if self._has_captcha(response):
            return self._handle_captcha(
                response,
                self._get_rating_by_star_by_individual_request
            )
        reqs = response.meta.get('reqs', [])
        product = response.meta['product']
        mkt_place_link = response.meta.get("mkt_place_link")
        current_star = response.meta['_current_star']
        current_star_int = [
            i + 1 for i, _star in enumerate(self.buyer_reviews_stars)
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
            num_of_reviews_for_star = num_of_reviews_for_star \
                .replace(',', '').replace('.', '')
            rating_by_star[str(current_star_int)] \
                = int(num_of_reviews_for_star)
        if not str(current_star_int) in rating_by_star.keys():
            rating_by_star[str(current_star_int)] = 0

        product['buyer_reviews']['rating_by_star'] = rating_by_star
        # If spider was unable to scrape average rating and num_of reviews, calculate them from rating_by_star
        if len(product['buyer_reviews']['rating_by_star']) >= 5:
            try:
                r_num = product['buyer_reviews']['num_of_reviews']
                product['buyer_reviews']['num_of_reviews'] \
                    = int(r_num) if type(r_num) is unicode or type(r_num) is str else sum(rating_by_star.values())
            except BaseException:
                self.log("Unable to convert num_of_reviews value to int: #%s#"
                         % product['buyer_reviews']['num_of_reviews'], level=WARNING)
                product['buyer_reviews']['num_of_reviews'] = sum(rating_by_star.values())
            try:
                arating = product['buyer_reviews']['average_rating']
                product['buyer_reviews']['average_rating'] \
                    = float(arating) if type(arating) is unicode or type(arating) is str else None
            except BaseException:
                self.log("Unable to convert average_rating value to float: #%s#"
                         % product['buyer_reviews']['average_rating'], level=WARNING)
                product['buyer_reviews']['average_rating'] = None
            if not product['buyer_reviews']['average_rating']:
                total = 0
                for key, value in rating_by_star.iteritems():
                    total += int(key) * int(value)
                product['buyer_reviews']['average_rating'] = round(float(total) / sum(rating_by_star.values()), 2)
            # ok we collected all marks for all stars - can return the product
            product['buyer_reviews'] = BuyerReviews(**product['buyer_reviews'])
            if mkt_place_link:
                return self.mkt_request(mkt_place_link, {"product": product})
            elif reqs:
                return self.send_next_request(reqs, response)
            return product

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """
        req = reqs.pop(0)
        new_meta = response.meta.copy()

        if reqs:
            new_meta["reqs"] = reqs

        return req.replace(meta=new_meta)

    # Captcha handling functions.
    def _has_captcha(self, response):
        is_captcha = response.xpath('.//*[contains(text(), "Enter the characters you see below")]')
        # DEBUG
        # is_captcha = True
        if is_captcha:
            # This may turn on crawlera for all requests
            # self.log("Detected captcha, turning on crawlera for all requests", level=WARNING)
            # self.dont_proxy = False
            self.log("Detected captcha, using captchabreaker", level=WARNING)
            return True
        return False

    def _solve_captcha(self, response):
        forms = response.xpath('//form')
        assert len(forms) == 1, "More than one form found."

        captcha_img = forms[0].xpath(
            '//img[contains(@src, "/captcha/")]/@src').extract()[0]

        self.log("Extracted captcha url: %s" % captcha_img, level=DEBUG)
        return self._cbw.solve_captcha(captcha_img)

    def _handle_captcha(self, response, callback):
        # import pdb; pdb.set_trace()
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

    def exit_point(self, product, next_req):
        if next_req:
            next_req.replace(meta={"product": product})
            return next_req
        return product

    def _marketplace_seller_name_parse(self, name):
        if not name:
            return name

        if ' by ' in name:  # most likely it's ' and Fulfilled by' remains
            name = name.split('and Fulfilled', 1)[0].strip()
            name = name.split('and fulfilled', 1)[0].strip()
            name = name.split('Dispatched from', 1)[0].strip()
            name = name.split('Gift-wrap', 1)[0].strip()
        if ' by ' in name:
            self.log('Multiple "by" occurrences found', WARNING)
        if 'Inc. ' in name:
            name = name.split(', Inc.', 1)[0] + ', Inc.'
        if 'Guarantee Delivery' in name:
            name = name.split('Guarantee Delivery', 1)[0].strip()
        if 'Deals in' in name:
            name = name.split('Deals in', 1)[0].strip()
        if 'Choose' in name:
            name = name.split('Choose', 1)[0].strip()
        if 'tax' in name:
            name = name.split('tax', 1)[0].strip()
        if 'in easy-to-open' in name:
            name = name.split('in easy-to-open', 1)[0].strip()
        if 'easy-to-open' in name:
            name = name.split('easy-to-open', 1)[0].strip()
        if '(' in name:
            name = name.split('(', 1)[0].strip()
        if 'exclusively for Prime members' in name:
            name = name.split('exclusively for Prime members', 1)[0].strip()
        if name.endswith('.'):
            name = name[0:-1]
        return name

    def _parse_marketplace_from_top_block(self, response):
        """ Parses "top block" marketplace ("Sold by ...") """
        top_block = response.xpath('//*[contains(@id, "sns-availability")]'
                                   '//*[contains(text(), "old by")]')
        if not top_block:
            top_block = response.xpath('//*[contains(@id, "merchant-info")]'
                                       '[contains(text(), "old by")]')
        if not top_block:
            return

        seller_id = re.search(r'seller=([a-zA-Z0-9]+)">', top_block.extract()[0])
        if not seller_id:
            seller_id = re.search(r'seller=([a-zA-Z0-9]+)&', top_block.extract()[0])
        if seller_id:
            seller_id = seller_id.group(1)

        sold_by_str = ''.join(top_block.xpath('.//text()').extract()).strip()
        sold_by_str = sold_by_str.replace('.com.', '.com').replace('\t', '') \
            .replace('\n', '').replace('Gift-wrap available', '').replace(' .', '').strip()
        sold_by_whom = sold_by_str.split('by', 1)[1].strip()
        sold_by_whom = self._marketplace_seller_name_parse(sold_by_whom)
        if not sold_by_whom:
            self.log('Invalid "sold by whom" at %s' % response.url, ERROR)
            return
        product = response.meta['product']
        _marketplace = product.get('marketplace', [])
        _price = product.get('price', None)
        _currency = None
        _price_decimal = None
        if _price is not None:
            _price_decimal = float(_price.price)
            _currency = _price.priceCurrency
        _marketplace.append({
            'currency': _currency if _price else None,
            'price': _price_decimal if _price else None,
            'name': sold_by_whom,
            'seller_id': seller_id if seller_id else None
        })
        product['marketplace'] = _marketplace
        return product

    @staticmethod
    def _strip_currency_from_price(val):
        return val.strip().replace('$', '').replace('£', '') \
            .replace('CDN', '').replace(u'\uffe5', '').replace('EUR', '') \
            .replace(',', '.').strip()

    @staticmethod
    def _replace_duplicated_seps(price):
        """ 1.264.67 --> # 1264.67, 1,264,67 --> # 1264,67 """
        if '.' in price:
            sep = '.'
        elif ',' in price:
            sep = ','
        else:
            return price
        left_part, reminder = price.rsplit(sep, 1)
        return left_part.replace(sep, '') + '.' + reminder

    @staticmethod
    def _fix_dots_commas(price):
        if '.' and ',' in price:
            dot_index = price.find('.')
            comma_index = price.find(',')
            if dot_index < comma_index:  # 1.264,67
                price = price.replace('.', '')
            else:  # 1,264.45
                price = price.replace(',', '')
        if price.count('.') >= 2 or price.count(',') >= 2:  # something's wrong - # 1.264.67
            price = AmazonBaseClass._replace_duplicated_seps(price)
        return price

    def _get_marketplace_price_from_cart(self, response, marketplace_block):
        data_modal = {}
        try:
            data_modal = json.loads(marketplace_block.xpath(
                '//*[contains(@data-a-modal, "hlc")]/@data-a-modal'
            ).extract()[0])
        except Exception as e:
            self.log('Error while parsing JSON modal data %s at %s' % (
                str(e), response.url), ERROR)
        get_price_url = data_modal.get('url', None)
        if get_price_url.startswith('/') and not get_price_url.startswith('//'):
            domain = urlparse.urlparse(response.url).netloc
            get_price_url = urlparse.urljoin('http://' + domain, get_price_url)
        if get_price_url:
            self.log('Getting "cart" seller price at %s for %s' % (
                response.url, get_price_url))
            seller_price_cont = requests.get(
                get_price_url,
                headers={'User-Agent': random.choice(self.MKTP_USER_AGENTS)}
            ).text
            lxml_doc = lxml.html.fromstring(seller_price_cont)
            seller_price = lxml_doc.xpath(
                '//*[contains(@id, "priceblock_ourprice")]//text()')
            if seller_price:
                _price = ' '.join([p.strip() for p in seller_price])
                _price = re.search(r' .{0,2}([\d\.,]+) ', _price)
                if _price:
                    return [_price.group(1)]

    def _parse_marketplace_from_static_right_block_more(self, response):
        product = response.meta['product']
        reqs = response.meta.get('reqs')

        _prod_price = product.get('price', [])
        _prod_price_currency = None
        if _prod_price:
            _prod_price_currency = _prod_price.priceCurrency

        _marketplace = product.get('marketplace', [])
        for seller_row in response.xpath('//*[@id="olpOfferList"]//div[contains(@class,"olpOffer")]'):
            _name = seller_row.xpath('div[4]//h3//a/text()|div[4]//@alt').extract()
            _price = seller_row.xpath('div[1]//*[contains(@class,"olpOfferPrice")]/text()').extract()
            _price = float(self._strip_currency_from_price(
                self._fix_dots_commas(_price[0].strip()))) if _price else None

            _seller_id = seller_row.xpath('div[4]//h3//a/@href').re('seller=(.*)\&?') or seller_row.xpath(
                'div[4]//h3//a/@href').re('shops/(.*?)/')
            _seller_id = _seller_id[0] if _seller_id else None

            if _name:
                _name = self._marketplace_seller_name_parse(_name[0])
                _marketplace.append({
                    'name': _name.replace('\n', '').strip(),
                    'price': _price,
                    'currency': _prod_price_currency,
                    'seller_id': _seller_id
                })
        if _marketplace:
            product['marketplace'] = _marketplace
        else:
            product['marketplace'] = []

        next_page = response.xpath('//*[@class="a-pagination"]/li[@class="a-last"]/a/@href').extract()
        meta = response.meta
        if next_page:
            return Request(
                url=urlparse.urljoin(response.url, next_page[0]),
                callback=self._parse_marketplace_from_static_right_block_more,
                meta=meta,
                dont_filter=True
            )

        elif reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_marketplace_from_static_right_block(self, response):
        # try to collect marketplaces from the main page first, before sending extra requests
        product = response.meta['product']

        others_sellers = response.xpath('//*[@id="mbc"]//a[contains(@href, "offer-listing")]/@href').extract()
        if not others_sellers:
            others_sellers = response.xpath('//span[@id="availability"]/a/@href').extract()
        if not others_sellers:
            others_sellers = response.xpath('//div[@id="availability"]/span/a/@href').extract()
        if others_sellers:
            meta = response.meta
            return product, Request(url=urlparse.urljoin(response.url, others_sellers[0]),
                                    callback=self._parse_marketplace_from_static_right_block_more,
                                    meta=meta,
                                    dont_filter=True,
                                    )

        _prod_price = product.get('price', [])
        _prod_price_currency = None
        if _prod_price:
            _prod_price_currency = _prod_price.priceCurrency

        _marketplace = product.get('marketplace', [])
        for mbc_row in response.xpath('//*[@id="mbc"]//*[contains(@class, "mbc-offer-row")]'):
            _price = mbc_row.xpath('.//*[contains(@class, "a-color-price")]/text()').extract()
            _name = mbc_row.xpath('.//*[contains(@class, "mbcMerchantName")]/text()').extract()

            _json_data = None
            try:
                _json_data = json.loads(mbc_row.xpath(
                    './/*[contains(@class, "a-declarative")]'
                    '[contains(@data-a-popover, "{")]/@data-a-popover').extract()[0])
            except Exception as e:
                self.log("Error while parsing json_data: %s at %s" % (
                    str(e), response.url), ERROR)
            merchant_id = None
            if _json_data:
                merchant_url = _json_data.get('url', '')
                merchant_id = re.search(r'&me=([A-Za-z\d]{3,30})&', merchant_url)
                if merchant_id:
                    merchant_id = merchant_id.group(1)

            if not _price:  # maybe price for this seller available only "in cart"
                _price = self._get_marketplace_price_from_cart(response, mbc_row)

            _price = float(self._strip_currency_from_price(
                self._fix_dots_commas(_price[0]))) \
                if _price else None

            if _name:
                _name = self._marketplace_seller_name_parse(_name)
                # handle values like 1.264,67
                _marketplace.append({
                    'name': _name.replace('\n', '').strip(),
                    'price': _price,
                    'currency': _prod_price_currency,
                    'seller_id': merchant_id
                })

        product['marketplace'] = _marketplace
        return product, None
