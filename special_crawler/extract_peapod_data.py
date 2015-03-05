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


class PeapodScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is (https|http)://www\.peapod\.com/itemDetailView.jhtml\?.*"

    reviews_tree = None
    max_score = None
    min_score = None
    review_count = None
    average_review = None
    reviews = None
    feature_count = None
    features = None

    def check_url_format(self):
        # for ex: https://www.peapod.com/itemDetailView.jhtml?productId=191177&NUM=1424733320503
        m = re.match(r"^(https|http)://www\.peapod\.com/itemDetailView.jhtml\?.*", self.product_page_url)
        return not not m

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        rows = self.tree_html.xpath("//dd[@class='productImage']//div[@id='productImageHolder']")
        if len(rows) > 0:
            return False
        return True

    # method that returns xml tree of page, to extract the desired elemets from
    def _extract_page_tree(self):
        """Overwrites parent class method that builds and sets as instance variable the xml tree of the product page
        Returns:
            lxml tree object
        """
        formdata = {
            '_dyncharset': '',
            '/peapod/handler/iditarod/ZipHandler.continueURL': '',
            '_D:/peapod/handler/iditarod/ZipHandler.continueURL': '',
            '/peapod/handler/iditarod/ZipHandler.submitSuccessURL': '',
            '_D:/peapod/handler/iditarod/ZipHandler.submitSuccessURL': '',
            '/peapod/handler/iditarod/ZipHandler.submitFailureURL': '',
            '_D:/peapod/handler/iditarod/ZipHandler.submitFailureURL': '',
            '_D:zipcode': '',
            '/peapod/handler/iditarod/ZipHandler.collectProspectURL': '',
            '_D:/peapod/handler/iditarod/ZipHandler.collectProspectURL': '',
            '/peapod/handler/iditarod/ZipHandler.storeClosedURL': '',
            '_D:/peapod/handler/iditarod/ZipHandler.storeClosedURL': '',
            '/peapod/handler/iditarod/ZipHandler.defaultGuestParameters': '',
            '_D:/peapod/handler/iditarod/ZipHandler.defaultGuestParameters': '',
            '_DARGS': '',
            'Continue': '',
            '_D:Continue': '',
        }
        start_url = "https://www.peapod.com/site/gateway/zip-entry"\
                    "/top/zipEntry_main.jsp"
        contents = urllib.urlopen(start_url).read()
        tree = html.fromstring(contents)

        new_data = {}
        for key in formdata.keys():
            path = '//form[@name="zipEntryForm"]//input[@name="%s"]/@value' % key
            new_data[key] = tree.xpath(path)[0].strip()
        # populate static info
        new_data['zipcode'] = '10036' # '10036'
        new_data['memberType'] = 'C'
        new_data['_D:memberType'] = ''
        agent = ''
        if self.bot_type == "google":
            print 'GOOOOOOOOOOOOOGGGGGGGLEEEE'
            agent = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        else:
            agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20140319 Firefox/24.0 Iceweasel/24.4.0'

        headers ={'User-agent': agent}
        for i in range(self.MAX_RETRIES):
            # Use 'with' to ensure the session context is closed after use.
            with requests.Session() as s:
                url = tree.xpath('//form[@name="zipEntryForm"]/@action')[0].strip()
                s.post('https://peapod.com' + url, data=new_data)
                # An authorised request.
                response = s.get('https://peapod.com/',headers=headers, timeout=15)
                response = s.get(self.product_page_url,headers=headers, timeout=15)
                if response != 'Error' and response.ok:
                    contents = response.text
                    try:
                        self.tree_html = html.fromstring(contents.decode("utf8"))
                    except UnicodeError, e:
                        # if string was not utf8, don't deocde it
                        print "Warning creating html tree from page content: ", e.message
                        self.tree_html = html.fromstring(contents)
                    return

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        product_id = self.tree_html.xpath("//div[@class='buy_button']//a/@href")[0].strip()
        product_id = re.findall(r'\d+', product_id)[0]
        return product_id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//div[@id='product']//dl//dt//text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//div[@id='product']//dl//dt//text()")[0].strip()

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
        line_txts = []
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
        rows = self.tree_html.xpath("//div[@id='productDetails-details']//p")
        line_txts = []
        header_txts = ['<b>Warnings:</b>', '<b>Country of Origin:</b>', '<br>Manufacturer:</b>',
                       '<b>Address:</b>', '<b>Phone:</b>', '>View Substitute Product<',
                       '>View Disclaimer Information<', '<b>Ingredients:</b>']
        rows_begin = self.tree_html.xpath("//div[@id='productDetails-details']/text()")
        rows_begin = [self._clean_text(r) for r in rows_begin if len(self._clean_text(r)) > 0]
        for row in rows_begin:
            line_txt = row
            flag = False
            for header_txt in header_txts:
                if header_txt in line_txt:
                    flag = True
                    break
            if flag:
                break
            if len(line_txt) > 0:
                line_txts.append(line_txt)
                break

        if len(line_txts) < 1:
            for row in rows:
                line_txt = html.tostring(row)
                flag = False
                for header_txt in header_txts:
                    if header_txt in line_txt:
                        flag = True
                        break
                if flag:
                    break
                if len(line_txt) > 0:
                    line_txts.append(line_txt)
                    break
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
        rows = self.tree_html.xpath("//div[@id='productDetails-details']//p")
        line_txts = []
        header_txts = ['<b>Warnings:</b>', '<b>Country of Origin:</b>', '<br>Manufacturer:</b>',
                       '<b>Address:</b>', '<b>Phone:</b>', '>View Substitute Product<',
                       '>View Disclaimer Information<']
        idx = 0
        rows_begin = self.tree_html.xpath("//div[@id='productDetails-details']/text()")
        rows_begin = [self._clean_text(r) for r in rows_begin if len(self._clean_text(r)) > 0]
        for row in rows_begin:
            line_txt = row
            flag = False
            for header_txt in header_txts:
                if header_txt in line_txt:
                    flag = True
                    break
            if flag:
                break
            if len(line_txt) > 0:
                if idx > 0:
                    line_txts.append(line_txt)
                idx += 1

        for row in rows:
            line_txt = html.tostring(row)
            flag = False
            for header_txt in header_txts:
                if header_txt in line_txt:
                    flag = True
                    break
            if flag:
                break
            if len(line_txt) > 0:
                if idx > 0:
                    line_txts.append(line_txt)
                idx += 1
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
        image_url = self.tree_html.xpath("//input[@id='imageURL']/@value")
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
        return None

    def _review_count(self):
        return 0

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
            price = self.tree_html.xpath("//dd[@class='productPrice']//text()")[0].strip()
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
        script_txt = "\n".join(self.tree_html.xpath("//script[@type = 'text/javascript']//text()"))
        m = re.findall(r"tm_category: '(.*?)'", script_txt, re.DOTALL)
        all = [m[0]]
        out = [self._clean_text(r) for r in all]
        if len(out) < 1:
            return None
        return out

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        brand = None
        script_txt = "\n".join(self.tree_html.xpath("//script[@type = 'text/javascript']//text()"))
        m = re.findall(r"tm_brand: '(.*?)\n", script_txt, re.DOTALL)
        brand = m[0][:-1]
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

