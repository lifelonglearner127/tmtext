#!/usr/bin/python

import urllib
import re
import sys
import json
import os.path
from lxml import html
from lxml import etree

import time
import requests
from extract_data import Scraper

class KMartScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################
    table = None
    reviews = None
    price = None
    
    INVALID_URL_MESSAGE = "Expected URL format is http://www.kmart.com/.*"
    
    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^http://www.kmart.com/.*$", self.product_page_url)

        return not not m


    def _pre_scrape(self):
        try:
            table = "http://www.kmart.com/content/pdp/config/products/v1/products/%s?site=kmart"
            table = table%self._product_id()
            contents = requests.get(table).text
            table = json.loads(str(contents))
            self.table = table
        except Exception as e:
            print ("PreScrape Error - Table : ", e)

        try:
            reviews = "http://www.kmart.com/content/pdp/ratings/single/search/Kmart/%s&targetType=product&limit=10&offset=0"
            reviews = reviews%self._product_id()
            contents = requests.get(reviews).text
            reviews = json.loads(str(contents))
            self.reviews = reviews
        except Exception as e:
            print ("PreScrape Error - Reviews: ", e)

        try:
            price = "http://www.kmart.com/content/pdp/products/pricing/v1/get/price/display/json?pid=%s&pidType=0&priceMatch=Y&memberStatus=G&storeId=10151"
            price = price%self._product_id()[:-1]#There's a 'P' on the end that needs to come off
            contents = requests.get(price).text
            price = json.loads(str(contents))
            self.price = price
        except Exception as e:
            print ("PreScrape Error - Price: ", e)




    ##########################################
    ############### CONTAINER : NONE
    ##########################################
    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        #http://www.kmart.com/radar-rpx-800-p185-70r13-86t-bw-all/p-072W005512515001P?prdNo=2&blockNo=2&blockType=G2
        prod_id = re.findall(r'/\S-(\w+)\??\/?.*$', self.product_page_url)
        prod_id = str(prod_id[0])
        return prod_id

    def _site_id(self):
        return None

    def _status(self):
        return "success"







    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.table['data']['product']['name']

    def _product_title(self):
        return self.table['data']['seo']['title']

    def _title_seo(self):
        return self.table['data']['seo']['title']

    def _model(self):
        return self.table['data']['mfr']['modelNo']

    def _upc(self):
        return self.table['data']['identity']['ssin']

    def _features(self):
        xml = self.table['data']['product']['desc'][0]['val']
        xml = "<body>" + xml + "</body>"
        xml = etree.XML(xml)
        features = xml.xpath('.//ul/li/text()')
        return features

    def _feature_count(self):
        return len(self._features())

    def _model_meta(self):
        return None

    def _description(self):
        return None

    def _long_description(self):
        desc = self.table['data']['product']['desc'][1]['val']
        return desc


    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
        
    def _mobile_image_same(self):
        pass
    
    def _image_urls(self):
        imgs = self.table['data']['product']['assets']['imgs'][0]['vals']
        imgs = [x['src'] for x in imgs]
        return imgs
    
    def _image_count(self):
        return len(self._image_urls())

    def _video_urls(self):
        return None

    def _video_count(self):
        urls = self._video_urls()
        if urls is not None:
            return len(urls)
        return None

    def _pdf_urls(self):
        pdfs = self.table['data']['product']['assets']['attachments']
        pdfs = [x['link']['attrs']['href'] for x in pdfs]
        return pdfs

    def _pdf_count(self):
        urls = self._pdf_urls()
        return len(urls)

    def _webcollage(self):
        return None

    def _htags(self):
        htags_dict = {}
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    def _keywords(self):
        return None

    def _no_image(self):
        return None





    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    def _average_review(self):
        return self.reviews['data']['overall_rating']

    def _review_count(self):
        return self.reviews['data']['review_count']
 
    def _max_review(self):
        buckets = self.reviews['data']['overall_rating_breakdown']
        if self._review_count() == 0:
            return None
        max = 0
        for x in buckets:
            if(float(x['count'])>0 and float(x['name'])>max):
                max = float(x['name'])
        return max

    def _min_review(self):
        if self._review_count() == 0:
            return None
        buckets = self.reviews['data']['overall_rating_breakdown']
        min = 5
        for x in buckets:
            if(float(x['count'])>0 and float(x['name'])<min):
                min = float(x['name'])
        return min


    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        return self.price['priceDisplay']['response'][0]['finalPrice']['display']

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
    def _category_name(self):
        return self._categories()[0]
    
    def _categories(self):
        cat = self.table['data']['product']['taxonomy']['web']['sites']['kmart']['hierarchies'][0]['specificHierarchy']
        cat = [x['name'] for x in cat]
        return cat

    def _brand(self):
        return self.table['data']['product']['brand']['name']





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
        "upc" : _upc,\
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



