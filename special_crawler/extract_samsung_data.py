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


class SamsungScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.samsung.com/.*"

    reviews_tree = None
    max_score = None
    min_score = None
    review_count = None
    average_review = None
    reviews = None
    feature_count = None
    features = None

    def check_url_format(self):
        # http://www.samsung.com/us/home-appliances/refrigerators/4-door-flex/36-wide-34-cu-ft-capacity-4-door-flex-chef-collection-refrigerator-with-sparkling-water-dispenser-rf34h9960s4-aa/
        self.image_urls = None
        self.video_urls = None
        m = re.match("^http://www\.samsung\.com/.*$", self.product_page_url)
        return (not not m)

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        rows = self.tree_html.xpath("//div[contains(@class,'product-details__photo')]")
        if len(rows) > 0:
            return False
        return True

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        product_id = self.tree_html.xpath("//h2[contains(@class,'type-p3 product-details__info-sku')]/text()")[0].strip()
        return product_id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//h1[@itemprop='name']/text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//h1[@itemprop='name']/text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()
    
    def _model(self):
        return None

    def _upc(self):
        return None

    def _features(self):
        if self.feature_count is not None:
            return self.features
        self.feature_count = 0
        spec_cards = self.tree_html.xpath("//div[@class='spec-card']//text()")
        line_txts = []
        for spec_card in spec_cards:
            line = spec_card.xpath(".//text()")
            line = [r.strip() for r in line if len(r.strip()) > 0]
            line = " ".join(line)
            if len(line) > 0:
                line_txts.append(line)
        if len(line_txts) < 1:
            return None
        self.feature_count = len(line_txts)
        return line_txts

    def _feature_count(self):
        if self.feature_count is None:
            self._features()
        return self.feature_count

    def _model_meta(self):
        return None

    def _description(self):
        description = self._description_helper()
        if description is None or len(description) < 1:
            return self._long_description_helper()
        return description

    def _description_helper(self):
        rows = self.tree_html.xpath("//div[contains(@class,'product-details__info-description')]//text()")
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        line_txts = rows

        if len(line_txts) < 1:
            return None
        description = "".join(line_txts)
        return description

    def _long_description(self):
        description = self._description_helper()
        if description is None or len(description) < 1:
            return None
        return self._long_description_helper()

    def _long_description_helper(self):
        line_txts = []

        feature_items = self.tree_html.xpath("//div[contains(@class,'feature-benefit--inline')]")
        for r in feature_items:
            line = r.xpath(".//text")
            line = [r.strip() for r in line if len(r.strip()) > 0]
            line = " ".join(line)
            if len(line) > 0:
                line_txts.append(line)

        if len(line_txts) < 1:
            return None
        description = "".join(line_txts)
        return description

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_url = self.tree_html.xpath(
            "//div[contains(@class,'product-details__thumbnail')]"
            "//img[contains(@class,'product-details__img')]/@src")
        if len(image_url) < 1:
            return None
        try:
            if self._no_image(image_url[0]):
                return None
        except Exception, e:
            print "WARNING: ", e.message
        return image_url

    def _image_count(self):
        image_urls = self._image_urls()
        if image_urls:
            return len(image_urls)
        return 0

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
            pdf_url_txts = [self._clean_text(r) for r in pdf.xpath(".//text()") if len(self._clean_text(r)) > 0]
            if len(pdf_url_txts) > 0:
                pdf_hrefs.append(pdf.attrib['href'])
        if len(pdf_hrefs) < 1:
            return None
        pdf_hrefs = list(set(pdf_hrefs))
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
    def _average_review(self):
        if self.review_count is not None:
            return self.average_review
        self._reviews()
        return self.average_review

    def _review_count(self):
        if self.review_count is not None:
            return self.review_count
        self._reviews()
        return self.review_count

    def _max_review(self):
        if self.review_count is not None:
            return self.max_score
        self._reviews()
        return self.max_score

    def _min_review(self):
        if self.review_count is not None:
            return self.min_score
        self._reviews()
        return self.min_score

    def _reviews(self):
        if self.review_count is not None:
            return self.reviews

        lines = self.tree_html.xpath("//div[contains(@class,'star-details')]//div[contains(@class,'star-text')]//text()")
        lines = [r.strip() for r in lines if len(r.strip()) > 0]
        try:
            self.average_review = float(lines[0])
        except:
            pass

        lines = self.tree_html.xpath("//div[contains(@class,'reviews__total')]//text()")
        lines = [r.strip() for r in lines if len(r.strip()) > 0]
        try:
            num = re.findall(r"(\d+)", lines[0], re.DOTALL)[0]
            self.review_count = int(num)
        except:
            pass


        # link = self.tree_html.xpath("//span[contains(@class,'star-text__total')]//a/@href")
        # if len(link) > 0:
        #     link = "http://www.samsung.com%s" % link[0]
        #
        #     agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20140319 Firefox/24.0 Iceweasel/24.4.0'
        #     headers ={'User-agent': agent}
        #     with requests.Session() as s:
        #         s.get(self.product_page_url, headers=headers, timeout=30)
        #         response = s.get(link, headers=headers, timeout=30)
        #         if response != 'Error' and response.ok:
        #             contents = response.content
        #             # document.location.replace('
        #             tree = html.fromstring(contents)
        #             rows = tree.xpath("//text()")
        #             line_txts = []

        return None

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        try:
            price = self.tree_html.xpath(
                "//div[contains(@class,'product-details__info-price')]"
                "/span[contains(@class,'epp-price')]/text()"
            )[0].strip()
            arr = self.tree_html.xpath(
                "//div[contains(@class,'product-details__info-price')]"
                "/span[contains(@class,'after')]/text()")
            if '$' in arr:
                price = '$' + price
            return price
        except IndexError:
            pass
        return price

    def _price_amount(self):
        price = self._price()
        price = price.replace(",", "")
        price_amount = re.findall(r"[\d\.]+", price)[0]
        return float(price_amount)

    def _price_currency(self):
        price = self._price()
        price = price.replace(",", "")
        price_amount = re.findall(r"[\d\.]+", price)[0]
        price_currency = price.replace(price_amount, "")
        if price_currency == "$":
            return "USD"
        return price_currency

    def _in_stores(self):
        '''in_stores - the item can be ordered online for pickup in a physical store
        or it can not be ordered online at all and can only be purchased in a local store,
        irrespective of availability - binary
        '''
        return 0

    def _marketplace(self):
        '''marketplace: the product is sold by a third party and the site is just establishing the connection
        between buyer and seller. E.g., "Sold by X and fulfilled by Amazon" is also a marketplace item,
        since Amazon is not the seller.
        '''
        return 0

    def _marketplace_sellers(self):
        '''marketplace_sellers - the list of marketplace sellers - list of strings (["seller1", "seller2"])
        '''
        return None

    def _marketplace_lowest_price(self):
        # marketplace_lowest_price - the lowest of marketplace prices - floating-point number
        return None

    def _marketplace_out_of_stock(self):
        """Extracts info on whether currently unavailable from any marketplace seller - binary
        Uses functions that work on both old page design and new design.
        Will choose whichever gives results.
        Returns:
            1/0
        """
        return None

    def _site_online(self):
        # site_online: the item is sold by the site (e.g. "sold by Amazon") and delivered directly, without a physical store.
        return 1

    def _site_online_out_of_stock(self):
        #  site_online_out_of_stock - currently unavailable from the site - binary
        rows = self.tree_html.xpath("//span[contains(@class,'outOfStock')]//text()")
        if "out of stock" in rows:
            return 1
        rows = self.tree_html.xpath("//div[@class='buy_button']")
        if len(rows) < 1:
            return 1
        return 0

    def _in_stores_out_of_stock(self):
        '''in_stores_out_of_stock - currently unavailable for pickup from a physical store - binary
        (null should be used for items that can not be ordered online and the availability may depend on location of the store)
        '''
        return None

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        arr = self.tree_html.xpath("//ol[@typeof='BreadcrumbList']//li//a")
        line_txts = []
        for r in arr:
            line = r.xpath(".//text()")
            line = [r.strip() for r in line if len(r.strip()) > 0]
            line = "".join(line)
            if len(line) > 0:
                line_txts.append(line)
        if len(line_txts) < 1:
            return None
        return line_txts

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        brand = "samsung"
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
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "mobile_image_same" : _mobile_image_same, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "in_stores" : _in_stores, \
        "marketplace": _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \
        "site_online" : _site_online, \
        "site_online_out_of_stock" : _site_online_out_of_stock, \
        "in_stores_out_of_stock" : _in_stores_out_of_stock, \


         # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \

        "loaded_in_seconds": None \
        }


    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
    }

