# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
import re
from datetime import datetime
from scrapy.log import ERROR

from product_ranking.amazon_tests import AmazonTests
from product_ranking.amazon_base_class import AmazonBaseClass
from product_ranking.validators.amazonde_validator import AmazonDeValidatorSettings


class AmazonProductsSpider(AmazonTests, AmazonBaseClass):
    name = 'amazonde_products'
    allowed_domains = ["amazon.de"]

    settings = AmazonDeValidatorSettings

    use_proxies = False

    handle_httpstatus_list = [502, 503, 504]

    def __init__(self, captcha_retries='20', *args, **kwargs):
        super(AmazonProductsSpider, self).__init__(*args, **kwargs)

        self.captcha_retries = int(captcha_retries)

        # String from html body that means there's no results ( "no results.", for example)
        self.total_match_not_found_re = 'ergab leider keine Produkttreffer.'
        # Regexp for total matches to parse a number from html body
        self.total_matches_re = r'von ((?:\d+.?)+) Ergebnissen'

        # Price currency
        self.price_currency = 'EUR'
        self.price_currency_view = 'EUR'

        # Locale
        self.locale = 'de_DE'

    def _format_last_br_date(self, date):
        """
        Parses date that is gotten from HTML.
        """
        months = {'Januar': 'January',
                  'Februar': 'February',
                  u'M\xe4rz': 'March',
                  'Mai': 'May',
                  'Juni': 'June',
                  'Juli': 'July',
                  'Oktober': 'October',
                  'Dezember': 'December'
                  }

        date = self._is_empty(
            re.findall(
                r'am (\d+. \w+ \d+)', date
            ), ''
        )

        if date:
            for key in months.keys():
                if key in date:
                    date = date.replace(key, months[key])
            try:
                d = datetime.strptime(date.replace('.', ''), '%d %B %Y')
                return d
            except ValueError as exc:
                self.log(
                    'Unable to parse last buyer review date: {exc}'.format(
                        exc=exc
                    ),
                    ERROR
                )

        return None

