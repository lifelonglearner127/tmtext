#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, json, requests
from lxml import html

from extract_data import Scraper
from spiders_shared_code.jet_variants import JetVariants


class JetScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = 'Expected URL format is https?://(www.)?jet.com/<product-name>/<product-id>'

    API_URL = 'https://jet.com/api/product/v2'

    def __init__(self, **kwargs):
        Scraper.__init__(self, **kwargs)

        self.response = None
        self.product_data = None
        self.jv = JetVariants()

    def _extract_page_tree(self):
        for i in range(self.MAX_RETRIES):
            try:
                s = requests.session()

                self.page_raw_text = s.get(self.product_page_url).content
                self.tree_html = html.fromstring(self.page_raw_text)

                csrf_token = self.tree_html.xpath('//*[@data-id="csrf"]/@data-val')[0]
                csrf_token = csrf_token.replace('"','')

                headers = {'X-Requested-With': 'XMLHttpRequest',
                    'content-type': 'application/json',
                    'x-csrf-token': csrf_token}

                body = json.dumps({"sku": self._product_id(), "origination": "none"})

                self.product_data = s.post(self.API_URL, headers=headers, data=body).content

                self.jv.setupCH(self.product_data)

                self.product_data = json.loads(self.product_data)['result']

            except Exception as e:
                print e

    def check_url_format(self):
        m = re.match('^https?://(www\.)?jet\.com/product/.+/.+$', self.product_page_url, re.U)
        return bool(m)

    def not_a_product(self):
        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################
    def _product_id(self):
        return re.search('([^/]+)$', self._url()).group(1)

    def _url(self):
        return self.product_page_url

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.product_data['title']

    def _product_title(self):
        return self._product_name()

    def _model(self):
        return self.product_data['part_no']

    def _upc(self):
        return self.product_data['upc']

    def _description(self):
        return self.product_data['description']

    def _long_description(self):
        if self.product_data['bullets']:
            long_description = '<ul>'

            for bullet in self.product_data['bullets']:
                long_description += '<li>' + bullet + '</li>'

            return long_description + '</ul>'

    def _specs(self):
        specs = {}

        for attribute in self.product_data['attributes']:
            if attribute['display']:
                specs[attribute['name']] = attribute['value']

        if specs:
            return specs

    def _variants(self):
        return self.jv._variants_v2()

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################

    def _image_urls(self):
        return map(lambda i: i['raw'], self.product_data['images'])

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
        return self.product_data['productPrice']['referencePrice']

    def _price_currency(self):
        return 'USD'

    def _temp_price_cut(self):
        if self.product_data['productPrice']['listPrice'] == 0:
            return 0
        return 1

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):
        if not self.product_data['display']:
            return 1

        if self._site_online() == 0:
            return None

        in_stock = self.tree_html.xpath('//div[contains(@class, "were_sorry")]//text()')
        in_stock = " ".join(in_stock)
        if 'this item is unavailable right now' in in_stock.lower():
            return 1

        return 0

    def _web_only(self):
        return 1

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        return self.product_data['categoryPath'].split('|')

    def _category_name(self):
        return self._categories()[0]

    def _brand(self):
        return self.product_data['manufacturer']

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
        "product_title" : _product_title, \
        "model" : _model, \
        "upc" : _upc, \
        "description" : _description, \
        "long_description" : _long_description, \
        "specs" : _specs, \
        "variants" : _variants, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \

        # CONTAINER : REVIEWS

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "temp_price_cut" : _temp_price_cut, \
        "site_online" : _site_online, \
        "site_online_out_of_stock" : _site_online_out_of_stock, \
        "web_only" : _web_only, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
    }
