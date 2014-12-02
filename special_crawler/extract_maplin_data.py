#!/usr/bin/python

import urllib
import re
import sys
import json
import os.path
import urllib, cStringIO
from io import BytesIO
from PIL import Image
import mmh3 as MurmurHash
from lxml import html
from lxml import etree
import time
import requests
from extract_data import Scraper


class MaplinScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.maplin.co.uk/p/<product-id>"

    def check_url_format(self):
        #for ex: http://www.maplin.co.uk/p/black-heated-socks-1-pair-n57ds
        m = re.match(r"^http://www\.maplin\.co\.uk/p/([a-zA-Z0-9\-]+)?$", self.product_page_url)
        return not not m

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        product_id = self.product_page_url.split('/')[-1]
        return product_id

    def _site_id(self):
        return None

    def _status(self):
        return 'success'

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//h1[@itemprop='name']")[0].text

    def _product_title(self):
        return self.tree_html.xpath("//h1[@itemprop='name']//text()").strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()
    
    def _model(self):
        return None

    def _upc(self):
        return self.tree_html.xpath("//span[@itemprop='sku']//text()")[0].strip()

    def _features(self):
        rows = self.tree_html.xpath("//table[@class='product-specs']//tr")
        
        # list of lists of cells (by rows)
        cells = map(lambda row: row.xpath(".//*//text()"), rows)
        # list of text in each row
        cells = cells[1:]
        rows_text = map(\
            lambda row: ":".join(\
                map(lambda cell: cell.strip(), row)\
                ), \
            cells)
        all_features_text = "\n".join(rows_text)

        # return dict with all features info
        return all_features_text

    def _feature_count(self):
        rows = self.tree_html.xpath("//table[@class='product-specs']//tr")
        cells = map(lambda row: row.xpath(".//*//text()"), rows)
        # list of text in each row
        return len(cells) - 1

    def _model_meta(self):
        return None

    def _description(self):
        description = "\n".join(self.tree_html.xpath("//div[@class='product-summary']//ul[1]//li//text()")).strip()
        return description

    def _long_description(self):
        d1 = self._description()
        d2 = self._long_description_temp()

        if d1 == d2:
            return None
        return d2

    def _long_description_temp(self):
        long_description = self.tree_html.xpath("//div[@class='productDescription']//text()")[0].strip()
        return long_description

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_url = self.tree_html.xpath("//ul[@id='carousel_alternate']//img/@src")
        return image_url

    def _image_count(self):
        image_urls = self._image_urls()
        return len(image_urls)

    def _video_urls(self):
        return None

    def _video_count(self):
        urls = self._video_urls()
        if urls:
            return len(urls)
        return 0

    def _pdf_helper(self):
        pdfs = self.tree_html.xpath("//a[@title='Terms & Conditions']/@href")
        self.pdfs = map(lambda pdf: "http://www.maplin.co.uk%s" % pdf, pdfs)
        return self.pdfs

    def _pdf_urls(self):
        return self._pdf_helper()

    def _pdf_count(self):
        urls = self._pdf_helper()
        if urls is not None:
            return len(urls)
        return 0

    def _webcollage(self):
        return 0

    # extract htags (h1, h2) from its product product page tree
    def _htags(self):
        htags_dict = {}
        # add h1 tags text to the list corresponding to the "h1" key in the dict
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        # add h2 tags text to the list corresponding to the "h2" key in the dict
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    def _keywords(self):
        return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]

    # return True if there is a no-image image and False otherwise
    # Certain products have an image that indicates "there is no image available"
    # a hash of these "no-images" is saved to a json file and new images are compared to see if they're the same
    def _no_image(self):
        return None

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    def _average_review(self):
        average_review = self.tree_html.xpath("//span[@itemprop='ratingValue']//text()")[0].strip()
        return average_review

    def _review_count(self):
        try:
            review_count = self.tree_html.xpath("//span[@itemprop='ratingCount']//text()")[0].strip()
            return review_count
        except IndexError:
            return 0

    def _max_review(self):
        average_review = self.tree_html.xpath("//span[@itemprop='bestRating']//text()")[0].strip()
        return average_review

    def _min_review(self):
        return None

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        price = self.tree_html.xpath("//meta[@itemprop='price']/@content")[0].strip()
        currency = self.tree_html.xpath("//meta[@itemprop='priceCurrency']/@content")[0].strip()
        if price and currency:
            return "%s %s" % (currency, price)
        else:
            return None

    def _in_stores_only(self):
        return None

    def _in_stores(self):
        return None

    def _owned(self):
        return 1
    
    def _marketplace(self):
        return 0

    def _owned_out_of_stock(self):
        return None

    def _marketplace_sellers(self):
        return None

    def _marketplace_lowest_price(self):
        return None

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        all = self.tree_html.xpath("//ul[contains(@class, 'breadcrumb')]//li//span/text()")
        out = all[1:-1]#the last value is the product itself, and the first value is "home"
        out = [self._clean_text(r) for r in out]
        #out = out[::-1]
        return out

    def _category_name(self):
        return self._categories()[-1]

    def load_universal_variable(self):
        js_content = ' '.join(self.tree_html.xpath('//script//text()'))

        universal_variable = {}
        universal_variable["manufacturer"] = re.findall(r'"manufacturer": "(.*?)"', js_content)[0]
        return universal_variable

    def _brand(self):
        return self.load_universal_variable()["manufacturer"]

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces
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
        "event" : _event, \
        "product_id" : _product_id, \
        "site_id" : _site_id, \
        "status" : _status, \

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "upc" : _upc,\
        "features" : _features, \
        "feature_count" : _feature_count, \
        "model_meta" : _model_meta, \
        "description" : _description, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "keywords" : _keywords, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "in_stores_only" : _in_stores_only, \
        "in_stores" : _in_stores, \
        "owned" : _owned, \
        "owned_out_of_stock" : _owned_out_of_stock, \
        "marketplace": _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \

        "loaded_in_seconds": None \
        }


    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        # CONTAINER : PAGE_ATTRIBUTES
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "mobile_image_same" : _mobile_image_same, \
        "no_image" : _no_image,\

        # CONTAINER : PRODUCT_INFO
        "model" : _model, \
        "long_description" : _long_description, \

        # CONTAINER : REVIEWS
        "average_review" : _average_review, \
        "review_count" : _review_count, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \

        # CONTAINER : CLASSIFICATION
        "brand" : _brand, \
    }

