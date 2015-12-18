#!/usr/bin/python

import urllib
import re
import sys
import json
import ast

from lxml import html, etree
import time
import requests
from extract_data import Scraper


class CVSScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.cvs.com/shop/<category-product-name>/skuid-<skuid>"
    BASE_URL_REVIEWSREQ = 'http://cvspharmacy.ugc.bazaarvoice.com/3006-en_us/{0}/reviews.djs?format=embeddedhtml'
    BASE_URL_WEBCOLLAGE = 'http://content.webcollage.net/cvs/smart-button?ird=true&channel-product-id={0}'

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.product_json = None
        self.max_score = None
        self.min_score = None
        self.review_count = None
        self.average_review = None
        self.reviews = None
        self.is_review_checked = False
        self.is_webcollage_checked = False
        self.webcollage_content = None
        self.wc_360 = 0
        self.wc_emc = 0
        self.wc_video = 0
        self.wc_pdf = 0
        self.wc_prodtour = 0

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^http://www.cvs.com/shop/.*-skuid-[0-9]+$", self.product_page_url)
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
            if not self.tree_html.xpath('//span[@itemtype="http://schema.org/Product"]'):
                raise Exception()
        except Exception:
            return True

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _canonical_link(self):
        canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

        return canonical_link

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        sku_id = re.findall ('skuid-(.*?)$', self.product_page_url, re.DOTALL)[0]
        return sku_id

    def _site_id(self):
        return self._product_id()

    def _status(self):
        return "success"

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//h1[@class="prodName"]/text()')[0].strip()

    def _product_title(self):
        return self.tree_html.xpath('//h1[@class="prodName"]/text()')[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath('//h1[@class="prodName"]/text()')[0].strip()

    def _model(self):
        model = self._find_between(html.tostring(self.tree_html).lower(), "model # ", "<").strip()

        if model:
            return model

        return None

    def _upc(self):
        return None

    def _features(self):
        return None

    def _feature_count(self):
        return 0

    def _model_meta(self):
        return None

    def _description(self):
        description = ""

        for element in self.tree_html.xpath("//div[@id='prodDesc']/*"):
            if element.tag in ["strong", "b"]:
                break

            if element.tag not in ["script", "style"]:
                description = description + html.tostring(element).strip()

        if description:
            return description

        return None

    def _long_description(self):
        description = ""
        start_point = False

        for element in self.tree_html.xpath("//div[@id='prodDesc']/*"):
            if element.tag in ["strong", "b"]:
                start_point = True

            if start_point:
                description = description + html.tostring(element).strip()

        if description:
            return description

        return None

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):        
        image_list = self.tree_html.xpath("//img[@itemprop='image']/@src")

        for index, url in enumerate(image_list):
            if not url.startswith("http://www.cvs.com"):
                image_list[index] = "http://www.cvs.com/" + url

        if image_list:
            return image_list

        return None

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def _video_urls(self):
        return None

    def _video_count(self):
        return 0

    def _pdf_urls(self):
        return None

    def _pdf_count(self):
        return 0

    def _webcollage(self):
        """Uses video and pdf information
        to check whether product has any media from webcollage.
        Returns:
            1 if there is webcollage media
            0 otherwise
        """
        if not self.is_webcollage_checked:
            self.is_webcollage_checked = True
            self.webcollage_content = urllib.urlopen(self.BASE_URL_WEBCOLLAGE.format(self._product_id())).read()

        if "_wccontent" in self.webcollage_content:
            self.wc_emc = 1

        if self.wc_360 + self.wc_emc + self.wc_pdf + self.wc_prodtour + self.wc_video > 0:
            return 1

        return 0

    def _wc_360(self):
        self._webcollage()

        return self.wc_360

    def _wc_emc(self):
        self._webcollage()

        return self.wc_emc

    def _wc_pdf(self):
        self._webcollage()

        return self.wc_pdf

    def _wc_prodtour(self):
        self._webcollage()

        return self.wc_prodtour

    def _wc_video(self):
        self._webcollage()

        return self.wc_video

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
    def _load_reviews(self):
        try:
            if not self.is_review_checked:
                self.is_review_checked = True
                # http://macys.ugc.bazaarvoice.com/7129aa/694761/reviews.djs?format=embeddedhtml
                contents = urllib.urlopen(self.BASE_URL_REVIEWSREQ.format(self._product_id())).read()
                # contents = re.findall(r'"BVRRRatingSummarySourceID":"(.*?)"}', contents)[0]
                reviews = re.findall(r'<span class=\\"BVRRHistAbsLabel\\">(.*?)<\\/span>', contents)[:5]
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
                for review in reversed(reviews):
                    self.reviews.append([score, int(review)])
                    score += 1

                if not self.reviews:
                    self.reviews = None
        except:
            self.reviews = None
            pass

    def _average_review(self):
        self._load_reviews()
        count = 0
        score = 0
        for review in self.reviews:
            count += review[1]
            score += review[0]*review[1]
        return round(1.0*score/count, 1)

    def _review_count(self):
        self._load_reviews()
        count = 0

        if not self.reviews:
            return 0

        for review in self.reviews:
            count += review[1]
        return count

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
        return self.tree_html.xpath("//span[@itemprop='price']/text()")[0].strip()

    def _price_amount(self):
        price = self._find_between(html.tostring(self.tree_html), "product_price :", ",")
        price = re.findall(r"\d*\.\d+|\d+", price.replace(",", ""))[0]

        return float(price)

    def _price_currency(self):
        return self._find_between(html.tostring(self.tree_html), 'currency : "', '"',)

    def _in_stores(self):
        return 0

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):
        if "no stock" in self._find_between(html.tostring(self.tree_html), "balance_on_hand_stock_level", ",").lower():
            return 1

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
        breadcrumb = self._find_between(html.tostring(self.tree_html), "breadcrumb : ", "],") + "]"
        categories = ast.literal_eval(breadcrumb)

        return categories[:-1]

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        brand = self._find_between(html.tostring(self.tree_html), 'product_brand : ["', '"]')

        return brand

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
        "wc_360": _wc_360, \
        "wc_emc": _wc_emc, \
        "wc_video": _wc_video, \
        "wc_pdf": _wc_pdf, \
        "wc_prodtour": _wc_prodtour, \
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
