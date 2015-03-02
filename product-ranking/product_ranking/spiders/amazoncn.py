# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import json
import re
import string

from scrapy.http.request.form import FormRequest
from scrapy.log import msg, ERROR, WARNING, INFO, DEBUG

from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.spiders import (BaseProductsSpider, cond_set,
                                     cond_set_value, FormatterWithDefaults)


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
    name = 'amazoncn_products'
    allowed_domains = ["amazon.cn"]

    SEARCH_URL = "http://www.amazon.cn/s/?field-keywords={search_term}"
    #SEARCH_URL = "http://www.amazon.cn/s/ref=sr_st_{sort_mode}" \
    #             "?keywords={search_term}&rh=k:{search_term},i:{sort_category}"

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

    def parse(self, response):
        if self._has_captcha(response):
            result = self._handle_captcha(response, self.parse)
        else:
            result = super(AmazonProductsSpider, self).parse(response)
        return result

    def parse_product(self, response):
        prod = response.meta['product']

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

    def _populate_from_html(self, response, product):
        cond_set(product, 'brand', response.css('#brand ::text').extract())
        cond_set(
            product,
            'price',
            response.css('#priceblock_ourprice ::text '
                         ', .price3P::text'
                         ', .priceLarge::text').extract(),
        )
        if product.get('price', None):
            if u'\uffe5' not in product.get('price', ''):
                self.log('Invalid price at: %s' % response.url, level=ERROR)
            else:
                product['price'] = Price(
                    price=product['price'].replace(u'\uffe5', '').replace(
                        ' ', '').replace(',', '').strip(),
                    priceCurrency='CNY'
                )
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
        self._buyer_reviews_from_html(response, product)

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
            count_matches = response.xpath(
                '//*[@id="resultCount"]/text()').re(u'([\d, ]+)')
            if count_matches and count_matches[-1]:
                total_matches = int(
                    count_matches[-1].replace(',', '').strip())
            else:
                total_matches = None
        return total_matches

    def _scrape_product_links(self, response):
        links = response.css(
            'div.listView div.productTitle a ::attr(href)').extract()
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

    def _buyer_reviews_from_html(self, response, product):
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
        buyer_reviews = BuyerReviews(num_of_reviews=total,
                                     average_rating=average,
                                     rating_by_star=ratings)
        cond_set_value(product, 'buyer_reviews', buyer_reviews)