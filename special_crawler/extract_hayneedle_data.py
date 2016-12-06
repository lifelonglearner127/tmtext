#!/usr/bin/python

import urllib
import cookielib
import re
import sys
import json

from lxml import html, etree
import time
import mechanize
import requests
from requests.auth import HTTPProxyAuth
from extract_data import Scraper
from spiders_shared_code.nike_variants import NikeVariants


class HayneedleScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.hayneedle.com/<product-name>"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.product_json = None
        # whether product has any webcollage media
        self.review_json = None
        self.review_list = None
        self.is_review_checked = False
        self.store_url = 'http://www.hayneedle.com'
        self.nv = NikeVariants()
        self.variants = None
        self.is_variant_checked = False
        self.proxy_host = self.CRAWLERA_HOST
        self.proxy_port = self.CRAWLERA_PORT
        self.proxy_auth = HTTPProxyAuth(self.CRAWLERA_APIKEY, "")
        self.proxies = {"http": "http://{}:{}/".format(self.proxy_host, self.proxy_port)}
        self.proxy_config = {"proxy_auth": self.proxy_auth, "proxies": self.proxies}

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^http://www.hayneedle.com/.*?$", self.product_page_url)
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
            self.nv.setupCH(self.tree_html)
        except:
            pass

        if self.tree_html.xpath('//div[contains(@class, "product-page-container")]'):
            return False

        return True

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _extract_product_json(self):
        if self.product_json:
            return self.product_json

        try:
            product_json_text = self.tree_html.xpath("//script[@id='product-data']/text()")[0]
            self.product_json = json.loads(product_json_text)
        except:
            self.product_json = None

        return self.product_json

    def _canonical_link(self):
        canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

        return canonical_link

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        product_id = self.tree_html.xpath("//row[contains(@class, 'title-container')]//div[contains(@class, 'sku-display')]/span[contains(@class, 'text-large')]/following-sibling::span/text()")[0]
        return product_id

    def _site_id(self):
        return None

    def _status(self):
        return "success"






    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//row[contains(@class, 'title-container')]//h1[contains(@class, 'inline')]/text()")[0]

    def _product_title(self):
        return self.tree_html.xpath("//row[contains(@class, 'title-container')]//h1[contains(@class, 'inline')]/text()")[0]

    def _title_seo(self):
        return self.tree_html.xpath("//row[contains(@class, 'title-container')]//h1[contains(@class, 'inline')]/text()")[0]

    def _model(self):
        return None

    def _upc(self):
        return None

    def _features(self):
        feature_txts = iter(self.tree_html.xpath("//table[@class='specs-table']//tr/td/text()"))

        features = []
        for k, v in zip(feature_txts, feature_txts):
            if k.strip():
                features.append("%s: %s" % (k.strip(), v.strip()))

        if features:
            return features

        return None

    def _feature_count(self):
        if self._features():
            return len(self._features())

        return None

    def _model_meta(self):
        return None

    def _description(self):
        return self.tree_html.xpath("//div[contains(@class, 'desc-section')]/h2[text()='Description']/following-sibling::div")[0].text_content().strip()

    def _long_description(self):
        return self.tree_html.xpath("//div[contains(@class, 'desc-section')]/h2[text()='Description']/following-sibling::div")[0].text_content().strip()

    def _variants(self):
        if self.is_variant_checked:
            return self.variants

        self.is_variant_checked = True

        self.variants = self.nv._variants()

        return self.variants

    def _swatches(self):
        return self.nv.swatches()

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_urls = self.tree_html.xpath("//div[@class='preloaded-preview-container']/img/@src")
        image_urls = [self._fix_image_url(url) for url in image_urls]

        return image_urls

    def _fix_image_url(self, url):
        if isinstance(url, (list, tuple)):
            if not url:
                return
            url = url[0]
        url = url.replace('?is=70,70,0xffffff', '')
        return url

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def _video_urls(self):
        return None

    def _video_count(self):
        videos = self._video_urls()

        if videos:
            return len(videos)

        return 0

    def _pdf_urls(self):
        return None

    def _pdf_count(self):
        if self._pdf_urls():
            return len(self._pdf_urls())

        return 0

    def _webcollage(self):
        return None

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
        if self._review_count() == 0:
            return None

        average = self.tree_html.xpath('//div[contains(@class, "pr-snapshot-rating")]//span[contains(@class, "pr-rating")]/text()')[0]
        if average:
            return float(average)

        return None

    def _review_count(self):
        self._reviews()

        count = self.tree_html.xpath(
            '//div[contains(@class, "pr-snapshot-rating")]//p[contains(@class, "pr-snapshot-average-based-on-text")]/span[@class="count"]/text()'
        )[0]

        if count:
            return int(count)
        return 0

    def _max_review(self):
        if self._review_count() == 0:
            return None

        for i, review in enumerate(self.review_list):
            if review[1] > 0:
                return 5 - i

    def _min_review(self):
        if self._review_count() == 0:
            return None

        for i, review in enumerate(reversed(self.review_list)):
            if review[1] > 0:
                return i + 1

    def _reviews(self):
        if self.is_review_checked:
            return self.review_list

        self.is_review_checked = True

        ul = self.tree_html.xpath(
            '//div[contains(@class, "pr-snapshot-rating")]//ul[contains(@class, "pr-ratings-histogram-content")]/li//p[@class="pr-histogram-count"]/span/text()'
        )

        review_list = [[5 - i, int(re.findall('\d+', mark)[0])] for i, mark in enumerate(ul)]

        # for li in ul:
        #     review = []
        #     mark = re.findall(r'\d+', li.xpath("./@class")[0])
        #     count = re.findall(r'\d+', li.xpath(".//p[@class='pr-histogram-count']/span/text()")[0])

        if not review_list:
            review_list = None

        self.review_list = review_list

        return self.review_list

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        return self.tree_html.xpath("//column[contains(@class, 'display-price-container label')]/div/text()")[0].strip()

    def _price_amount(self):
        return None

    def _price_currency(self):
        return self.tree_html.xpath("//meta[@property='og:price:currency']/@content")[0]

    def _in_stores(self):
        return 0

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):
        if not self.product_json["trackingData"]["product"]["inStock"]:
            return 1

        return 0

    def _in_stores_out_of_stock(self):
        return None

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
        return [self.product_json["trackingData"]["product"]["category"]]

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        brand = self.tree_html.xpath("//table[@class='specs-table']//tr/td/text()")[1].strip()
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
        "variants": _variants,
        "swatches": _swatches,
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
