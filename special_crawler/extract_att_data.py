#!/usr/bin/python

import re
import HTMLParser
import json
import requests

from lxml import html, etree
from extract_data import Scraper


class ATTScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is https://www.att.com/.*.html(?)(#sku=sku<skuid>)"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.wc_360 = 0
        self.wc_emc = 0
        self.wc_video = 0
        self.wc_pdf = 0
        self.wc_prodtour = 0

        self.videos = None
        self.videos_checked = False

        self.variants = None
        self.variants_checked = False

        self.pricearea_html = None
        self.pricearea_html_checked = False

        self.product_xml = None
        self.product_xml_checked = False

        self.product_details = None
        self.product_details_checked = False

        self.product_json = None

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match('^https://www.att.com/.*\.html\??(#sku=sku\d+)?$', self.product_page_url)
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
        return re.findall('sku(\d+)', html.tostring(self.tree_html))[0]

    def _site_id(self):
        return self._product_id()

    def _status(self):
        return "success"

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _load_product_json(self):
        if not self.product_json:
            product_json = json.loads( self.load_page_from_url_with_number_of_retries('https://api.bazaarvoice.com/data/batch.json?passkey=9v8vw9jrx3krjtkp26homrdl8&apiversion=5.5&displaycode=4773-en_us&resource.q0=products&filter.q0=id%3Aeq%3Asku' + self._product_id() + '&stats.q0=questions%2Creviews'))

            self.product_json = product_json['BatchedResults']['q0']['Results'][0]

    def _get_pricearea_html(self):
        if not self.pricearea_html_checked:
            self.pricearea_html_checked = True

            url = re.match('(.*).html.*', self.product_page_url).group(1) + '.pricearea.xhr.html?locale=en_US&skuId=sku' + self._product_id() + '&pageType=accessoryDetails&_=1461605909259'

            self.pricearea_html = html.fromstring( self.load_page_from_url_with_number_of_retries(url))

        return self.pricearea_html

    def _get_product_xml(self):
        if not self.product_xml_checked:
            self.product_xml_checked = True

            response = requests.get('https://www.att.com/shop/360s/xml/' + self._product_id() + '.xml')

            if response.status_code == 200:
                self.product_xml = etree.XML(response.content.replace(' encoding="UTF-8"', '').replace('&', '&amp;'))

        return self.product_xml

    def _get_product_details(self):
        if not self.product_details_checked:
            self.product_details_checked = True

            try:
                product_details = json.loads( self.load_page_from_url_with_number_of_retries('https://www.att.com/services/shopwireless/model/att/ecom/api/DeviceDetailsActor/getDeviceProductDetails?includeAssociatedProducts=true&includePrices=true&skuId=sku' + self._product_id()))

                self.product_details = product_details['result']['methodReturnValue']

            except:
                pass

        return self.product_details

    def _product_name(self):
        self._load_product_json()
        return self.product_json['Name']

    def _product_title(self):
        return self.tree_html.xpath('//meta[@property="og:title"]/@content')[0]

    def _title_seo(self):
        return self._product_title()

    def _model(self):
        return None

    def _upc(self):
        self._load_product_json()
        return self.product_json['UPCs'][0]

    def _model_meta(self):
        return None

    def _description(self):
        return self.tree_html.xpath('//meta[@property="og:description" or @name="og:description"]/@content')[0]

    def _long_description(self):
        return None

    def _variants(self):
        if self.variants_checked:
            return self.variants

        self.variants_checked = True

        variants = []

        if self._get_product_details():

            if len( self.product_details['skuItems']) > 1:

                for skuId in self.product_details['skuItems']:

                    variant_json = self.product_details['skuItems'][skuId]

                    variant = {
                        'color' : variant_json['color'],
                        'selected' : variant_json['selectedSku'],
                        'price' : self._get_price( variant_json['priceList'])[0],
                        'outOfStock' : variant_json['outOfStock']
                    }

                    variants.append(variant)

        else:
            for variant_html in self._get_pricearea_html().xpath('//span[@id="colorInput"]/a'):

                price = self._clean_text( self.pricearea_html.xpath('//div[@id="dueToday"]/div[contains(@class,"price")]/text()')[0])

                out_of_stock = self.pricearea_html.xpath('//div[@id="deliveryPromise"]/@data-outofstock')[0] == 'true'

                variant = {
                    'color' : variant_html.get('title'),
                    'selected' : 'current' in variant_html.get('class'),
                    'price' : price,
                    'outOfStock' : out_of_stock
                }

                variants.append(variant)

        if variants:
            self.variants = variants

        return self.variants

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        #images = self.tree_html.xpath('//meta[@property="og:image"]/@content')
        images = self.tree_html.xpath('//img[@itemprop="image"]/@src')

        if self._get_product_xml():
            for image in self.product_xml.xpath('//image_info'):
                images.append('https://www.att.com' + image.get('path') + image.get('suffix'))

        if images:
            return images

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def _video_urls(self):
        if self.videos_checked:
            return self.videos

        self.videos_checked = True

        videos = []

        if self._get_product_xml():
            for gvpURL in self.product_xml.xpath('//movie/@gvpURL'):

                response = self.load_page_from_url_with_number_of_retries( 'https://www.att.com/global-search/GenericLayer.jsp?q=id:' + gvpURL + '&core=videoservice&handler=select')

                for url in re.findall('url_videoMain_en":"([^"]+)"', response):
                    videos.append( url[2:] + '/'+ url.split('/')[-1] + '.mp4')

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

        htags_dict['h1'] = filter(lambda t: not re.match('{{', t), htags_dict['h1'])

        return htags_dict

    def _keywords(self):
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0]


    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    def _average_review(self):
        self._load_product_json()

        return round( self.product_json['ReviewStatistics']['AverageOverallRating'], 1)

    def _review_count(self):
        self._load_product_json()

        return self.product_json['ReviewStatistics']['TotalReviewCount']

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
        self._load_product_json()

        reviews = []

        ratings_distribution = self.product_json['ReviewStatistics']['RatingDistribution']

        if ratings_distribution:
            for i in range(0,5):
                ratingFound = False

                for rating in ratings_distribution:
                    if rating['RatingValue'] == i + 1:
                        reviews.append([rating['RatingValue'], rating['Count']])
                        ratingFound = True
                        break

                if not ratingFound:
                    reviews.append([i+1, 0])

            return reviews[::-1] # reverses list

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        if self._get_product_details():
            return self._get_price( self._get_selected_variant()['priceList'])[0]

        return self._clean_text( self._get_pricearea_html().xpath('//div[@id="dueToday"]/div[contains(@class,"price")]/text()')[0])

    def _price_amount(self):
        return self._price()[1:]

    def _price_currency(self):
        return 'USD'

    def _in_stores(self):
        return 0

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):
        if self._get_product_details():
            if self._get_selected_variant()['outOfStock']:
                return 1
            return 0

        if self._get_pricearea_html().xpath('//div[@id="addToCartDiv"]'):
            return 0
        return 1

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

    def _temp_price_cut(self):
        if self._get_product_details():
            return self._get_price( self._get_selected_variant()['priceList'])[1]

        if self._get_pricearea_html().xpath('//div[contains(@class,"pricingregular")]//div[contains(@class,"price")]/text()')[0] != self._price():
            return 1

        return 0

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        #self._url().split('/')[3:-1]
        breadcrumbs = self.tree_html.xpath('//div[@ng-controller="breadCrumbsController"]/@ng-init')[0]
        return re.findall('"title":"([^"]+)"', breadcrumbs)[:-1]

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        self._load_product_json()
        return self.product_json['Brand']['Name']

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        text = HTMLParser.HTMLParser().unescape(text)
        text = re.sub('[\r\n]', '', text)
        return text.strip()

    def _get_price(self, price_list):
        low_price = None
        on_sale = 0

        for price_json in price_list:
            if price_json['leaseTotalMonths'] == 0:
                if price_json['salePrice']:
                    price = price_json['salePrice']
                    on_sale = 1
                else:
                    price = price_json['dueToday']

            if not low_price or price < low_price:
                low_price = price

        return ('$' + str(low_price), on_sale)

    def _get_selected_variant(self):
        if self._get_product_details():
            for skuId in self.product_details['skuItems']:
                variant_json = self.product_details['skuItems'][skuId]
                if variant_json['selectedSku'] or len(self.product_details['skuItems']) == 1:
                    return variant_json

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
        "model_meta" : _model_meta, \
        "description" : _description, \
        "long_description" : _long_description, \
        "variants" : _variants, \

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
        "temp_price_cut" : _temp_price_cut, \

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
