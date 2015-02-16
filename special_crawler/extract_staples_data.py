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


class StaplesScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www\.staples\.com/([a-zA-Z0-9\-/]+)/product_([a-zA-Z0-9]+)"

    reviews_tree = None
    max_score = None
    min_score = None
    review_count = None
    average_review = None
    reviews = None

    def check_url_format(self):
        # for ex: http://www.staples.com/Epson-WorkForce-Pro-WF-4630-Color-Inkjet-All-in-One-Printer/product_242602?cmArea=home_box1
        m = re.match(r"^http://www\.staples\.com/([a-zA-Z0-9\-/]+)/product_([a-zA-Z0-9]+)", self.product_page_url)
        return not not m

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        rows = self.tree_html.xpath("//img[@id='largeProductImage']")
        if len(rows) > 0:
            return False
        return True

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        return None

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//div[contains(@class,'productDetails')]/h1/text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//div[contains(@class,'productDetails')]/h1/text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()
    
    def _model(self):
        txt = self.tree_html.xpath("//p[@class='itemModel']//text()")[0].strip()
        model = re.findall(r"Model\: ([A-Za-z0-9]+)", txt)[0].strip()
        return model

    def _upc(self):
        txt = self.tree_html.xpath("//p[@class='itemModel']//text()")[0].strip()
        upc = re.findall(r"Item\: ([A-Za-z0-9]+)", txt)[0].strip()
        return upc

    def _features(self):
        rows = self.tree_html.xpath("//table[@id='tableSpecifications']//tr")
        line_txts = []
        for row in rows:
            txt = row.xpath(".//td//text()")
            txt = ": ".join(txt)
            if len(txt.strip()) > 0:
                line_txts.append(txt)
        return line_txts

    def _feature_count(self):
        return len(self._features())

    def _model_meta(self):
        return None

    def _description(self):
        description = self._description_helper()
        if description is None or len(description) < 1:
            return self._long_description_helper()
        return description

    def _description_helper(self):
        line_txts = self.tree_html.xpath("//div[contains(@class,'productDetails')]//div[@class='copyBullets']//text()")
        line_txts = [self._clean_text(r) for r in line_txts if len(self._clean_text(r)) > 1 and self._clean_text(r) != 'See more details']
        description = "\n".join(line_txts)
        if len(description) < 1:
            return None
        return description

    def _long_description(self):
        description = self._description_helper()
        if description is None or len(description) < 1:
            return None
        return self._long_description_helper()

    def _long_description_helper(self):
        line_txts = self.tree_html.xpath("//div[@id='subdesc_content']//text()")
        line_txts = [self._clean_text(r) for r in line_txts if len(self._clean_text(r)) > 1 and self._clean_text(r) != 'PRODUCT DETAILS' and self._clean_text(r) != 'Compare with similar items' and self._clean_text(r) != u'Would you like to give' and self._clean_text(r) != u'on product content, images, or tell us about a lower price?' and self._clean_text(r) != 'feedback']
        description = "\n".join(line_txts)
        return description
        # line_txts = []
        # try:
        #     line_txts += self.tree_html.xpath("//div[@id='subdesc_content']//h2//text()")
        # except IndexError:
        #     pass
        #
        # try:
        #     line_txts += self.tree_html.xpath("//div[@id='subdesc_content']//p[@class='skuShortDescription']//text()")
        # except IndexError:
        #     pass
        #
        # try:
        #     rows = self.tree_html.xpath("//div[@id='subdesc_content']//ul//text()")
        #     rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 1]
        #     line_txts += rows
        # except IndexError:
        #     pass
        # description = "\n".join(line_txts)
        # return description

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_url = self.tree_html.xpath("//div[@class='imageCarousel']//li//img/@src")
        if len(image_url) < 1:
            return None
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
            rows = self.tree_html.xpath("//p[@class='pr-histogram-count']//text()")
            self.reviews = []
            idx = 5
            rv_scores = []
            for row in rows:
                try:
                    cnt = int(re.findall(r"[0-9]+", row)[0].strip())
                except IndexError:
                    cnt = 0
                if cnt > 0:
                    self.reviews.append([idx, cnt])
                    rv_scores.append(idx)
                idx -= 1
                if idx < 1:
                    break
            self.max_score = max(rv_scores)
            self.min_score = min(rv_scores)

    def _average_review(self):
        avg_review = self.tree_html.xpath("//span[contains(@class,'average')]//text()")[0].strip()
        avg_review = round(float(avg_review), 2)
        return avg_review

    def _review_count(self):
        review_cnt = self.tree_html.xpath("//span[@class='count']//text()")[0].strip()
        return int(review_cnt)

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
        try:
            price = self.tree_html.xpath("//dd[@class='finalPrice']//text()")[0].strip()
            return price
        except IndexError:
            pass
        try:
            price = self.tree_html.xpath("//span[@class='finalPrice']//text()")[0].strip()
            price = price.replace("*", "")
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
        rows = self.tree_html.xpath("//div[contains(@class,'moneyBoxContainer')]//div[contains(@class,'moneyBoxBtn')]//text()")
        if "Visit your local Club for pricing & availability" in rows:
            return 1
        rows = self.tree_html.xpath("//p[@id='availableInStore']//text()")
        for row in rows:
            if "Available In-Store Only" in row:
                return 1
        rows = self.tree_html.xpath("//div[@class='checkmarks']//ul/li")
        for row in rows:
            txt = " ".join(row.xpath(".//text()"))
            if "FREE Shipping to store" in txt:
                return 1
            if "Check inventory in other stores" in txt:
                return 1
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
        rows = self.tree_html.xpath("//div[contains(@class,'moneyBoxContainer')]//div[contains(@class,'moneyBoxBtn')]//text()")
        if "Unavailable online" in rows:
            return 0
        rows = self.tree_html.xpath("//p[@id='availableInStore']//text()")
        for row in rows:
            if "Available In-Store Only" in row:
                return 0
        return 1

    def _site_online_out_of_stock(self):
        #  site_online_out_of_stock - currently unavailable from the site - binary
        if self._site_online() == 0:
            return None
        rows = self.tree_html.xpath("//div[contains(@class,'biggraybtn')]//text()")
        if "Out of stock online" in rows:
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
        all = self.tree_html.xpath("//div[contains(@class, 'breadcrumbs')]//a//text()")
        out = [self._clean_text(r) for r in all]
        if len(out) < 1:
            return None
        return out

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        brand = None
        trs = self.tree_html.xpath("//table[@class='data-table']//tr")
        for tr in trs:
            try:
                head_txt = tr.xpath("//th//text()")[0].strip()
                if head_txt == "Brand":
                    brand = tr.xpath("//td//text()")[0].strip()
            except IndexError:
                pass
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

