#!/usr/bin/python
#  -*- coding: utf-8 -*-

import urllib
import re
import sys
import json
import lxml
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

from spiders_shared_code.target_variants import TargetVariants

class TargetScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www\.target\.com/p/([a-zA-Z0-9\-]+)/-/A-([0-9A-Za-z]+)"

    reviews_tree = None
    max_score = None
    min_score = None
    review_count = None
    average_review = None
    reviews = None
    video_count = None

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        self.tv = TargetVariants()
        self.product_json = None

    def check_url_format(self):
        # for ex: http://www.target.com/p/skyline-custom-upholstered-swoop-arm-chair/-/A-15186757#prodSlot=_1_1
        m = re.match(r"^http://www\.target\.com/p/([a-zA-Z0-9\-]+)/-/A-([0-9A-Za-z]+)", self.product_page_url)
        return not not m

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''

        self.tv.setupCH(self.tree_html)

        if len(self.tree_html.xpath("//h2[starts-with(@class, 'product-name item')]/span/text()")) < 1:
            return True

        self._extract_product_json()

        return False

    def _extract_product_json(self):
        if self.tree_html.xpath("//script[contains(text(), 'Target.globals.refreshItems =')]/text()"):
            product_json = self.tree_html.xpath("//script[contains(text(), 'Target.globals.refreshItems =')]/text()")[0]
            start_index = product_json.find("Target.globals.refreshItems =") + len("Target.globals.refreshItems =")
            product_json = product_json[start_index:]
            product_json = json.loads(product_json)
        else:
            product_json = None

        self.product_json = product_json

        return self.product_json

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
        return self.tree_html.xpath("//meta[@property='og:upc']/@content")[0].strip()

    def _features(self):
        rows = self.tree_html.xpath("//ul[@class='normal-list']//li")
        feature_list = []

        for row in rows:
            feature_list.append(row.text_content().strip())

        if feature_list:
            return feature_list

        return None

    def _feature_count(self):
        features = len(self._features())
        if features is None:
            return 0
        return len(self._features())

    def _model_meta(self):
        return None

    def _description(self):
        description = "".join(self.tree_html.xpath("//span[@itemprop='description']//text()")).strip()
        description_copy = "".join(self.tree_html.xpath("//div[@class='details-copy']//text()")).strip()
        if description in description_copy:
            description = description_copy
        rows = self.tree_html.xpath("//ul[@class='normal-list']//li")
        lis = []
        for r in rows:
            try:
                strong = r.xpath(".//strong//text()")[0].strip()
                if strong[-1:] == ":":
                    break
            except IndexError:
                pass
            #not feature
            row_txt = " ".join([self._clean_text(i) for i in r.xpath(".//text()") if len(self._clean_text(i)) > 0]).strip()
            row_txt = row_txt.replace("\t", "")
            row_txt = row_txt.replace("\n", "")
            row_txt = row_txt.replace(" , ", ", ")
            lis.append(row_txt)
        description_2nd = "\n".join(lis)
        if len(description_2nd) > 0:
            description += description_2nd
        return description

    def _color(self):
        return self.tv._color()

    def _size(self):
        return self.tv._size()

    def _style(self):
        return self.tv._style()

    def _color_size_stockstatus(self):
        return self.tv._color_size_stockstatus()

    def _stockstatus_for_variants(self):
        return self.tv._stockstatus_for_variants()

    def _variants(self):
        return self.tv._variants()

    def _swatches(self):
        return self.tv._swatches()

    def _price_for_variants(self):
        return self.tv._price_for_variants()

    def _selected_variants(self):
        return self.tv._selected_variants()

    def _long_description(self):
        long_desc_block = self.tree_html.xpath("//ul[starts-with(@class,'normal-list reduced-spacing-list')]")[0]

        return self._clean_text(html.tostring(long_desc_block))

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_urls = self.tree_html.xpath("//ul[@id='carouselContainer']//li//img/@src")

        if not image_urls:
            image_urls = self.tree_html.xpath("//div[@class='HeroPrimContainer']//a//img//@src")

        image_urls = [url.replace("wid=60&hei=60?qlt=85", "wid=480&hei=480") for url in image_urls]

        return image_urls

    def _image_count(self):
        image_urls = self._image_urls()
        return len(image_urls)

    def _video_urls(self):
        self.video_count = 0
        video_url = self.tree_html.xpath("//div[@class='videoblock']//div//a/@href")
        video_url = [("http://www.target.com%s" % r) for r in video_url]
        video_url2 = video_url[:]
        video_url = []
        for item in video_url2:
            contents = urllib.urlopen(item).read()
            tree = html.fromstring(contents)
            links = tree.xpath("//ul[@class='media-thumbnails']//a/@href")
            flag = False
            for link in links:
                try:
                    link = re.findall(r'^(.*?),', link)[0]
                    video_url.append(link)
                    flag = True
                except:
                    pass
            # if not flag:
            #     video_url.append(item)
            if len(video_url) < 1:
                self.video_count = len(tree.xpath("//ul[@id='carouselContainer']//li//img"))
        demo_url = self.tree_html.xpath("//div[starts-with(@class, 'demoblock')]//span//a/@href")
        demo_url = [r for r in demo_url if len(self._clean_text(r)) > 0]
        for item in demo_url:
            contents = urllib.urlopen(item).read()
            tree = html.fromstring(contents)
            redirect_link = tree.xpath("//div[@id='slow-reporting-message']//a/@href")[0]
            redirect_contents = urllib.urlopen(redirect_link).read()
            redirect_tree = html.fromstring(redirect_contents)
            tabs = redirect_tree.xpath("//div[@class='wc-ms-navbar']//li//a")
            for tab in tabs:
                tab_txt = ""
                try:
                    tab_txt = tab.xpath(".//span/text()")[0].strip()
                except IndexError:
                    continue
                # if tab_txt == "Video" or tab_txt == "Videos" or tab_txt == "360 View Video":
                # if "video" in tab_txt.lower():
                if '360 view video' == tab_txt.lower() or 'videos' == tab_txt.lower() or 'video' == tab_txt.lower():
                    redirect_link2 = tab.xpath("./@href")[0]
                    redirect_link2 = "http://content.webcollage.net" + redirect_link2
                    redirect_contents2 = urllib.urlopen(redirect_link2).read()
                    redirect_tree2 = html.fromstring(redirect_contents2)
                    video_urls_tmp = redirect_tree2.xpath("//div[@class='wc-gallery-thumb']//img/@wcobj")
                    if len(video_urls_tmp) > 0:
                        video_url += video_urls_tmp
                    else:
                        video_url.append(item)
        self.video_count += len(video_url)
        if len(video_url) < 1:
            return None
        return video_url

    def _video_count(self):
        # urls = self._video_urls()
        # if urls:
        #     return len(urls)
        # return 0
        if self.video_count is None:
            self._video_urls()
        return self.video_count

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

        return pdf_hrefs if pdf_hrefs else None

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
                self.reviews = None

                min_ratingval = None
                max_ratingval = None

                if self.review_count > 0:
                    self.reviews = [[1, 0], [2, 0], [3, 0], [4, 0], [5, 0]]

                    for review in review_info['RatingDistribution']:
                        if min_ratingval == None or review['RatingValue'] < min_ratingval:
                            if review['Count'] > 0:
                                min_ratingval = review['RatingValue']
                        if max_ratingval == None or review['RatingValue'] > max_ratingval:
                            if review['Count'] > 0:
                                max_ratingval = review['RatingValue']

                        self.reviews[int(review['RatingValue']) - 1][1] = int(review['Count'])

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
    def _temp_price_cut(self):
        temp_price_cut = self.tree_html.xpath("//div[@id='price_main']//div[contains(@class,'price')]//ul//li[contains(@class,'eyebrow')]//text()")
        if "TEMP PRICE CUT" in temp_price_cut:
            return 1
        return 0

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
        if price[0] == "$":
            return "USD"
        return price[0]

    def _in_stores(self):
        '''in_stores - the item can be ordered online for pickup in a physical store
        or it can not be ordered online at all and can only be purchased in a local store,
        irrespective of availability - binary
        '''

        if self.product_json:
            for item in self.product_json:
                if item["Attributes"]["callToActionDetail"]["soldInStores"] == True:
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
        if self.product_json:
            for item in self.product_json:
                if item["Attributes"]["callToActionDetail"]["soldOnline"] == True:
                    return 1

        return 0

    def _site_online_out_of_stock(self):
        #  site_online_out_of_stock - currently unavailable from the site - binary
        if self._site_online() == 1:
            if self.tree_html.xpath("//div[contains(@class,'buttonmsgcontainer')]//p[contains(@class,'availmsg')]") and \
                            "out of stock online" in self.tree_html.xpath("//div[contains(@class,'buttonmsgcontainer')]//p[contains(@class,'availmsg')]")[0].text_content():
                return 1

            return 0
        else:
            return None

    def _in_stores_out_of_stock(self):
        '''in_stores_out_of_stock - currently unavailable for pickup from a physical store - binary
        (null should be used for items that can not be ordered online and the availability may depend on location of the store)
        '''
        if self._in_stores() == 1:
            if self.tree_html.xpath("//div[contains(@class,'buttonmsgcontainer')]//p[contains(@class,'availmsg')]") and \
                            "out of stock in stores" in self.tree_html.xpath("//div[contains(@class,'buttonmsgcontainer')]//p[contains(@class,'availmsg')]")[0].text_content():
                return 1

            return 0
        else:
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
        # http://www.target.com/s?searchTerm=Target+toys+outdoor+toys+lawn+games+Wubble+Bubble
        url = "http://www.target.com/s?searchTerm=%s" % self._product_name()
        contents = urllib.urlopen(url.encode('utf8')).read()
        tree = html.fromstring(contents)
        lis = tree.xpath("//ul[contains(@class,'productsListView')]//li[contains(@class,'tile standard')]")
        for li in lis:
            try:
                title = li.xpath("//a[contains(@class,'productTitle')]//text()")[0].strip()
                title = title.replace("...", "")
                if title in self._product_name():
                    brand = li.xpath("//a[contains(@class,'productBrand')]//text()")[0].strip()
                    return brand
            except:
                pass
        return None

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces
#    def _clean_text(self, text):
#        return re.sub("&nbsp;", " ", text).strip()

    ##########################################
    ################ RETURN TYPES
    ##########################################
    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service
    DATA_TYPES = { \
        # CONTAINER : NONE
        "url" : _url, \
        "product_id" : _product_id, \
        "upc" : _upc, \

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "model" : _model, \
        "long_description" : _long_description, \
        "variants": _variants, \
        "swatches": _swatches, \
        # CONTAINER : PAGE_ATTRIBUTES
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
        "temp_price_cut" : _temp_price_cut, \
        "in_stores" : _in_stores, \
        "marketplace": _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \
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
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
    }

