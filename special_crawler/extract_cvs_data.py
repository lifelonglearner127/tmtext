#!/usr/bin/python

import urllib
import re
import sys
import json
import ast
import HTMLParser

from lxml import html, etree
import time
import requests
from extract_data import Scraper


class CVSScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.cvs.com/shop/(.+/)*<product-name>-prodid-<prodid>?skuid-<skuid>"
    BASE_URL_REVIEWSREQ = 'http://cvspharmacy.ugc.bazaarvoice.com/3006-en_us/{0}/reviews.djs?format=embeddedhtml'
    BASE_URL_WEBCOLLAGE = 'http://content.webcollage.net/cvs/smart-button?ird=true&channel-product-id={0}'

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.product_json = None
        self.breadcrumb_list = None
        self.product = None
        self.offer = None
        self.full_description = None
        self.reviews = None
        self.is_review_checked = False
        self.is_webcollage_checked = False
        self.webcollage_content = None
        self.wc_360 = 0
        self.wc_emc = 0
        self.wc_video = 0
        self.wc_pdf = 0
        self.wc_prodtour = 0

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        #m = re.match(r"^http://www.cvs.com/shop/(.+/)*.+-prodid-\d+\?skuId=\d+$", self.product_page_url)
        #return not not m
        return True

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """

        self.product_json = json.loads( self.load_page_from_url_with_number_of_retries('https://www.cvs.com/retail/frontstore/productDetails?apiKey=c9c4a7d0-0a3c-4e88-ae30-ab24d2064e43&apiSecret=4bcd4484-c9f5-4479-a5ac-9e8e2c8ad4b0&appName=CVS_WEB&channelName=WEB&code=' + self._product_id() + '&codeType=sku&deviceToken=2695&deviceType=DESKTOP&lineOfBusiness=RETAIL&operationName=getSkuDetails&serviceCORS=True&serviceName=productDetails&version=1.0'))

        self.breadcrumb_list = json.loads( self.tree_html.xpath('//script[@type="application/ld+json"]')[0].text_content(), strict=False)

        self.product = json.loads( self.tree_html.xpath('//script[@type="application/ld+json"]')[1].text_content(), strict=False)

        if self.product['@type'] == 'Product':
            return False

        return True

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
        return re.findall('skuId=(\d+)$', self.product_page_url)[0]

    def _site_id(self):
        return self._product_id()

    def _status(self):
        return "success"

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _load_description(self):
        if not self.full_description:
            # The first 'offer' has the full description
            self.full_description = self._clean_text( self.product['offers'][0]['itemOffered']['description'])

    def _load_offer(self):
        if not self.offer:
            for offer in self.product['offers']:
                if offer['itemOffered']['sku'] == self._product_id():
                    self.offer = offer

    def _product_name(self):
        return self._clean_text( self.product['name'])

    def _product_title(self):
        return self.tree_html.xpath('//title')[0].text_content()

    def _title_seo(self):
        return self._product_title()

    def _model(self):
        model = re.search('Model # (\w+)', html.tostring( self.tree_html))

        if model:
            return model.group(1)

    def _upc(self):
        return None

    def _features(self):
        self._load_description()

        # Features are anything between <ul></ul>
        ul = re.search('<ul>.*</ul>', self.full_description, re.I)
        if ul:
            return self._clean_text( ul.group(0))

    def _feature_count(self):
        if self._features():
            return len( self._features().split('</li><li>'))

    def _model_meta(self):
        return None

    def _description(self):
        self._load_offer()
        return self._clean_text( self.full_description.split('Overview:')[0])

    def _long_description(self):
        self._load_description()

        long_description = self.full_description.split('Overview:')[1]

        # Remove features
        long_description = re.sub('<ul>.*</ul>', '', long_description, re.I)

        # Stop at Directions
        long_description = long_description.split('Directions:')[0]

        return self._clean_text( long_description)

    def _ingredients(self):
        self._load_description()

        ingredients = self.full_description[ self.full_description.index('Ingredients:'): ]
        ingredients = re.sub('(\.)?[^\.:]+:', ',', ingredients).split(',')

        ingredients = map(lambda x: self._clean_text(x), ingredients)
        ingredients = filter(len, ingredients)

        if ingredients:
            return ingredients

    def _ingredient_count(self):
        if self._ingredients():
            return len( self._ingredients())

    def _variants(self):
        variants = []

        for offer in self.product['offers']:
            if offer['itemOffered']['sku'] != self._product_id():
                variants.append({
                    'name' : self._clean_text( offer['itemOffered']['name']),
                    'in_stock' : offer['availability'] == 'http://schema.org/InStock',
                    'image' : offer['itemOffered']['image'],
                    'price' : offer['price'],
                    'properties' : {
                        'color' : offer['itemOffered']['color'],
                        'weight' : offer['itemOffered']['weight']['value'] + ' LBS'
                        },
                    'selected' : False,
                })

        if variants:
            return variants

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        self._load_offer()

        image_urls = []

        for offer in self.product['offers']:
            image_urls.append( offer['itemOffered']['image'] )

        if image_urls:
            return image_urls

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def _video_urls(self):
        return None

    def _video_count(self):
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
        if not self.is_webcollage_checked:
            self.is_webcollage_checked = True
            self.webcollage_content = urllib.urlopen(self.BASE_URL_WEBCOLLAGE.format(self._product_id())).read()

        if "_wccontent" in self.webcollage_content:
            self.wc_emc = 1

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
        return None

    def _keywords(self):
        return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    def _load_reviews(self):
        if not self.reviews:
            reviews = self.load_page_from_url_with_number_of_retries('http://api.bazaarvoice.com/data/batch.json?passkey=ll0p381luv8c3ler72m8irrwo&apiversion=5.5&displaycode=3006-en_us&resource.q0=products&filter.q0=id%3Aeq%3A' + self._product_id() + '&stats.q0=questions%2Creviews&filteredstats.q0=questions%2Creviews&filter_questions.q0=contentlocale%3Aeq%3Aen_US&filter_answers.q0=contentlocale%3Aeq%3Aen_US&filter_reviews.q0=contentlocale%3Aeq%3Aen_US&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_US&resource.q1=reviews&filter.q1=isratingsonly%3Aeq%3Afalse&filter.q1=productid%3Aeq%3A' + self._product_id() + '&filter.q1=contentlocale%3Aeq%3Aen_US&sort.q1=relevancy%3Aa1&stats.q1=reviews&filteredstats.q1=reviews&include.q1=authors%2Cproducts%2Ccomments&filter_reviews.q1=contentlocale%3Aeq%3Aen_US&filter_reviewcomments.q1=contentlocale%3Aeq%3Aen_US&filter_comments.q1=contentlocale%3Aeq%3Aen_US&limit.q1=8&offset.q1=0&limit_comments.q1=3&resource.q2=reviews&filter.q2=productid%3Aeq%3A' + self._product_id() + '&filter.q2=contentlocale%3Aeq%3Aen_US&limit.q2=1&resource.q3=reviews&filter.q3=productid%3Aeq%3A' + self._product_id() + '&filter.q3=isratingsonly%3Aeq%3Afalse&filter.q3=rating%3Agt%3A3&filter.q3=totalpositivefeedbackcount%3Agte%3A3&filter.q3=contentlocale%3Aeq%3Aen_US&sort.q3=totalpositivefeedbackcount%3Adesc&include.q3=authors%2Creviews%2Cproducts&filter_reviews.q3=contentlocale%3Aeq%3Aen_US&limit.q3=1&resource.q4=reviews&filter.q4=productid%3Aeq%3A' + self._product_id() + '&filter.q4=isratingsonly%3Aeq%3Afalse&filter.q4=rating%3Alte%3A3&filter.q4=totalpositivefeedbackcount%3Agte%3A3&filter.q4=contentlocale%3Aeq%3Aen_US&sort.q4=totalpositivefeedbackcount%3Adesc&include.q4=authors%2Creviews%2Cproducts&filter_reviews.q4=contentlocale%3Aeq%3Aen_US&limit.q4=1&callback=bv_1111_26782')

            self.reviews = json.loads( re.match('bv[_\d]+\(({.*})', reviews).group(1))

    def _average_review(self):
        self._load_reviews()
        return round( self.reviews['BatchedResults']['q0']['Results'][0]['FilteredReviewStatistics']['AverageOverallRating'], 2)

    def _review_count(self):
        self._load_reviews()
        return self.reviews['BatchedResults']['q0']['Results'][0]['FilteredReviewStatistics']['TotalReviewCount']

    def _max_review(self):
        self._load_reviews()
        for review in self._reviews():
            if not review[1] == 0:
                return review[0]
        return None

    def _min_review(self):
        self._load_reviews()
        for review in self._reviews()[::-1]:
            if not review[1] == 0:
                return review[0]
        return None

    def _reviews(self):
        self._load_reviews()

        reviews = []

        ratings_distribution = self.reviews['BatchedResults']['q0']['Results'][0]['FilteredReviewStatistics']['RatingDistribution']

        for rating in ratings_distribution:
            reviews.append([rating['RatingValue'], rating['Count']])

        if reviews:
            return reviews[::-1] # reverses list

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        return '$' + str( self._price_amount())

    def _price_amount(self):
        self._load_offer()
        return float( self.offer['price'])

    def _price_currency(self):
        return self._find_between(html.tostring(self.tree_html), 'currency : "', '"',)

    def _in_stores(self):
        return 0

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):
        if self.offer['availability'] != 'http://schema.org/InStock':
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
        breadcrumbs = map( lambda x: self._clean_text( x['item']['name']), self.breadcrumb_list['itemListElement'])
        # First two are 'home' and 'shop'
        return breadcrumbs[2:]

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        return self._clean_text( self.product['brand'])

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        text = HTMLParser.HTMLParser().unescape( text)
        text = re.sub('[\r\n\t]', '', text)
        text = re.sub('>\s+<', '><', text)
        return re.sub('\s+', ' ', text).strip()

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
        "variants": _variants, \

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
