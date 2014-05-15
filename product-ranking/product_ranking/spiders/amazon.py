from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
from future_builtins import *

import sys
import json

from scrapy.log import ERROR, WARNING
from scrapy.selector import Selector

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set

try:
    from captcha_solver import CaptchaBreakerWrapper
except ImportError as e:
    print("### Failed to import CaptchaBreaker.",
          "Will continue without solving captchas:", e,
          file=sys.stderr)

    class FakeCaptchaBreaker(object):
        @staticmethod
        def solve_captcha(url):
            msg("No CaptchaBreaker to solve: %s" % url, level=WARNING)
            return None
    CaptchaBreakerWrapper = FakeCaptchaBreaker


class AmazonProductsSpider(BaseProductsSpider):
    name = 'amazon_products'
    allowed_domains = ["amazon.com"]

    SEARCH_URL = "http://www.amazon.com/s/?field-keywords={search_term}"

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

        if self._has_captcha(response):
            result = self._handle_captcha(response, self.parse_product)
        elif response.meta.get('captch_solve_try', 0) >= self.captcha_retries:
            self.log("Giving up on trying to solve the captcha challenge after"
                     " %s tries for: %s" % (self.captcha_retries, prod['url']),
                     level=WARNING)
            result = None
        else:
            sel = Selector(response)

            self._populate_from_js(response.url, sel, prod)

            self._populate_from_html(response.url, sel, prod)

            cond_set(prod, 'locale', ['en-US'])  # Default locale.

            result = prod
        return result

    def _populate_from_html(self, url, sel, product):
        cond_set(product, 'brand', sel.css('#brand ::text').extract())
        cond_set(product, 'price',
                 sel.css('#priceblock_ourprice ::text').extract())
        cond_set(product, 'description',
                 sel.css('.productDescriptionWrapper').xpath('node()')
                 .extract(), lambda descs: descs[0].strip())
        cond_set(product, 'image_url',
                 sel.css('#imgTagWrapperId > img ::attr(data-old-hires)')
                 .extract())
        cond_set(product, 'title',
                 sel.css('#productTitle ::text').extract())

        # Some data is in a list (ul element).
        model = None
        for li in sel.css('td.bucket > .content > ul > li'):
            raw_keys = li.xpath('b/text()').extract()
            if not raw_keys:
                # This is something else, ignore.
                continue

            key = raw_keys[0].strip(' :').upper()
            if key == 'UPC':
                # Some products have several UPCs. The first one is used.
                raw_upc = li.xpath('text()').extract()[0]
                cond_set(product, 'upc', raw_upc.strip().split(' '),
                         lambda upcs: int(upcs[0]))
            elif key == 'ASIN' and model is None or key == 'ITEM MODEL NUMBER':
                model = li.xpath('text()').extract()
        if model is not None:
            cond_set(product, 'model', model)

    def _populate_from_js(self, url, sel, product):
        # Images are not always on the same spot...
        img_jsons = sel.css('#landingImage ::attr(data-a-dynamic-image)') \
            .extract()
        if img_jsons:
            imgs = json.loads(img_jsons[0])
            cond_set(product, 'image_url',
                     max(imgs.items(), key=lambda (_, size): size[0]),
                     lambda (url, _): url)

    def _scrape_total_matches(self, sel):
        # Where this value appears is a little weird and changes a bit so we
        # need two alternatives to capture it consistently.

        # The first possible place is where it normally is in a fully rendered
        # page.
        values = sel.css('#resultCount > span ::text').re(
            '\s+of\s+(\d+(,\d\d\d)*)\s+[Rr]esults')
        if not values:
            # Otherwise, it appears within a comment.
            values = sel.css('#result-count-only-next').xpath('comment()').re(
                '\s+of\s+(\d+(,\d\d\d)*)\s+[Rr]esults\s+')

        if values:
            return int(values[0].replace(',', ''))
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_product_links(self, sel):
        links = sel.css('.prod > h3 > a ::attr(href)').extract()
        if not links:
            self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, sel):
        next_pages = sel.css('#pagnNextLink ::attr(href)').extract()
        next_page_url = None
        if len(next_pages) == 1:
            next_page_url = next_pages[0]
        elif len(next_pages) > 1:
            self.log("Found more than one 'next page' link.", ERROR)
        return next_page_url

    ## Captcha handling functions.

    def _has_captcha(self, response):
        return '.images-amazon.com/captcha/' in response.body_as_unicode()

    def _solve_captcha(self, response):
        forms = Selector(response).xpath('//form')
        assert len(forms) == 1, "More than one form found."

        captcha_img = forms[0].xpath(
            '//img[contains(@src, "/captcha/")]/@src').extract()[0]

        self.log("Extracted capcha url: %s" % captcha_img, level=DEBUG)
        return self._cbw.solve_captcha(captcha_img)

    def _handle_captcha(self, response, callback):
        captcha_solve_try = response.meta.get('captcha_solve_try', 0)
        product = response.meta['product']

        self.log("Captcha challenge for %s (try %d)."
                 % (product.url, captcha_solve_try),
                 level=INFO)

        captcha = self._solve_captcha(response)

        if captcha is None:
            self.log("Failed to guess captcha for '%s' (try: %d)."
                     % (product.url, captcha_solve_try), level=ERROR)
        else:
            self.log("On try %d, submitting captcha '%s' for '%s'."
                     % (captcha_solve_try, captcha, captcha_img),
                     level=INFO)
            result = FormRequest.from_response(
                response,
                formname='',
                formdata={'field-keywords': captcha},
                callback=callback)
            result.meta['captcha_solve_try'] = captcha_solve_try + 1
            result.meta['product'] = product

        return result