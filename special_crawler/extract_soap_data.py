#!/usr/bin/python
#  -*- coding: utf-8 -*-

import urllib
import urllib2
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


class SoapScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www\.soap\.com/p/(.*)"

    reviews_tree = None
    max_score = None
    min_score = None
    review_count = None
    average_review = None
    reviews = None

    def check_url_format(self):
        # for ex: http://www.soap.com/p/nordic-naturals-complete-omega-3-6-9-1-000-mg-softgels-lemon-64714
        m = re.match(r"^http://www\.soap\.com/p/(.*)", self.product_page_url)
        return not not m

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''

        if len(self.tree_html.xpath("//div[@class='productDetailPic']//a//img")) < 1:
            return True
        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        product_id = self.tree_html.xpath("//input[@id='productIDTextBox']/@value")[0].strip()
        return product_id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//div[@class='productTitle']//h1//text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//div[@class='productTitle']//h1//text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()
    
    def _model(self):
        return None

    def _upc(self):
        return None

    def _features(self):
        line_txts = []
        all_features_text = line_txts
        if len(all_features_text) < 1:
            return None
        return all_features_text

    def _feature_count(self):
        features = len(self._features())
        if features is None:
            return 0
        return len(self._features())

    def _model_meta(self):
        return None

    def _description(self):
        description = self._description_helper()
        if description is None or len(description) < 1:
            return self._long_description_helper()
        return description

    def _description_helper(self):
        divs = self.tree_html.xpath("//div[@class='naturalBadgeContent']")
        description = ""
        for div in divs:
            rows = div.xpath(".//text()")
            rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
            description += "\n".join(rows)
            break

        rows = self.tree_html.xpath("//dl[@class='descriptTabContent']//dd[@id='Tab1DetailInfo']//text()")
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        if len(rows) > 0:
            description += "\n" + "\n".join(rows)
        description = description.replace("\n.", ".")
        if len(description) < 1:
            return None
        return description

    def _long_description(self):
        description = self._description_helper()
        if description is None or len(description) < 1:
            return None
        return self._long_description_helper()

    def _long_description_helper(self):
        tab_headers = self.tree_html.xpath("//ul[contains(@class,'descriptTab')]//li")
        txts = []
        ids = []
        description = ""
        for tab_header in tab_headers:
            txt = "".join(tab_header.xpath(".//text()")).strip()
            if txt == "Description" or txt in txts:
                continue
            txts.append(txt)
            try:
                id = tab_header.xpath(".//a/@id")[0].strip()
                id = re.findall(r"\d+", id)[0]
                id = "Tab%sDetailInfo" % id
                ids.append(id)
                rows = self.tree_html.xpath("//dl[@class='descriptTabContent']//dd[@id='%s']//text()" % id)
                rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
                if len(rows) > 0:
                    description += "\n" + "\n".join(rows)
                description = description.replace("\n.", ".")
            except:
                pass

        if len(description) < 1:
            return None
        return description

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_url = self.tree_html.xpath("//div[contains(@class,'magicThumbBox')]/a/@href")
        image_url = [self._clean_text(r) for r in image_url if len(self._clean_text(r)) > 0]
        if len(image_url) < 1:
            return None
        return image_url

    def _image_count(self):
        image_urls = self._image_urls()
        return len(image_urls)

    def _video_urls(self):
        # http://www.soap.com/Product/ProductDetail!GetProductVideo.qs?groupId=98715&videoType=Consumer
        # url = "http://www.soap.com/Product/ProductDetail!GetProductVideo.qs?groupId=%s&videoType=Consumer" % self._product_id()
        url = "http://www.soap.com/Product/ProductDetail!GetProductVideo.qs?groupId=%s" % self._product_id()
        req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
        redirect_contents = urllib2.urlopen(req).read()
        redirect_tree = html.fromstring(redirect_contents)

        rows = redirect_tree.xpath("//div[contains(@class,'productVideoList')]//div[@class='videoImage']//a/@onclick")
        video_url = []
        for row in rows:
            m = re.findall(r"playProductVideo\('(.*?)'", row.strip())
            if len(m) > 0:
                video_url.append(m[0])
        if len(video_url) < 1:
            return None
        return video_url

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
        atags = self.tree_html.xpath("//a[contains(@href, 'webcollage.net/')]")
        if len(atags) > 0:
            return 1
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
        if not self.max_score or not self.min_score:
            # AMAZON.COM REVIEWS
            # http://www.soap.com/amazon_reviews/06/47/14/mosthelpful_Default.html
            product_id = self._product_id()
            if len(product_id) % 2 == 1:
                product_id = "0%s" % product_id
            product_id = [product_id[i:i+2] for i in range(0, len(product_id), 2)]
            product_id = "/".join(product_id)
            url = "http://www.soap.com/amazon_reviews/%s/mosthelpful_Default.html" % product_id
            req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
            redirect_contents = urllib2.urlopen(req).read()
            redirect_tree = html.fromstring(redirect_contents)

            review_count = redirect_tree.xpath("//span[@class='pr-review-num']//text()")[0].strip()
            m = re.findall(r"\d+", review_count)
            if len(m) > 0:
                self.review_count = int(m[0])
            average_review = redirect_tree.xpath("//span[contains(@class, 'pr-rating pr-rounded average')]//text()")[0].strip()
            m = re.findall(r"\d+", average_review)
            if len(m) > 0:
                self.average_review = float(m[0])

            rows = redirect_tree.xpath("//div[contains(@class,'pr-info-graphic-amazon')]//dl//dd[3]//text()")
            self.reviews = []
            idx = 5
            rv_scores = []
            for row in rows:
                cnt = int(re.findall(r"\d+", row)[0])
                if cnt > 0:
                    self.reviews.append([idx, cnt])
                    rv_scores.append(idx)
                idx -= 1
                if idx < 1:
                    break
            self.max_score = max(rv_scores)
            self.min_score = min(rv_scores)

            # SOAP.COM REVIEWS

    def _average_review(self):
        self._load_reviews()
        return self.average_review

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
        price = self.tree_html.xpath("//span[@class='singlePrice']//text()")[0].strip()
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
        if len(self.tree_html.xpath("//input[@id='AddCartButton']")) < 1:
            return 1
        return 0

    def _marketplace_sellers(self):
        return None

    def _marketplace_lowest_price(self):
        return None

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        all = self.tree_html.xpath("//div[contains(@class,'positionNav')]//a//text()")
        out = [self._clean_text(r) for r in all]
        if out[0].lower() == "home":
            out = out[1:]
        if len(out) < 1:
            return None
        return out

    def _category_name(self):
        return self._categories()[-1]

    def load_universal_variable(self):
        js_content = ' '.join(self.tree_html.xpath('//script//text()'))

        universal_variable = {}
        universal_variable["manufacturer"] = re.findall(r'"manufacturer": "(.*?)"', js_content)[0]
        return universal_variable

    def _brand(self):
        return None

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
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "model" : _model, \
        "long_description" : _long_description, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "keywords" : _keywords, \
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
        # CONTAINER : CLASSIFICATION
         # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \

        # CONTAINER : PAGE_ATTRIBUTES
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
    }

