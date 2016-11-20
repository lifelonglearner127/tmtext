#!/usr/bin/python

import urllib
import re
import sys
import json

from lxml import html, etree
import time
import requests
from extract_data import Scraper


class OfficeDepotScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.officedepot.com/a/products/<product-id>/<product-name>/"
    REVIEW_URL = "http://officedepot.ugc.bazaarvoice.com/2563/{0}/reviews.djs?format=embeddedhtml"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        # whether product has any webcollage media
        self.review_json = None
        self.review_list = None
        self.is_review_checked = False

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^http://www\.officedepot\.com/a/products/[0-9]+(/.*)?$", self.product_page_url)
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
            itemtype = self.tree_html.xpath('//body[@id="product"]')

            if not itemtype:
                raise Exception()

        except Exception:
            return True

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _canonical_link(self):
        return self.tree_html.xpath('//link[@rel="canonical"]/@href')[0]

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        return re.search('http://www.officedepot.com/a/products/(\d+)', self.product_page_url).group(1)

    def _site_id(self):
        return None

    def _status(self):
        return "success"

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//h1[@itemprop="name"]/text()')[0].strip()

    def _product_title(self):
        return self.tree_html.xpath('//h1[@itemprop="name"]/text()')[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath('//h1[@itemprop="name"]/text()')[0].strip()

    def _model(self):
        return None

    def _upc(self):
        return None

    def _features(self):
        features_tr_list = self.tree_html.xpath('//section[@id="productDetails"]//table[@class="data tabDetails gw9"]//tbody//tr')
        features_list = []

        for tr in features_tr_list:
            features_list.append(tr.xpath(".//td")[0].text_content().strip() + ": " + tr.xpath(".//td")[1].text_content().strip())

        if features_list:
            return features_list

        return None

    def _feature_count(self):
        if self._features():
            return len(self._features())

        return None

    def _model_meta(self):
        return None

    def _description(self):
        description_block = self.tree_html.xpath("//div[@class='sku_desc show']")[0]
        short_description = ""

        for description_item in description_block:
            if description_item.tag == "ul":
                break

            if description_item.tag != "p":
                continue

            short_description = short_description + html.tostring(description_item)

        short_description = self._clean_text(short_description.strip())

        if short_description:
            return short_description

        return None

    def _long_description(self):
        description_block = self.tree_html.xpath("//div[@class='sku_desc show']")[0]
        long_description = ""
        long_description_start = False

        for description_item in description_block:
            if description_item.tag == "ul":
                long_description_start = True

            if long_description_start:
                long_description = long_description + html.tostring(description_item)

        long_description = self._clean_text(long_description.strip())

        if long_description:
            return long_description

        return None

    def _no_longer_available(self):
        if self.tree_html.xpath('//div[contains(@class,"no_longer_avail")]'):
            return 1
        return 0

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_list = None

        if self.tree_html.xpath("//div[@id='productImageThumbs']"):
            image_list = self.tree_html.xpath("//div[@id='productImageThumbs']//ul/li//img/@src")
            image_list = [url[:url.rfind("?")] for url in image_list]
        else:
            main_image_url = self.tree_html.xpath("//img[@id='mainSkuProductImage']/@src")[0]
            main_image_url = main_image_url[:main_image_url.rfind("?")]
            image_list = [main_image_url]

        if image_list:
            return image_list

        return None

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def _video_urls(self):
        video_urls = []

        resource_base = re.search('data-resources-base="([^"]+)"', html.tostring(self.tree_html))
        if resource_base:
            resource_base = resource_base.group(1)[:-1] # remove trailing '/'

        wc_json = self.tree_html.xpath('//div[contains(@class,"wc-json-data")]/text()')

        if wc_json:
            wc_json = json.loads(wc_json[0])

            for video in wc_json['videos']:
                video_urls.append( resource_base + video['src']['src'])

        if video_urls:
            return video_urls

        return None

    def _video_count(self):
        videos = self._video_urls()

        embedded_videos = self.tree_html.xpath('//span[@class="LimelightEmbeddedPlayer"]')

        if videos:
            return len(videos) + len(embedded_videos)

        else:
            return len(embedded_videos)

    def _pdf_urls(self):
        urls = []

        pops = map( lambda x: x.get('href'), self.tree_html.xpath('//ul[@class="sku_icons"]/li/a'))
        for pop in pops:
            category = re.search( '/([^/]+)\.do', pop ).group(1).lower()
            id = re.search( '\?id=(\d+)', pop ).group(1)
            urls.append('http://www.officedepot.com/pdf/%s/%s.pdf' % (category, id))

        if urls:
            return urls

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
    
    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################

    def _average_review(self):
        if self._review_count() == 0:
            return None

        average_review = round(float(self.review_json["jsonData"]["attributes"]["avgRating"]), 1)

        if str(average_review).split('.')[1] == '0':
            return int(average_review)
        else:
            return float(average_review)

    def _review_count(self):
        self._reviews()

        if not self.review_json:
            return 0

        return int(self.review_json["jsonData"]["attributes"]["numReviews"])

    def _max_review(self):
        if self._review_count() == 0:
            return None

        for i, review in enumerate(self.review_list):
            if review[1] > 0:
                return 5 - i

    def _min_review(self):
        if self._review_count() == 0:
            return None

        for i, review in enumerate(reversed(self.review_list)):
            if review[1] > 0:
                return i + 1

    def _reviews(self):
        if self.is_review_checked:
            return self.review_list

        self.is_review_checked = True

        h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        b = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        s.mount('https://', b)
        contents = s.get(self.REVIEW_URL.format(self._product_id()), headers=h, timeout=5).text

        try:
            start_index = contents.find("webAnalyticsConfig:") + len("webAnalyticsConfig:")
            end_index = contents.find(",\nwidgetInitializers:initializers", start_index)

            self.review_json = contents[start_index:end_index]
            self.review_json = json.loads(self.review_json)
        except:
            self.review_json = None

        review_html = html.fromstring(re.search('"BVRRSecondaryRatingSummarySourceID":" (.+?)"},\ninitializers={', contents).group(1))
        reviews_by_mark = review_html.xpath("//*[contains(@class, 'BVRRHistAbsLabel')]/text()")
        reviews_by_mark = reviews_by_mark[:5]
        review_list = [[5 - i, int(re.findall('\d+', mark)[0])] for i, mark in enumerate(reviews_by_mark)]

        if not review_list:
            review_list = None

        self.review_list = review_list

        return self.review_list

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        return "$" + self.tree_html.xpath("//meta[@itemprop='price']/@content")[0]

    def _price_amount(self):
        return float(self.tree_html.xpath("//meta[@itemprop='price']/@content")[0])

    def _price_currency(self):
        return self.tree_html.xpath("//meta[@itemprop='priceCurrency']/@content")[0]

    def _in_stores(self):
        sold_in_stores = self.tree_html.xpath("//div[@class='soldInStores']")

        if sold_in_stores and "sold in stores" in sold_in_stores[0].text_content().lower().strip():
            return 1

        return 0

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):

        if self._site_online() == 0:
            return None

        delivery_message = self.tree_html.xpath("//div[@class='deliveryMessage']")

        if delivery_message:
            delivery_message = delivery_message[0].text_content().strip().lower()

            if "out of stock for delivery" in delivery_message:
                return 1

        return 0

    def _in_stores_out_of_stock(self):
        if self._in_stores() == 0:
            return None

        delivery_message = self.tree_html.xpath("//div[@class='deliveryMessage']")

        if delivery_message:
            delivery_message = delivery_message[0].text_content().strip().lower()

            if "out of stock for delivery" in delivery_message:
                return 1

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
        categories = self.tree_html.xpath("//div[@id='siteBreadcrumb']//li//span[@itemprop='name']/text()")

        return categories[1:]

    def _category_name(self):
        return self._categories()[-1]
    
    def _brand(self):
        return self.tree_html.xpath("//td[@id='attributebrand_namekey']/text()")[0].strip()

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces

    def _clean_text(self, text):
        text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
       	text = re.sub("&nbsp;", " ", text).strip()

        return re.sub(r'\s+', ' ', text)

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
        "no_longer_available" : _no_longer_available, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
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
