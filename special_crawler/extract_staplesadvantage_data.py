#!/usr/bin/python
#  -*- coding: utf-8 -*-

import urllib
import re
import sys
import json
import os.path
import cStringIO
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

    INVALID_URL_MESSAGE = "Expected URL format is http(s)://www\.staplesadvantage\.com/webapp/wcs/stores/servlet/StplShowItem\?(.*)"

    description = None
    long_description = None
    shelf_description = None
    reviews_tree = None
    max_score = None
    min_score = None
    review_count = None
    average_review = None
    reviews = None
    pdf_urls = None
    pdf_count = 0
    video_urls = None
    video_count = None
    feature_count = None
    features = None

    def check_url_format(self):
        # for ex: https://www.staplesadvantage.com/webapp/wcs/stores/servlet/StplShowItem?cust_sku=383249&catalogId=4&item_id=71504599&langId=-1&currentSKUNbr=383249&storeId=10101&itemType=0&pathCatLvl1=125128966&pathCatLvl2=125083501&pathCatLvl3=-999999&pathCatLvl4=117896272
        m = re.match(r"^(http|https)://www\.staplesadvantage\.com/webapp/wcs/stores/servlet/StplShowItem\?(.*)", self.product_page_url)
        return not not m

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        rows = self.tree_html.xpath("//div[contains(@class, 'product-detail-container')]")
        if len(rows) > 0:
            return False
        return True

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        # https://www.staplesadvantage.com/webapp/wcs/stores/servlet/StplShowItem?cust_sku=310342&catalogId=4&item_id=71341298&langId=-1&currentSKUNbr=310342&storeId=10101&itemType=0&pathCatLvl1=125128966&pathCatLvl2=125083501&pathCatLvl3=-999999&pathCatLvl4=125083516&addWE1ToCart=true
        try:
            id = self.tree_html.xpath("//div[@class='maindetailitem']//input[@name='currentSKUNumber']/@value")[0].strip()
        except IndexError:
            id = self.tree_html.xpath("//input[@name='currentSKUNumber']/@value")[0].strip()
        return id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        product_name = self.tree_html.xpath("//h1[contains(@class,'search-prod-desc')]//text()[normalize-space()!='']")[0]
        return product_name

    def _product_title(self):
        return self.tree_html.xpath("//h1[contains(@class,'search-prod-desc')]//text()[normalize-space()!='']")[0]

    def _title_seo(self):
        return self.tree_html.xpath("//h1[contains(@class,'search-prod-desc')]//text()[normalize-space()!='']")[0]
    
    def _model(self):
        return None

    def _upc(self):
        upc = self.tree_html.xpath("//span[@class='staplesSKUNumber']//text()")[0].strip()
        return upc

    def _features(self):
        if self.feature_count is not None:
            return self.features
        self.feature_count = 0
        line_txts = []
        # https://scontent.webcollage.net/stapleslink-en/sb-for-ppp?ird=true&channel-product-id=957754
        url = "https://scontent.webcollage.net/stapleslink-en/sb-for-ppp?ird=true&channel-product-id=%s" % self._product_id()
        contents = urllib.urlopen(url).read()
        # wcsb:url=\"http:\/\/content.webcollage.net\/stapleslink-en\/product-content-page?channel-product-id=957754&amp;wcpid=lysol-1358965925135&amp;report-event=product-button-click&amp;usemap=0\"
        # \/552b9366-55ed-443c-b21e-02ede6dd89aa.mp4.mobile.mp4\"
        m = re.findall(r'wcsb:url="(.*?)"', contents.replace("\\",""), re.DOTALL)
        if len(m) > 0:
            url_wc = m[0]
            contents_wc = urllib.urlopen(url_wc).read()
            # document.location.replace('
            m_wc = re.findall(r'document.location.replace\(\'(.*?)\'\);', contents_wc.replace("\\",""), re.DOTALL)
            if len(m_wc) > 0:
                url_wc2 = m_wc[0]
                contents_wc2 = urllib.urlopen(url_wc2).read()
                tree = html.fromstring(contents_wc2)
                rows = tree.xpath("//div[contains(@class,'wc-pc-tabs')]//li")
                for row in rows:
                    txt = " ".join(row.xpath(".//text()"))
                    if "Features" in txt:
                        url_wc3 = "http://content.webcollage.net%s" % row.xpath(".//a/@href")[0].strip()
                        contents_wc3 = urllib.urlopen(url_wc3).read()
                        tree3 = html.fromstring(contents_wc3)
                        h3_tags = tree3.xpath("//div[@id='wc-reset']//ul/li//h3//text()")
                        div_tags = tree3.xpath("//div[@id='wc-reset']//ul/li//div[contains(@class,'wc-rich-content-description')]//text()")
                        try:
                            for i in range(len(h3_tags)):
                                line_txts.append("%s: %s" % (h3_tags[i], div_tags[i]))
                        except IndexError:
                            pass

        if len(line_txts) < 1:
            rows = self.tree_html.xpath("//div[contains(@class,'product-details-speci')]//table[@class='specy-table']//tr")
            line_txts = []
            for row in rows:
                try:
                    head_txt = "".join(row.xpath(".//td[1]//text()")).strip()
                    txt = "".join(row.xpath(".//td[2]//text()")).strip()
                    txt = "%s: %s" % (head_txt, txt)
                    if len(txt.strip()) > 0:
                        line_txts.append(txt)
                except:
                    pass
        self.features = line_txts
        self.feature_count = len(self.features)
        return self.features

    def _feature_count(self):
        if self.feature_count is None:
            self._features()
        return self.feature_count

    def _model_meta(self):
        return None

    def _description(self):
        self._description_helper()

        if self.description:
            return self.description

    def _shelf_description(self):
        self._description_helper()

        if self.shelf_description:
            return self.shelf_description

    def _long_description(self):
        self._description_helper()

        if self.long_description:
            return self.long_description

    def _description_helper(self):
        if not self.description or not self.shelf_description or self.long_description:
            headline = self.tree_html.xpath("//div[contains(@class,'product-details')]//p[contains(@class, 'headliner')]//text()")[0]
            expanded_descr = self.tree_html.xpath("//div[contains(@class,'product-details')]//p[contains(@class, 'whyBuyProductDetailPage')]//text()")[0]
            bullet_list = self.tree_html.xpath("//div[contains(@class,'product-details-desc')]//ul/li//text()")
            bullet_list = [r for r in bullet_list if len(self._clean_text(r)) > 0]
            if len(bullet_list) < 1:
                return None
            bullet_list = "\n".join(bullet_list)

            self.description = headline
            self.shelf_description = expanded_descr
            self.long_description = headline + "\n" + expanded_descr + "\n" + bullet_list

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        rows = self.tree_html.xpath("//div[@id='altquickimgalt']//ul/li//a/img/@src")
        image_url = ["https://www.staplesadvantage.com%s" % r for r in rows]
        if len(image_url) < 1:
            script = "\n".join(self.tree_html.xpath("//script//text()"))
            m = re.findall("enlargedImageURL = '([^']*)'", script, re.DOTALL)
            image_url = list(set(m))
            image_url = ["https://www.staplesadvantage.com%s" % r for r in image_url]
        if len(image_url) < 1:
            return None
        try:
            if self._no_image(image_url[0]):
                return None
        except Exception, e:
            print "WARNING: ", e.message
        # image_url = self.tree_html.xpath("//div[@class='maindetailitem']//div[@class='productpics']//li//img/@src")
        # image_url = ["https://www.staplesadvantage.com%s" % r for r in image_url if "s0930105_sc7" not in r]
        # if len(image_url) < 1:
        #     image_url = self.tree_html.xpath("//div[@class='maindetailitem']//div[@class='productpics']//div[contains(@class,'showinprint')]//img[@class='mainproductimage']/@src")
        #     image_url = ["https://www.staplesadvantage.com%s" % r for r in image_url if "s0930105_sc7" not in r]
        #     if len(image_url) < 1:
        #         return None
        return image_url

    def _image_count(self):
        image_urls = self._image_urls()
        if image_urls:
            return len(image_urls)
        return 0

    def _video_urls(self):
        if self.video_count is not None:
            return self.video_urls
        self.video_count = 0
        video_urls = []
        # https://scontent.webcollage.net/stapleslink-en/sb-for-ppp?ird=true&channel-product-id=957754
        url = "https://scontent.webcollage.net/stapleslink-en/sb-for-ppp?ird=true&channel-product-id=%s" % self._product_id()
        contents = urllib.urlopen(url).read()
        # wcsb:url=\"http:\/\/content.webcollage.net\/stapleslink-en\/product-content-page?channel-product-id=957754&amp;wcpid=lysol-1358965925135&amp;report-event=product-button-click&amp;usemap=0\"
        # \/552b9366-55ed-443c-b21e-02ede6dd89aa.mp4.mobile.mp4\"
        m = re.findall(r'wcsb:url="(.*?)"', contents.replace("\\",""), re.DOTALL)
        if len(m) > 0:
            url_wc = m[0]
            contents_wc = urllib.urlopen(url_wc).read()
            # document.location.replace('
            m_wc = re.findall(r'document.location.replace\(\'(.*?)\'\);', contents_wc.replace("\\",""), re.DOTALL)
            if len(m_wc) > 0:
                url_wc2 = m_wc[0]
                contents_wc2 = urllib.urlopen(url_wc2).read()
                tree = html.fromstring(contents_wc2)
                rows = tree.xpath("//div[contains(@class,'wc-pc-tabs')]//li")
                for row in rows:
                    txt = " ".join(row.xpath(".//text()"))
                    if "Customer Reviews" in txt:
                        url_wc3 = "http://content.webcollage.net%s" % row.xpath(".//a/@href")[0].strip()
                        contents_wc3 = urllib.urlopen(url_wc3).read()
                        tree3 = html.fromstring(contents_wc3)
                        url_wc4 = tree3.xpath("//iframe/@src")[0].strip()
                        contents_wc4 = urllib.urlopen(url_wc4).read()
                        tree4 = html.fromstring(contents_wc4)
                        playerKey = tree4.xpath("//param[@name='playerKey']/@value")[0].strip()
                        video_ids = tree4.xpath("//div[@id='video_slider']//li[contains(@class,'video_slider_item')]/@video_id")
                        for video in video_ids:
                            # http://client.expotv.com/video/config/539028/4ac5922e8961d0cbec0cc659740a5398
                            url_wc5 = "http://client.expotv.com/video/config/%s/%s" % (video, playerKey)
                            contents_wc5 = urllib.urlopen(url_wc5).read()
                            jsn = json.loads(contents_wc5)
                            jsn = jsn["sources"]
                            for item in jsn:
                                try:
                                    file_name = item['file']
                                    video_urls.append(file_name)
                                    break
                                except:
                                    pass
                if len(rows) < 1:
                    url_wc4 = tree.xpath("//iframe/@src")[0].strip()
                    contents_wc4 = urllib.urlopen(url_wc4).read()
                    tree4 = html.fromstring(contents_wc4)
                    playerKey = tree4.xpath("//param[@name='playerKey']/@value")[0].strip()
                    video_ids = tree4.xpath("//div[@id='video_slider']//li[contains(@class,'video_slider_item')]/@video_id")
                    for video in video_ids:
                        # http://client.expotv.com/video/config/539028/4ac5922e8961d0cbec0cc659740a5398
                        url_wc5 = "http://client.expotv.com/video/config/%s/%s" % (video, playerKey)
                        contents_wc5 = urllib.urlopen(url_wc5).read()
                        jsn = json.loads(contents_wc5)
                        jsn = jsn["sources"]
                        for item in jsn:
                            try:
                                file_name = item['file']
                                video_urls.append(file_name)
                                break
                            except:
                                pass

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

        if not self.review_count or self.average_review or self.max_score or not self.min_score:
            prod_id = self._product_id()
            url = "https://yotpo.staplesadvantage.com/v1/widget/RP5gD6RV7AVy75jjXQPUI1AOChyNNClZqkm94Ttb/products/" + prod_id + "/reviews.json?per_page=10&page=1&sort=votes_up&direction=desc&fromAjax=Y"
            product_json = json.loads(self.load_page_from_url_with_number_of_retries(
                url))
            review_info = product_json["response"]["bottomline"]

            self.review_count = review_info["total_review"]
            self.average_review = review_info["average_score"]
            self.reviews = review_info["star_distribution"]

            rv_scores = []
            for score, cnt in self.reviews.iteritems():
                if cnt > 0:
                    rv_scores.append(score)

            self.max_score = max(rv_scores)
            self.min_score = min(rv_scores)

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

    def _owned(self):
        '''General function for setting value of legacy field "owned".
        It will be inferred from value of "site_online_in_stock" field.
        Method can be overwritten by scraper class if different implementation
        is available.
        '''
        return self._site_online()

    def _owned_out_of_stock(self):
        '''General function for setting value of legacy field "owned_out_of_stock".
        It will be inferred from value of "site_online_out_of_stock" field.
        Method can be overwritten by scraper class if different implementation
        is available.
        '''
        return 0

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        all = self.tree_html.xpath("//ul[contains(@class,'search-breadcrumb')]//li//a//text()")
        out = [self._clean_text(r) for r in all]
        if out[0] == "Home":
            out = out[1:]
        if len(out) < 1:
            return None
        return out

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        brand = self.tree_html.xpath("//td[@class='productspeci-value']//text()")[0].strip()
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
        "model" : _model, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
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
        # CONTAINER : PRODUCT_INFO
        "description" : _description, \
        "shelf_description" : _shelf_description, \
        "long_description" : _long_description, \

        # CONTAINER : PRODUCT_INFO
        "features" : _features, \
        "feature_count" : _feature_count, \

        # CONTAINER : PAGE_ATTRIBUTES
        "webcollage" : _webcollage, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
    }

