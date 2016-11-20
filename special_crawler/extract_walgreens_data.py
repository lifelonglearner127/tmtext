#!/usr/bin/python

import re
import json
import copy
import requests

from lxml import html, etree
from HTMLParser import HTMLParser
from extract_data import Scraper

class WalgreensScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http(s)://www.walgreens.com/store/c/<product-name>/ID=prod<id>-product"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.webcollage = None
        self.wc_360 = 0
        self.wc_emc = 0
        self.wc_video = 0
        self.wc_pdf = 0
        self.wc_prodtour = 0

        self.product_json = None
        self.price_info = None
        self.inventory = None
        self.ingredients = None
        self.images = None
        self.videos = None
        self.reviews = None

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        if re.match('^https?://www.walgreens.com/store/c/.+/ID=prod\d+-product$', self.product_page_url):
            return True
        return False

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        try:
            if not self.tree_html.xpath('//span[@itemtype="http://schema.org/Product"]'):
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
        return re.search('ID=prod(\d+)', self.product_page_url).group(1)

    def _site_id(self):
        return self._product_id()

    def _status(self):
        return "success"

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _load_product_json(self):
        if not self.product_json:
            self.product_json = json.loads( self.load_page_from_url_with_number_of_retries('http://api.bazaarvoice.com/data/batch.json?passkey=tpcm2y0z48bicyt0z3et5n2xf&apiversion=5.5&displaycode=2001-en_us&resource.q0=products&filter.q0=id%3Aeq%3Aprod' + self._product_id() + '&stats.q0=reviews'))

    def _product_name(self):
        return self._clean_text( self.tree_html.xpath('//h1[@id="productName"]/text()')[0])

    def _product_title(self):
        return self._clean_text( self.tree_html.xpath('//title/text()')[0])

    def _title_seo(self):
        return self._product_title()

    def _model(self):
        self._load_product_json()

        return self.product_json['BatchedResults']['q0']['Results'][0]['ModelNumbers'][0]

    def _upc(self):
        self._load_product_json()

        return self.product_json['BatchedResults']['q0']['Results'][0]['UPCs'][0]

    def _features(self):
        return None

    def _feature_count(self):
        return None

    def _model_meta(self):
        return None

    def _description(self):
        description = '<ul>'

        description_elements = self.tree_html.xpath('//ul[@id="wag-vpd-overview-ul"]//li[not(contains(@class,"wag-list-unstyled"))]')

        if not description_elements:
            desc = re.search('&lt;ul id=&quot;wag-vpd-overview-ul&quot;.*?&lt;/ul&gt;', self.page_raw_text, re.DOTALL).group(0)

            desc = HTMLParser().unescape(desc)
            desc = self._exclude_javascript_from_description(desc)
            desc = html.fromstring(desc)

            description_elements = desc.xpath('//ul[@id="wag-vpd-overview-ul"]//li[not(contains(@class,"wag-list-unstyled"))]')

        for li in description_elements:
            description += self._clean_html( html.tostring(li))

        if description != '<ul>':
            return description + '</ul>'


    def _long_description(self):
        product_info = requests.get('http://api.bazaarvoice.com/data/batch.json?passkey=tpcm2y0z48bicyt0z3et5n2xf&apiversion=5.5&displaycode=2001-en_us&resource.q0=products&filter.q0=id%3Aeq%3Aprod' + self._product_id()).content

        product_info = json.loads(product_info)['BatchedResults']['q0']
        product_info = product_info['Results'][0]['Description']

        return re.sub('([a-z][a-z\).])([A-Z\d])', r'\1\n\2', product_info)

    def _ingredients(self):
        if not self.ingredients:
            if self.tree_html.xpath('//section[@id="collapseFive"]'):
                ingredients = self.tree_html.xpath('//section[@id="collapseFive"]/section')[0].text_content().split("\n")

                self.ingredients = []

                for ingredient in ingredients:
                    ingredient = self._clean_text( ingredient.replace(',', ''))

                    if ingredient and not 'Ingredients' in ingredient:
                        self.ingredients.append( ingredient)

        if self.ingredients:
            return self.ingredients

    def _ingredient_count(self):
        self._ingredients()

        if self.ingredients:
            return len(self.ingredients)

    def _variants(self):
        self._load_price_info_and_inventory()

        variants = []

        if self.inventory.get('relatedProducts'):
            i = 0
            for property in self.inventory['relatedProducts'].keys():
                j = 0
                for product in self.inventory['relatedProducts'][property]:
                    if i == 0:
                        variant = {
                            'in_stock' : product['isavlbl'] == 'yes',
                            'properties' : {
                                property : product['value']
                                },
                            }

                        if product.get('key'):
                            variant['sku'] = product['key'][3:], # remove 'sku'

                        variants.append(variant)
                    else:
                        if j == 0:
                            for variant in variants:
                                variant['properties'][property] = product['value']
                        else:
                            for variant in copy.deepcopy(variants):
                                variant2 = copy.deepcopy(variant)
                                variant2['properties'][property] = product['value']
                                if product['isavlbl'] == 'no':
                                    variant2['in_stock'] == 'no'
                                variants.append(variant2)
                    j += 1
                i += 1

        if variants:
            return variants

    def _swatches(self):
        self._load_price_info_and_inventory()

        swatches = []

        if self.inventory.get('relatedProducts'):
            for product in self.inventory['relatedProducts']['color']:
                swatch = {
                    'color' : product['value'],
                    'hero' : 0,
                    'hero_image' : None,
                    'swatch_name' : 'color',
                }

                if product.get('url'):
                    swatch['hero_image'] = [product['url'].split('?')[0][2:]]
                    swatch['hero'] = len( swatch['hero_image'])

                swatches.append(swatch)

        if swatches:
            return swatches


    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _load_webcollage(self):
        if not self.webcollage:
            self.webcollage = self.load_page_from_url_with_number_of_retries('http://content.webcollage.net/walgreens/smart-button?ird=true&channel-product-id=prod' + self._product_id())

    def _mobile_image_same(self):
        return None

    def _thumbnail(self):
        thumbnail = self.tree_html.xpath('//a[@id="product-50x50_a"]/img/@src')
        return thumbnail[0][2:] # remove initial '//'

    def _image_urls(self):
        if not self.images:
            images = []

            image_urls = self.tree_html.xpath('(figure[contains(@class,"wag-vpd-product-images")]|//ul[@id="proImgThumbnail"])//img/@src')

            for image in image_urls:
                if re.search('/([\d_]+).jpg', image):
                    image = re.sub('(\d+).jpg', '450.jpg', image)
                    if not image[2:] in images:
                        images.append( image[2:]) # remove initial '//'

            if images:
                self.images = images

        return self.images

    def _image_count(self):
        self._image_urls()

        if self.images:
            return len(self.images)

        return 0

    def _video_urls(self):
        self._load_webcollage()

        if not self.videos:
            base_url = re.search(r'data-resources-base=\\"([^"]+)\\"', self.webcollage)

            if base_url:
                base_url = base_url.group(1).replace('\\', '')

                video_urls = []

                for mp4 in re.findall(r'"([^"]+mp4full.mp4)\\"', self.webcollage):
                    video_urls.append( base_url + mp4.replace('\\', ''))

                if video_urls:
                    self.videos = video_urls

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

        htags_dict['h2'] = filter(lambda t: not re.match('{{.*}}', t), htags_dict['h2'])

        return htags_dict

    def _keywords(self):
        return None


    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    def _load_reviews(self):
        self._load_product_json()

        if self.product_json and not self.reviews:
            self.reviews = self.product_json['BatchedResults']['q0']['Results'][0]['ReviewStatistics']

    def _average_review(self):
        self._load_reviews()

        if self.reviews:
            if self.reviews['AverageOverallRating']:
                return round( self.reviews['AverageOverallRating'], 1)

    def _review_count(self):
        self._load_reviews()

        if self.reviews:
            return self.reviews['TotalReviewCount']

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

        if self._review_count() > 0:
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

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _load_price_info_and_inventory(self):
        if not (self.price_info or self.inventory):
            price_info_and_inventory = json.loads( self.load_page_from_url_with_number_of_retries('http://www.walgreens.com/svc/products/prod' + self._product_id() + '/(PriceInfo+Inventory)'))

            self.price_info = price_info_and_inventory['priceInfo']
            self.inventory = price_info_and_inventory['inventory']

    def _price(self):
        self._load_price_info_and_inventory()

        # Account for price format 2/$p2 or 1/$p1 (use p1)
        if self.price_info.get('salePrice'):
            return self.price_info['salePrice'].split('or')[-1].split('/')[-1]
        elif self.price_info.get('regularPrice'):
            return self.price_info['regularPrice'].split('or')[-1].split('/')[-1]

    def _price_amount(self):
        if self._price():
            return float( self._price()[1:])

    def _price_currency(self):
        if self._price():
            return 'USD'

    def _in_stores(self):
        self._load_price_info_and_inventory()

        if self.inventory.get('pickupAvailableMessage') and self.inventory['pickupAvailableMessage'] == 'Not sold in stores':
            return 0

        return 1

    def _site_online(self):
        self._load_price_info_and_inventory()

        if self.inventory.get('shipAvailableMessage') and self.inventory['shipAvailableMessage'] == 'Not sold online':
            return 0

        return 1

    def _site_online_out_of_stock(self):
        self._load_price_info_and_inventory()

        if self.inventory.get('shipAvailableMessage') and self.inventory['shipAvailableMessage'] == 'Temporarily out of stock':
            return 1

        return 0

    def _in_stores_out_of_stock(self):
        self._load_price_info_and_inventory()

        if self._in_stores():
            if not 'Pickup' in self.inventory['availableOptions']:
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

    def _temp_price_cut(self):
        self._load_price_info_and_inventory()

        if self.price_info.get('salePrice'):
            return 1

        return 0

    def _web_only(self):
        return not self._in_stores()

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        categories = self.tree_html.xpath('//ul[contains(@class, "breadcrumb")]/li/a/text()')
        return categories[2:] # remove Home, Shop

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        self._load_product_json()

        if self.product_json:
            return self.product_json['BatchedResults']['q0']['Results'][0]['Brand']['Name']

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        text = re.sub('[\r\n\t]', '', text)
        return text.strip()

    def _clean_html(self, html):
        html = HTMLParser().unescape( html)
        html = re.sub( ' \w+="[^"]+"', '', html)
        return html

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
        "variants" : _variants, \
        "swatches" : _swatches, \

        # CONTAINER : PAGE_ATTRIBUTES
        "thumbnail" : _thumbnail,\
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
        "web_only" : _web_only, \

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
