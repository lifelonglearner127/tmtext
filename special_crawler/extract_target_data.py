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


class TargetScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www\.target\.com/p/([a-zA-Z0-9\-]+)/-/A-([0-9]+)"

    reviews_tree = None
    max_score = None
    min_score = None
    review_count = None
    average_review = None
    reviews = None

    def check_url_format(self):
        # for ex: http://www.target.com/p/skyline-custom-upholstered-swoop-arm-chair/-/A-15186757#prodSlot=_1_1
        m = re.match(r"^http://www\.target\.com/p/([a-zA-Z0-9\-]+)/-/A-([0-9]+)", self.product_page_url)
        return not not m

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        product_id = str(self.tree_html.xpath("//input[@id='omniPartNumber']/@value")[0])
        return product_id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//h2[starts-with(@class, 'product-name item')]/span/text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//h2[starts-with(@class, 'product-name item')]/span/text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()
    
    def _model(self):
        return None

    def _upc(self):
        return self.tree_html.xpath("//span[@itemprop='sku']//text()")[0].strip()

    def _features(self):
        rows = self.tree_html.xpath("//ul[@class='normal-list']//li")
        line_txts = []
        for row in rows:
            row_txts = row.xpath(".//text()")
            row_txts = [self._clean_text(r) for r in row_txts]
            row_txts = "".join(row_txts)
            line_txts.append(row_txts)
        all_features_text = line_txts
        return all_features_text

    def _feature_count(self):
        return len(self._features())

    def _model_meta(self):
        return None

    def _description(self):
        description = "".join(self.tree_html.xpath("//span[@itemprop='description']//text()")).strip()
        return description

    def _long_description(self):
        rows = self.tree_html.xpath("//ul[starts-with(@class,'normal-list reduced-spacing-list')]//li")
        line_txts = []
        for row in rows:
            row_txts = row.xpath(".//text()")
            row_txts = [self._clean_text(r) for r in row_txts]
            row_txts = "".join(row_txts)
            line_txts.append(row_txts)
        long_description = "\n".join(line_txts)
        return long_description

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_url = self.tree_html.xpath("//ul[@id='carouselContainer']//li//img/@src")
        if len(image_url) < 1:
            image_url = self.tree_html.xpath("//div[@class='HeroPrimContainer']//a//img//@src")
        return image_url

    def _image_count(self):
        image_urls = self._image_urls()
        return len(image_urls)

    def _video_urls(self):
        video_url = self.tree_html.xpath("//div[@class='videoblock']//div//a/@href")
        video_url = [("http://www.target.com%s" % r) for r in video_url]
        demo_url = self.tree_html.xpath("//div[starts-with(@class, 'demoblock')]//span//a/@href")
        demo_url = [r for r in demo_url if len(self._clean_text(r)) > 0]
        for item in demo_url:
            contents = urllib.urlopen(item).read()
            tree = html.fromstring(contents)
            redirect_link = tree.xpath("//div[@id='slow-reporting-message']//a/@href")[0]
            redirect_contents = urllib.urlopen(redirect_link).read()
            redirect_tree = html.fromstring(redirect_contents)
            tabs = redirect_tree.xpath("//div[@class='wc-ms-navbar']//li//a//span/text()")
            if "Video" in tabs or "Product Video" in tabs:
                #have video
                video_url.append(item)

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

        # get from webcollage
        url = "http://content.webcollage.net/target/smart-button?ird=true&channel-product-id=%s" % self._product_id()
        contents = urllib.urlopen(url).read()
        wc_pdfs = re.findall(r'href=\\\"([^ ]*?\.pdf)', contents, re.DOTALL)
        wc_pdfs = [r.replace("\\", "") for r in wc_pdfs]
        pdf_hrefs += wc_pdfs
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
        try:
            if not self.max_score or not self.min_score:
                # url = "http://reviews.pgestore.com/3300/PG_00%s/reviews.htm?format=embedded"
                passkey = str(self.tree_html.xpath("//input[@id='bvSecAttrUrl']/@value")[0])
                # url = "%s %s" % (passkey, self._product_id())
                #url = "%s&resource.q0=products&filter.q0=id%3Aeq%3A%s&stats.q0=reviews&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Aen_US&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_US" % (passkey, self._product_id())
                url = passkey + "&resource.q0=products&filter.q0=id%3Aeq%3A" + self._product_id() + "&stats.q0=reviews&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Aen_US&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_US"
                #url = "%s&resource.q0=products&filter.q0=ideq%s&stats.q0=reviews&filteredstats.q0=reviews&filter_reviews.q0=contentlocaleeqen_US&filter_reviewcomments.q0=contentlocaleeqen_US" % (passkey, self._product_id())
                contents = urllib.urlopen(url).read()
                jsn = json.loads(contents)
                review_info = jsn['BatchedResults']['q0']['Results'][0]['ReviewStatistics']
                self.review_count = review_info['TotalReviewCount']
                self.average_review = review_info['AverageOverallRating']

                min_ratingval = None
                max_ratingval = None
                self.reviews = []
                for review in review_info['RatingDistribution']:
                    if min_ratingval == None or review['RatingValue'] < min_ratingval:
                        if review['Count'] > 0:
                            min_ratingval = review['RatingValue']
                    if max_ratingval == None or review['RatingValue'] > max_ratingval:
                        if review['Count'] > 0:
                            max_ratingval = review['RatingValue']
                    self.reviews.append(["%s star(s)" % review['RatingValue'], review['Count']])

                self.min_score = min_ratingval
                self.max_score = max_ratingval
        except:
            pass

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
        price = self.tree_html.xpath("//span[@itemprop='price']//text()")[0].strip()
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
        if 'disabled' in self.tree_html.xpath("//button[@id='addToCart']/@class")[0]:

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
        all = self.tree_html.xpath("//div[contains(@id, 'breadcrumbs')]//a/text()")
        out = [self._clean_text(r) for r in all]
        return out[1:]

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

