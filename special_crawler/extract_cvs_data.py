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
        self.full_description = None
        self.reviews = None
        self.images = None
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
        m = re.match(r"^http://www.cvs.com/shop/(.+/)*.+-prodid-\d+\?skuId=\d+$", self.product_page_url)
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
            self.product = json.loads( self.tree_html.xpath('//script[@type="application/ld+json"]')[1].text_content(), strict=False)

            if self.product['@type'] == 'Product':
                return False
        except:
            pass

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
    def _load_product_json(self):
        if not self.product_json:
            self.product_json = json.loads( self.load_page_from_url_with_number_of_retries('https://www.cvs.com/retail/frontstore/productDetails?apiKey=c9c4a7d0-0a3c-4e88-ae30-ab24d2064e43&apiSecret=4bcd4484-c9f5-4479-a5ac-9e8e2c8ad4b0&appName=CVS_WEB&channelName=WEB&code=' + self._product_id() + '&codeType=sku&deviceToken=2695&deviceType=DESKTOP&lineOfBusiness=RETAIL&operationName=getSkuDetails&serviceCORS=True&serviceName=productDetails&version=1.0'))

    def _load_breadcrumb_list(self):
        if not self.breadcrumb_list:
            self.breadcrumb_list = json.loads( self.tree_html.xpath('//script[@type="application/ld+json"]')[0].text_content(), strict=False)

    def _load_description(self):
        if not self.full_description:
            # The first 'offer' has the full description
            self.full_description = self._clean_text( self.product['offers'][0]['itemOffered']['description'])

    def _offer(self):
        for offer in self.product['offers']:
            if offer['itemOffered']['sku'] == self._product_id():
                return offer

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

        ul = re.search('<ul>.*</ul>', self.full_description, re.I)
        if ul:
            return self._clean_text( ul.group(0))

    def _feature_count(self):
        if self._features():
            return len( self._features().split('</li><li>'))

    def _model_meta(self):
        return None

    def _description(self):
        self._load_description()
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

        if len( self.product['offers']) > 1:
            for offer in self.product['offers']:
                variants.append({
                    'name' : self._clean_text( offer['itemOffered']['name']),
                    'in_stock' : offer['availability'] == 'http://schema.org/InStock',
                    'image' : offer['itemOffered']['image'],
                    'price' : offer['price'],
                    'properties' : {
                        'color' : offer['itemOffered']['color'],
                        'weight' : offer['itemOffered']['weight']['value'] + ' LBS'
                        },
                    'selected' : offer['itemOffered']['sku'] == self._product_id(),
                })

        if variants:
            return variants

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        if self.images:
            return self.images

        image_urls = []

        num_images = 6
        first_offer = True

        for offer in self.product['offers']:
            if not offer['itemOffered']['image'] in image_urls:
                image_urls.append( offer['itemOffered']['image'] )

                for i in range(2, num_images):
                    image_url = offer['itemOffered']['image'][:-4] + '_' + str(i) + '.jpg'
                    if requests.head( image_url).status_code == 200:
                        image_urls.append(image_url)
                    elif first_offer:
                        num_images = i
                        first_offer = False

        self.images = image_urls

        if image_urls:
            return image_urls

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def _video_urls(self):
        self._webcollage()

        video_urls = []

        for wcobj in re.findall(r'wcobj=\\"([^"]+)\\"', self.webcollage_content):
            if re.search('.flv$', wcobj.replace('\\', '')):
                video_urls.append( wcobj.replace('\\', ''))

        if video_urls:
            return video_urls

    def _video_count(self):
        video_urls = self._video_urls()

        if video_urls:
            return len( video_urls)

    def _pdf_urls(self):
        self._webcollage()

        pdf_urls = []

        for wcobj in re.findall(r'wcobj=\\"([^"]+)\\"', self.webcollage_content):
            if re.search('.pdf$', wcobj.replace('\\', '')):
                pdf_urls.append( wcobj.replace('\\', ''))

        if pdf_urls:
            return pdf_urls

    def _pdf_count(self):
        pdf_urls = self._pdf_urls()

        if pdf_urls:
            return len( pdf_urls)

    def _webcollage(self):
        """Uses video and pdf information
        to check whether product has any media from webcollage.
        Returns:
            1 if there is webcollage media
            0 otherwise
        """
        if not self.is_webcollage_checked:
            self.is_webcollage_checked = True
            self.webcollage_content = self.load_page_from_url_with_number_of_retries('http://content.webcollage.net/cvs/power-page?ird=true&channel-product-id=' + self._product_id())

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
            reviews = self.load_page_from_url_with_number_of_retries('http://api.bazaarvoice.com/data/batch.json?passkey=ll0p381luv8c3ler72m8irrwo&apiversion=5.5&displaycode=3006-en_us&resource.q0=products&filter.q0=id%3Aeq%3A' + self._product_id() + '&stats.q0=questions%2Creviews')

            try:
                self.reviews = json.loads(reviews)['BatchedResults']['q0']['Results'][0]['ReviewStatistics']
            except:
                pass

    def _average_review(self):
        self._load_reviews()

        if self.reviews:
            return round(self.reviews['AverageOverallRating'], 1)

    def _review_count(self):
        self._load_reviews()

        if self.reviews:
            return self.reviews['TotalReviewCount']
        else:
            return 0

    def _max_review(self):
        if self._reviews():
            for review in self._reviews():
                if not review[1] == 0:
                    return review[0]

    def _min_review(self):
        if self._reviews():
            for review in self._reviews()[::-1]: # reverses list
                if not review[1] == 0:
                    return review[0]

    def _reviews(self):
        self._load_reviews()

        if self.reviews:
            reviews = []

            ratings_distribution = self.reviews['RatingDistribution']

            for rating in ratings_distribution:
                reviews.append( [rating['RatingValue'], rating['Count']])

            if reviews:
                # Insert 0 for nonexistant ratings
                for i in range(0,5):
                    if len(reviews) <= i or not reviews[i][0] == i + 1:
                        reviews.insert(i, [i+1, 0])

                return reviews[::-1] # reverses list

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        return '$' + str( self._price_amount())

    def _price_amount(self):
        return float( self._offer()['price'])

    def _price_currency(self):
        return self._find_between(html.tostring(self.tree_html), 'currency : "', '"',)

    def _in_stores(self):
        return 0

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):
        if self._offer()['availability'] != 'http://schema.org/InStock':
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
        self._load_breadcrumb_list()
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
