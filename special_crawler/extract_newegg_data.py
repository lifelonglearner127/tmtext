#!/usr/bin/python

import urllib
import re
import sys
import json

from lxml import html, etree
import time
import requests
from extract_data import Scraper


class NeweggScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.newegg.com/Product/Product.aspx?Item=<product-id>"
    REVIEW_URL = "http://www.newegg.com/Product/Product.aspx?Item=[a-zA-Z0-9]+"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        self.hdGroupItemModelString_json = None
        self.hdGroupItemsString_json = None
        self.related_item_id = None
        self.imgGalleryConfig_json = None
        self.overviewData_json = None
        self.review_json = None
        self.review_list = None
        self.is_review_checked = False

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^http://www\.newegg\.com/Product/Product\.aspx\?Item=[a-zA-Z0-9]+$", self.product_page_url)
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
            if not self.tree_html.xpath('//div[@itemtype="http://schema.org/Product"]'):
                raise Exception()
        except Exception:
            return True

        self._extract_product_json()

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _extract_product_json(self):
        try:
            self.hdGroupItemModelString_json = json.loads(self._find_between(html.tostring(self.tree_html), "var hdGroupItemModelString = ", ";\r"))

            for item in self.hdGroupItemModelString_json:
                if item["SellerItem"] == self._product_id():
                    self.related_item_id = item["ParentItem"]
                    break
        except:
            print "Issue(Newegg): product hdGroupItemModelString json loading"

        try:
            self.hdGroupItemsString_json = json.loads(self._find_between(html.tostring(self.tree_html), "var hdGroupItemsString = ", ";\r"))
        except:
            print "Issue(Newegg): product hdGroupItemsString json loading"

        try:
            self.imgGalleryConfig_json = json.loads(self._find_between(html.tostring(self.tree_html), "imgGalleryConfig.Items=", ";\r"))
        except:
            print "Issue(Newegg): product imgGalleryConfig json loading"

        try:
            self.overviewData_json = json.loads(self._find_between(html.tostring(self.tree_html), "\n                     var data = ", " || {}"))
        except:
            print "Issue(Newegg): product imgGalleryConfig json loading"

    def _canonical_link(self):
        canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

        return canonical_link

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        return self._canonical_link().split('=')[-1]

    def _site_id(self):
        return None

    def _status(self):
        return "success"

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//h1[@id='grpDescrip_h']/span[@itemprop='name']/text()")[0]

    def _product_title(self):
        return self.tree_html.xpath("//h1[@id='grpDescrip_h']/span[@itemprop='name']/text()")[0]

    def _title_seo(self):
        return self.tree_html.xpath("//h1[@id='grpDescrip_h']/span[@itemprop='name']/text()")[0]

    def _model(self):
        for item in self.hdGroupItemModelString_json:
            if item["SellerItem"] == self._product_id():
                return item["Model"]

        return None

    def _upc(self):
        return None

    def _features(self):
        features_dl_list = self.tree_html.xpath('//div[@id="detailSpecContent"]//dl')
        features_list = []

        for feature in features_dl_list:
            features_list.append(feature.xpath("./dt")[0].text_content().strip() + ": " + feature.xpath("./dd")[0].text_content().strip())

        if features_list:
            return features_list

        return None

    def _feature_count(self):
        features = self._features()
        return len(features) if features else 0

    def _model_meta(self):
        return None

    def _description(self):
        description_block = self.tree_html.xpath("//ul[@id='grpBullet_{0}']".format(self.related_item_id))

        if description_block:
            description_block = html.tostring(description_block[0])
            description_block = self._clean_text(self._exclude_javascript_from_description(description_block))
            return description_block if description_block else None

        return None

    def _long_description(self):
        long_description = None

        try:
            for overview in self.overviewData_json:
                if overview["ParentItem"] == self.related_item_id:
                    long_description = self._clean_text(html.fromstring(self._exclude_javascript_from_description(overview["Overview"])).text_content())
                    return long_description if long_description else None
        except:
            pass

        try:
            long_description = html.tostring(self.tree_html.xpath("//div[@id='Overview_Content']")[0])
            long_description = self._clean_text(html.fromstring(self._exclude_javascript_from_description(long_description)).text_content())
            return long_description if long_description else None
        except:
            pass

        return None

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):        
        image_list = []

        base_url_for_s7 = "http://images17.newegg.com/is/image/"
        base_url_for_non_s7 = "http://images10.newegg.com/productimage/"

        for item in self.imgGalleryConfig_json:
            if item["itemNumber"] == self._product_id():
                if item["normalImageInfo"]:
                    image_list = [base_url_for_non_s7 + img_name for img_name in item["normalImageInfo"]["imageNameList"].split(",")]
                elif item["scene7ImageInfo"]:
                    image_list = [base_url_for_s7 + img_name for img_name in item["scene7ImageInfo"]["imageSetImageList"].split(",")]
                break

        if image_list:
            return image_list

        return None

    def _image_count(self):
        image_urls = self._image_urls()
        return len(image_urls) if image_urls else 0

    def _video_urls(self):
        return None

    def _video_count(self):
        videos = self._video_urls()

        if videos:
            return len(videos)

        return 0

    def _pdf_urls(self):
        pdf_urls = self.tree_html.xpath("//div[@id='moreResource_{0}']//a[contains(@href, '.pdf')]/@href".format(self.related_item_id))
        return pdf_urls if pdf_urls else None

    def _pdf_count(self):
        if self._pdf_urls():
            return len(self._pdf_urls())

        return 0

    def _webcollage(self):
        webcollage = self.tree_html.xpath("//div[@id='Overview_Content']//script[contains(@src, 'http://content.webcollage.net')]")
        return 1 if webcollage else 0

    def _htags(self):
        htags_dict = {}
        # add h1 tags text to the list corresponding to the "h1" key in the dict
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        # add h2 tags text to the list corresponding to the "h2" key in the dict
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    def _keywords(self):
        return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]

    def _no_image(self):
        return None
    
    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################

    def _average_review(self):
        rws = self._reviews()
        if rws:
            s = n = 0
            for r in rws:
                s += r[0] * r[1]
                n += r[1]
            if n > 0:
                return round(s/float(n),2)
        return None


    def _review_count(self):
        nr_reviews = self.tree_html.xpath('//*[@id="linkSumRangeAll"]/span//text()')
        return self._toint(nr_reviews[0].strip()[1:-1]) if len(nr_reviews) > 0 else 0

    def _reviews(self):
        res = []
        for i in range(1,6):
            rvm = self.tree_html.xpath('//span[@id="reviewNumber%s"]//text()' % i)
            if len(rvm) > 0 and  self._toint(rvm[0]) > 0:
                res.append([i, self._toint(rvm[0])])
        if len(res) > 0: return res
        return None

    def _tofloat(self,s):
        try:
            t=float(s)
            return t
        except ValueError:
            return 0.0

    def _toint(self,s):
        try:
            s = s.replace(',','')
            t=int(s)
            return t
        except ValueError:
            return 0

    def _max_review(self):
        rv = self._reviews()
        if rv !=None and len(rv)>0:
            return rv[-1][0]
        return None

    def _min_review(self):
        rv = self._reviews()
        if rv !=None and len(rv)>0:
            return rv[0][0]
        return None


    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        return None

    def _price_amount(self):
        return None

    def _price_currency(self):
        return None

    def _in_stores(self):
        return 0

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):
        return 0

    def _in_stores_out_of_stock(self):
        return 0

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
        return None

    def _category_name(self):
        return None
    
    def _brand(self):
        return None


    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces


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
