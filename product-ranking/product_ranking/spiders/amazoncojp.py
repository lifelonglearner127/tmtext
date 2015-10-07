# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
import re
from datetime import datetime

from product_ranking.amazon_tests import AmazonTests
from product_ranking.amazon_base_class import AmazonBaseClass


class AmazoncojpValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
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
        'alhpa beta vinigretto': 0,
        'dandy united': [30, 300],
        'magi yellow': [5, 150],
        'Led Tv screen': [40, 300],
        'red ship coat': [10, 150],
        'trash smash': [20, 250],
        'all for PC now': [15, 150],
        'iphone blast': [10, 200],
        'genius electronics black': [5, 120],
        'batteries 330v': [40, 270]
    }

class AmazonProductsSpider(AmazonTests, AmazonBaseClass):
    name = 'amazonjp_products'
    allowed_domains = ["amazon.co.jp"]

    settings = AmazoncojpValidatorSettings()

    def __init__(self, *args, **kwargs):
        super(AmazonProductsSpider, self).__init__(*args, **kwargs)

        # Variables for total matches method (_scrape_total_matches)
        self.total_match_not_found = '検索に一致する商品はありませんでした'
        self.total_matches_re = r'検索結果\s?([\d,.\s?]+)'

        # Price currency
        self.price_currency = 'JPY'
        self.price_currency_view = '￥'

        self.locale = 'ja_JP'

    def _format_last_br_date(self, date):
        """
        Parses date that is gotten from HTML.
        """
        date = re.findall(
            r'(\d+)',
            date
        )

        if date:
            date = ' '.join(date)
            d = datetime.strptime(date, '%Y %m %d')
            return d

        return None
