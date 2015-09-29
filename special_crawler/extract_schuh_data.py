#!/usr/bin/python

import urllib
import re
import sys
import json

from lxml import html, etree
import time
import requests
from extract_data import Scraper

class SchuhScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.schuh.co.uk/p/<product-name>/<product-id>"

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^http://www.schuh.co.uk/.*?$", self.product_page_url)
        return not not m

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        try:
            itemtype = self.tree_html.xpath("//div[@itemtype='http://schema.org/Product']")

            if not itemtype:
                raise Exception()

        except Exception:
            return True

        return False

    def _find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _canonical_link(self):
        canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")
        return canonical_link

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        product_id = self.tree_html.xpath("//span[@itemprop='sku']/text()")[0]
        return product_id

    def _site_id(self):
        return None

    def _status(self):
        return "success"

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################

    def _product_name(self):
        return self.tree_html.xpath('//link[@rel="alternate"]/@title')[0]

    def _product_title(self):
        return self.tree_html.xpath('//link[@rel="alternate"]/@title')[0]

    def _features(self):
        features = self.tree_html.xpath('//div[@itemprop="description"]/ul/li/text()')
        features_list = []

        for i in features:
            features_list.append(i)

        if features_list:
            return features_list

    def _feature_count(self):
        if self._features():
            return len(self._features())

        return None

    def _description(self):
        desc = self.tree_html.xpath("//div[@itemprop='description']/text()")
        short_description = desc[0].strip()
        return short_description

    def _long_description(self):
        desc = self.tree_html.xpath("//div[@itemprop='description']")[0]
        long_description = ""
        long_description_start = False

        for description_item in desc:
            if description_item.tag == "ul":
                long_description_start = True

            if long_description_start:
                long_description = long_description + html.tostring(description_item)

        long_description = long_description.strip()

        if long_description:
            return long_description

        return None

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################

    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        images = self.tree_html.xpath('//div[@id="swipe"]//ul/li/img/@data-mob-src')
        image_list = []

        first_img = self.tree_html.xpath('//div[@id="swipe"]//ul/li/span/img/@data-mob-src')[0]
        image_list.append(first_img)

        for media_item in images:
            image_list.append(media_item)

        if image_list:
            return image_list

        return None

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def _keywords(self):
        return self.tree_html.xpath('//meta[@id="metaKeywords"]/@content')[0]

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################

    def _average_review(self):
        average_review = self.tree_html.xpath('//meta[@itemprop="ratingValue"]/@content')[0]
        assessment = float(average_review)
        if assessment:
            return assessment

    def _review_count(self):
        count = self.tree_html.xpath('//div[@id="itemRating"]/a/text()')[1]
        count_int = re.search('\d+', count)

        if count_int:
            return int(count_int.group(0))

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################

    def _price(self):
        return self.tree_html.xpath('//span[@id="price"]/text()')[0]

    def _price_amount(self):
        price = self.tree_html.xpath('//span[@id="price"]/text()')[0]
        price_int = re.search('\d{1,}.\d{2}', price)
        return float(price_int.group(0))

    def _price_currency(self):
        return "EUR"

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################

    def _brand(self):
        brands = self.tree_html.xpath('//span[@id="itemLogo"]//img/@title')
        brand = brands[0].replace('logo', '')
        return brand.strip()

    ##########################################
    ################ RETURN TYPES
    ##########################################

    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service

    DATA_TYPES = {
        # CONTAINER : NONE
        "url" : _url, \
        "product_id" : _product_id, \
        "site_id" : _site_id, \
        "status" : _status, \

        # CONTAINER : PRODUCT_INFO
        'product_name' : _product_name, \
        "product_title" : _product_title, \
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "long_description" : _long_description, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count, \
        "image_urls" : _image_urls, \
        "keywords" : _keywords, \
        "canonical_link" : _canonical_link, \

        # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \

        # CONTAINER : CLASSIFICATION
        "brand" : _brand, \
    }
