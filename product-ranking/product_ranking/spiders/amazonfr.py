# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import re
from datetime import datetime

from product_ranking.amazon_tests import AmazonTests

from product_ranking.amazon_base_class import AmazonBaseClass
from product_ranking.validators.amazonfr_validator import AmazonfrValidatorSettings


is_empty = lambda x, y=None: x[0] if x else y


class AmazonProductsSpider(AmazonTests, AmazonBaseClass):
    name = 'amazonfr_products'
    allowed_domains = ["amazon.fr"]

    settings = AmazonfrValidatorSettings()

    SEARCH_URL = "http://www.amazon.fr/s/?field-keywords={search_term}"

    REVIEW_DATE_URL = "http://www.amazon.fr/product-reviews/" \
                      "{product_id}/ref=cm_cr_pr_top_recent?" \
                      "ie=UTF8&showViewpoints=0&" \
                      "sortBy=bySubmissionDateDescending"

    def __init__(self, *args, **kwargs):
        super(AmazonProductsSpider, self).__init__(*args, **kwargs)

        # Variables for total matches method (_scrape_total_matches)
        self.total_match_not_found = 'ne correspond à aucun article.'
        self.total_matches_re = r'sur\s?([\d,.\s?]+)'

        # Price currency
        self.price_currency = 'EUR'
        self.price_currency_view = 'EUR'

        # Locale
        self.locale = 'fr_FR'

    def _format_last_br_date(self, date):
        """
        Parses date that is gotten from HTML.
        """
        months = {'janvier': 'January',
                  u'f\xe9vrier': 'February',
                  'mars': 'March',
                  'avril': 'April',
                  'mai': 'May',
                  'juin': 'June',
                  'juillet': 'July',
                  u'ao\xfbt': 'August',
                  'septembre': 'September',
                  'octobre': 'October',
                  'novembre': 'November',
                  u'd\xe9cembre': 'December'
                  }

        date = self._is_empty(
            re.findall(
                r'le (\d+ .+ \d+)',
                date
            )
        )

        if date:
            for key in months.keys():
                if key in date:
                    date = date.replace(key, months[key])

            d = datetime.strptime(date, '%d %B %Y')

            return d

        return None
