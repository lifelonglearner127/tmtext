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
    review_count = 0
    average_review = None
    reviews = None
    image_urls = None
    image_count = -1


    def check_url_format(self):
        # for ex: http://www.samsclub.com/sams/dawson-fireplace-fall-2014/prod14520017.ip?origin=item_page.rr1&campaign=rr&sn=ClickCP&campaign_data=prod14170040
        m = re.match(r"^http://www\.samsclub\.com/sams/(.+)?/(.+)", self.product_page_url)
        return not not m

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''

        if len(self.tree_html.xpath("//div[contains(@class, 'imgCol')]//div[@id='plImageHolder']//img")) < 1:
            return True
        return False

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
        lis = self.tree_html.xpath("//div[contains(@class,'itemFeatures')]//li")
        rows = []
        for li in lis:
            txt = "".join(li.xpath(".//text()"))
            rows.append(txt)
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        if len(rows) < 1:
            trs = self.tree_html.xpath("//div[contains(@class,'itemFeatures')]//table//tr")
            rows = []
            for tr in trs:
                tds = tr.xpath(".//td")
                if len(tds) > 0:
                    row_txt = " ".join([self._clean_text(r) for r in tr.xpath(".//text()") if len(self._clean_text(r)) > 0])
                    rows.append(row_txt)
            if len(rows) < 1:
                return None
        return rows

    def _feature_count(self):
        features = len(self._features())
        if features is None:
            return 0
        return len(self._features())

    def _model_meta(self):
        return None

    def _description(self):
        description = self._description_helper()
        if len(description) < 1:
            return self._long_description_helper()
        return description

    def _description_helper(self):
        rows = self.tree_html.xpath("//div[contains(@class,'itemBullets')]//text()")
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        description = "\n".join(rows)
        return description

    def _long_description(self):
        description = self._description_helper()
        if len(description) < 1:
            return None
        return self._long_description_helper()

    def _long_description_helper(self):
        rows = self.tree_html.xpath("//div[@itemprop='description']//text()")
        long_description = "".join(rows)
        long_description = long_description.replace("View a video of this product.", "")
        long_description = long_description.replace("View a video of this product", "")
        rows = self.tree_html.xpath("//div[@itemprop='description']/*")
        row_txts = []
        for row in rows:
            if row.tag == 'style' or row.tag == 'h3':
                row_txt = "".join(row.xpath(".//text()"))
                long_description = long_description.replace(row_txt, "")
        # row_txts = [self._clean_text(r) for r in row_txts if len(self._clean_text(r)) > 0]
        # if row_txts[0] == "Description":
        #     row_txts = row_txts[1:]
        # long_description = "\n".join(row_txts)
        return long_description.strip()

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        if self.image_count == -1:
            self.image_urls = None
            self.image_count = 0
            script = "/n".join(self.tree_html.xpath("//div[@class='container']//script//text()"))
            m = re.findall(r"imageList = '([0-9]+)?'", script)
            imglist = m[0]
            url = "http://scene7.samsclub.com/is/image/samsclub/%s?req=imageset,json&id=init" % imglist
            contents = urllib.urlopen(url).read()
            m2 = re.findall(r'\"IMAGE_SET\"\:\"(.*?)\"', contents)
            img_set = m2[0]
            img_urls = []
            if len(img_set) > 0:
                img_arr = img_set.split(",")
                for img in img_arr:
                    img2 = img.split(";")
                    img_url = "http://scene7.samsclub.com/is/image/%s" % img2[0]
                    if img_url[-1:] not in "0123456789":
                        img_urls.append(img_url)

            if len(img_urls) == 0:
                img_urls = self.tree_html.xpath("//div[contains(@class, 'imgCol')]//div[@id='plImageHolder']//img/@src")
                if len(img_urls) < 1:
                    return None
            self.image_urls = img_urls
            self.image_count = len(img_urls)
            return img_urls
        else:
            return self.image_urls

    def _image_count(self):
        if self.image_count == -1:
            image_urls = self.image_urls()
        return self.image_count

    def _video_urls(self):
        rows = self.tree_html.xpath("//div[@id='tabItemDetails']//a/@href")
        rows = [r for r in rows if "video." in r]
        if len(rows) < 1:
            return None
        return rows

    def _video_count(self):
        urls = self._video_urls()
        if urls:
            return len(urls)
        return 0

    def _pdf_urls(self):
        pdf_hrefs = []
        pdfs = self.tree_html.xpath("//a[contains(@href,'.pdf')]")
        for pdf in pdfs:
            try:
                pdf_hrefs.append(pdf.attrib['href'])
            except KeyError:
                pass
        pdfs = self.tree_html.xpath("//a[contains(@href,'pdfpdf')]")
        for pdf in pdfs:
            try:
                pdf_hrefs.append(pdf.attrib['href'])
            except KeyError:
                pass
        pdfs = self.tree_html.xpath("//a[contains(@href,'pdf')]")
        for pdf in pdfs:
            try:
                if pdf.attrib['href'].endswith("pdf"):
                    pdf_hrefs.append(pdf.attrib['href'])
            except KeyError:
                pass
        pdfs = self.tree_html.xpath("//a[contains(@onclick,'.pdf')]")
        for pdf in pdfs:
            # window.open('http://graphics.samsclub.com/images/pool-SNFRound.pdf','_blank')
            try:
                url = re.findall(r"open\('(.*?)',", pdf.attrib['onclick'])[0]
                pdf_hrefs.append(url)
            except IndexError:
                pass
        pdf_hrefs = [r for r in pdf_hrefs if "JewelryDeliveryTimeline.pdf" not in r]
        if len(pdf_hrefs) < 1:
            return None
        return pdf_hrefs

    def _pdf_count(self):
        urls = self._pdf_urls()
        if urls:
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
                    review = review.replace(",", "")
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
        if len(self.reviews) < 1:
            return None
        return self.reviews

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        try:
            price = self.tree_html.xpath("//span[@class='price']//text()")[0].strip()
            currency = self.tree_html.xpath("//span[@class='superscript']//text()")[0].strip()
            superscript = self.tree_html.xpath("//span[@class='superscript']//text()")[1].strip()
            price = "%s%s.%s" % (currency, price, superscript)
            return price
        except:
            pass
        try:
            txt = self.tree_html.xpath("//span[contains(@class,'ipClubSelector')]//text()")[0].strip()
            if "Select your Club" in txt:
                return "in stores only - no online price"
        except:
            pass

        if len(self.tree_html.xpath("//h2[contains(text(),'Select your options')]//text()")) > 0:
            return "price depends on option"
        return None

    def _in_stores_only(self):
        return None

    def _in_stores(self):
        return None

    def _owned(self):
        return 1
    
    def _marketplace(self):
        return 0

    def _owned_out_of_stock(self):
        out_of_stock = self.tree_html.xpath("//div[contains(@class,'biggraybtn')]//text()")[0].strip()
        if 'Out of stock online' in out_of_stock:
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
        all = self.tree_html.xpath("//div[contains(@id, 'breadcrumb')]//a/text()")
        out = [self._clean_text(r) for r in all]
        return out[1:]

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

