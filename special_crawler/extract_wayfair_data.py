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
import time
import requests
from extract_data import Scraper
from spiders_shared_code.wayfair_variants import WayfairVariants

is_empty = lambda x, y=None: x[0] if x else y

class WayfairScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################
    INVALID_URL_MESSAGE = "Expected URL format is (http|https)://www.wayfair.com/(.*)"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)
        self.wv = WayfairVariants()

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^(https|http)://www\.wayfair\.com/(.*)", self.product_page_url)
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
            if self.tree_html.xpath("//meta[@property='og:type']/@content")[0].strip() != "wayfairus:product":
                raise Exception

        except Exception:
            return True

        self.wv.setupCH(self.tree_html)

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _canonical_link(self):
        canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

        return canonical_link

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        return None

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//span[contains(@class,"js-product-title-name")]//text()')[0].strip()

    def _product_title(self):
        return self.tree_html.xpath('//span[contains(@class,"js-product-title-name")]//text()')[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _model(self):
        return None

    def _upc(self):
        return self.tree_html.xpath("//meta[@property='og:upc']/@content")[0]

    def _features(self):
        features = self.tree_html.xpath("//ul[preceding-sibling::p/text()='Features']/li/text()")

        if not features:
            return None

        return features

    def _feature_count(self):
        features = self._features()

        if not features:
            return 0

        return len(features)

    def _description(self):
        return self.tree_html.xpath("//p[@class='product_section_description']")[0].text_content().strip()

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description(self):
        content_block = self.tree_html.xpath("//div[@class='js-content-contain']")[0]
        long_description_content = ""

        for child_block in content_block:
            try:
                if child_block.attrib["class"] == "product_section_description":
                    continue

                if '<p class="product_sub_section_header">Features</p>' in html.tostring(child_block):
                    continue
            except:
                pass

            long_description_content = long_description_content + child_block.text_content().strip()

        long_description_content = re.sub('\\n+', ' ', long_description_content).strip()
        long_description_content = re.sub('\\t+', ' ', long_description_content).strip()
        long_description_content = re.sub(' +', ' ', long_description_content).strip()

        if len(long_description_content) > 0:
            return long_description_content

        return None

    def _variants(self):
        return self.wv._variants()

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        pass

    def _image_urls(self):
        image_urls = self.tree_html.xpath(
            "//div[contains(@class, 'ProductDetailImagesThumbnails-content')]//img/@src"
        )

        if not image_urls:
            return None

        image_urls = [url.replace("/42/", "/49/") for url in image_urls]

        return image_urls

    def _image_count(self):
        image_urls = self._image_urls()

        if not image_urls:
            return 0

        return len(image_urls)

    def _video_urls(self):
        return None

    def _video_count(self):
        return 0

    # return dictionary with one element containing the PDF
    def _pdf_urls(self):
        return self.tree_html.xpath("//a[contains(@href, '.pdf')]/@href")

    def _pdf_count(self):
        pdf_urls = self._pdf_urls()

        if not pdf_urls:
            return 0

        return len(pdf_urls)

    def _webcollage(self):
        return None

    def _htags(self):
        htags_dict = {}
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    def _keywords(self):
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0].strip()


    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################

    def _average_review(self):
        return float(self.tree_html.xpath('//span[@itemprop="ratingValue"]/text()')[0])

    def _review_count(self):
        return int(self.tree_html.xpath('//*[@itemprop="reviewCount"]/text()')[0])

    def _max_review(self):
        reviews = self._reviews()

        if not reviews:
            return None

        max_review = 0

        for review in reviews:
            if max_review < review[0] and review[1] > 0:
                max_review = review[0]

        return max_review

    def _min_review(self):
        reviews = self._reviews()

        if not reviews:
            return None

        min_review = 5

        for review in reviews:
            if min_review > review[0] and review[1] > 0:
                min_review = review[0]

        return min_review

    def _reviews(self):
        histogram = re.findall(r'"formatted_histogram_stats":\s?\[(.[^]]+)',
                       html.tostring(self.tree_html))

        rating_by_star = []

        if not histogram or not self._average_review():
            return None
        else:
            histogram = histogram[0]
            histogram = "[{0}]".format(histogram)

            try:
                stars_data = json.loads(histogram)

                for star in stars_data:
                    rating_by_star.append([int(star['id']), int(star['he_count'])])
            except:
                pass

        if not rating_by_star:
            return None

        return rating_by_star

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        price_text = "$" + str(self._price_amount())

        return price_text

    def _price_amount(self):
        return float(self.tree_html.xpath("//meta[@property='og:price:amount']/@content")[0])

    def _price_currency(self):
        return self.tree_html.xpath("//meta[@property='og:price:currency']/@content")[0]

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):
        return 0

    def _in_stores(self):
        return 0

    def _marketplace(self):
        return 0


    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        return self.tree_html.xpath("//div[contains(@class, 'product__nova__breadcrumbs')]/a/text()")


    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        return self.tree_html.xpath('//meta[@property="og:brand"]/@content')[0]

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
        "upc" : _upc,\
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "long_description" : _long_description, \
        "variants": _variants,

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
        "in_stores" : _in_stores, \
        "site_online_out_of_stock": _site_online_out_of_stock, \
        "marketplace" : _marketplace, \
        "site_online": _site_online, \
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



