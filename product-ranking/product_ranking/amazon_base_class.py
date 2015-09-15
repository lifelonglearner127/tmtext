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
    cond_set_value, FLOATING_POINT_RGEX
from product_ranking.guess_brand import guess_brand_from_first_words
from product_ranking.marketplace import Amazon_marketplace
from spiders_shared_code.amazon_variants import AmazonVariants
from product_ranking.amazon_bestsellers import amazon_parse_department
from product_ranking.amazon_modules import build_categories


is_empty = lambda x, y=None: x[0] if x else y

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

    ZERO_REVIEWS_STAR = {
        '1': {'percentage': 0.0, 'total': 0},
        '2': {'percentage': 0.0, 'total': 0},
        '3': {'percentage': 0.0, 'total': 0},
        '4': {'percentage': 0.0, 'total': 0},
        '5': {'percentage': 0.0, 'total': 0}
    }
    ZERO_REVIEWS_VALUE = {
        'num_of_reviews': 0,
        'average_rating': 0.0,
        'rating_by_star': ZERO_REVIEWS_STAR
    }

    def __init__(self, captcha_retries='10', *args, **kwargs):
        super(AmazonBaseClass, self).__init__(*args, **kwargs)

        self.mtp_class = Amazon_marketplace(self)

        # Defaults --- for English Amazon's
        # String from html body that means there's no results ( "no results.", for example)
        self.total_match_not_found = 'did not match any products.'
        # Regexp for total matches to parse a number from html body
        self.total_matches_re = r'of\s?([\d,.\s?]+)'

        # Default locale
        self.locale = 'en-US'

        # Default price currency
        self.price_currency = 'USD'
        self.price_currency_view = '$'

        self.captcha_retries = int(captcha_retries)

        self._cbw = CaptchaBreakerWrapper()

    def _scrape_total_matches(self, response):
        """
        Overrides BaseProductsSpider method to scrape total result matches. total_matches_str
        and total_matches_re need to be set for every concrete amazon spider.
        :param response:
        :return: Number of total matches (int)
        """

        if unicode(self.total_match_not_found) in response.body_as_unicode():
            total_matches = 0
        else:
            count_matches = is_empty(
                response.xpath(
                    '//h2[@id="s-result-count"]/text()'
                ).re(unicode(self.total_matches_re))
            )
            if count_matches:
                total_matches = int(count_matches.replace(
                    ' ', '').replace(u'\xa0', '').replace(',', '').replace('.', ''))
            else:
                total_matches = None

        if not total_matches:
            total_matches = int(is_empty(response.xpath(
                '//h2[@id="s-result-count"]/text()'
            ).re(FLOATING_POINT_RGEX), 0))

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
        lis = response.xpath("//div[@id='resultsCol']//ul//li |"
                             "//div[@id='mainResults']//ul//li"
                             "[contains(@id, 'result')] |"
                             "//div[@id='atfResults']//ul//li"
                             "[contains(@id, 'result')] |"
                             "//div[@id='mainResults']//div"
                             "[contains(@id, 'result')]")
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
            data_asin = is_empty(
                li.xpath('@id').extract()
            )

            try:
                idx = int(is_empty(
                    re.findall(r'\d+', data_asin)
                ))
            except ValueError:
                continue

            if idx > last_idx:
                link = is_empty(
                    li.xpath(
                        ".//a[contains(@class,'s-access-detail-page')]/@href |"
                        ".//h3[@class='newaps']/a/@href"
                    ).extract()
                )

                if 'slredirect' in link:
                    link = urlparse.urljoin('http://amazon.com/', link)

                links.append((link, is_prime, is_prime_pantry))
            else:
                break

            last_idx = idx

        if len(links) < 1:
            self.log("Found no product links.", WARNING)

        for link, is_prime, is_prime_pantry in links:
            prime = None
            if is_prime:
                prime = 'Prime'
            if is_prime_pantry:
                prime = 'PrimePantry'
            yield link, SiteProductItem(prime=prime)

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

        # Set locale
        cond_set_value(product, 'locale', self.locale)

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

        # Parse marketplaces
        marketplace_req = self._parse_marketplace(response)
        if marketplace_req:
            reqs.append(marketplace_req)

        # Parse category
        category = self._parse_category(response)
        cond_set_value(product, 'category', category)

        build_categories(product)

        if category:
            # Parse departments and bestseller rank
            department = amazon_parse_department(category)
            if department is not None:
                department, bestseller_rank = department.items()[0]

                cond_set_value(product, 'department', department)
                cond_set_value(product, 'bestseller_rank', bestseller_rank)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

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

        title = is_empty(
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
                  '//*[@id="imgTagWrapperId"]/.//img/@data-old-hires'
        if add_xpath:
            xpathes += ' |' + add_xpath

        image = is_empty(
            response.xpath(xpathes).extract(), ''
        )

        if not image:
            # Another try to parse img_url: from html body as JS data
            img_re = is_empty(
                re.findall(
                    r"'colorImages':\s*\{\s*'initial':\s*(.*)\},|colorImages\s*=\s*\{\s*\"initial\":\s*(.*)\}",
                    response.body), ''
            )

            img_re = is_empty(list(img_re))

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
                  '//a[contains(@href, "field-author")]/text() |' \
                  '//*[@id="contributorLink"]/text() |' \
                  '//*[@id="by-line"]/.//a/text() |' \
                  '//*[@id="artist-container"]/.//a/text() |' \
                  '//*[@id="byline"]/.//*[contains(@class,"author")]/a/text() |' \
                  '//div[@class="buying"]/.//a[contains(@href, "search-type=ss")]/text() |' \
                  '//a[@id="ProductInfoArtistLink"]/text()'
        if add_xpath:
            xpathes += ' |' + add_xpath

        product = response.meta['product']
        title = product.get('title', '')

        brand = response.xpath(xpathes).extract()

        if brand and (u'®' in brand):
            brand = brand.replace(u'®', '')

        if not brand:
            brand_logo = is_empty(
                response.xpath('//a[@id="brand"]/@href').extract()
            )
            if brand_logo:
                brand = brand_logo.split('/')[1]

        if not brand and title:
            brand = guess_brand_from_first_words(title)
            if brand:
                brand = [brand]

        brand = brand or ['NO BRAND']

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

        price_ss = is_empty(
            response.xpath(xpathes).extract(), None
        )
        if price_ss and price_ss.startswith('$'):
            price_ss = price_ss.replace(' ', '').replace(',', '').strip('$')
            try:
                price_ss = float(price_ss)
            except ValueError as exc:
                self.log(
                    "Unable to extract price Subscribe&Save on {url}: {exc}".format(
                        url=response.url, exc=exc
                    ), WARNING
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
            is_empty(response.xpath(
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
                  'b[contains(text(), "ASIN")]/../text() |' \
                  '//table/tbody/tr/' \
                  'td[contains(@class, "label") and contains(text(), "ASIN")]/' \
                  '../td[contains(@class, "value")]/text() |' \
                  '//div[contains(@class, "content")]/ul/li/' \
                  'b[contains(text(), "ISBN-10")]/../text()'
        if add_xpath:
            xpathes += ' |' + add_xpath

        model = is_empty(
            response.xpath(xpathes).extract(), ''
        )

        if not model:
            spans = response.xpath('//span[@class="a-text-bold"]')
            for span in spans:
                text = is_empty(span.xpath('text()').extract())
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
                  '//div[contains(@data-reftag,"atv_dp_bb_est_sd_movie")]/button/text()'

        if add_xpath:
            xpathes += ' |' + add_xpath

        price_currency_view = unicode(self.price_currency_view)
        price = is_empty(
            response.xpath(xpathes).extract(), ''
        )

        if price:
            if price_currency_view not in price:
                price = '0.00'
                if 'FREE' not in price:
                    self.log('Currency symbol not recognized: %s' % response.url,
                             level=WARNING)
            else:
                price = is_empty(re.findall(r'[\d,.]+\d', price), '0.00')
                price = price.replace(price_currency_view, '').replace(',', '')
        else:
            price = '0.00'

        price = round(float(price.strip()), 2)
        price = Price(price=price, priceCurrency=self.price_currency)

        return price

    def _parse_price_original(self, response, add_xpath=None):
        """
        Parses product's original price.
        :param add_xpath: Additional xpathes, so you don't need to change base class
        """
        xpathes = '//*[@id="price"]/.//*[contains(@class, "a-text-strike")]' \
                  '/text()'

        if add_xpath:
            xpathes += ' |' + add_xpath

        price_original = is_empty(
            response.xpath(xpathes).extract()
        )

        if price_original:
            price_original = price_original.replace('$', '').strip()
            try:
                price_original = float(price_original)
            except ValueError:
                price_original = None

        return price_original

    def _parse_category(self, response):
        """
        Parses product categories.
        """
        meta = response.meta.copy()
        product = meta['product']

        category = {
            ' > '.join(map(
                unicode.strip, itm.css('.zg_hrsr_ladder a::text').extract())
            ): int(re.sub('[ ,]', '', itm.css('.zg_hrsr_rank::text').re(
                '([\d, ]+)'
            )[0]))
            for itm in response.css('.zg_hrsr_item')
        }

        prim_a = response.css('#SalesRank::text, #SalesRank .value::text').re(
            '(\d+){0,1}\.{0,1}(\d+) .*en (.+)\('
        )
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
            category.update(prim)
        category = [{'category': k, 'rank': v} for k, v in category.iteritems()]

        return category

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
                  '//div[@id="bookDescription_feature_div"]/noscript |' \
                  '//div[@id="featurebullets_feature_div"]'

        if add_xpath:
            xpathes += ' |' + add_xpath

        description = is_empty(response.xpath(xpathes).extract())
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

        return description

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

    def _parse_buyer_reviews(self, response):
        product = response.meta['product']

        # scrape new buyer reviews request (that will lead to a new page)
        buyer_rev_link = 'http://www.amazon.com/product-reviews/{id}/' \
                         'ref=acr_dpx_see_all?ie=UTF8&showViewpoints=1'.format(
                             id=self._get_asin_from_url(product['url'])
                         )

        buyer_reviews = {}

        total = response.xpath(
            '//*[@id="summaryStars"] |'
            '//div[@id="acr"]/div[@class="txtsmall"]/div[contains(@class, "acrCount")] |'
            '//*[@id="acrCustomerReviewText"]/text()'
        ).re(FLOATING_POINT_RGEX)
        total = is_empty(total, '')
        if not total:
            return BuyerReviews(**self.ZERO_REVIEWS_VALUE)

        buyer_reviews['num_of_reviews'] = int(total.replace(',', ''))

        average = response.xpath(
            '//*[@id="summaryStars"]/a/@title |'
            '//div[@id="acr"]/div[@class="txtsmall"]'
            '/div[contains(@class, "acrRating")]/text()'
        )
        average = is_empty(average.extract(), '')

        if average:
            average = average.replace('out of 5 stars', '')
            buyer_reviews['average_rating'] = float(average)

            buyer_reviews['rating_by_star'] = {}
            buyer_reviews, table = self._get_rating_by_star(response, buyer_reviews)

            if not buyer_reviews['rating_by_star'] or response.meta.get('is_perc'):
                buyer_rev_req = Request(
                    url=buyer_rev_link,
                    callback=self.get_buyer_reviews_from_2nd_page
                )
                # now we can safely return Request
                #  because it'll be re-crawled in the `parse_product` method
                return buyer_rev_req

        else:
            buyer_rev_req = Request(
                url=buyer_rev_link,
                callback=self.get_buyer_reviews_from_2nd_page
            )
            # now we can safely return Request
            #  because it'll be re-crawled in the `parse_product` method
            return buyer_rev_req

        return BuyerReviews(**buyer_reviews)

    def _get_rating_by_star_by_individual_request(self, response):
        meta = response.meta.copy()
        product = meta['product']
        mkt_place_link = meta.get("mkt_place_link")

        counter = product['buyer_reviews']['counter']
        product['buyer_reviews']['counter'] += 1

        current_star = meta['_current_star']
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
            rating_by_star[str(current_star_int)]['total'] = int(num_of_reviews_for_star)
        else:
            rating_by_star[str(current_star_int)]['total'] = 0

        if not str(current_star_int) in rating_by_star.keys():
            rating_by_star[str(current_star_int)]['total'] = 0

        product['buyer_reviews']['rating_by_star'] = rating_by_star

        if counter >= 4:
            # ok we collected all marks for all stars - can return the product
            del product['buyer_reviews']['counter']
            product['buyer_reviews'] = BuyerReviews(**product['buyer_reviews'])
            return product

    def _get_asin_from_url(self, url):
        match = re.search(r'/([A-Z0-9]{4,15})/?', url)
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
            meta['product']['buyer_reviews']['counter'] = 0

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

        num_of_reviews = is_empty(
            response.xpath(
                '//span[contains(@class, "totalReviewCount")]'
                '/text()'
            ).extract(), '').replace(",", "")

        if num_of_reviews:
            buyer_reviews['num_of_reviews'] = int(num_of_reviews.strip())
        else:
            buyer_reviews = BuyerReviews(**self.ZERO_REVIEWS_VALUE)

        average = is_empty(response.xpath(
            '//div[contains(@class, "averageStarRatingNumerical")]//span/text()'
        ).extract(), "")

        buyer_reviews["average_rating"] = float(
            average.replace('out of 5 stars', '').strip()
        )

        buyer_reviews["rating_by_star"] = {}
        buyer_reviews = self._get_rating_by_star(response, buyer_reviews)[0]

        if not buyer_reviews.get('rating_by_star') or response.meta.get('is_perc'):
            response.meta['product']['buyer_reviews'] = buyer_reviews
            # if still no rating_by_star (probably the rating is percent-based)
            return self._create_post_requests(
                response, self._get_asin_from_url(response.url))

        return product

    def _get_rating_by_star(self, response, buyer_reviews):
        table = response.xpath(
            '//table[@id="histogramTable"]/.//tr[@class="a-histogram-row"]'
        )
        if table:
            for tr in table:
                rating = is_empty(tr.xpath(
                    'string(.//td[1])').re(FLOATING_POINT_RGEX))
                number = is_empty(tr.xpath(
                    'string(.//td[last()])').re(FLOATING_POINT_RGEX))
                is_perc = is_empty(tr.xpath(
                    'string(.//td[last()])').extract())
                if number:
                    number = int(
                        number.replace(',', '')
                    )
                    buyer_reviews['rating_by_star'][rating] = {}
                    if "%" in is_perc:
                        response.meta['is_perc'] = True
                        buyer_reviews['rating_by_star'][rating]['percentage'] = format(
                            number / 100, '.2f'
                        )
                    else:
                        buyer_reviews['rating_by_star'][rating]['total'] = number
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
                buyer_reviews['rating_by_star'][rating]['total'] = int(
                    number.replace(',', '')
                )
        return buyer_reviews, table

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
