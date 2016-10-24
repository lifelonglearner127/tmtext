# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
from datetime import datetime
import re

from product_ranking.amazon_tests import AmazonTests
from product_ranking.amazon_base_class import AmazonBaseClass
from product_ranking.validators.amazonca_validator import AmazoncaValidatorSettings


class AmazonProductsSpider(AmazonTests, AmazonBaseClass):
    name = 'amazonca_products'
    allowed_domains = ["amazon.ca", "amazon.com"]

    settings = AmazoncaValidatorSettings

    def __init__(self, *args, **kwargs):
        super(AmazonProductsSpider, self).__init__(*args, **kwargs)

        # String from html body that means there's no results ( "no results.", for example)
        self.total_match_not_found_re = 'did not match any products.'
        # Regexp for total matches to parse a number from html body
        self.total_matches_re = r'of\s?([\d,.\s?]+)'

        # Default price currency
        self.price_currency = 'CAD'
        self.price_currency_view = '$'

        # Locale
        self.locale = 'en_CA'

    def _format_last_br_date(self, date):
        """
        Parses date that is gotten from HTML.
        """
        date = self._is_empty(
            re.findall(
                r'on (\w+ \d+, \d+)', date
            ), ''
        )

        if date:
            date = date.replace(',', '').replace('.', '')

            try:
                d = datetime.strptime(date, '%B %d %Y')
            except ValueError:
                d = datetime.strptime(date, '%b %d %Y')

            return d

        return None
