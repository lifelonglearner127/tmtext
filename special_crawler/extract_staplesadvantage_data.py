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


class StaplesAdvantageScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www\.staplesadvantage\.com/webapp/wcs/stores/servlet/StplShowItem\?(.*)"

    reviews_tree = None
    max_score = None
    min_score = None
    review_count = None
    average_review = None
    reviews = None
    pdf_urls = None
    pdf_count = 0
    video_urls = None
    video_count = 0

    def check_url_format(self):
        # for ex: http://www.staplesadvantage.com/webapp/wcs/stores/servlet/StplShowItem?cust_sku=383249&catalogId=4&item_id=71504599&langId=-1&currentSKUNbr=383249&storeId=10101&itemType=0&pathCatLvl1=125128966&pathCatLvl2=125083501&pathCatLvl3=-999999&pathCatLvl4=117896272
        m = re.match(r"^http://www\.staplesadvantage\.com/webapp/wcs/stores/servlet/StplShowItem\?(.*)", self.product_page_url)
        return not not m

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        rows = self.tree_html.xpath("//div[@class='productpics']//div[@id='s7FlashViewer']")
        if len(rows) > 0:
            return False
        return True

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        # http://www.staplesadvantage.com/webapp/wcs/stores/servlet/StplShowItem?cust_sku=310342&catalogId=4&item_id=71341298&langId=-1&currentSKUNbr=310342&storeId=10101&itemType=0&pathCatLvl1=125128966&pathCatLvl2=125083501&pathCatLvl3=-999999&pathCatLvl4=125083516&addWE1ToCart=true
        id = self.tree_html.xpath("//div[@class='maindetailitem']//input[@name='currentSKUNumber']/@value")[0].strip()
        return id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//div[@class='maindetailitem']//h3//text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//div[@class='maindetailitem']//h3//text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//div[@class='maindetailitem']//h3//text()")[0].strip()
    
    def _model(self):
        return None

    def _upc(self):
        upc = self.tree_html.xpath("//span[@class='staplesSKUNumber']//text()")[0].strip()
        return upc

    def _features(self):
        rows = self.tree_html.xpath("//table[@class='specifications']//tr")
        line_txts = []
        for row in rows:
            try:
                head_txt = "".join(row.xpath(".//th//text()")).strip()
                txt = "".join(row.xpath(".//td//text()")).strip()
                txt = "%s: %s" % (head_txt, txt)
                if len(txt.strip()) > 0:
                    line_txts.append(txt)
            except:
                pass
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
        line_txts = []
        rows = self.tree_html.xpath("//div[contains(@id, 'section1_pane')]")
        for row in rows:
            try:
                txt = row.xpath(".//div[@class='tabs_instead_title']//text()")[0].strip()
            except IndexError:
                continue
            if txt == "Description":
                line_txts = row.xpath(".//text()")
                if line_txts[0] == "Description":
                    line_txts = line_txts[1:]

        if len(line_txts) < 1:
            return None
        description = "\n".join(line_txts)
        return description

    def _long_description(self):
        description = self._description_helper()
        if description is None or len(description) < 1:
            return None
        return self._long_description_helper()

    def _long_description_helper(self):
        return None

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_url = self.tree_html.xpath("//div[@class='maindetailitem']//div[@class='productpics']//li//img/@src")
        image_url = ["http://www.staplesadvantage.com%s" % r for r in image_url if "s0930105_sc7" not in r]
        if len(image_url) < 1:
            image_url = self.tree_html.xpath("//div[@class='maindetailitem']//div[@class='productpics']//div[contains(@class,'showinprint')]//img[@class='mainproductimage']/@src")
            image_url = ["http://www.staplesadvantage.com%s" % r for r in image_url if "s0930105_sc7" not in r]
            if len(image_url) < 1:
                return None
        return image_url

    def _image_count(self):
        image_urls = self._image_urls()
        if image_urls:
            return len(image_urls)
        return 0

    def _video_urls(self):
        if self.video_urls is not None:
            return self.video_urls
        video_urls = []
        # https://scontent.webcollage.net/stapleslink-en/sb-for-ppp?ird=true&channel-product-id=957754
        url = "https://scontent.webcollage.net/stapleslink-en/sb-for-ppp?ird=true&channel-product-id=%s" % self._product_id()
        req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
        contents = urllib2.urlopen(req).read()
        # wcsb:url=\"http:\/\/content.webcollage.net\/stapleslink-en\/product-content-page?channel-product-id=957754&amp;wcpid=lysol-1358965925135&amp;report-event=product-button-click&amp;usemap=0\"
        # \/552b9366-55ed-443c-b21e-02ede6dd89aa.mp4.mobile.mp4\"
        m = re.findall(r'wcsb:url="(.*?)"', contents.replace("\\",""), re.DOTALL)
        if len(m) > 0:
            url_wc = m[0]
            req_wc = urllib2.Request(url_wc, headers={'User-Agent' : "Magic Browser"})
            contents_wc = urllib2.urlopen(req_wc).read()
            # document.location.replace('
            m_wc = re.findall(r'document.location.replace\(\'(.*?)\'\);', contents_wc.replace("\\",""), re.DOTALL)
            if len(m_wc) > 0:
                url_wc2 = m_wc[0]
                req_wc2 = urllib2.Request(url_wc2, headers={'User-Agent' : "Magic Browser"})
                contents_wc2 = urllib2.urlopen(req_wc2).read()
                tree = html.fromstring(contents_wc2)
                rows = tree.xpath("//div[contains(@class,'wc-pc-tabs')]//li")
                for row in rows:
                    txt = " ".join(row.xpath(".//text()"))
                    if "Customer Reviews" in txt:
                        url_wc3 = "http://content.webcollage.net%s" % row.xpath(".//a/@href")[0].strip()
                        req_wc3 = urllib2.Request(url_wc3, headers={'User-Agent' : "Magic Browser"})
                        contents_wc3 = urllib2.urlopen(req_wc3).read()
                        tree3 = html.fromstring(contents_wc3)
                        url_wc4 = tree3.xpath("//iframe/@src")[0].strip()
                        req_wc4 = urllib2.Request(url_wc4, headers={'User-Agent' : "Magic Browser"})
                        contents_wc4 = urllib2.urlopen(req_wc4).read()
                        tree4 = html.fromstring(contents_wc4)
                        playerKey = tree4.xpath("//param[@name='playerKey']/@value")[0].strip()
                        video = tree4.xpath("//param[@name='video']/@value")[0].strip()
                        # http://client.expotv.com/video/config/539028/4ac5922e8961d0cbec0cc659740a5398
                        url_wc5 = "http://client.expotv.com/video/config/%s/%s" % (video, playerKey)
                        req_wc5 = urllib2.Request(url_wc5, headers={'User-Agent' : "Magic Browser"})
                        contents_wc5 = urllib2.urlopen(req_wc5).read()
                        jsn = json.loads(contents_wc5)
                        jsn = jsn["sources"]
                        for item in jsn:
                            try:
                                file_name = item['file']
                                video_urls.append(file_name)
                            except:
                                pass
        if len(video_urls) < 1:
            return None
        self.video_urls = video_urls
        self.video_count = len(self.video_urls)
        return video_urls

    def _video_count(self):
        if self.video_urls is None:
            self._video_urls()
        return self.video_count

    def _pdf_urls(self):
        if self.pdf_urls is not None:
            return self.pdf_urls
        pdfs = self.tree_html.xpath("//a[contains(@href,'.pdf')]")
        pdf_hrefs = []
        for pdf in pdfs:
            pdf_url_txts = [self._clean_text(r) for r in pdf.xpath(".//text()") if len(self._clean_text(r)) > 0]
            if len(pdf_url_txts) > 0:
                pdf_hrefs.append(pdf.attrib['href'])

        # get from webcollage
        # https://scontent.webcollage.net/stapleslink-en/smart-button?ird=true&channel-product-id=616321
        url = "https://scontent.webcollage.net/stapleslink-en/smart-button?ird=true&channel-product-id=%s" % self._product_id()
        contents = urllib.urlopen(url).read()
        wc_pdfs = re.findall(r'href=\\\"([^ ]*?\.pdf)', contents, re.DOTALL)
        wc_pdfs = [r.replace("\\", "") for r in wc_pdfs]
        pdf_hrefs += wc_pdfs
        if len(pdf_hrefs) < 1:
            return None
        self.pdf_count = len(pdf_hrefs)
        return pdf_hrefs

    def _pdf_count(self):
        if self.pdf_urls is None:
            self._pdf_urls()
        return self.pdf_count

    def _webcollage(self):
        # https://scontent.webcollage.net/stapleslink-en/smart-button?ird=true&channel-product-id=823292
        url = "https://scontent.webcollage.net/stapleslink-en/smart-button?ird=true&channel-product-id=%s" % self._product_id()
        contents = urllib.urlopen(url).read()
        m = re.findall(r"_wccontent = (\{.*?\});", contents, re.DOTALL)
        # jsn = json.loads(m[0].replace("\r\n", ""))
        # html = jsn["aplus"]["html"]
        html = m[0]
        if ".webcollage.net" in html:
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
            txt = self.tree_html.xpath("//div[contains(@class,'maindetailitem')]//div[@class='pr-snippet-stars']//div[contains(@data-histogram,'noOfReviews')]/@data-histogram")[0].strip()
            # ["{'noOfReviews':7,'numOfFives':4,'numOfFours':3,'numOfThrees':0,'numOfTwos':0,'numOfOnes':0}"]
            rows = []
            cnt_tmp = int(re.findall(r"numOfFives'\:(\d+)", txt)[0].strip())
            rows.append(cnt_tmp)
            cnt_tmp = int(re.findall(r"numOfFours'\:(\d+)", txt)[0].strip())
            rows.append(cnt_tmp)
            cnt_tmp = int(re.findall(r"numOfThrees'\:(\d+)", txt)[0].strip())
            rows.append(cnt_tmp)
            cnt_tmp = int(re.findall(r"numOfTwos'\:(\d+)", txt)[0].strip())
            rows.append(cnt_tmp)
            cnt_tmp = int(re.findall(r"numOfOnes'\:(\d+)", txt)[0].strip())
            rows.append(cnt_tmp)

            self.reviews = []
            idx = 5
            rv_scores = []
            for cnt in rows:
                if cnt > 0:
                    self.reviews.append([idx, cnt])
                    rv_scores.append(idx)
                idx -= 1
                if idx < 1:
                    break
            self.max_score = max(rv_scores)
            self.min_score = min(rv_scores)

    def _average_review(self):
        txt = self.tree_html.xpath("//div[contains(@class,'maindetailitem')]//div[@class='pr-snippet-stars']//span[contains(@class,'pr-snippet-rating-decimal')]//text()")[0].strip()
        avg_review = re.findall(r"^(.*?) of", txt)[0].strip()
        avg_review = round(float(avg_review), 2)
        return avg_review

    def _review_count(self):
        txt = self.tree_html.xpath("//div[contains(@class,'maindetailitem')]//a[contains(@class,'pr-snippet-link')]//text()")[0].strip()
        review_cnt = re.findall(r"^(.*?) reviews", txt)[0].strip()
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
        price = "price depends on customer"
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
        return None

    def _in_stores_out_of_stock(self):
        '''in_stores_out_of_stock - currently unavailable for pickup from a physical store - binary
        (null should be used for items that can not be ordered online and the availability may depend on location of the store)
        '''
        return None

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        all = self.tree_html.xpath("//ul[@id='breadcrumbs']//li//a//text()")
        out = [self._clean_text(r) for r in all]
        if out[0] == "Home":
            out = out[1:]
        if len(out) < 1:
            return None
        return out

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        brand = None
        trs = self.tree_html.xpath("//table[@class='specifications']//tr")
        for tr in trs:
            try:
                head_txt = tr.xpath(".//th//text()")[0].strip()
                if head_txt == "Brand Name":
                    brand = tr.xpath(".//td//text()")[0].strip()
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
        # CONTAINER : PAGE_ATTRIBUTES
        "webcollage" : _webcollage, \
    }

