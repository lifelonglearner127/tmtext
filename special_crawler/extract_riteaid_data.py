#!/usr/bin/python

import re
import HTMLParser

import requests
from lxml import html, etree
from extract_data import Scraper
import json


class RiteAidScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is https://shop.riteaid.com/<product-name>-<skuid>$"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.wc_360 = 0
        self.wc_emc = 0
        self.wc_video = 0
        self.wc_pdf = 0
        self.wc_prodtour = 0

        self.features = None
        self.ingredients = None
        self.images = None
        self.videos = None
        self.reviews = None

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match('^https://shop.riteaid.com/.*-\d+$', self.product_page_url)
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
            if not self.tree_html.xpath('//div[@itemtype="http://schema.org/Product"]'):
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
        return self.tree_html.xpath('//meta[@itemprop="sku"]/@content')[0]

    def _site_id(self):
        return self._product_id()

    def _status(self):
        return "success"

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//span[@itemprop="name"]/text()')[0]

    def _product_title(self):
        return self.tree_html.xpath('//title/text()')[0]

    def _title_seo(self):
        return self._product_title()

    def _model(self):
        model = self.tree_html.xpath('//th[text()="Model"]/following-sibling::td/text()')

        if model:
            return model[0]

    def _upc(self):
        return None

    def _features(self):
        if not self.features:
            features = html.tostring(self.tree_html.xpath('//div[@class="std"]/ul')[0])
            self.features = self._clean_text(features)

        return self.features

    def _feature_count(self):
        self._features()

        if self.features:
            return len(self.features.split('</li><li>'))

    def _model_meta(self):
        return None

    def _description(self):
        description = ''

        for element in self.tree_html.xpath('//dd[@class="tab-container"]')[0].xpath("./*"):
            if not element.text_content():
                continue

            description += self._clean_html(html.tostring(element))

        if description:
            return description

    def _long_description(self):
        description = ''

        if description:
            if description != self._description():
                return description

    def _ingredients(self):
        if not self.ingredients:
            stds = self.tree_html.xpath('//div[@class="std"]')

            if len(stds) > 3:
                ingredients = stds[2].text_content().split(',')

                ingredients = map(lambda x: self._clean_text(x), ingredients)
                ingredients = filter(len, ingredients)

                if ingredients:
                    self.ingredients = ingredients

        return self.ingredients

    def _ingredient_count(self):
        self._ingredients()

        if self.ingredients:
            return len(self.ingredients)


    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        if not self.images:
            images = []

            image_urls = self.tree_html.xpath('//div[@class="images"]//img/@src')

            for image in image_urls:
                is_video_image = False

                # Do not include video images
                for video_image in self.tree_html.xpath('//a[@data-colorbox="video"]/@style'):
                    if image.split('/')[-1] in video_image:
                        is_video_image = True
                        break

                if is_video_image:
                    continue

                if '/media/catalog/product' in image and not image in images:
                    images.append(image)

            if images:
                self.images = images

        return self.images

    def _image_count(self):
        self._image_urls()

        if self.images:
            return len(self.images)

        return 0

    def _video_urls(self):
        if not self.videos:
            videos = []

            video_urls = self.tree_html.xpath('//a[@data-colorbox="video"]/@href')

            for video in video_urls:
                if not video in videos:
                    videos.append(video)

            if videos:
                self.videos = videos

        return self.videos

    def _video_count(self):
        self._video_urls()

        if self.videos:
            return len(self.videos)

        return 0

    def _pdf_urls(self):
        return None

    def _pdf_count(self):
        return 0

    def _webcollage(self):
        """Uses video and pdf information
        to check whether product has any media from webcollage.
        Returns:
            1 if there is webcollage media
            0 otherwise
        """
        if self.wc_360 + self.wc_emc + self.wc_pdf + self.wc_prodtour + self.wc_video > 0:
            return 1

        return 0

    def _wc_360(self):
        self._webcollage()

        return self.wc_360

    def _wc_emc(self):
        self._webcollage()

        return self.wc_emc

    def _wc_pdf(self):
        self._webcollage()

        return self.wc_pdf

    def _wc_prodtour(self):
        self._webcollage()

        return self.wc_prodtour

    def _wc_video(self):
        self._webcollage()

        return self.wc_video

    def _htags(self):
        htags_dict = {}

        htags_dict['h1'] = map(lambda t: self._clean_text(t), self.tree_html.xpath('//h1//text()[normalize-space()!=""]'))
        htags_dict['h2'] = map(lambda t: self._clean_text(t), self.tree_html.xpath('//h2//text()[normalize-space()!=""]'))

        return htags_dict

    def _keywords(self):
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0]


    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    def _load_reviews(self):
        if not self.reviews:
            try:
                sku = self.tree_html.xpath('//meta[@itemprop="sku"]/@content')[0]

                reviews_json = self.load_page_from_url_with_number_of_retries(
                    "http://api.bazaarvoice.com/data/reviews.json?apiversion=5.4"
                    "&passkey=tezax0lg4cxakub5hhurfey5o&Filter=ProductId:{}"
                    "&Include=Products&Stats=Reviews".format(sku))

                self.reviews = json.loads(reviews_json).get("Includes", {}).get(
                    "Products", {}).get(sku, {}).get("ReviewStatistics", {})
            except Exception as ex:
                print ex

    def _average_review(self):
        self._load_reviews()
        rating_value = self.reviews.get("AverageOverallRating")
        rating_value = round(rating_value, 2) if rating_value else None
        if rating_value:
            return rating_value

    def _review_count(self):
        self._load_reviews()
        review_count = self.reviews.get("TotalReviewCount")
        if review_count:
            return review_count

    def _max_review(self):
        reviews = self._reviews()

        if reviews:
            for review in reviews:
                if review[1] != 0:
                    return review[0]

    def _min_review(self):
        reviews = self._reviews()

        if reviews:
            for review in reviews[::-1]:
                if review[1] != 0:
                    return review[0]

    def _reviews(self):
        self._load_reviews()
        if self.reviews['RatingDistribution']:
            reviews = []

            for i in range(1,6):
                has_value = False

                for review in self.reviews['RatingDistribution']:
                    if review['RatingValue'] == i:
                        reviews.append([i, review['Count']])
                        has_value = True

                if not has_value:
                    reviews.append([i, 0])

            return reviews[::-1]
        return None

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        return self.tree_html.xpath('//span[@class="price"]/text()')[0]

    def _price_amount(self):
        return float(self._price()[1:])

    def _price_currency(self):
        return self.tree_html.xpath('//meta[@itemprop="priceCurrency"]/@content')[0]

    def _in_stores(self):
        return 0

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):
        if self.tree_html.xpath('//link[@itemprop="availability"]/@href')[0] == 'http://schema.org/OutOfStock':
            return 1

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
        #return self.tree_html.xpath('//div[@class="breadcrumbs"]//li/a/text()')[1:]
        categories = []

        for category in self.tree_html.xpath('//meta[@itemprop="category"]/@content')[0].split(' > '):
            if category and category not in categories:
                categories.append(category)

        return categories

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        brand = re.search('brand": "([^"]+)"', html.tostring(self.tree_html))

        if brand:
            return brand.group(1)

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        text = HTMLParser.HTMLParser().unescape(text)
        text = re.sub('[\r\n]', '', text)
        return text.strip()

    def _clean_html(self, html):
        html = re.sub('<(\w+)[^>]*>', r'<\1>', html)
        return self._clean_text(html)
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
        "ingredients" : _ingredients, \
        "ingredient_count" : _ingredient_count, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
        "pdf_count" : _pdf_count, \
        "pdf_urls" : _pdf_urls, \
        "wc_360": _wc_360, \
        "wc_emc": _wc_emc, \
        "wc_video": _wc_video, \
        "wc_pdf": _wc_pdf, \
        "wc_prodtour": _wc_prodtour, \
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
