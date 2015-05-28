#!/usr/bin/python

import re
import lxml
import lxml.html
import requests
import urllib
import json
import ast

from itertools import groupby

from lxml import html, etree
from extract_data import Scraper


class AsdaScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.ulta.com/ulta/browse/productDetail.jsp?productId=<product-id>"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # product json
        self.product_json = None

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match(r"^http://groceries\.asda\.com/asda-webstore/landing/home\.shtml\?cmpid=ahc-_-ghs-d1-_"
                     r"-asdacom-dsk-_-hp/search/.+#/product/.+$", self.product_page_url)

        return not not m

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        self._product_json()

        if not self.product_json:
            return True

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################
    def _url(self):
        return self.product_page_url

    def _product_json(self):
        item_id_start_index = self.product_page_url.rfind("/", 0)
        item_id = self.product_page_url[item_id_start_index + 1:]
        product_json_url = "http://groceries.asda.com/api/items/view?itemid=" + item_id + \
                           "&responsegroup=extended&cacheable=true&storeid=4565&shipdate=currentDate&requestorigin=gi"

        contents = urllib.urlopen(product_json_url).read()

        try:
            self.product_json = json.loads(contents)
        except:
            self.product_json = None

    def _product_id(self):
        if not self.product_json:
            self._product_json()

        return self._product_json["items"][0]["cin"]

    def _item_id(self):
        item_id_start_index = self.product_page_url.rfind("/", 0)
        item_id = self.product_page_url[item_id_start_index + 1:]

        return item_id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        if not self.product_json:
            self._product_json()

        return self.product_json["items"][0]["name"]

    def _product_title(self):
        if not self.product_json:
            self._product_json()

        return self.product_json["items"][0]["name"]

    def _title_seo(self):
        if not self.product_json:
            self._product_json()

        return self.product_json["items"][0]["name"]

    def _model(self):
        return None

    def _features(self):
        if not self.product_json:
            self._product_json()

        if "nutritionalValues" not in self.product_json["items"][0]["productDetails"] or \
                len(self.product_json["items"][0]["productDetails"]["nutritionalValues"]) == 0:
            return None

        features_json = self.product_json["items"][0]["productDetails"]["nutritionalValues"]["values"]
        features_string_list = []

        for feature in features_json:
            features_string_list.append(feature["value1"] + " " + feature["value2"] + " " + feature["value3"])

        return features_string_list

    def _feature_count(self):
        features = self._features()

        if not features:
            return 0

        return len(features)

    def _description(self):
        if not self.product_json:
            self._product_json()

        return self.product_json["items"][0]["description"]

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description(self):
        long_description_url = "http://groceries.asda.com/asda-webstore/pages/product_details/view1.shtml?A521198.RWD"
        contents = urllib.urlopen(long_description_url).read()
        start_index = contents.find('<h4 class="sect-title">Product Information</h4><p class="p-text">')
        start_index += len('<h4 class="sect-title">Product Information</h4><p class="p-text">')
        end_index = contents.find("</p><% if(typeof ACCELERATOR.CONFIG.enableProductRatingReview")

        return contents[start_index:end_index]

    def _ingredients(self):
        if not self.product_json:
            self._product_json()

        ingredients = None

        if len(self.product_json["items"][0]["productDetails"]["ingredients"]) == 0:
            return None

        ingredients = self.product_json["items"][0]["productDetails"]["ingredients"][1:-1]

        ingredients = ingredients.split(",")

        return ingredients

    def _ingredients_count(self):
        if not self._ingredients():
            return 0

        return len(self._ingredients())

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        pass
        
    def _image_urls(self):
        if not self.product_json:
            self._product_json()

        image_urls = []
        image_urls.append(self.product_json["items"][0]["images"]["largeImage"])

        return image_urls

    def _image_count(self):
        if not self._image_urls():
            return 0

        return len(self._image_urls())

    def _video_urls(self):
        return None

    def _video_count(self):
        return 0

    # return dictionary with one element containing the PDF
    def _pdf_urls(self):
        return None

    def _pdf_count(self):
        return 0

    def _webcollage(self):
        return 0

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
        if not self.product_json:
            self._product_json()

        return int(self.product_json["items"][0]["totalReviewCount"])

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
        if not self.product_json:
            self._product_json()

        return self.product_json["items"][0]["price"]

    def _price_amount(self):
        if not self.product_json:
            self._product_json()

        return float(self.product_json["items"][0]["price"][1:])

    def _price_currency(self):
        currency = "GBP"

        return currency

    def _owned(self):
        return 0

    def _marketplace(self):
        return 0

    def _site_online(self):
        return 1

    def _site_online_only(self):
        return 0

    def _in_stores(self):
        return 1

    def _in_stores_only(self):
        return 0

    def _site_online_out_of_stock(self):
        return 0

    def _owned_out_of_stock(self):
        return 0

    def _marketplace_sellers(self):
        return None

    def _marketplace_out_of_stock(self):
        return 0

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################    
    def _categories(self):
        return None

    def _category_name(self):
        return None

    def _brand(self):
        if not self.product_json:
            self._product_json()

        return self.product_json["items"][0]["brandName"]

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    def _clean_text(self, text):
        return re.sub("&nbsp;", " ", text).strip()

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
        "title_seo" : _title_seo, \
        "model" : _model, \
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "long_description" : _long_description, \
        "ingredients": _ingredients, \
        "ingredient_count": _ingredients_count,

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
        "owned" : _owned, \
        "marketplace" : _marketplace, \
        "site_online": _site_online, \
        "site_online_out_of_stock": _site_online_out_of_stock, \
        "in_stores" : _in_stores, \
        "owned_out_of_stock": _owned_out_of_stock, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_out_of_stock": _marketplace_out_of_stock, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "mobile_image_same" : _mobile_image_same, \
    }
