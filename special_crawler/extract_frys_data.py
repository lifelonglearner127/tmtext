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


class FrysScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www\.frys\.com/product/(.*)"

    feature_count = None
    features = None
    video_urls = None
    video_count = None
    pdf_urls = None
    pdf_count = None
    wc_content = None

    def check_url_format(self):
        # for ex: http://www.frys.com/product/8007994
        m = re.match(r"^http://www\.frys\.com/product/(.*)", self.product_page_url)
        return not not m

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''

        #if len(self.tree_html.xpath("//div[@id='imageZoomer']//div[contains(@class,'main-view-holder')]/img")) < 1:
        #    return True
        if len(self.tree_html.xpath("//label[contains(@class,'product_title')]")) < 1:
            return True
        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        product_id = self.tree_html.xpath("//input[@id='zplu']/@value")[0].strip()
        return product_id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//label[contains(@class,'product_title')]//text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//label[contains(@class,'product_title')]//text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()
    
    def _model(self):
        rows = self.tree_html.xpath("//div[@id='ProductAttributes']//text()")
        rows = [r for r in rows if len(self._clean_text(r)) > 0]
        model = None
        for r in rows:
            if "Model" in r:
                model = r.replace("Model", "").strip()
        return model

    def _upc(self):
        rows = self.tree_html.xpath("//div[@id='ProductAttributes']//text()")
        rows = [r for r in rows if len(self._clean_text(r)) > 0]
        upc = None
        for r in rows:
            if "UPC" in r:
                upc = r.replace("UPC", "").strip()
        return upc

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
        rows = self.tree_html.xpath("//div[@id='shortDescrDiv']//text()")
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        if len(rows) > 0:
            description += "\n".join(rows)
        if len(description) < 1:
            return None
        return description

    def _long_description(self):
        description = self._description_helper()
        if description is None or len(description) < 1:
            return None
        return self._long_description_helper()

    def _long_description_helper(self):
        tables = self.tree_html.xpath("//table")
        for t in tables:
            try:
                width = t.xpath("./@width")[0].strip()
                if width == "94%":
                    rows = t.xpath(".//text()")
                    description = "\n".join([r for r in rows if len(self._clean_text(r)) > 0]).strip()
                    if len(description) < 1:
                        return None
                    return description
            except IndexError:
                continue
        return None

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_url = self.tree_html.xpath("//div[@id='navigator']//div[contains(@class,'thumbnails')]//img/@src")
        image_url = [self._clean_text(r) for r in image_url if len(self._clean_text(r)) > 0]
        if len(image_url) < 1:
            image_url = self.tree_html.xpath("//div[@id='large_image']//a//img/@src")
            if len(image_url) < 1:
                return None

        if len(image_url) == 1:
            try:
                if self._no_image(image_url[0]):
                    return None
            except Exception, e:
                print "WARNING: ", e.message

        return image_url

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
        contents = self._wc_content()
        m = re.findall(r'"src":"([^"]*?\.flv)",', contents, re.DOTALL)
        m = ["http://content.webcollage.net%s" % r for r in m]
        if len(m) > 0:
            video_urls += m
        self.wc_video_count = len(video_urls)
        # m2 = re.findall(r'wc-media wc-iframe(.*?)>', contents.replace("\\",""), re.DOTALL)
        # try:
        #     m = re.findall(r'data-asset-url="(.*?)"', m2[0], re.DOTALL)
        #     if len(m) > 0:
        #         video_urls += m
        # except IndexError:
        #     pass

        # m = re.findall(r'wcobj="(.*?)"', contents.replace("\\",""), re.DOTALL)
        # if len(m) > 0:
        #     url_wc = m[0]
        #     contents_wc = urllib.urlopen(url_wc).read()
        #     # document.location.replace('
        #     tree = html.fromstring(contents_wc)
        #     try:
        #         playerKey = tree.xpath("//param[@name='playerKey']/@value")[0].strip()
        #         videos = tree.xpath("//li[contains(@class,'video_slider_item')]/@video_id")
        #         for video in videos:
        #             # http://client.expotv.com/video/config/539028/4ac5922e8961d0cbec0cc659740a5398
        #             url_wc2 = "http://client.expotv.com/video/config/%s/%s" % (video, playerKey)
        #             contents_wc2 = urllib.urlopen(url_wc2).read()
        #             jsn = json.loads(contents_wc2)
        #             jsn = jsn["sources"]
        #             for item in jsn:
        #                 try:
        #                     file_name = item['file']
        #                     video_urls.append(file_name)
        #                     break
        #                 except:
        #                     pass
        #     except IndexError:
        #         pass

        if len(video_urls) < 1:
            return None
        self.video_urls = video_urls
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
        pdfs = self.tree_html.xpath("//div[@id='MainContainer']//a[contains(@href,'.pdf')]")
        pdf_hrefs = []
        for pdf in pdfs:
            pdf_url_txts = [self._clean_text(r) for r in pdf.xpath(".//text()") if len(self._clean_text(r)) > 0]
            if len(pdf_url_txts) > 0:
                pdf_hrefs.append(pdf.attrib['href'])

        contents = self._wc_content()
        m = re.findall(r'wcobj="([^"]*?\.pdf)"', contents, re.DOTALL)
        m = ["http://content.webcollage.net%s" % r for r in m]
        if len(m) > 0:
            pdf_hrefs += m

        if len(pdf_hrefs) < 1:
            return None
        self.pdf_count = len(pdf_hrefs)
        return pdf_hrefs

    def _pdf_count(self):
        if self.pdf_count is None:
            self._pdf_urls()
        return self.pdf_count

    def _wc_content(self):
        if self.wc_content == None:
            url = "http://content.webcollage.net/frys/smart-button?ird=true&channel-product-id=%s" % self._product_id()
            html = urllib.urlopen(url).read()
            if "_wccontent" in html:
                self.wc_content = html.replace("\\","")
                return self.wc_content
            else:
                self.wc_content = ""
                return ""
        return self.wc_content

    def _wc_360(self):
        html = self._wc_content()
        if "wc-360" in html: return 1
        return 0


    def _wc_pdf(self):
        html = self._wc_content()
        if ".pdf" in html: return 1
        return 0

    def _wc_video(self):
        html = self._wc_content()
        if ".mp4" in html: return 1
        return 0

    def _wc_emc(self):
        html = self._wc_content()
        if "wc-aplus" in html: return 1
        return 0

    def _wc_prodtour(self):
        html = self._wc_content()
        if 'id="wc-tour"' in html: return 1
        return 0

    def _flixmedia(self):
        if "media.flix" in etree.tostring(self.tree_html):
            return 1
        else:
            return 0

    def _webcollage(self):
        # http://content.webcollage.net/pg-estore/power-page?ird=true&channel-product-id=037000864868
        url = "http://content.webcollage.net/frys/smart-button?ird=true&channel-product-id=%s" % self._product_id()
        html = urllib.urlopen(url).read()
        m = re.findall(r'_wccontent = (\{.*?\});', html, re.DOTALL)
        try:
            if ".webcollage.net" in m[0]:
                return 1
        except IndexError:
            pass
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
        return None

    def _review_count(self):
        count = 0
        return count

    def _max_review(self):
        return None

    def _min_review(self):
        return None

    def _reviews(self):
        return None

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        try:
            price = self.tree_html.xpath("//div[@id='did_price1valuediv']//label//text()")[0].strip()
        except IndexError:
            price = None
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
        return 1

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
        all = self.tree_html.xpath("//div[@id='product_bread_crums']//a//text()")
        out = [r.strip() for r in all]
        out = out[1:]
        if len(out) < 1:
            return None
        categories = []
        idx = 0
        for r in out:
            if idx < len(out)-1:
                categories.append(r[:-1])
            else:
                categories.append(r)
        return categories

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        rows = self.tree_html.xpath("//div[@id='ProductAttributes']//text()")
        rows = [r for r in rows if len(self._clean_text(r)) > 0]
        brand = None
        for r in rows:
            if "Manufacturer" in r:
                brand = r.replace("Manufacturer", "").strip()
                brand = brand.replace(": ", "")
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
        "upc" : _upc, \
        "long_description" : _long_description, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "mobile_image_same" : _mobile_image_same, \

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
        "marketplace": _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \
        "marketplace_out_of_stock" : _marketplace_out_of_stock, \
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
        # CONTAINER : PAGE_ATTRIBUTES
        "webcollage" : _webcollage, \
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        "wc_emc" : _wc_emc, \
        "wc_video" : _wc_video, \
        "wc_pdf" : _wc_pdf, \
        "wc_prodtour" : _wc_prodtour, \
        "flixmedia" : _flixmedia, \
        }


