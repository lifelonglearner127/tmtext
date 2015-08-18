# ~~coding=utf-8~~

import re
import urlparse
import json
import string

from scrapy.http import Request
from scrapy.http.request.form import FormRequest
from scrapy.log import msg, ERROR, WARNING, INFO, DEBUG

from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    cond_set_value, FLOATING_POINT_RGEX
from product_ranking.amazon_tests import AmazonTests
from product_ranking.amazon_bestsellers import amazon_parse_department
from product_ranking.guess_brand import guess_brand_from_first_words


is_empty = lambda x, y=None: x[0] if x else y


class AmazonBaseClass(BaseProductsSpider):

    # Defaults --- for English Amazon's
    # String from html body that means there's no results ( "no results.", for example)
    total_match_not_found = 'did not match any products.'
    # Regexp for total matches to parse a number from html body
    total_matches_re = r'of\s?([\d,.\s?]+)'

    # Default locale
    locale = 'en-US'

    # Default price currency
    price_currency = 'USD'
    price_currency_view = '$'

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

        lis = response.xpath('//ul/li[contains(@class, "s-result-item")] |'
                             '//div[@id="mainResults"]/div[contains(@class, "prod")] |'
                             '//*[contains(@class, "sx-table-item")]')
        links = []

        for no, li in enumerate(lis):
            href = li.xpath(
                ".//a[contains(@class,'s-access-detail-page')]/@href |"
                ".//a/@href")

            if href:
                href = is_empty(href.extract())
                is_prime = li.xpath(
                    "*/descendant::i[contains(concat(' ',@class,' '),' a-icon-premium ')] |"
                    "*/descendant::i[contains(@class, 'a-icon-prime]')]").extract()
                is_prime_pantry = li.xpath(
                    "*/descendant::i[contains(concat(' ',@class,' '),' a-icon-premium-pantry ')] |"
                    "*/descendant::i[contains(@class, 'a-icon-prime-pantry')] |"
                    "*/descendant::i[contains(@class, 'a-icon-primepantry')]").extract()
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
        cond_set_value(product, 'price_subscribe_save', price_subscribe_save)

        # Parse model
        model = self._parse_model(response)
        cond_set_value(product, 'model', model, conv=string.strip)

        # Parse price
        price = self._parse_price(response)
        cond_set_value(product, 'price', price)

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
        brand = [br.strip() for br in brand]

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
            response.xpath(xpathes).extract(), ''
        ).strip()
        if price_ss and price_ss.startswith('$'):
            price_ss = price_ss.replace(' ', '').replace(',', '').strip('$')
            try:
                price_ss = float(price_ss)
            except Exception as exc:
                self.log(
                    "Unable to extract price Subscribe&Save on {url}: {exc}".format(
                        url=response.url, exc=exc
                    ), WARNING
                )

        return price_ss

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
                  '//*[@id="priceblock_ourprice"][contains(@class, "a-color-price")]/text()[normalize-space()] |' \
                  '//*[@id="priceBlock"]/.//span[@class="priceLarge"]/text()[normalize-space()] |' \
                  '//*[@id="actualPriceValue"]/*[@class="priceLarge"]/text()[normalize-space()] |' \
                  '//*[@id="actualPriceValue"]/text()[normalize-space()] |' \
                  '//*[@id="buyNewSection"]/.//*[contains(@class, "offer-price")]/text()[normalize-space()] |' \
                  '//div[contains(@class, "a-box")]/div[@class="a-row"]/text()[normalize-space()] |' \
                  '//span[@id="priceblock_dealprice"]/text()[normalize-space()] |' \
                  '//*[contains(@class, "price3P")]/text()[normalize-space()] |' \
                  '//span[@id="ags_price_local"]/text()[normalize-space()] |' \
                  '//div[@id="olpDivId"]/.//span[@class="price"]/text()[normalize-space()]'

        if add_xpath:
            xpathes += ' |' + add_xpath

        price_currency_view = unicode(self.price_currency_view)
        price = is_empty(
            response.xpath(xpathes).extract(), ''
        )

        print('*'*50)
        print price
        print('*'*50)
        print(response.xpath('//*[@id="soldByThirdParty"]/span[1]').extract())
        print('*'*50)

        if price:
            if price_currency_view not in price:
                price = '0.00'
                if 'FREE' not in price:
                    self.log('Currency symbol not recognized: %s' % response.url,
                             level=WARNING)
            else:
                price = is_empty(re.findall(r'[\d,.]+\d', price), '0.00')
                price = price.replace(price_currency_view, '').replace(',', '.')
        else:
            price = '0.00'

        price = round(float(price.strip()), 2)
        price = Price(price=price, priceCurrency=self.price_currency)

        return price

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
