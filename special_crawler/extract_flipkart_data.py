#!/usr/bin/python

import re
import lxml
import lxml.html
import requests
import json

from itertools import groupby

from lxml import html, etree
from extract_data import Scraper


class FlipkartScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.flipkart.com/<product-name>/p/<product-id>"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.reviews = None
        self.average_review = 0
        self.max_review = 0
        self.min_review = 0
        self.review_count = 0
        self.is_review_checked = False

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match(r"^http://www\.flipkart\.com/.*/p/.*$", self.product_page_url)

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
            if 'var PAGE_NAME = "ProductPage";' not in (" " . join(self.tree_html.xpath("//script/text()"))):
                raise Exception
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

    def _product_id(self):
        return self.product_page_url.split('/')[-1]

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//h1[@itemprop='name']/text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//h1[@itemprop='name']/text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//h1[@itemprop='name']/text()")[0].strip()

    def _model(self):
        return None

    def _features(self):
        features_list = []

        try:
            features = []
            features_td_list = self.tree_html.xpath("//div[@class='productSpecs specSection']//table[@class='specTable']//tr/td")

            for index, td in enumerate(features_td_list):
                if (index + 1) % 2 != 0:
                    continue

                features.append(self._clean_text(features_td_list[index - 1].text_content()) + ": " + self._clean_text(td.text_content()))

            if features:
                features_list.extend(features)
        except:
            pass

        if not features_list:
            return None

        return features_list

    def _feature_count(self):
        features = self._features()

        if not features:
            return 0

        return len(features)

    def _description(self):
        try:
            description = self._clean_text(self.tree_html.xpath("//ul[@class='keyFeaturesList']")[0].text_content().strip())

            description = re.sub('\\n+', ' ', description).strip()
            description = re.sub('\\t+', ' ', description).strip()
            description = re.sub(' +', ' ', description).strip()

            if description:
                return description
        except:
            pass

        return None

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description(self):
        try:
            long_description = self._clean_text(self.tree_html.xpath("//div[@class='description specSection']")[0].text_content().strip())

            long_description = re.sub('\\n+', ' ', long_description).strip()
            long_description = re.sub('\\t+', ' ', long_description).strip()
            long_description = re.sub(' +', ' ', long_description).strip()

            if long_description:
                return long_description
        except:
            pass

        try:
            long_description = self._clean_text(self.tree_html.xpath("//div[@class='rpdSection']")[0].text_content().strip())

            long_description = re.sub('\\n+', ' ', long_description).strip()
            long_description = re.sub('\\t+', ' ', long_description).strip()
            long_description = re.sub(' +', ' ', long_description).strip()

            if long_description:
                return long_description
        except:
            pass

        return None

    def _ingredients(self):
        return None

    def _ingredients_count(self):
        return None

    def _variants(self):
        return None

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        pass
        
    def _image_urls(self):
        urls = self.tree_html.xpath("//div[@class='thumbContainer']/div[@class='thumb']/@style")
        urls = [re.search('background-image:url\((.+?)\)', url).group(1).replace("100x100", "400x400") for url in urls]

        if not urls:
            return None

        return urls

    def _image_count(self):
        image_urls = self._image_urls()

        if not image_urls:
            return 0

        return len(image_urls)

    def _video_urls(self):
        return None

    def _video_count(self):
        return 0

    # return dictionary with one element containing the PDF
    def _pdf_urls(self):
        return None

    def _pdf_count(self):
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

    def _average_review(self):
        return float(self.tree_html.xpath("//div[@class='avgWrapper']//div[@class='bigStar']/text()")[0])

    def _review_count(self):
        reviews = self._reviews()

        if not reviews:
            return 0

        review_count = 0

        for review in reviews:
            review_count = review_count + review[1]

        return review_count

    def _max_review(self):
        reviews = self._reviews()

        for review in reviews:
            if review[1] > 0:
                return review[0]

    def _min_review(self):
        reviews = self._reviews()

        for review in reversed(reviews):
            if review[1] > 0:
                return review[0]

    def _reviews(self):
        review_list = self.tree_html.xpath("//ul[@class='ratingsDistribution']/li//div[@class='bar']/div[@class='progress']/text()")

        for mark, rating_count in enumerate(review_list):
            review_list[mark] = [5-mark, int(rating_count)]

        if not review_list:
            return None

        return review_list

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        return self.tree_html.xpath("//div[@class='price-wrap']//span[contains(@class, 'selling-price')]/text()")[0]

    def _price_amount(self):
        return float(float(self.tree_html.xpath("//div[@class='price-wrap']//meta[@itemprop='price']/@content")[0].replace(",", "")))

    def _price_currency(self):
        return self.tree_html.xpath("//div[@class='price-wrap']//meta[@itemprop='priceCurrency']/@content")[0]

    def _site_online(self):
        return 1

    def _in_stores(self):
        return 0

    def _site_online_out_of_stock(self):
        try:
            if "Out of Stock!" in self.tree_html.xpath("//div[@class='out-of-stock-text']")[0].text_content():
                return 1
        except:
            pass

        return 0

    def _marketplace(self):
        if not self._marketplace_sellers():
            return 0

        return 1

    def _marketplace_prices(self):
        marketplace_json = self.tree_html.xpath("//div[@class='seller-table-wrap section']/@data-config")[0]
        marketplace_json = json.loads(marketplace_json)
        marketplace_prices = []

        for seller in marketplace_json["dataModel"]:
            marketplace_prices.append(float(seller["priceInfo"]["sellingPrice"]))

        if not marketplace_prices:
            return None

        return marketplace_prices

    def _marketplace_sellers(self):
        marketplace_json = self.tree_html.xpath("//div[@class='seller-table-wrap section']/@data-config")[0]
        marketplace_json = json.loads(marketplace_json)
        marketplace_sellers = []

        for seller in marketplace_json["dataModel"]:
            marketplace_sellers.append(seller["sellerInfo"]["name"])

        if not marketplace_sellers:
            return None

        return marketplace_sellers

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################    
    def _categories(self):
        return [self._clean_text(category) for category in self.tree_html.xpath("//div[@class='breadcrumb-wrap line']//ul/li/a/text()")][1:]

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        return None

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    def _clean_text(self, text):
        text = re.sub("&nbsp;", " ", text).strip()

        return text

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
        "variants": _variants,

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
        "pdf_count" : _pdf_count, \
        "pdf_urls" : _pdf_urls, \
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
        "site_online": _site_online, \
        "site_online_out_of_stock": _site_online_out_of_stock, \
        "in_stores" : _in_stores, \
        "marketplace": _marketplace, \
        "marketplace_prices" : _marketplace_prices, \
        "marketplace_sellers": _marketplace_sellers, \

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
