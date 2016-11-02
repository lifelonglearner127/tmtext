#!/usr/bin/python

import urllib
import re
import sys
import json

from lxml import html, etree
import time
import requests
from extract_data import Scraper
from requests.auth import HTTPProxyAuth


class LowesScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.lowes.com/pd_.*__?productId=<product-id>(&pl=1)?"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        self.webcollage_content = None
        self.webcollage_checked = False
        self.wc_video = 0
        
        self.reviews = None
        self.reviews_html = None
        self.is_review_checked = False

        self.proxy_host = "proxy.crawlera.com"
        self.proxy_port = "8010"
        self.proxy_auth = HTTPProxyAuth(self.CRAWLERA_APIKEY, "")
        self.proxies = {"http": "http://{}:{}/".format(self.proxy_host, self.proxy_port)}
        self.proxy_config = {"proxy_auth": self.proxy_auth, "proxies": self.proxies}

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match('^http://www.lowes.com/pd_.*__\?productId=\d+(&pl=1)?$', self.product_page_url)
        return not not m

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        return False


    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _canonical_link(self):
        return self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        return re.search('.*productId=(\d+)', self.product_page_url).group(1)

    def _site_id(self):
        return None

    def _status(self):
        return "success"


    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//div[@class="itemInfo"]/h1/text()')[0]

    def _product_title(self):
        return self.tree_html.xpath('//title/text()')[0]

    def _title_seo(self):
        return self._product_title()

    def _model(self):
        return self.tree_html.xpath('//span[@id="ModelNumber"]/text()')[0]

    def _upc(self):
        return None

    def _features(self):
        return None

    def _feature_count(self):
        return None

    def _model_meta(self):
        return None

    def _description(self):
        return self.tree_html.xpath('//div[@id="description-tab"]/p/text()')[0]

    def _long_description(self):
        long_description = ''

        for element in self.tree_html.xpath('//div[@id="description-tab"]/*'):
            if element.tag in ['p', 'ul']:
                long_description += html.tostring(element)

        return self._clean_text(long_description)

    def _swatches(self):
        swatches = []

        for menuitem in self.tree_html.xpath('//li[@role="menuitem"]'):
            for media in menuitem.xpath('a/div[@class="media"]'):
                swatch = {
                    'color' : media.xpath('div[contains(@class,"media-body")]/span/text()')[0],
                    'hero' : 1,
                    'hero_image' : media.xpath('div[contains(@class,"media-left")]/img/@src'),
                }

                swatches.append(swatch)

        if swatches:
            return swatches

    def _variants(self):
        variants = []

        for menuitem in self.tree_html.xpath('//li[@role="menuitem"]'):
            for media in menuitem.xpath('a/div[@class="media"]'):
                variant = {
                    'properties' : {
                        'color' : media.xpath('div[contains(@class,"media-body")]/span/text()')[0]
                    },
                    'selected' : bool(media.xpath('div[contains(@class,"media-right")]')),
                }

                variants.append(variant)

        if variants:
            return variants


    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_urls = []

        for image in self.tree_html.xpath('//div[contains(@class,"product-image-set")]//img/@src'):
            image = re.sub('sm.jpg', 'lg.jpg', image)
            if not image in image_urls:
                image_urls.append( image)

        return image_urls

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def _video_urls(self):
        self._webcollage()

        video_urls = []

        if self.webcollage_content:
            for url_frag in re.findall('"([^"]*mp4.mp4full.mp4)"', self.webcollage_content):
                video_urls.append('http://media.webcollage.net/rlfp/wc/live/module/moencreativespecialties' + url_frag)

                self.wc_video = 1

        if video_urls:
            return video_urls

    def _video_count(self):
        num_videos = len( self.tree_html.xpath('//a[contains(@data-setid, "video")]'))

        if self._video_urls():
            return len( self._video_urls()) + num_videos

        return num_videos

    def _wc_360(self):
        if self.tree_html.xpath('//a[contains(@data-setid, "spinset")]'):
            return 1
        return 0

    def _wc_video(self):
        self._webcollage()

        return self.wc_video

    def _pdf_urls(self):
        return None

    def _pdf_count(self):
        return 0

    def _webcollage(self):
        if not self.webcollage_checked:
            self.webcollage_checked = True

            webcollage_src = self.tree_html.xpath('//iframe[@id="productVideoFrame"]/@data-src')

            if webcollage_src:
                self.webcollage_content = self.load_page_from_url_with_number_of_retries( webcollage_src[0])

        if self.webcollage_content:
            return 1

        return 0

    def _htags(self):
        htags_dict = {}
        # add h1 tags text to the list corresponding to the "h1" key in the dict
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        # add h2 tags text to the list corresponding to the "h2" key in the dict
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    def _keywords(self):
        return None


    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################

    def _average_review(self):
        self._reviews()

        average_review = self.reviews_html.xpath('//span[@itemprop="aggregateRating"]/span[@itemprop="ratingValue"]/text()')[0]

        return float(average_review)

    def _review_count(self):
        self._reviews()

        return int(self.reviews_html.xpath('//meta[@itemprop="reviewCount"]/@content')[0])

    def _max_review(self):
        if self._review_count() == 0:
            return None

        for i, review in enumerate(self.reviews):
            if review[1] > 0:
                return 5 - i

    def _min_review(self):
        if self._review_count() == 0:
            return None

        for i, review in enumerate(reversed(self.reviews)):
            if review[1] > 0:
                return i + 1

    def _reviews(self):
        if self.is_review_checked:
            return self.reviews

        self.is_review_checked = True

        self.reviews_html = html.fromstring( self.load_page_from_url_with_number_of_retries('http://lowes.ugc.bazaarvoice.com/0534/' + self._product_id() + '/reviews.djs?format=embeddedhtml').replace('\\', ''))

        reviews = []

        for i in reversed(range(1,6)):
            j = self.reviews_html.xpath('//div[contains(@class,"BVRRHistogramBarRow%s")]/span[@class="BVRRHistAbsLabel"]/text()' % i)[0]

            reviews.append([i, int(j)])

        if reviews:
            self.reviews = reviews
            return self.reviews


    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        return self.tree_html.xpath('//div[@id="pricing"]/span[@class="price"]/text()')[0]

    def _price_amount(self):
        return float(self._price()[1:])

    def _price_currency(self):
        return 'USD'

    def _in_stores(self):
        return 1

    def _site_online(self):
        if re.search('"parcelAvailable" : "1"', html.tostring(self.tree_html)):
            return 1
        return 0

    def _site_online_out_of_stock(self):
        return 0

    def _in_stores_out_of_stock(self):
        return 0

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
        return self.tree_html.xpath('//ul[@id="breadcrumbs-list"]/li/a/text()')

    def _category_name(self):
        return self._categories()[-1]
    
    def _brand(self):
        brand = re.search('"brandName" : "([^"]+)"', html.tostring(self.tree_html)).group(1)
        return brand.replace('_', ' ')


    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        return re.sub('[\r\n\t]', '', text).strip()


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
        "swatches" : _swatches, \
        "variants" : _variants, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
        "pdf_count" : _pdf_count, \
        "pdf_urls" : _pdf_urls, \
        "webcollage" : _webcollage, \
        "wc_360": _wc_360, \
        "wc_video": _wc_video, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "canonical_link": _canonical_link, \

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
