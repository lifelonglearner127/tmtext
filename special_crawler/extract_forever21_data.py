#!/usr/bin/python

import urllib
import cookielib
import re
import sys
import json

from lxml import html, etree
import time
import mechanize
import requests
from extract_data import Scraper


class Forever21Scraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.homedepot.com/p/<product-name>/<product-id>"
    REVIEW_URL = "http://nike.ugc.bazaarvoice.com/9191-en_us/{0}/reviews.djs?format=embeddedhtml"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.product_json = None
        # whether product has any webcollage media
        self.review_json = None
        self.review_list = None
        self.is_review_checked = False
        self.store_url = 'http://store.nike.com/us/en_us'
        self.browser = mechanize.Browser()
        self.variants = None
        self.is_variant_checked = False

    def _initialize_browser_settings(self):
        # Cookie Jar
        cj = cookielib.LWPCookieJar()
        self.browser.set_cookiejar(cj)

        # Browser options
        self.browser.set_handle_equiv(True)
        self.browser.set_handle_gzip(True)
        self.browser.set_handle_redirect(True)
        self.browser.set_handle_referer(True)
        self.browser.set_handle_robots(False)

        # Follows refresh 0 but not hangs on refresh > 0
        self.browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        # Want debugging messages?
        #br.set_debug_http(True)
        #br.set_debug_redirects(True)
        #br.set_debug_responses(True)

        # User-Agent (this is cheating, ok?)
        self.browser.addheaders = [('User-agent', self.select_browser_agents_randomly())]

    def _extract_page_tree(self, captcha_data=None, retries=0):
        try:
            self._initialize_browser_settings()
            self.browser.open(self.store_url)
            contents = self.browser.open(self.product_page_url).read()
        except Exception, e:
            contents = requests.get(self.product_page_url).text

        try:
            # replace NULL characters
            contents = self._clean_null(contents).decode("utf8")
        except UnicodeError, e:
            # if string was not utf8, don't deocde it
            print "Warning creating html tree from page content: ", e.message

            # replace NULL characters
            contents = self._clean_null(contents)

        self.page_raw_text = contents
        self.tree_html = html.fromstring(contents)

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^http://www.forever21.com/Product/Product.aspx\?.*?$", self.product_page_url)
        return not not m

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """

        try:
            itemtype = self.tree_html.xpath('//meta[@property="og:type"]/@content')[0].strip()

            if itemtype != "product":
                raise Exception()

        except Exception:
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

    def _event(self):
        return None

    def _product_id(self):
        return re.findall('ProductID=(\d+)', self.product_page_url, re.DOTALL)[0]

    def _site_id(self):
        return None

    def _status(self):
        return "success"






    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//h1[@class="item_name_p"]/text()')[0].strip()

    def _product_title(self):
        return self.tree_html.xpath('//h1[@class="item_name_p"]/text()')[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath('//h1[@class="item_name_p"]/text()')[0].strip()

    def _model(self):
        return None

    def _upc(self):
        return None

    def _features(self):
        return None

    def _feature_count(self):
        if self._features():
            return len(self._features())

        return None

    def _model_meta(self):
        return None

    def _description(self):
        description_block = html.fromstring(html.tostring(self.tree_html.xpath("//article[@class='ac-small']")[0]))

        for style in description_block.xpath('.//style'):
            style.getparent().remove(style)

        for script in description_block.xpath('.//script'):
            script.getparent().remove(script)

        return html.tostring(description_block.xpath("./*")[0])

    def _long_description(self):
        description_block = html.fromstring(html.tostring(self.tree_html.xpath("//article[@class='ac-small']")[0]))

        for style in description_block.xpath('.//style'):
            style.getparent().remove(style)

        for script in description_block.xpath('.//script'):
            script.getparent().remove(script)

        short_description_block = description_block.xpath("./*")[0]
        short_description_block.getparent().remove(short_description_block)

        return html.tostring(description_block)

    def _variants(self):
        return None

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_urls = self.tree_html.xpath("//ul[@id='pdp_thumbnail']//a/@href")
        image_urls = [re.findall("ItemImage\.Main','(.*)'\);", url, re.DOTALL)[0] for url in image_urls]

        if image_urls:
            return image_urls

        return None

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def _video_urls(self):
        return None

    def _video_count(self):
        videos = self._video_urls()

        if videos:
            return len(videos)

        return 0

    def _pdf_urls(self):
        return None

    def _pdf_count(self):
        if self._pdf_urls():
            return len(self._pdf_urls())

        return 0

    def _webcollage(self):
        return None

    def _htags(self):
        htags_dict = {}
        # add h1 tags text to the list corresponding to the "h1" key in the dict
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        # add h2 tags text to the list corresponding to the "h2" key in the dict
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    def _keywords(self):
        return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]

    def _no_image(self):
        return None
    
    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################

    def _average_review(self):
        return float(self.tree_html.xpath("//span[@class='pr-snippet-rating-decimal pr-rounded']/text()")[0])

    def _review_count(self):
        review_count = self.tree_html.xpath("//a[@data-pr-event='snippet-read-reviews']/span/text()")

        if review_count:
            return int(review_count[0][1:-1])

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
        return self.tree_html.xpath("//span[@itemprop='offerDetails']//span[@itemprop='price']/text()")[0].strip()

    def _price_amount(self):
        price_text = self._price()
        price = re.findall(r"\d*\.\d+|\d+", price_text.replace(",", ""))
        return float(price[0])

    def _price_currency(self):
        return self.tree_html.xpath("//span[@itemprop='offerDetails']//meta[@itemprop='currency']/@content")[0]

    def _in_stores(self):
        return 0

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):
        return 0

    def _in_stores_out_of_stock(self):
        return None

    def _marketplace(self):
        return 0

    def _seller_from_tree(self):
        return None

    def _marketplace_sellers(self):
        return None

    def _marketplace_lowest_price(self):
        return None





    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        return self.tree_html.xpath("//div[@id='div_breadcrumb']/span/a/text()")[1:]

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
        "event" : _event, \
        "product_id" : _product_id, \
        "site_id" : _site_id, \
        "status" : _status, \

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "model" : _model, \
        "upc" : _upc,\
        "features" : _features, \
        "feature_count" : _feature_count, \
        "model_meta" : _model_meta, \
        "description" : _description, \
        "long_description" : _long_description, \
        "variants": _variants,
        "swatches": _swatches,
        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
        "no_image" : _no_image, \
        "pdf_count" : _pdf_count, \
        "pdf_urls" : _pdf_urls, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "canonical_link": _canonical_link,

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
        "site_online": _site_online, \
        "site_online_out_of_stock": _site_online_out_of_stock, \
        "in_stores_out_of_stock": _in_stores_out_of_stock, \
        "marketplace" : _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \



        "loaded_in_seconds" : None, \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "mobile_image_same" : _mobile_image_same, \
    }
