#!/usr/bin/python

import re
import lxml
import lxml.html
import requests
import json

from itertools import groupby

from lxml import html, etree
from extract_data import Scraper


class KohlsScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.ulta.com/ulta/browse/productDetail.jsp?productId=<product-id>"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.review_json = None
        self.price_json = None

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match(r"^http://www.kohls.com/product/prd-\d+/.+\.jsp$", self.product_page_url)

        return not not m

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        self._extract_price_json()
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
    def _url(self):
        return self.product_page_url

    def _product_id(self):
        product_id = self.tree_html.xpath("//input[@class='preSelectedskuId']/@value")[0].strip()[:-1]

        return product_id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//meta[@property="og:title"]/@content')[0].strip()

    def _product_title(self):
        return self.tree_html.xpath('//meta[@property="og:title"]/@content')[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath('//meta[@property="og:title"]/@content')[0].strip()

    def _model(self):
        return None

    def _features(self):
        description_block = self.tree_html.xpath("//div[@class='Bdescription']")[0]
        is_features_found = False
        features_title_list = ["Product Features:", "PRODUCT FEATURES", "Product Features", "Features"]

        for element_block in description_block:
            inner_text = "".join([t.strip() for t in element_block.itertext()])
            inner_text = inner_text.strip()

            if inner_text in features_title_list:
                is_features_found = True
                break

        if not is_features_found:
            return None

        try:
            features_block = element_block.xpath(".//following-sibling::ul")[0]
            features_list = []

            features_list = [x.text_content() for x in features_block.xpath(".//li")]

            return features_list
        except:
            return None

    def _feature_count(self):
        if self._features():
            return len(self._features())

        return 0

    def _description(self):
        description_block = self.tree_html.xpath("//div[@class='Bdescription']")[0]
        short_description = ""
        features_title_list = ["Product Features:", "PRODUCT FEATURES", "Product Features", "Features"]

        if self._features():
            features_ul = 0

            for element_block in description_block:
                inner_text = "".join([t.strip() for t in element_block.itertext()])
                inner_text = inner_text.strip()

                if inner_text in features_title_list:
                    break

                short_description += html.tostring(element_block)
        else:
            for element_block in description_block:
                if element_block.tag == "ul":
                    break

                short_description += html.tostring(element_block)

        if not short_description.strip():
            return None
        else:
            return short_description

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description(self):
        description_block = self.tree_html.xpath("//div[@id='pdp_details_segment']//div[@class='Bdescription']")
        features_title_list = ["Product Features:", "PRODUCT FEATURES", "Product Features", "Features"]

        if not description_block:
            return None

        description_block = description_block[0]

        long_description = ""

        if self._features():
            features_ul = 0

            for element_block in description_block:
                if html.tostring(element_block).startswith("<!--"):
                    continue

                inner_text = "".join([t.strip() for t in element_block.itertext()])
                inner_text = inner_text.strip()

                if inner_text in features_title_list:
                    features_ul = 1
                    continue

                if features_ul == 1:
                    features_ul = 2
                    continue

                if features_ul == 2:
                    long_description += html.tostring(element_block)
        else:
            is_long_description = False

            for element_block in description_block:
                if not is_long_description and element_block.tag == "ul":
                    is_long_description = True

                if is_long_description:
                    long_description += html.tostring(element_block)

        if not long_description.strip():
            return None
        else:
            return long_description

    def _ingredients(self):
        return None

    def _ingredients_count(self):
        return 0

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        pass
        
    def _image_urls(self):
        image_urls = self.tree_html.xpath("//div[@id='leftCarousel']/div[@class='ver-carousel']/ul/li//img/@src")

        image_urls = [x for x in image_urls if "videoPlayer_Icon.png" not in x]

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
        video_count = 0
        image_urls = self.tree_html.xpath("//div[@id='leftCarousel']/div[@class='ver-carousel']/ul/li//img/@src")

        video_urls = [x for x in image_urls if "videoPlayer_Icon.png" in x]

        if not video_urls:
            return 0

        return len(video_urls)

    # return dictionary with one element containing the PDF
    def _pdf_urls(self):
        return None

    def _pdf_count(self):
        return 0

    def _webcollage(self):
        return 0

    def _htags(self):
        htags_dict = {}
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))

        return htags_dict

    def _keywords(self):
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0].strip()

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################

    def _extract_review_json(self):
        try:
            h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}

            contents = requests.get("http://kohls.ugc.bazaarvoice.com/9025/%s/reviews.djs?format=embeddedhtml" % self._product_id(), headers=h).text
            start_index = contents.find("webAnalyticsConfig:") + len("webAnalyticsConfig:")
            end_index = contents.find("}},", start_index) + 2

            self.review_json = contents[start_index:end_index]
            self.review_json = json.loads(self.review_json)
        except:
            self.review_json = None

    def _extract_price_json(self):
        if self.price_json:
            return

        price_json = self.tree_html.xpath("//script[@type='text/javascript' and contains(text(), 'var pageData=')]")

        if price_json:
            price_json = price_json[0].text
            start_index = price_json.find("var pageData=") + len("var pageData=")
            end_index = price_json.find("};", start_index) + 1
            price_json = price_json[start_index:end_index]
            self.price_json = json.loads(price_json)

    def _average_review(self):
        if self._review_count() == 0:
            return None

        average_review = round(float(self.review_json["jsonData"]["attributes"]["avgRating"]), 1)

        if str(average_review).split('.')[1] == '0':
            return int(average_review)
        else:
            return float(average_review)

    def _review_count(self):
        if not self.review_json:
            self._extract_review_json()

        return int(self.review_json["jsonData"]["attributes"]["numReviews"])

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
        self._extract_price_json()

        if not self.price_json:
            return None

        if not self.price_json["product_Details"]["itemSalePrice"]:
            return self.price_json["product_Details"]["itemOriginalPrice"]

        return self.price_json["product_Details"]["itemSalePrice"]

    def _price_amount(self):
        self._extract_price_json()

        if not self.price_json:
            return None

        price_amount = 0

        if not self.price_json["product_Details"]["itemSalePrice"]:
            price_amount = self.price_json["product_Details"]["itemOriginalPrice"]

        price_amount = self.price_json["product_Details"]["itemSalePrice"]

        return float(price_amount[1:])

    def _price_currency(self):
        return self.tree_html.xpath("//meta[@property='og:price:currency']/@content")[0]

    def _owned(self):
        return 0

    def _marketplace(self):
        return 0

    def _site_online(self):
        return 1

    def _in_stores(self):
        if self.tree_html.xpath("//img[@alt='Online_Exclusive.gif']"):
            return 0

        return 1

    def _site_online_out_of_stock(self):
        return 0

    def _marketplace_sellers(self):
        return None

    def _marketplace_out_of_stock(self):
        return 0

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################    
    def _categories(self):
        return None

    def _category_name(self):
        return None

    def _brand(self):
        return None

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
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
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "long_description" : _long_description, \
        "ingredients": _ingredients, \
        "ingredient_count": _ingredients_count,

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
        "owned" : _owned, \
        "marketplace" : _marketplace, \
        "site_online": _site_online, \
        "site_online_out_of_stock": _site_online_out_of_stock, \
        "in_stores" : _in_stores, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_out_of_stock": _marketplace_out_of_stock, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "mobile_image_same" : _mobile_image_same, \
    }
