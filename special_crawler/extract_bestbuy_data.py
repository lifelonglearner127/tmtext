#!/usr/bin/python

import urllib
import re
import sys
import json
import os.path
from lxml import html
import time
import requests
from extract_data import Scraper

class BestBuyScraper(Scraper):
    
    ##########################################
    ############### PREP
    ##########################################
    INVALID_URL_MESSAGE = "Expected URL format is http://www.bestbuy.com/site/<product-name>/<product-id>.*"
    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
        True if valid, False otherwise
        """
        m = re.match(r"^http://www.bestbuy.com/.*$", self.product_page_url)
        return not not m




    ##########################################
    ############### CONTAINER : NONE
    ##########################################
    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        prod_id = self.tree_html.xpath('//div[@id="pdp-model-data"]/@data-product-id')[0]
        return prod_id

    def _site_id(self):
        return None

    def _status(self):
        return "success"




    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//meta[@itemprop="name"]/@content')[0]
    
    def _product_title(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _model(self):
        return self.tree_html.xpath('//span[@id="model-value"]/text()')[0]

    def _upc(self):
        return self.tree_html.xpath('//div[@id="pdp-model-data"]/@data-sku-id')[0]

    def _features(self):
        rows = self.tree_html.xpath("//div[@id='features']")
        # list of lists of cells (by rows)
        cells = map(lambda row: row.xpath(".//div[@class='feature']//text()"), rows)
        # list of text in each row
        rows_text = map(\
            lambda row: ":".join(\
                map(lambda cell: cell.strip(), row)\
                ), \
            cells)
        all_features_text = "\n".join(rows_text)
        # return dict with all features info
        return all_features_text

    def _feature_count(self):
        # select table rows with more than 2 cells (the others are just headers), count them
        return len(filter(lambda row: len(row.xpath(".//text()"))>0, self.tree_html.xpath("//div[@id='features']/div[@class='feature']")))

    def _model_meta(self):
        return None

    def _description(self):
        return None

    def _long_description(self):
        full_description = self.tree_html.xpath('//div[@id="long-description"]//text()')[0]
        return full_description




    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_url = self.tree_html.xpath('//div[@id="pdp-model-data"]/@data-gallery-images')[0]
        json_list = json.loads(image_url)
        image_url = []
        for i in json_list:
            image_url.append(i['url'])
        return image_url
    
    def _image_count(self):
        return len(self._image_urls())

    def _video_urls(self):
        video_url = "\n".join(self.tree_html.xpath("//script//text()"))
        video_url = re.sub(r"\\", "", video_url)
        video_url = re.findall("url.+(http.+flv)\"", video_url)
        return video_url

    def _video_count(self):
        return len(self._video_urls())

    def _pdf_urls(self):
        return None
    
    def _pdf_count(self):
        pdf = self._pdf_urls()
        if pdf is not None:
            return len(pdf)
        return None

    def _webcollage(self):
        return None

    def _htags(self):
        htags_dict = {}
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    def _keywords(self):
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0]

    # extracts whether the first product image is the "no-image" picture
    def _no_image(self):
        None






    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    def reviews_for_url(self):
        return self.tree_html.xpath('//span[@itemprop="ratingValue"]//text()')[0]

    def nr_reviews(self):
        return self.tree_html.xpath('//meta[@itemprop="reviewCount"]/@content')[0]
 
    def _max_review(self):
        return None

    def _min_review(self):
        return None





    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        meta_price = self.tree_html.xpath('//meta[@itemprop="price"]//@content')
        if meta_price:
            return meta_price[0].strip()
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

    def _seller_from_tree(self):
        return None
    
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
        all = self.tree_html.xpath("//ul[@id='breadcrumb-list']/li/a/text()")
        return all

    def _category_name(self):
        dept = " ".join(self.tree_html.xpath("//ul[@id='breadcrumb-list']/li[1]/a/text()")).strip()
        return dept
    
   def _brand(self):
        return self.tree_html.xpath('//meta[@id="schemaorg-brand-name"]/@content')[0]
    



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
        "event" : _event, \
        "product_id" : _product_id, \
        "site_id" : _site_id, \
        "status" : _status, \

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "model" : _model, \
        "upc" : _asin,\
        "features" : _features, \
        "feature_count" : _feature_count, \
        "model_meta" : _model_meta, \
        "description" : _description, \
        "long_description" : _long_description, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
        "no_image" : _no_image, \
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

        # CONTAINER : SELLERS
        "price" : _price, \
        "in_stores_only" : _in_stores_only, \
        "in_stores" : _in_stores, \
        "owned" : _owned, \
        "owned_out_of_stock" : _owned_out_of_stock, \
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



