#!/usr/bin/python
#  -*- coding: utf-8 -*-

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


class SamsclubScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.samsclub.com/sams/(.+)?/(.+)"

    reviews_tree = None
    max_score = None
    min_score = None
    review_count = None
    average_review = None
    reviews = None

    def check_url_format(self):
        # for ex: http://www.samsclub.com/sams/dawson-fireplace-fall-2014/prod14520017.ip?origin=item_page.rr1&campaign=rr&sn=ClickCP&campaign_data=prod14170040
        m = re.match(r"^http://www\.samsclub\.com/sams/(.+)?/(.+)", self.product_page_url)
        return not not m

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        product_id = self.tree_html.xpath("//input[@id='mbxProductId']/@value")[0].strip()
        return product_id
        # product_id = self.tree_html.xpath("//span[@itemprop='productID']//text()")[0].strip()
        # m = re.findall(r"[0-9]+", product_id)
        # if len(m) > 0:
        #     return m[0]
        # else:
        #     return None

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//span[@itemprop='name']//text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//span[@itemprop='name']//text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()
    
    def _model(self):
        return self.tree_html.xpath("//span[@itemprop='model']//text()")[0].strip()

    def _upc(self):
        return self.tree_html.xpath("//input[@id='mbxSkuId']/@value")[0].strip()

    def _features(self):
        rows = self.tree_html.xpath("//div[starts-with(@class,'itemdetailsDescription')]")
        line_txts = []
        for row in rows:
            row_txts = row.xpath(".//p//text()")
            row_txts = [self._clean_text(r) for r in row_txts]
            row_txts = ": ".join(row_txts)
            line_txts.append(row_txts)
        return line_txts

    def _feature_count(self):
        return len(self.tree_html.xpath("//div[starts-with(@class,'itemdetailsDescription')]"))

    def _model_meta(self):
        return None

    def _description(self):
        description = "\n".join(self.tree_html.xpath("//div[starts-with(@class,'itemBullets')]//ul//li//text()"))
        description += "\n" + self.tree_html.xpath("//div[starts-with(@class,'itemDescription')]//p[contains(@class,'itemDetailsPara')]//text()")[0].strip()
        return description

    def _long_description(self):
        rows = self.tree_html.xpath("//div[starts-with(@class,'itemFeatures')]//text()")
        row_txts = [self._clean_text(r) for r in rows]
        long_description = "\n".join(row_txts)
        return long_description

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        script = "/n".join(self.tree_html.xpath("//div[@class='container']//script//text()"))
        m = re.findall(r"imageList = '([0-9]+)?'", script)
        imglist = m[0]
        url = "http://scene7.samsclub.com/is/image/samsclub/%s?req=imageset,json&id=init" % imglist
        contents = urllib.urlopen(url).read()
        m2 = re.findall(r'\"IMAGE_SET\"\:\"(.*?)\"', contents)
        img_set = m2[0]
        img_arr = img_set.split(",")
        img_urls = []
        for img in img_arr:
            img2 = img.split(";")
            img_url = "http://scene7.samsclub.com/is/image/%s" % img2[0]
            img_urls.append(img_url)

        if len(img_urls) == 0:
            return None
        return img_urls

    def _image_count(self):
        image_urls = self._image_urls()
        if len(image_urls) == 0:
            return 0
        return len(image_urls)

    def _video_urls(self):
        return None

    def _video_count(self):
        urls = self._video_urls()
        if urls:
            return len(urls)
        return 0

    def _pdf_urls(self):
        pdfs = self.tree_html.xpath("//a[contains(@href,'.pdf')]")
        pdf_hrefs = []
        for pdf in pdfs:
            pdf_hrefs.append(pdf.attrib['href'])
        return pdf_hrefs

    def _pdf_count(self):
        urls = self._pdf_urls()
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

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    #populate the reviews_tree variable for use by other functions
    def _load_reviews(self):
        try:
            if not self.max_score or not self.min_score:
                # for ex: http://samsclub.ugc.bazaarvoice.com/1337/prod12250457/reviews.djs?format=embeddedhtml
                url = "http://samsclub.ugc.bazaarvoice.com/1337/%s/reviews.djs?format=embeddedhtml" % self._product_id()
                contents = urllib.urlopen(url).read()
                tmp_reviews = re.findall(r'<span class=\\"BVRRHistAbsLabel\\">(.*?)<\\/span>', contents)
                reviews = []
                for review in tmp_reviews:
                    m = re.findall(r'([0-9]+)', review)
                    reviews.append(m[0])

                reviews = reviews[:5]
                score = 5
                for review in reviews:
                    if int(review) > 0:
                        self.max_score = score
                        break
                    score -= 1

                score = 1
                for review in reversed(reviews):
                    if int(review) > 0:
                        self.min_score = score
                        break
                    score += 1

                self.reviews = []
                score = 1
                total_review = 0
                review_cnt = 0
                for review in reversed(reviews):
                    self.reviews.append([score, int(review)])
                    total_review += score * int(review)
                    review_cnt += int(review)
                    score += 1
                self.review_count = review_cnt
                self.average_review = total_review * 1.0 / review_cnt
                # self.reviews_tree = html.fromstring(contents)
        except:
            pass

    def _average_review(self):
        self._load_reviews()
        return "%.2f" % self.average_review

    def _review_count(self):
        self._load_reviews()
        return self.review_count

    def _max_review(self):
        self._load_reviews()
        return self.max_score

    def _min_review(self):
        self._load_reviews()
        return self.min_score

    def _reviews(self):
        self._load_reviews()
        return self.reviews

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        price = self.tree_html.xpath("//span[@class='price']//text()")[0].strip()
        superscript = self.tree_html.xpath("//span[@class='superscript']//text()")[1].strip()
        price = int(price) + int(superscript) * 0.01
        return price

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
        all = self.tree_html.xpath("//div[contains(@id, 'breadcrumb')]//a/text()")
        out = [self._clean_text(r) for r in all]
        return out

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        return self.tree_html.xpath("//span[@itemprop='brand']//text()")[0].strip()

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
        "product_id" : _product_id, \

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "model" : _model, \
        "upc" : _upc,\
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "long_description" : _long_description, \

        # CONTAINER : PAGE_ATTRIBUTES
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "mobile_image_same" : _mobile_image_same, \

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
        "brand" : _brand, \

        "loaded_in_seconds": None \
        }


    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        # CONTAINER : PAGE_ATTRIBUTES
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \

         # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \
    }

