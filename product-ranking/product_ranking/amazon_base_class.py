# ~~coding=utf-8~~
from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
import re
import urlparse
from urllib import unquote
import json
import string

from scrapy.http import Request
from scrapy.http.request.form import FormRequest
from scrapy.log import msg, ERROR, WARNING, INFO, DEBUG

from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    cond_set_value, FLOATING_POINT_RGEX, FormatterWithDefaults
from product_ranking.guess_brand import guess_brand_from_first_words
from product_ranking.marketplace import Amazon_marketplace
from spiders_shared_code.amazon_variants import AmazonVariants
from product_ranking.amazon_bestsellers import amazon_parse_department
from product_ranking.amazon_modules import build_categories
from product_ranking.settings import ZERO_REVIEWS_VALUE


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

    SEARCH_URL = 'http://{domain}/s/ref=nb_sb_noss_1?url=search-alias' \
                 '%3Daps&field-keywords={search_term}'

    REVIEW_DATE_URL = 'http://{domain}/product-reviews/{product_id}/' \
                      'ref=cm_cr_pr_top_recent?ie=UTF8&showViewpoints=0&' \
                      'sortBy=bySubmissionDateDescending'
    REVIEW_URL_1 = 'http://{domain}/ss/customer-reviews/ajax/reviews/get/' \
                   'ref=cm_cr_pr_viewopt_sr'
    REVIEW_URL_2 = 'http://{domain}/product-reviews/{product_id}/' \
                   'ref=acr_dpx_see_all?ie=UTF8&showViewpoints=1'

    handle_httpstatus_list = [404]

    def __init__(self, captcha_retries='10', *args, **kwargs):
        super(AmazonBaseClass, self).__init__(
            site_name=self.allowed_domains[0],
            url_formatter=FormatterWithDefaults(
                domain=self.allowed_domains[0]
            ),
            *args, **kwargs)
        self.mtp_class = Amazon_marketplace(self)
        self.captcha_retries = int(captcha_retries)
        self._cbw = CaptchaBreakerWrapper()

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

                links.append((link, is_prime, is_prime_pantry))
            else:
                break

            last_idx = idx

        if not links:
            self.log("Found no product links.", WARNING)

        if links:
            for link, is_prime, is_prime_pantry in links:
                prime = None
                if is_prime:
                    prime = 'Prime'
                if is_prime_pantry:
                    prime = 'PrimePantry'
                prod = SiteProductItem(prime=prime)
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

        # Parse product link
        url = is_empty(response.xpath('//link[@rel="canonical"]'
                                      '/@href').extract())
        product['url'] = url

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

        # Prime & PrimePantry
        if not product.get('prime', None) and self._parse_prime_pantry(response):
            product['prime'] = self._parse_prime_pantry(response)

        # Parse variants
        variants = self._parse_variants(response)
        product['variants'] = variants

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
        _prod = self._parse_marketplace_from_static_right_block(response)
        if _prod:
            product = _prod

        # TODO: fix the block below - it removes previously scraped marketplaces
        #marketplace_req = self._parse_marketplace(response)
        #if marketplace_req:
        #    reqs.append(marketplace_req)

        # Parse category
        categories = self._parse_category(response)
        # cond_set_value(product, 'category', category)

        # build_categories(product)
        category_rank = self._parse_category_rank(response)
        cond_set_value(product, 'categories', categories)
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
        if "nichtauflager" in _avail.lower().replace(' ', ''):
            product['is_out_of_stock'] = True
        else:
            product['is_out_of_stock'] = False


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

    def _parse_category(self, response):
        cat = response.xpath(
            '//span[@class="a-list-item"]/'
            'a[@class="a-link-normal a-color-tertiary"]/text()')
        if not cat:
            cat = response.xpath('//li[@class="breadcrumb"]/a[@class="breadcrumb-link"]/text()')

        category = []
        for cat_sel in cat:
            category.append(cat_sel.extract().strip())

        if category:
            return category


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

        if 'base64' in image:
            img_jsons = response.xpath(
                '//*[@id="imgBlkFront"]/@data-a-dynamic-image | '
                '//*[@id="landingImage"]/@data-a-dynamic-image'
            ).extract()

            if img_jsons:
                img_data = json.loads(img_jsons[0])

                image = max(img_data.items(), key=lambda (_, size): size[0])[0]

        return image

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

        if brand and (u'®' in brand):
            brand = brand.replace(u'®', '')

        if not brand:
            brand_logo = self._is_empty(
                response.xpath('//a[@id="brand"]/@href').extract()
            )
            if brand_logo:
                brand = brand_logo.split('/')[1]

        if not brand and title:
            try:
                brand = guess_brand_from_first_words(title)
            except:
                brand = guess_brand_from_first_words(title[0])
            if brand:
                brand = [brand]

        if isinstance(brand, list):
            brand = [br for br in brand if brand and 'search result' not in br.lower()]

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
            price2 = re.search('\|([\d\.]+)\|baseItem"}',response.body)
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
                return ZERO_REVIEWS_VALUE
        buyer_reviews['num_of_reviews'] = int(total[0].replace(',', '').
                                              replace('.', ''))

        average = response.xpath(
            '//*[@id="summaryStars"]/a/@title')
        if not average:
            average = response.xpath(
                '//div[@id="acr"]/div[@class="txtsmall"]'
                '/div[contains(@class, "acrRating")]/text()'
            )
        average = average.extract()[0].replace('out of 5 stars','')
        average = average.replace('von 5 Sternen', '').replace('5つ星のうち','')\
            .replace('平均','').replace(' 星','').replace('étoiles sur 5', '')\
            .strip()
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
            return self._create_post_requests(response)
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

    def exit_point(self, product, next_req):
        if next_req:
            next_req.replace(meta={"product": product})
            return next_req
        return product

    def _parse_marketplace_from_top_block(self, response):
        """ Parses "top block" marketplace ("Sold by ...") """
        top_block = response.xpath('//*[contains(@id, "sns-availability")]'
                                   '//*[contains(text(), "old by")]')
        if not top_block:
            top_block = response.xpath('//*[contains(@id, "merchant-info")]'
                                       '[contains(text(), "old by")]')
        if not top_block:
            return
        sold_by_str = ''.join(top_block.xpath('.//text()').extract()).strip()
        sold_by_str = sold_by_str.replace('.com.', '.com').replace('\t', '')\
            .replace('\n', '').replace('Gift-wrap available', '').replace(' .', '').strip()
        sold_by_whom = sold_by_str.split('by', 1)[1].strip()
        if ' by ' in sold_by_whom:  # most likely it's ' and Fulfilled by' remains
            sold_by_whom = sold_by_whom.split('and Fulfilled', 1)[0].strip()
            sold_by_whom = sold_by_whom.split('and fulfilled', 1)[0].strip()
            sold_by_whom = sold_by_whom.split('Dispatched from', 1)[0].strip()
            sold_by_whom = sold_by_whom.split('Gift-wrap', 1)[0].strip()
        if ' by ' in sold_by_whom:
            self.log('Multiple "by" occurrences found at %s' % response.url, ERROR)
        if 'Inc. ' in sold_by_whom:
            sold_by_whom = sold_by_whom.split(', Inc.', 1)[0] + ', Inc.'
        if 'Guarantee Delivery' in sold_by_whom:
            sold_by_whom = sold_by_whom.split('Guarantee Delivery', 1)[0].strip()
        if 'Deals in' in sold_by_whom:
            sold_by_whom = sold_by_whom.split('Deals in', 1)[0].strip()
        if 'Choose' in sold_by_whom:
            sold_by_whom = sold_by_whom.split('Choose', 1)[0].strip()
        if 'tax' in sold_by_whom:
            sold_by_whom = sold_by_whom.split('tax', 1)[0].strip()
        if 'in easy-to-open' in sold_by_whom:
            sold_by_whom = sold_by_whom.split('in easy-to-open', 1)[0].strip()
        if 'easy-to-open' in sold_by_whom:
            sold_by_whom = sold_by_whom.split('easy-to-open', 1)[0].strip()
        if '(' in sold_by_whom:
            sold_by_whom = sold_by_whom.split('(', 1)[0].strip()
        if sold_by_whom.endswith('.'):
            sold_by_whom = sold_by_whom[0:-1]
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
        })
        product['marketplace'] = _marketplace
        return product

    @staticmethod
    def _strip_currency_from_price(val):
        return val.strip().replace('$', '').replace('£', '')\
            .replace('CDN', '').replace(u'\uffe5', '').replace('EUR', '')\
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

    def _parse_marketplace_from_static_right_block(self, response):
        # try to collect marketplaces from the main page first, before sending extra requests
        product = response.meta['product']
        _prod_price = product.get('price', [])
        _prod_price_currency = None
        if _prod_price:
            _prod_price_currency = _prod_price.priceCurrency

        _marketplace = product.get('marketplace', [])
        for mbc_row in response.xpath('//*[@id="mbc"]//*[contains(@class, "mbc-offer-row")]'):
            _price = mbc_row.xpath('.//*[contains(@class, "a-color-price")]/text()').extract()
            _name = mbc_row.xpath('.//*[contains(@class, "mbcMerchantName")]/text()').extract()
            if _price and _name:
                # handle values like 1.264,67
                _marketplace.append({
                    'name': _name[0].replace('\n', '').strip(),
                    'price': float(self._strip_currency_from_price(
                        self._fix_dots_commas(_price[0]))),
                    'currency': _prod_price_currency
                })
        product['marketplace'] = _marketplace
        return product