# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
from datetime import datetime
import re

from product_ranking.amazon_tests import AmazonTests
from product_ranking.amazon_base_class import AmazonBaseClass
from product_ranking.validators.amazoncn_validator import AmazoncnValidatorSettings


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
