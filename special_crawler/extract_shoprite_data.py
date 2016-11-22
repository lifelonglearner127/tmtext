#!/usr/bin/python

import os
import re
import uuid
import requests
import json
from extract_data import Scraper


class ShopriteScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is https://shop.shoprite.com/store/<store-id>#/product/sku/<product-id>"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.product_json = None

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^https://shop.shoprite.com/store/.*?$", self.product_page_url)
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
            token_string = self._find_between(self.page_raw_text, '{"Token":"', '",')
            store_id = self._find_between(self.product_page_url, "shop.shoprite.com/store/", "#/product/sku/")
            product_id = self.product_page_url.split("/")[-1]
            headers = {'Authorization': token_string,
                       'Accept-Encoding': 'gzip, deflate, sdch, br',
                       'Accept-Language': 'en-US',
                       'User-Agent': self.select_browser_agents_randomly(),
                       'Accept': 'application/vnd.mywebgrocer.product+json',
                       'Cache-Control': 'max-age=0',
                       'X-Requested-With': 'XMLHttpRequest',
                       'Referer': 'https://shop.shoprite.com/store/{0}'.format(product_id)}

            response_text = requests.get('https://shop.shoprite.com/api/product/v5/product/store/{0}/sku/{1}'.
                                         format(store_id, product_id), headers=headers).text

            self.product_json = json.loads(response_text)
        except Exception as e:
            print e
            return True

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _canonical_link(self):
        return None

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        return self.product_json["Sku"]

    def _site_id(self):
        return None

    def _status(self):
        return "success"

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.product_json["Name"]

    def _product_title(self):
        return self.product_json["Name"]

    def _title_seo(self):
        return self.product_json["Name"]

    def _model(self):
        return None

    def _upc(self):
        return self.product_json["Sku"]

    def _features(self):
        return None

    def _feature_count(self):
        if self._features():
            return len(self._features())

        return None

    def _model_meta(self):
        return None

    def _description(self):
        return self.product_json["Description"] if self.product_json["Description"] else None

    def _long_description(self):
        long_description_string = ""

        for label in self.product_json["Labels"]:
            if not label["Description"] or label["Title"] == 'No additional information available for this product':
                continue

            long_description_string += "<li>"
            long_description_string += ("<h4>" + label["Title"] + "</h4>")
            long_description_string += ("<span>" + label["Description"] + "</span>")
            long_description_string += "</li>"

        long_description_string = long_description_string.strip()

        return long_description_string if long_description_string else None

    def _swatches(self):
        return None

    def _variants(self):
        return None

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        for image_info in self.product_json["ImageLinks"]:
            if image_info["Rel"] == "large":
                return [image_info["Uri"]]

        return None

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def _video_urls(self):
        return None

    def _video_count(self):
        videos = self._video_urls()

        return len(videos) if videos else 0

    def _pdf_urls(self):
        return None

    def _pdf_count(self):
        if self._pdf_urls():
            return len(self._pdf_urls())

        return 0

    def _webcollage(self):
        return None

    def _htags(self):
        return None

    def _keywords(self):
        return None
    
    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################

    def _average_review(self):
        return None

    def _review_count(self):
        return 0

    def _max_review(self):
        return None

    def _min_review(self):
        return None

    def _reviews(self):
        return None

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        return self.product_json["CurrentPrice"]

    def _price_amount(self):
        return float(self._price()[1:])

    def _price_currency(self):
        return "USD"

    def _in_stores(self):
        return 1

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):
        return 1 if self.product_json["InStock"] else 0

    def _in_stores_out_of_stock(self):
        return 1 if self.product_json["InStock"] else 0

    def _marketplace(self):
        return 0

    def _seller_from_tree(self):
        return None

    def _marketplace_sellers(self):
        return None

    def _marketplace_lowest_price(self):
        return None

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        return [self.product_json["Category"]]

    def _category_name(self):
        return self._categories()[-1]
    
    def _brand(self):
        return self.product_json["Brand"]


    ##########################################
    ################ RETURN TYPES
    ##########################################

    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service

    DATA_TYPES = { \
        # CONTAINER : NONE
        "url" : _url, \
        "event" : _event, \
        "product_id" : _product_id, \
        "site_id" : _site_id, \
        "status" : _status, \

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "model" : _model, \
        "upc" : _upc,\
        "features" : _features, \
        "feature_count" : _feature_count, \
        "model_meta" : _model_meta, \
        "description" : _description, \
        "long_description" : _long_description, \
        "swatches" : _swatches, \
        "variants" : _variants, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
        "pdf_count" : _pdf_count, \
        "pdf_urls" : _pdf_urls, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "canonical_link": _canonical_link,

        # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "in_stores" : _in_stores, \
        "site_online": _site_online, \
        "site_online_out_of_stock": _site_online_out_of_stock, \
        "in_stores_out_of_stock": _in_stores_out_of_stock, \
        "marketplace" : _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \

        "loaded_in_seconds" : None, \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "mobile_image_same" : _mobile_image_same, \
    }
