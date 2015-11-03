# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import json
import re
import string
import urlparse
from datetime import datetime

from scrapy.http import Request
from scrapy.http.request.form import FormRequest
from scrapy.log import msg, ERROR, WARNING, INFO, DEBUG

from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set,\
    cond_set_value, FLOATING_POINT_RGEX
from product_ranking.amazon_tests import AmazonTests

from product_ranking.amazon_bestsellers import amazon_parse_department

from product_ranking.amazon_base_class import AmazonBaseClass

is_empty = lambda x, y=None: x[0] if x else y


class AmazonfrValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
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
        'nothing_found_1234654654': 0,
        'samsung t9500 battery 2600 li-ion warranty': [5, 175],
        'water pump mini': [5, 150],
        'ceiling fan industrial white system': [5, 50],
        'kaspersky total': [5, 75],
        'car navigator garmin maps 44LM': [1, 30],
        'yamaha drums midi': [1, 300],
        'black men shoes size 8 red': [20, 200],
        'car audio equalizer': [5, 150]
    }

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
