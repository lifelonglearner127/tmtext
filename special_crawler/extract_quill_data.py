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


class QuillScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www\.quill\.com/(.*)"

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
    image_urls = None
    image_count = None

    def check_url_format(self):
        # for ex: http://www.quill.com/clorox-toilet-bowl-cleaner-bleach/cbs/040672.html#SkuTabs
        m = re.match(r"^http://www\.quill\.com/(.*)", self.product_page_url)
        return not not m

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''

        if len(self.tree_html.xpath("//div[@class='skuImageZoom']//img")) < 1:
            return True
        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        try:
            product_id = self.tree_html.xpath("//input[@id='SkuData_Sku']//@value")[0].strip()
        except IndexError:
            # http://www.quill.com/hp-elitebook-840-g1-notebook-pc-i5-4300u/cbs/627840.html
            product_id = re.findall(r"(\d*?)\.html", self._url())[0].strip()
        return product_id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//h1[@itemprop='name']//text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//h1[@itemprop='name']//text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()
    
    def _model(self):
        model = self.tree_html.xpath("//div[@itemprop='model']//text()")[0].strip()
        model = re.findall(r"[\d-]+", model)[0].strip()
        return model

    def _upc(self):
        return None

    def _features(self):
        if self.feature_count is not None:
            return self.features
        self.feature_count = 0
        rows = self.tree_html.xpath("//div[@id='skuTabSpecifications']//table//tr")
        line_txts = []
        for row in rows:
            cols = row.xpath(".//td")
            line_txt = ""
            idx = 0
            for col in cols:
                if idx == 0:
                    idx += 1
                    continue
                idx += 1
                col_txt = "".join(col.xpath("./text()"))
                try:
                    cls = col.xpath("./@class")[0].strip()
                except IndexError:
                    cls = []
                if ("attrname" in cls or "attrName" in cls) and len(col_txt) > 0:
                    line_txt += col_txt
                elif ("attrval" in cls or "attrVal" in cls) and len(col_txt) > 0:
                    line_txt += " " +col_txt
                    line_txts.append(line_txt)
                    line_txt = ""
        if len(line_txts) < 1:
            return None
        self.feature_count = len(line_txts)
        self.features = line_txts
        return self.features
        # if self.feature_count is not None:
        #     return self.features
        # self.feature_count = 0
        # rows = self.tree_html.xpath("//div[@id='divSpecifications']//dd")
        # line_txts = []
        # for row in rows:
        #     txt = "".join([r for r in row.xpath(".//text()") if len(self._clean_text(r)) > 0]).strip()
        #     if len(txt) > 0:
        #         line_txts.append(txt)
        # if len(line_txts) < 1:
        #     return None
        # self.feature_count = len(line_txts)
        # self.features = line_txts
        # return self.features

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
        rows = self.tree_html.xpath("//div[contains(@class,'skuDetailsRow')]//ul//li//text()")
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        if len(rows) > 0:
            description += "\n".join(rows)
        if len(description) < 1:
            return None
        return description
        # description = ""
        # rows = self.tree_html.xpath("//div[@class='skuDetailsScene7']//div[contains(@class,'formRow darkGray')]//text()")
        # rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        # if len(rows) > 0:
        #     description += "\n".join(rows)
        # if len(description) < 1:
        #     return None
        # return description

    def _long_description(self):
        description = self._description_helper()
        if description is None or len(description) < 1:
            return None
        return self._long_description_helper()

    def _long_description_helper(self):
        rows = self.tree_html.xpath("//div[@id='SkuTabDescription']//div[contains(@class,'accTabPanel')]//text()")
        line_txts = []
        txt = "".join([r for r in rows if len(self._clean_text(r)) > 0]).strip()
        if len(txt) > 0:
            line_txts.append(txt)
        if len(line_txts) < 1:
            return None
        description = "\n".join(line_txts)
        return description
        # rows = self.tree_html.xpath("//div[@id='divDescription']//ul//li")
        # line_txts = []
        # for row in rows:
        #     txt = "".join([r for r in row.xpath(".//text()") if len(self._clean_text(r)) > 0]).strip()
        #     if len(txt) > 0:
        #         line_txts.append(txt)
        # if len(line_txts) < 1:
        #     return None
        # description = "\n".join(line_txts)
        # return description

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        if self.image_count is not None:
            return self.image_urls
        self.image_count = 0
        image_url = self.tree_html.xpath("//div[@class='s7Thumbs']//div[@class='carouselWrap']//img/@src")
        image_url_tmp = [self._clean_text(r) for r in image_url if len(self._clean_text(r)) > 0]
        if len(image_url_tmp) < 1:
            image_url_tmp = self.tree_html.xpath("//div[contains(@class,'skuImgColScene7')]//div[contains(@class,'skuImageInner')]//img[contains(@class,'skuImageSTD')]/@src")
        image_url = []
        for r in image_url_tmp:
            if "https:" in r:
                image_url.append(r)
            elif "http:" not in r:
                image_url.append("http:%s" % r)
            else:
                image_url.append(r)
        if len(image_url) < 1:
            image_url = self.tree_html.xpath("//div[@class='skuImgColScene7']//div[@class='skuImageZoom']//img/@src")
            image_url = [self._clean_text(r) for r in image_url if len(self._clean_text(r)) > 0]
            if len(image_url) < 1:
                return None
        if len(image_url) == 1:
            try:
                if self._no_image(image_url[0]):
                    return None
            except Exception, e:
                print "WARNING: ", e.message

        if len(image_url) < 1:
            return None
        self.image_urls = image_url
        self.image_count = len(self.image_urls)

        return self.image_urls

    def _image_count(self):
        if self.image_count is None:
            self._image_urls()
        return self.image_count

    def _video_urls(self):
        if self.video_count is not None:
            return self.video_urls
        self.video_count = 0
        video_urls = []
        # Request URL:http://content.webcollage.net/quill/smart-button?ignore-jsp=true&ird=true&channel-product-id=267655
        try:
            sku_data = self.tree_html.xpath("//input[@id='SkuData_Sku']/@value")[0].strip()
        except IndexError:
            sku_data = None

        if sku_data is not None:
            url = "http://content.webcollage.net/quill/smart-button?ignore-jsp=true&ird=true&channel-product-id=%s" % sku_data
            contents = urllib.urlopen(url).read()
            # wcsb:url=\"http:\/\/content.webcollage.net\/stapleslink-en\/product-content-page?channel-product-id=957754&amp;wcpid=lysol-1358965925135&amp;report-event=product-button-click&amp;usemap=0\"
            # \/552b9366-55ed-443c-b21e-02ede6dd89aa.mp4.mobile.mp4\"
            m = re.findall(r'"src":"([^"]*?\.flv)",', contents.replace("\\",""), re.DOTALL)
            m = ["http://content.webcollage.net%s" % r for r in m]
            if len(m) > 0:
                video_urls += m

            m2 = re.findall(r'wc-media wc-iframe(.*?)>', contents.replace("\\",""), re.DOTALL)
            try:
                m = re.findall(r'data-asset-url="(.*?)"', m2[0], re.DOTALL)
                if len(m) > 0:
                    video_urls += m
            except IndexError:
                pass

            m = re.findall(r'wcobj="(.*?)"', contents.replace("\\",""), re.DOTALL)
            if len(m) > 0:
                url_wc = m[0]
                contents_wc = urllib.urlopen(url_wc).read()
                # document.location.replace('
                tree = html.fromstring(contents_wc)
                try:
                    playerKey = tree.xpath("//param[@name='playerKey']/@value")[0].strip()
                    videos = tree.xpath("//li[contains(@class,'video_slider_item')]/@video_id")
                    for video in videos:
                        # http://client.expotv.com/video/config/539028/4ac5922e8961d0cbec0cc659740a5398
                        url_wc2 = "http://client.expotv.com/video/config/%s/%s" % (video, playerKey)
                        contents_wc2 = urllib.urlopen(url_wc2).read()
                        jsn = json.loads(contents_wc2)
                        jsn = jsn["sources"]
                        for item in jsn:
                            try:
                                file_name = item['file']
                                video_urls.append(file_name)
                                break
                            except:
                                pass
                except IndexError:
                    pass

        # http://media.flixcar.com/delivery/inpage/show/751/us/846426/json?c=jsonpcar751us846426&complimentary=0&type=.html
        # data-flix-distributor="751"
        try:
            flix_distributor = self.tree_html.xpath("//div[@id='Quill']//script/@data-flix-distributor")[0].strip()
            flix_lang = self.tree_html.xpath("//div[@id='Quill']//script/@data-flix-language")[0].strip()
            data_flix_mpn = self.tree_html.xpath("//div[@id='Quill']//script/@data-flix-mpn")[0].strip()
            data_flix_mpn = data_flix_mpn.replace('#', '%23')
            url = "http://media.flixcar.com/delivery/js/minisite/%s/%s/mpn/%s/null/%s" % (flix_distributor, flix_lang, data_flix_mpn, self._product_id())
            contents = urllib.urlopen(url).read()
            ff_id = re.findall(r'_FFMatcher\._FFmain\((.*?)\)', contents, re.DOTALL)[0].strip()
            ff_id = re.findall(r"'us','(.*?)'", ff_id, re.DOTALL)[0].strip()
            url_flix = "http://media.flixcar.com/delivery/inpage/show/%s/%s/%s/" % (flix_distributor, flix_lang, ff_id)
            # contents_flix = urllib.urlopen(url_flix).read()
            contents_flix = requests.get(url_flix).text
            tree_flix = html.fromstring(contents_flix)
            videos = tree_flix.xpath("//div[contains(@class,'inpage_cap_videos')]//ul[contains(@class,'inpage_block_inner')]/li[contains(@class,'inpage_cap_gallery_link')]/a/@href")
            video_urls += videos
        except IndexError:
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
        if self.pdf_count is not None:
            return self.pdf_urls
        self.pdf_count = 0
        pdfs = self.tree_html.xpath("//div[@id='PageInner']//a[contains(@href,'.pdf')]")
        pdf_hrefs = []
        for pdf in pdfs:
            pdf_url_txts = [self._clean_text(r) for r in pdf.xpath(".//text()") if len(self._clean_text(r)) > 0]
            if len(pdf_url_txts) > 0:
                pdf_hrefs.append(pdf.attrib['href'])

        # get from webcollage
        # http://content.webcollage.net/quill/smart-button?ignore-jsp=true&ird=true&channel-product-id=392495
        url = "http://content.webcollage.net/quill/smart-button?ignore-jsp=true&ird=true&channel-product-id=%s" % self._product_id()
        contents = urllib.urlopen(url).read()
        contents = contents.replace("\\", "")
        wc_pdfs = re.findall(r'wcobj="(.*?)"', contents, re.DOTALL)
        wc_pdfs = [r.replace("\\", "") for r in wc_pdfs if r.endswith(".pdf")]
        pdf_hrefs += wc_pdfs

        # Request URL:http://media.flixcar.com/delivery/inpage/show/751/us/833093/json?c=jsonpcar751us833093&complimentary=0&type=.html
        # Request URL:http://media.flixcar.com/delivery/inpage/show/751/us/833093/json?c=jsonpcar751us833093&complimentary=0&type=.html
        # http://media.flixcar.com/delivery/js/minisite/751/us/mpn/E3E02A%23B1H/null/50686187?d=751&l=us&mpn=E3E02A%23B1H&sku=50686187&dom=flix-minisite&fl=en&ext=.js
        try:
            flix_distributor = self.tree_html.xpath("//div[@id='Quill']//script/@data-flix-distributor")[0].strip()
            flix_lang = self.tree_html.xpath("//div[@id='Quill']//script/@data-flix-language")[0].strip()
            data_flix_mpn = self.tree_html.xpath("//div[@id='Quill']//script/@data-flix-mpn")[0].strip()
            data_flix_mpn = data_flix_mpn.replace('#', '%23')
            url = "http://media.flixcar.com/delivery/js/minisite/%s/%s/mpn/%s/null/%s" % (flix_distributor, flix_lang, data_flix_mpn, self._product_id())
            contents = urllib.urlopen(url).read()
            ff_id = re.findall(r'_FFMatcher\._FFmain\((.*?)\)', contents, re.DOTALL)[0].strip()
            ff_id = re.findall(r"'us','(.*?)'", ff_id, re.DOTALL)[0].strip()
            url = "http://media.flixcar.com/delivery/inpage/show/%s/%s/%s/json?c=jsonpcar%s%s%s&complimentary=0&type=.html" % \
                  (flix_distributor, flix_lang, ff_id, flix_distributor, flix_lang, ff_id)
            # contents = urllib.urlopen(url).read()
            contents = requests.get(url).text
            tree = html.fromstring(contents.replace("\\", ""))
            ff_pdfs = tree.xpath("//div[contains(@class,'inpage_cap_more-info')]//a/@href")
            ff_pdfs = list(set(ff_pdfs))
            pdf_hrefs += ff_pdfs
        except IndexError:
            pass

        if len(pdf_hrefs) < 1:
            return None
        self.pdf_count = len(pdf_hrefs)
        return pdf_hrefs

    def _pdf_count(self):
        if self.pdf_count is None:
            self._pdf_urls()
        return self.pdf_count

    def _webcollage(self):
        # http://content.webcollage.net/pg-estore/power-page?ird=true&channel-product-id=037000864868
        url = "http://content.webcollage.net/quill/smart-button?ignore-jsp=true&ird=true&channel-product-id=%s" % self._product_id()
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
    #populate the reviews_tree variable for use by other functions
    def _load_reviews(self):
        if not self.max_score or not self.min_score:
            self.review_count = int(self.tree_html.xpath("//span[@class='count']//text()")[0].strip())
            self.average_review = float(self.tree_html.xpath("//span[@class='pr-rating pr-rounded average']//text()")[0].strip())
            rows = self.tree_html.xpath("//p[@class='pr-histogram-count']//text()")
            self.reviews = []
            idx = 5
            rv_scores = []
            for row in rows:
                cnt = int(re.findall(r"\d+", row)[0])
                if cnt > 0:
                    self.reviews.append([idx, cnt])
                    rv_scores.append(idx)
                idx -= 1
                if idx < 1:
                    break
            self.max_score = max(rv_scores)
            self.min_score = min(rv_scores)

            # SOAP.COM REVIEWS

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
        rows = self.tree_html.xpath("//a[@id='myAddToCart_sku']")
        if len(rows) > 0:
            return 0
        return 1

    def _in_stores_out_of_stock(self):
        '''in_stores_out_of_stock - currently unavailable for pickup from a physical store - binary
        (null should be used for items that can not be ordered online and the availability may depend on location of the store)
        '''
        return None

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        all = self.tree_html.xpath("//div[@id='skuBreadCrumbs']//span[@itemprop='title']//text()")
        out = [self._clean_text(r) for r in all]
        if len(out) < 1:
            return None
        return out

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        if self.feature_count is None:
            self._features()
        for item in self.features:
            if "Brand :" in item or "brand :" in item or "Brand:" in item or "brand:" in item:
                brand = item.replace("Brand :", "")
                brand = brand.replace("Brand:", "")
                brand = brand.replace("brand :", "")
                brand = brand.replace("brand", "")
                brand = brand.strip()
                return brand
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
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \
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

        # CONTAINER : PAGE_ATTRIBUTES
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        "webcollage" : _webcollage, \
    }

