# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
import re
import urlparse
from datetime import datetime

from scrapy.http import Request
from scrapy.log import ERROR
from scrapy.selector import Selector

from product_ranking.amazon_tests import AmazonTests
from product_ranking.amazon_base_class import AmazonBaseClass

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


class AmazonProductsSpider(AmazonTests, AmazonBaseClass):
    name = "amazoncouk_products"
    allowed_domains = ["www.amazon.co.uk"]

    settings = AmazoncoukValidatorSettings
    use_proxies = True
    handle_httpstatus_list = [502, 503, 504]

    def __init__(self, captcha_retries='20', *args, **kwargs):
        # locations = settings.get('AMAZONFRESH_LOCATION')
        # loc = locations.get(location, '')
        super(AmazonProductsSpider, self).__init__(*args, **kwargs)

        # String from html body that means there's no results ( "no results.", for example)
        self.total_match_not_found_re = 'did not match any products.'
        # Regexp for total matches to parse a number from html body
        self.total_matches_re = r'of\s?([\d,.\s?]+)'

        # Price currency
        self.price_currency = 'GBP'
        self.price_currency_view = '£'

        # Locale
        self.locale = 'en_GB'

        self.captcha_retries = int(captcha_retries)

    def _format_last_br_date(self, date):
        """
        Parses date that is gotten from HTML.
        """
        date = self._is_empty(
            re.findall(
                r'on (\d+ \w+ \d+)', date
            ), ''
        )

        if date:
            date = date.replace(',', '').replace('.', '')

            try:
                d = datetime.strptime(date, '%d %B %Y')
            except ValueError:
                d = datetime.strptime(date, '%d %b %Y')

            return d

        return None

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

    def parse_502(self, response):
        parts = urlparse.urlparse(response.url)
        if parts.port and parts.port != 80:
            self.log('Got status %s - retrying without port' % response.status)
            return Request(
                response.url.replace(':' + str(parts.port) + '/', '/')
            )

    def parse_503(self, response):
        return self.parse_502(response)

    def parse_504(self, response):
        return self.parse_502(response)
