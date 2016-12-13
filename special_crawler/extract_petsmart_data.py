#!/usr/bin/python
#  -*- coding: utf-8 -*-

import re, json, requests
from lxml import html, etree
from extract_data import Scraper

class PetsmartScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = 'Expected URL format is http://www.petsmart.com/(.+/)*<product-name>-zid36-<id>/cat-36-catid-<product-id>'

    def __init__(self, **kwargs):
        Scraper.__init__(self, **kwargs)

        self.images_checked = False
        self.images = None

        self.reviews_checked = False
        self.review_values = None
        self.reviews_tree = None

    def check_url_format(self):
        if re.match('^http://www.petsmart.com/(.+/)*.+-zid36-\d+/cat-36-catid-\d+$', self.product_page_url):
            return True
        return False

    def not_a_product(self):
        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        return self.tree_html.xpath('//span[contains(@class,"ws-product-item-number-value")]/text()')[0]

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//h1[@data-dynamic-block-name="Title"]/text()')[0]

    def _product_title(self):
        return self._product_name()

    def _title_seo(self):
        return self.tree_html.xpath('//title/text()')[0].strip()

    def _descriptions(self):
        description_html = ''.join(map(lambda e: self._clean_html(html.tostring(e)), self.tree_html.xpath('//div[@data-dynamic-block-name="LongDescription"]/*')))

        try:
            split_index = re.search('(<p>)?((<b>)|(<strong>))', description_html).start()
            return (description_html[:split_index], description_html[split_index:])
        except:
            return (description_html, None)

    def _description(self):
        return self._descriptions()[0]

    def _long_description(self):
        return self._descriptions()[1]

    def _features(self):
        long_description = self._long_description()

        try:
            label_index = re.search('((<b>)|(<strong>))Features', long_description).start()
            label_index = long_description.find('Features', label_index)
        except:
            return None

        features_start_index = re.search('>\s*\w', long_description[label_index:]).start() + label_index + 1

        features_end_index = long_description.find('<', features_start_index)

        features = long_description[features_start_index:features_end_index]
        features = map(lambda i: i.strip(), features.split(';'))

        return features

    def _feature_count(self):
        if self._features():
            return len(self._features())
        return 0

    def _ingredients(self):
        long_description = self._long_description()

        try:
            label_index = re.search('((<b>)|(<strong>))Ingredients', long_description).start()
            label_index = long_description.find('Ingredients', label_index)
        except:
            return None

        ingredients_start_index = re.search('>\s*\w', long_description[label_index:]).start() + label_index + 1

        ingredients_end_index = long_description.find('<', ingredients_start_index)

        ingredients = long_description[ingredients_start_index:ingredients_end_index]
        ingredients = map(lambda i: i.split(':')[-1].strip(), ingredients.split(','))

        return ingredients

    def _ingredient_count(self):
        if self._ingredients():
            return len(self._ingredients())
        return 0

    def _directions(self):
        long_description = self._long_description()

        try:
            label_index = re.search('((<b>)|(<strong>))Directions', long_description).start()
            label_index = long_description.find('Directions', label_index)
        except:
            return None

        directions_start_index = re.search('>\s*\w', long_description[label_index:]).start() + label_index + 1

        directions_end_index = re.search('(<b>)|(<p>)|(<strong>)', long_description[directions_start_index:]).start() + directions_start_index

        return long_description[directions_start_index:directions_end_index]

    def _variants(self):
        uuid = self.tree_html.xpath('//div/@data-product')[0]

        c = requests.get('http://www.petsmart.com/gsi/webstore/WFS/PETNA-PETUS-Site/en_US/-/USD/GetProductData-FormatProduct?Format=JSON&ReturnVariable=true&ProductUUID=' + uuid).content

        j = json.loads(re.search('({.*})', c.replace("\\'", "'"), re.DOTALL).group(1))

        variants = []

        for id in j['productVariations']:
            variant = j['productVariations'][id]

            properties = {}

            for key in variant.keys():
                if key[0].isupper() and not key == 'ShopRunnerEligible':
                    key_name = key
                    if key == 'SizeCode':
                        key_name = 'Size'
                    properties[key_name] = variant[key]

            image_url = None

            for image in variant['images']:
                if image['size'] == 'ENH':
                    image_url = image['src']

            v = {
                'properties' : properties,
                'image_url' : image_url,
                'price' : self._price_amount(), # TODO: this is wrong
                'selected' : False,
                'in_stock' : variant['inStock'],
            }

            variants.append(v)

        if len(variants) > 1:
            return variants

    def _no_longer_available(self):
        return 0

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _keywords(self):
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0]

    def _htags(self):
        htags_dict = {}

        htags_dict['h1'] = map(lambda t: self._clean_text(t), self.tree_html.xpath('//h1//text()[normalize-space()!=""]'))
        htags_dict['h2'] = map(lambda t: self._clean_text(t), self.tree_html.xpath('//h2//text()[normalize-space()!=""]'))

        return htags_dict

    def _canonical_link(self):
        return self.tree_html.xpath('//link[@rel="canonical"]/@href')[0]

    def _image_urls(self):
        image_urls = []

        if self.images_checked:
            return self.image_urls

        self.images_checked = True

        uuid = self.tree_html.xpath('//div/@data-product')[0]

        c = requests.get('http://www.petsmart.com/gsi/webstore/WFS/PETNA-PETUS-Site/en_US/-/USD/GetProductData-FormatProduct?Format=JSON&ProductUUID=' + uuid).content

        j = json.loads(c.replace("\\'", "'"))

        main_image = None

        for image in j['images']:
            if image['size'] == 'ENH':
                if image['view'] == 'main':
                    main_image = image['src']

                else:
                    image_urls.append(image['src'])

        image_urls.sort()
        image_urls = [main_image] + image_urls

        if image_urls:
            self.image_urls = image_urls
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
        pdf_urls = []

        for link in self.tree_html.xpath('//a/@href'):
            if re.match('.*\.pdf$', link):
                pdf_urls.append(link)

        if pdf_urls:
            return pdf_urls

    def _pdf_count(self):
        if self._pdf_urls():
            return len(self._pdf_urls())
        return 0

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    def _load_reviews(self):
        if not self.reviews_checked:
            self.reviews_checked = True

            reviews_response = requests.get('http://petsmart.ugc.bazaarvoice.com/4830/' + self._product_id() + '/reviews.djs?format=embeddedhtml').content

            self.review_values = re.findall('BVDIValue.*?BVDINumber.*?(\d+)', reviews_response)

            xml_string = re.search('"BVRRRatingSummarySourceID":"(.*)","BVRRSecondaryRatingSummarySourceID', reviews_response).group(1)

            xml_string = xml_string.replace('\\n', '').replace('\\"', '"').replace('\\/', '/')
            xml_string = xml_string.replace('&nbsp;', ' ')

            self.reviews_tree = etree.fromstring(xml_string)

    def _average_review(self):
        self._load_reviews()

        average_review = self.reviews_tree.xpath('//span[contains(@class,"BVRRRatingNumber")]/text()')

        if average_review:
            return float(average_review[0])

    def _review_count(self):
        self._load_reviews()

        review_count = self.reviews_tree.xpath('//span[contains(@class,"BVRRCount")]/span/text()')

        if review_count:
            return int(review_count[0])
        return 0

    def _max_review(self):
        if self._reviews():
            for review in self._reviews():
                if review[1] != 0:
                    return review[0]

    def _min_review(self):
        if self._reviews():
            for review in reversed(self._reviews()):
                if review[1] != 0:
                    return review[0]

    def _reviews(self):
        self._load_reviews()

        reviews = []

        try:
            for i in range(5):
                num_reviews = self.review_values[i]

                reviews.append([5 - i, int(num_reviews)])

            return reviews
        except:
            return None

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        return self.tree_html.xpath('//div[contains(@class,"product-price-grp")]//span/text()')[0].replace('$ ', '$')

    def _price_amount(self):
        if self._price():
            low_price = self._price().split(' to ')[0]
            return float(low_price[1:].replace(',', ''))

    def _price_currency(self):
        if self._price() and self._price()[0] == '$':
            return 'USD'

    def _temp_price_cut(self):
        if len(self.tree_html.xpath('//div[contains(@class,"product-price-grp")]//span/text()')) > 1:
            return 1
        return 0

    def _site_online(self):
        if re.search('(Not Sold Online)|(Sold in Stores)', self.page_raw_text):
            return 0
        return 1

    def _site_online_out_of_stock(self):
        if self._site_online():
            if re.search('Out of Stock Online', self.page_raw_text):
                return 1
            return 0

    def _in_stores(self):
        if re.search('Not Sold In Stores', self.page_raw_text):
            return 0
        return 1

    def _web_only(self):
        if not self._in_stores():
            return 1
        return 0

    def _home_delivery(self):
        if self._site_online():
            return 1
        return 0

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        return self.tree_html.xpath('//li[@class="ws-breadcrumbs-list-item"]/a/text()')

    def _category_name(self):
        return self._categories()[-1]

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        return re.sub('\s+', ' ', text).strip()

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
        "product_id" : _product_id, \

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "long_description" : _long_description, \
        "ingredients" : _ingredients, \
        "ingredient_count" : _ingredient_count, \
        "directions" : _directions, \
        "variants" : _variants, \
        "no_longer_available" : _no_longer_available, \

        # CONTAINER : PAGE_ATTRIBUTES
        "htags" : _htags, \
        "keywords" : _keywords, \
        "canonical_link" : _canonical_link, \
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "temp_price_cut" : _temp_price_cut, \
        "site_online" : _site_online, \
        "site_online_out_of_stock" : _site_online_out_of_stock, \
        "in_stores" : _in_stores, \
        "web_only" : _web_only, \
        "home_delivery" : _home_delivery, \

         # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \

        "loaded_in_seconds": None \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
    }
