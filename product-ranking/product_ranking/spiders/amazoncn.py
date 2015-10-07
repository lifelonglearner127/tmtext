# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
from datetime import datetime
import re

from product_ranking.amazon_tests import AmazonTests
from product_ranking.amazon_base_class import AmazonBaseClass


class AmazoncnValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
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
        'adfhsadifgewrtgujoc2': 0,
        'iphone duos': [5, 175],
        'gold shell': [50, 200],
        'Led Tv screen': [20, 200],
        'told help': [5, 150],
        'crawl': [50, 400],
        'sony playstation 4': [50, 200],
        'store data all': [20, 300],
        'iphone stone': [40, 250]
    }

class AmazonProductsSpider(AmazonTests, AmazonBaseClass):
    name = 'amazoncn_products'
    allowed_domains = ["amazon.cn"]

    settings = AmazoncnValidatorSettings()

    def __init__(self, *args, **kwargs):
        super(AmazonProductsSpider, self).__init__(*args, **kwargs)

        # String from html body that means there's no results ( "no results.", for example)
        self.total_match_not_found = '没有找到任何与'
        # Regexp for total matches to parse a number from html body
        self.total_matches_re = r'共\s?([\d,.\s?]+)'

        # Default price currency
        self.price_currency = 'CNY'
        self.price_currency_view = u'\uffe5'

        self.locale = 'zh_CN'

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
