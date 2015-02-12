from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import json
import string

from scrapy.http.request.form import FormRequest
from scrapy.log import msg, ERROR, WARNING, INFO, DEBUG

from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, \
    cond_set, cond_set_value, FLOATING_POINT_RGEX


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


class AmazonProductsSpider(BaseProductsSpider):
    name = 'amazon_products'
    allowed_domains = ["amazon.com"]

    user_agent = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:35.0) Gecko'
                  '/20100101 Firefox/35.0')

    SEARCH_URL = ('http://www.amazon.com/s/ref=nb_sb_noss_1?url=search-alias'
                  '%3Daps&field-keywords={search_term}')

    def __init__(self, captcha_retries='10', *args, **kwargs):
        super(AmazonProductsSpider, self).__init__(*args, **kwargs)

        self.captcha_retries = int(captcha_retries)

        self._cbw = CaptchaBreakerWrapper()

    def parse(self, response):
        if self._has_captcha(response):
            result = self._handle_captcha(response, self.parse)
        else:
            result = super(AmazonProductsSpider, self).parse(response)
        return result

    def parse_product(self, response):
        prod = response.meta['product']

        prod['buyer_reviews'] = self._build_buyer_reviews(response)

        if not self._has_captcha(response):
            self._populate_from_js(response, prod)

            self._populate_from_html(response, prod)

            cond_set_value(prod, 'locale', 'en-US')  # Default locale.

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
            response.css('#priceblock_ourprice ::text').extract(),
        )
        if not product.get('price', None):
            cond_set(
                product,
                'price',
                response.css(
                    '#unqualifiedBuyBox .a-color-price ::text').extract(),
            )
        if not product.get('price', None):
            cond_set(
                product,
                'price',
                response.css(
                    '#priceblock_saleprice ::text').extract(),
            )
        if not product.get('price', None):
            cond_set(
                product,
                'price',
                response.css(
                    '#actualPriceValue ::text').extract(),
            )
        if not product.get('price', None):
            cond_set(
                product,
                'price',
                response.css(
                    '#buyNewSection .offer-price ::text').extract(),
            )
        if product.get('price', None):
            if not '$' in product['price']:
                self.log('Currency symbol not recognized: %s' % response.url,
                         level=ERROR)
            else:
                product['price'] = Price(
                    priceCurrency='USD',
                    price=product['price'].replace('$', '').strip()\
                        .replace(',', '')
                )

    def _populate_from_html(self, response, product):
        cond_set(product, 'brand', response.css('#brand ::text').extract())
        self._get_price(response, product)
        cond_set(
            product,
            'description',
            response.css('.productDescriptionWrapper').extract(),
        )
        cond_set(
            product,
            'image_url',
            response.css(
                '#imgTagWrapperId > img ::attr(data-old-hires)').extract()
        )
        cond_set(
            product, 'title', response.css('#productTitle ::text').extract())

        # Some data is in a list (ul element).
        model = None
        for li in response.css('td.bucket > .content > ul > li'):
            raw_keys = li.xpath('b/text()').extract()
            if not raw_keys:
                # This is something else, ignore.
                continue

            key = raw_keys[0].strip(' :').upper()
            if key == 'UPC':
                # Some products have several UPCs. The first one is used.
                raw_upc = li.xpath('text()').extract()[0]
                cond_set(
                    product,
                    'upc',
                    raw_upc.strip().split(' '),
                    conv=int
                )
            elif key == 'ASIN' and model is None or key == 'ITEM MODEL NUMBER':
                model = li.xpath('text()').extract()
        cond_set(product, 'model', model, conv=string.strip)

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

    def _build_buyer_reviews(self, response):
        buyer_reviews = {}

        total = response.xpath(
            'string(//*[@id="summaryStars"])').re(FLOATING_POINT_RGEX)
        if not total:
            return
        buyer_reviews['num_of_reviews'] = int(total[0].replace(',', ''))

        average = response.xpath(
            '//*[@id="summaryStars"]/a/@title').extract()[0].replace('out of 5 stars','')
        buyer_reviews['average_rating'] = float(average)

        buyer_reviews['rating_by_star'] = {}
        for tr in response.xpath(
            '//table[@id="histogramTable"]'
            '/tr[@class="a-histogram-row"]'): #td[last()]//text()').re('\d+')
            rating = tr.xpath('string(.//td[1])').re(FLOATING_POINT_RGEX)[0]
            number = tr.xpath('string(.//td[last()])').re(FLOATING_POINT_RGEX)[0]
            buyer_reviews['rating_by_star'][rating] = int(number.replace(',', ''))

        return BuyerReviews(**buyer_reviews)

    def _scrape_total_matches(self, response):
        # Where this value appears is a little weird and changes a bit so we
        # need two alternatives to capture it consistently.

        if response.css('#noResultsTitle'):
            return 0

        # Every result I saw is shown with this format
        #    1-16 of 424,831 results for
        #    2 results for
        values = response.css('#s-result-count ::text').re(
            '([0-9,]+)\s[Rr]esults for')
        if not values:
            # The first possible place is where it normally is in a fully
            # rendered page.
            values = response.css('#resultCount > span ::text').re(
                '\s+of\s+(\d+(,\d\d\d)*)\s+[Rr]esults')
            if not values:
                # Otherwise, it appears within a comment.
                values = response.css(
                    '#result-count-only-next'
                ).xpath(
                    'comment()'
                ).re(
                    '\s+of\s+(\d+(,\d\d\d)*)\s+[Rr]esults\s+'
                )

        if values:
            total_matches = int(values[0].replace(',', ''))
        else:
            self.log(
                "Failed to parse total number of matches for: %s"
                % response.url,
                level=ERROR
            )
            total_matches = None
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

    def _scrape_product_links(self, response):
        links = response.css(
            'a.s-access-detail-page ::attr(href)'
        ).extract()
        if not links:
            self.log("Found no product links.", WARNING)
        for link in links:
            yield link, SiteProductItem()

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
        product = response.meta['product']

        self.log("Captcha challenge for %s (try %d)."
                 % (product['url'], captcha_solve_try),
                 level=INFO)

        captcha = self._solve_captcha(response)

        if captcha is None:
            self.log(
                "Failed to guess captcha for '%s' (try: %d)." % (
                    product['url'], captcha_solve_try),
                level=ERROR
            )
            result = None
        else:
            self.log(
                "On try %d, submitting captcha '%s' for '%s'." % (
                    captcha_solve_try, captcha, product['url']),
                level=INFO
            )
            result = FormRequest.from_response(
                response,
                formname='',
                formdata={'field-keywords': captcha},
                callback=callback)
            result.meta['captcha_solve_try'] = captcha_solve_try + 1
            result.meta['product'] = product

        return result

    def _parse_single_product(self, response):
        return self.parse_product(response)

