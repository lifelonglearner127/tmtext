import json
import re

import scrapy.log
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.spider import Spider

from tesco_crawler.items import BazaarVoiceReviewsItem


class TescoReviewSpider(Spider):
    name = 'tesco_review'
    allowed_domains = ["tesco.com", "display.bazaarvoice.com"]
    start_urls = []

    _BV_TESCO_API_CONF_URL = \
        "http://display.bazaarvoice.com/static/Tesco/bvapi.js"

    _EXTRACT_REVIEWS_URL_RE = re.compile(
        r'prefetchConfigs:\s*\[\s*\{\s*url\s*:\s*"//([^"]+)', re.MULTILINE)

    def __init__(self, start_url=None, start_urls_fn=None):
        if start_url is not None:
            self.start_urls = [start_url]

        if start_urls_fn is not None:
            with open(start_urls_fn) as start_urls_f:
                self.start_urls = [url.strip() for url in start_urls_f]

        scrapy.log.msg("Created with urls: " + ', '.join(self.start_urls),
                       scrapy.log.INFO)

    def parse(self, response):
        sel = Selector(response)

        # Scrape BV configuration.
        prod_id, = sel.css('.details-container > script').re(
            r"productID\s*=\s*'([\d\w-]+)'")
        scrapy.log.msg("Processing product '%s'." % prod_id,
                       scrapy.log.INFO)

        r = Request(self._BV_TESCO_API_CONF_URL,
                    callback=self.parse_bv_conf)
        r.meta['product_id'] = prod_id
        return r

    def parse_bv_conf(self, response):
        prod_id = response.meta['product_id']

        # Parse review URL.
        m = self._EXTRACT_REVIEWS_URL_RE.search(response.body)
        if m is None:
            scrapy.log.msg(
                "Failed to parse URL from tesco.com's BV config URL for "
                "product '%s'." % prod_id,
                scrapy.log.ERROR)
            req = None
        else:
            scrapy.log.msg("Found config for product '%s'." % prod_id,
                           scrapy.log.INFO)

            url_template, = m.groups()
            url = 'http://' \
                + url_template.replace('___PRODUCTIDTOKEN___', prod_id)

            req = Request(url, callback=self.parse_bv)
        return req

    def parse_bv(self, response):
        """Parses a BazaarVoice Json response."""
        review = BazaarVoiceReviewsItem()
        review.bv_client = "tesco"
        responses = json.loads(response.body)
        review.data = responses['BatchedResults']['q1']['Includes']

        scrapy.log.msg("Got reviews for products: %s" % ', '.join(
            review.data['Products'].keys()),
            scrapy.log.INFO)

        return review
