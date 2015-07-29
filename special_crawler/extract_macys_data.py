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
from spiders_shared_code.macys_variants import MacysVariants


class MacysScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www1\.macys\.com/shop/(.*)"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.review_json = None
        self.price_json = None
        self.mv = MacysVariants()

    reviews_tree = None
    max_score = None
    min_score = None
    review_count = None
    average_review = None
    reviews = None
    feature_count = None
    features = None
    video_urls = None
    video_count = None
    pdf_urls = None
    pdf_count = None

    def check_url_format(self):
        # for ex: http://www1.macys.com/shop/product/closeout-biddeford-comfort-knit-fleece-heated-king-blanket?ID=694761
        m = re.match(r"^http://www1\.macys\.com/shop/(.*)", self.product_page_url)
        return not not m

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''

        self.mv.setupCH(self.tree_html)

        #if len(self.tree_html.xpath("//div[@id='imageZoomer']//div[contains(@class,'main-view-holder')]/img")) < 1:
        #    return True
        if len(self.tree_html.xpath("//h1[contains(@class,'productTitle')]")) < 1:
            return True
        if len(self.tree_html.xpath("//div[@id='viewCollectionItemsButton']")) > 0:
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

    def _product_id(self):
        return None

    def _site_id(self):
        site_id = self.tree_html.xpath("//input[@id='productId']/@value")[0].strip()
        return site_id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//h1[contains(@class,'productTitle')]//text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//h1[contains(@class,'productTitle')]//text()")[0].strip()

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
        rows = self.tree_html.xpath("//div[@id='prdDesc']//ul[contains(@class,'bullets')]/li")
        line_txts = []
        for row in rows:
            txt = "".join([r for r in row.xpath(".//text()") if len(self._clean_text(r)) > 0]).strip()
            if len(txt) > 0:
                line_txts.append(txt)
        if len(line_txts) < 1:
            return None
        self.feature_count = len(line_txts)
        self.features = line_txts
        return self.features

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
        description = ""
        rows = self.tree_html.xpath("//div[@id='prdDesc']//div[@itemprop='description']/text()")
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        if len(rows) > 0:
            description += "\n".join(rows)
        if len(description) < 1:
            description = ""
            rows = self.tree_html.xpath("//div[@id='productDetails']//text()")
            rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
            if len(rows) > 0:
                description += "\n".join(rows)
            if len(description) < 1:
                return None
            if description.startswith("Product Details"):
                description = description.replace("Product Details\n", "")
        return description

    def _long_description(self):
        description = self._description_helper()
        if description is None or len(description) < 1:
            return None
        return self._long_description_helper()

    def _long_description_helper(self):
        script = " ".join(self.tree_html.xpath("//script//text()"))
        link = re.findall(r"MACYS\.adLinkPopUp\.definePopup\('(.*?)'", script, re.DOTALL)
        try:
            link = "http://www1.macys.com/shop/media/popup/?popupFileName=%s" % link[0]
            req = urllib2.Request(link, headers={'User-Agent' : "Magic Browser"})
            contents = urllib2.urlopen(req).read()
            # document.location.replace('
            tree = html.fromstring(contents)
            rows = tree.xpath("//text()")
            line_txts = []
            txt = "\n".join([r for r in rows if len(self._clean_text(r)) > 0]).strip()
            if len(txt) > 0:
                line_txts.append(txt)
            if len(line_txts) < 1:
                return None
            description = "\n".join(line_txts)
            return description
        except IndexError:
            pass

    def _variants(self):
        return self.mv._variants()

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_url_primary = []
        image_url_tmp = re.findall(r"MACYS.pdp.primaryImages\[\d+\] = {(.*?)}", " ".join(self.tree_html.xpath("//script//text()")), re.DOTALL)
        if len(image_url_tmp) > 0:
            image_urls = image_url_tmp[0].split(",")
            for r in image_urls:
                img = r.split(":")
                if len(img) >= 2:
                    image_url_primary.append("http://slimages.macys.com/is/image/MCY/products/%s" % img[1].replace('"','').replace("'",""))

        image_url_additional = []
        image_url_tmp = re.findall(r"MACYS.pdp.additionalImages\[\d+\] = {(.*?)}", " ".join(self.tree_html.xpath("//script//text()")), re.DOTALL)
        if len(image_url_tmp) > 0:
            image_urls = image_url_tmp[0].split('",')
            for r in image_urls:
                img = r.split(":")
                if len(img) >= 2:
                    imgs = img[1].replace('"','').replace("'","").split(",")
                    for r in imgs:
                        image_url_additional.append("http://slimages.macys.com/is/image/MCY/products/%s" % r)

        image_url_imageZoomer = []
        image_url_tmp = re.findall(r"MACYS.pdp.imageZoomer = {(.*?)}", " ".join(self.tree_html.xpath("//script//text()")), re.DOTALL)
        if len(image_url_tmp) > 0:
            m = re.findall(r"imgList: '(.*?)'", image_url_tmp[0], re.DOTALL)
            if len(m) > 0:
                image_urls = m[0].split(',')
                for r in image_urls:
                    image_url_imageZoomer.append("http://slimages.macys.com/is/image/MCY/products/%s" % r)

        image_url = self.tree_html.xpath("//div[@id='imageZoomer']//div[contains(@class,'main-view-holder')]/img/@src")
        image_url = [self._clean_text(r) for r in image_url if len(self._clean_text(r)) > 0]
        if len(image_url) < 1:
            image_url = self.tree_html.xpath("//div[@class='productImageSection']//img/@src")

        if len(image_url) == 1:
            try:
                if self._no_image(image_url[0]):
                    return None
            except Exception, e:
                print "WARNING: ", e.message

        image_url = image_url + image_url_primary + image_url_imageZoomer + image_url_additional
        image_url2 = []
        for r in image_url:
            try:
                image_url_tmp = r.split("?")[0]
            except:
                image_url_tmp = r
            image_url2.append(image_url_tmp)
        image_url2 = list(set(image_url2))

        if self._site_id() == '1776509':
            return image_url2[1:]

        return image_url2

    def _image_count(self):
        image_urls = self._image_urls()
        if image_urls is None:
            return 0
        return len(image_urls)

    def _video_urls(self):
        if self.video_count is not None:
            return self.video_urls
        self.video_count = 0
        video_urls = []
        rows = re.findall(r'videoid: "(.*?)"', " ".join(self.tree_html.xpath("//script//text()")), re.DOTALL)
        video_urls = rows
        if len(video_urls) < 1:
            return None
        self.video_urls = ["http://c.brightcove.com/services/viewer/federated_f9?flashID=%s_v" % r for r in video_urls]
        self.video_count = len(self.video_urls)
        return video_urls

    def _video_count(self):
        if self.video_count is None:
            self._video_urls()
        return self.video_count

    def _pdf_urls(self):
        if self.pdf_count is not None:
            return self.pdf_urls
        self.pdf_count = 0
        pdf_hrefs = []
        if len(pdf_hrefs) < 1:
            return None
        self.pdf_count = len(pdf_hrefs)
        return pdf_hrefs

    def _pdf_count(self):
        if self.pdf_count is None:
            self._pdf_urls()
        return self.pdf_count

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
                # http://macys.ugc.bazaarvoice.com/7129aa/694761/reviews.djs?format=embeddedhtml
                url = "http://macys.ugc.bazaarvoice.com/7129aa/%s/reviews.djs?format=embeddedhtml" % self._product_id()
                contents = urllib.urlopen(url).read()
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

                # self.reviews_tree = html.fromstring(contents)
        except:
            pass

    def _average_review(self):
        self._load_reviews()
        count = 0
        score = 0
        for review in self.reviews:
            count += review[1]
            score += review[0]*review[1]
        return round(1.0*score/count, 2)

    def _review_count(self):
        self._load_reviews()
        count = 0
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
        price = self.tree_html.xpath("//meta[@itemprop='price']/@content")[0].strip()
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
        # MACYS.pdp.productAvailable = "true";
        script = " ".join(self.tree_html.xpath("//script//text()"))
        available = re.findall(r"MACYS\.pdp\.productAvailable = \"(.*?)\"", script, re.DOTALL)
        if len(available) > 0:
            if available[0] == "true":
                return 1
        return 0

    def _marketplace(self):
        return 0

    def _marketplace_sellers(self):
        return None

    def _marketplace_lowest_price(self):
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
        if self._site_online() == 0:
            return None
        rows = self.tree_html.xpath("//ul[@class='similarItems']//li//text()")
        if "This product is currently unavailable" in rows:
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
        all = self.tree_html.xpath("//div[@id='breadCrumbsDiv']//a[@class='bcElement']//text()")
        out = [self._clean_text(r) for r in all]
        if len(out) < 1:
            return None
        return out

    def _category_name(self):
        return self._categories()[-1]

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
        "site_id" : _site_id, \

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "model" : _model, \
        "long_description" : _long_description, \
        "variants" : _variants, \
        # CONTAINER : PAGE_ATTRIBUTES
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "canonical_link": _canonical_link,
        "mobile_image_same" : _mobile_image_same, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "in_stores" : _in_stores, \
        "marketplace": _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \
        "_marketplace_out_of_stock" : _marketplace_out_of_stock, \
        "site_online" : _site_online, \
        "site_online_out_of_stock" : _site_online_out_of_stock, \
        "in_stores_out_of_stock" : _in_stores_out_of_stock, \

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
    }


