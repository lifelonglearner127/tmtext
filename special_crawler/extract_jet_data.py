#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, json
from lxml import html
from extract_data import Scraper

class JetScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = 'Expected URL format is https?://www.jet.com/<product-name>/<product-id>'

    def __init__(self, **kwargs):
        Scraper.__init__(self, **kwargs)

        self.product_data = None
        self.product_data_checked = False

    def check_url_format(self):
        m = re.match(r'^https?://www\.jet\.com/product/.+/.+$', self.product_page_url, re.U)
        return bool(m)

    def not_a_product(self):
        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################
    def _product_id(self):
        return re.match('.*skuId=(\d+)', self._url()).group(1)

    def _url(self):
        return self.product_page_url

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_data(self):
        if not self.product_data_checked:
            self.product_data_checked = True

            self.product_data = json.loads( self.load_page_from_url_with_number_of_retries('https://grocery-api.walmart.com/v0.1/api/stores/5260/products/' + self._product_id()))

        return self.product_data

    def _product_name(self):
        return self._product_data()['data']['name']

    def _model(self):
        return self._product_data()['data']['modelNum']

    def _description(self):
        return self._product_data()['data']['description']

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################

    def _image_urls(self):
        return [self._product_data()['data']['images']['large']]

    def _image_count(self):
        images = self._image_urls()
        return len(images) if images else 0

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        return '$' + str(self._price_amount())

    def _price_amount(self):
        return self._product_data()['price']['list']

    def _price_currency(self):
        return 'USD'

    def _in_stock(self):
        if self._product_data()['data']['isOutOfStock']:
            return 0
        return 1

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################

    ##########################################
    ################ RETURN TYPES
    ##########################################

    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service

    DATA_TYPES = { \
        # CONTAINER : NONE
        "url" : _url, \
        "product_id" : _product_id, \

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "description" : _description, \
        "model": _model, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \

        # CONTAINER : REVIEWS

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \

        # CONTAINER : CLASSIFICATION
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
    }
