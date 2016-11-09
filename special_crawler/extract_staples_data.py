#!/usr/bin/python
#  -*- coding: utf-8 -*-

import urllib
import re
import sys
import json
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


class StaplesScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www\.staples\.com/([a-zA-Z0-9\-/]+)/product_([a-zA-Z0-9]+)"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.review_json = None
        self.price_json = None

        self.reviews_tree = None
        self.max_score = None
        self.min_score = None
        self.review_count = 0
        self.average_review = None
        self.reviews = None
        self.feature_count = None
        self.features = None
        self.video_urls = None
        self.video_count = None
        self.pdf_urls = None
        self.pdf_count = None
        self.is_review_checked = False
        self.product_info_json = None
        self.is_product_info_json_checked = False
        self.variant_info_jsons = None
        self.is_variant_info_jsons_checked = False
        self.description = None
        self.long_description = None
        self.bullet_list = None

    def check_url_format(self):
        # for ex: http://www.staples.com/Epson-WorkForce-Pro-WF-4630-Color-Inkjet-All-in-One-Printer/product_242602?cmArea=home_box1
        m = re.match(r"^http://www\.staples\.com/([a-zA-Z0-9\-/]+/)?product_([a-zA-Z0-9]+)$", self.product_page_url)
        return not not m

    def _extract_product_info_json(self):
        if self.is_product_info_json_checked:
            return self.product_info_json

        self.is_product_info_json_checked = True

        try:
            selected_sku = self._find_between(html.tostring(self.tree_html), 'var selectedSKU = "', '";')
            product_info_json = self._find_between(html.tostring(self.tree_html), 'products["{0}"] ='.format(selected_sku), ';products["StaplesUSCAS/en-US/1/')

            if not product_info_json:
                product_info_json = self._find_between(html.tostring(self.tree_html), 'products["{0}"] ='.format(selected_sku), ";\n")

            product_info_json = json.loads(product_info_json)
        except:
            product_info_json = None

        self.product_info_json = product_info_json

    def _extract_variant_info_jsons(self):
        if self.is_variant_info_jsons_checked:
            return self.variant_info_jsons

        self.is_variant_info_jsons_checked = True

        variant_info_jsons = []

        try:
            parent_sku = self._find_between(html.tostring(self.tree_html), 'parentSKU = "', '";')

            skus = re.findall('products\["([^"]+)"\]', html.tostring(self.tree_html))

            for sku in skus:
                if sku == parent_sku:
                    continue

                variant_info_json = self._find_between(html.tostring(self.tree_html), 'products["{0}"] ='.format(sku), ';products["StaplesUSCAS/en-US/1/')

                if not variant_info_json:
                    variant_info_json = self._find_between(html.tostring(self.tree_html), 'products["{0}"] ='.format(sku), ";\n")

                variant_info_jsons.append( json.loads(variant_info_json))
        except:
            variant_info_jsons = None

        self.variant_info_jsons = variant_info_jsons

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        if not self.tree_html.xpath("//meta[@property='og:type' and @content='product']"):
            return True

        self._extract_product_info_json()
        self._extract_variant_info_jsons()

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        return re.search('_(\w+)$', self.product_page_url).group(1)

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//h1[@ng-bind-html]/text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//h1[@ng-bind-html]/text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//h1[@ng-bind-html]/text()")[0].strip()
    
    def _model(self):
        return self.product_info_json["metadata"]["mfpartnumber"]

    def _upc(self):
        return self.product_info_json["metadata"]["upc_code"]

    def _features(self):
        features = []
        rows = self.tree_html.xpath("//div[@id='specificationsContent']//table[@class='stp--cell prod-specifications']//tr")

        for row in rows:
            feature_info = row.xpath(".//td//text()")
            if feature_info == ['[~spec.attribname~]', '[~spec.attrvalue~]']:
                continue
            feature_text = ": ".join(feature_info)
            features.append(feature_text)

        if features:
            return features

        return None

    def _feature_count(self):
        features = self._features()

        if features:
            return len(features)

        return 0

    def _model_meta(self):
        return None

    def _description(self):
        self._get_long_and_short_description()

        if self.description:
            return self.description

    def _long_description(self):
        self._get_long_and_short_description()

        if self.long_description and not self.long_description == self.description:
            return self.long_description

    def _bullets(self):
        self._get_long_and_short_description()

        if self.bullet_list:
            return self.bullet_list
        return None

    def _get_long_and_short_description(self):
        paragraph = ""
        headliner = ""
        bullet_list = ""
        expanded_descr = ""

        description_info_list = self.product_info_json["description"]["details"]

        for description_info in description_info_list:
            if description_info["description_type"]["name"] == 'Paragraph':
                for t in description_info["text"]:
                    paragraph += (t["value"] + "\n")

            if description_info["description_type"]["name"] == 'Bullets':
                for t in description_info["text"]:
                    bullet_list += (t["value"] + "\n")

            if description_info["description_type"]["name"] == 'Headliner':
                for t in description_info["text"]:
                    headliner += (t["value"] + "\n")

            if description_info["description_type"]["name"] == 'Expanded Descr':
                for t in description_info["text"]:
                    expanded_descr += (t["value"] + "\n")

        # description = headliner + paragraph + bullet_list
        # long_description = expanded_descr

        self.description = headliner
        self.long_description = paragraph
        self.bullet_list = bullet_list

    def _variants(self):
        vrs = []

        for variant in self.variant_info_jsons:
            vr = {}
            vr['name'] = variant['metadata']['name']
            vrs.append(vr)

        if vrs:
            return vrs

    def _no_longer_available(self):
        if self.tree_html.xpath('//div[@class="content"]/p/text()'):
            return 1
        return 0

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        if not self.product_info_json:
            image_urls = self.tree_html.xpath('//img[@u="image"]/@src')
            return map(lambda u: u.split('?')[0], image_urls)

        if self.product_info_json["description"]["media"]["images"].get("enlarged"):
            image_urls = self.product_info_json["description"]["media"]["images"]["enlarged"]
            image_urls = [image_url["path"] + "_sc7" for image_url in image_urls]
        else:
            image_urls = self.product_info_json["description"]["media"]["images"]["standard"]
            image_urls = [image_url["path"].split('?')[0] for image_url in image_urls]

        if image_urls:
            return image_urls

        return None

    def _image_count(self):
        images = self._image_urls()

        if images:
            return len(images)

        return 0

    def _video_urls(self):
        return None

    def _video_count(self):
        urls = self._video_urls()

        if urls:
            return len(urls)
        return 0

    def _pdf_urls(self):
        pdfs = self.tree_html.xpath("//a[contains(@href,'.pdf')]")
        pdf_hrefs = []

        for pdf in pdfs:
            pdf_url_txts = [self._clean_text(r) for r in pdf.xpath(".//text()") if len(self._clean_text(r)) > 0]
            if len(pdf_url_txts) > 0:
                pdf_hrefs.append(pdf.attrib['href'])

        if len(pdf_hrefs) < 1:
            return None

        return pdf_hrefs

    def _pdf_count(self):
        urls = self._pdf_urls()

        if urls:
            return len(urls)

        return 0

    def _webcollage(self):
        atags = self.tree_html.xpath("//a[contains(@href, 'webcollage.net/')]")

        if len(atags) > 0:
            return 1

        return 0

    def _cnet(self):
        c = requests.get('http://ws.cnetcontent.com/d5eea376/script/522bca68e4?cpn=' + self._product_id() + '&lang=EN&market=US&host=www.staples.com&nld=1').content

        cnet_images = re.findall('ndata-image-url="([^"]+)', c.replace('\\', ''))

        if cnet_images:
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
        if self.is_review_checked:
            return self.reviews

        self.is_review_checked = True

        if self.product_info_json["review"]["count"] == 0:
            return None

        app_key = "LEb2xjVQAMYaTVrGjJ9vDjkj0wRSmKlIf7sdKxqy"
        widget_version = "2015-08-19_11-39-31"
        pid = self.product_info_json["metadata"]["partnumber"]
        load_form_encoded_string = 'methods=' + urllib.quote('[{"method":"main_widget","params":{"pid":"%s"}}]' % (pid)) + '&app_key=' + app_key + '&is_mobile=false&widget_version=%s' % (widget_version)

        review_page_html = requests.post('http://staticw2.yotpo.com/batch', data=load_form_encoded_string).text
        review_page_html = json.loads(review_page_html)[0]["result"]
        review_page_html = html.fromstring(review_page_html)

        review_info_by_rating = review_page_html.xpath("//span[contains(@class, 'yotpo-sum-reviews text-xs font-color-primary')]")
        reviews = []
        max_score = min_score = None
        review_count = 0

        for review in review_info_by_rating:
            if not max_score and int(review.xpath("./text()")[0][1:-1]) > 0:
                max_score = int(review.xpath("./@data-score-distribution")[0])
                min_score = int(review.xpath("./@data-score-distribution")[0])

            if min_score and int(review.xpath("./text()")[0][1:-1]) > 0 and min_score > int(review.xpath("./@data-score-distribution")[0]):
                min_score = int(review.xpath("./@data-score-distribution")[0])

            reviews.append([int(review.xpath("./@data-score-distribution")[0]), int(review.xpath("./text()")[0][1:-1])])
            review_count += int(review.xpath("./text()")[0][1:-1])

        if reviews:
            self.reviews = reviews
            self.review_count = review_count
            self.max_score = max_score
            self.min_score = min_score
            #self.average_review = float(self.product_info_json["review"]["rating"])

            return self.reviews

        return None

    def _average_review(self):
        yotpo_review = self.load_page_from_url_with_number_of_retries('http://www.staples.com/asgard-node/v1/nad/staplesus/yotporeview/' + self._product_id())

        average_review = re.search( 'yotpo-star-digits&amp;quot;&amp;gt; ([\d\.]+)', yotpo_review)

        if average_review:
            return float( average_review.group(1))

        return None

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
    def _price(self):
        price = self.tree_html.xpath("//span[@itemprop='price' and @class='SEOFinalPrice']/text()")[0].strip()
        return price

    def _price_amount(self):
        return float(self._price()[1:])

    def _price_currency(self):
        return "USD"

    def _in_stores(self):
        '''in_stores - the item can be ordered online for pickup in a physical store
        or it can not be ordered online at all and can only be purchased in a local store,
        irrespective of availability - binary
        '''
        return 1

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
        # site_online: the item is sold by the site (e.g. "sold by Amazon") and delivered directly, without a physical store.
        return 1

    def _site_online_out_of_stock(self):
        #  site_online_out_of_stock - currently unavailable from the site - binary
        if self._site_online() == 0:
            return None

        sku = re.search('selectedSKU = "([^"]+)"', html.tostring(self.tree_html)).group(1)

        pricing = self.load_page_from_url_with_number_of_retries('http://www.staples.com/asgard-node/v1/nad/staplesus/price/%s?offer_flag=true&warranty_flag=true&coming_soon=0&price_in_cart=0&productDocKey=%s' % (self._product_id(), sku))

        if json.loads(pricing)['cartAction'] == 'currentlyOutOfStock':
            return 1

        return 0

    def _in_stores_out_of_stock(self):
        '''in_stores_out_of_stock - currently unavailable for pickup from a physical store - binary
        (null should be used for items that can not be ordered online and the availability may depend on location of the store)
        '''
        if self._in_stores() == 0:
            return None

        return self.product_info_json["metadata"]["outofstock_flag"]

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        categories = self.tree_html.xpath("//li[@typeof='v:Breadcrumb']/a/text()")[1:]
        categories = [category.strip() for category in categories]

        if categories:
            return categories

        return None

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        return None

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces

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
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "model" : _model, \
        "upc" : _upc, \
        "long_description" : _long_description, \
        "bullets" : _bullets, \
        "variants" : _variants, \
        "no_longer_available" : _no_longer_available, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        "webcollage" : _webcollage, \
        "cnet" : _cnet, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "mobile_image_same" : _mobile_image_same, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "in_stores" : _in_stores, \
        "marketplace": _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \
        "site_online" : _site_online, \
        "site_online_out_of_stock" : _site_online_out_of_stock, \
        "in_stores_out_of_stock" : _in_stores_out_of_stock, \

         # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \

        "loaded_in_seconds": None \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
    }
