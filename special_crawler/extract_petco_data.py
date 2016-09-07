#!/usr/bin/python
#  -*- coding: utf-8 -*-

import re, json, requests
from lxml import html, etree
from extract_data import Scraper
import urllib2, socket

class PetcoScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = 'Expected URL format is http://www.petco.com/shop/en/petcostore/<product-name>'

    def __init__(self, **kwargs):
        Scraper.__init__(self, **kwargs)

        self.reviews_checked = False
        self.reviews_json = None

        self.prod_jsons_checked = False
        self.prod_jsons = None

    def _extract_page_tree(self):
        request = urllib2.Request(self.product_page_url)

        agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20140319 Firefox/24.0 Iceweasel/24.4.0'
        request.add_header('User-Agent', agent)

        for i in range(self.MAX_RETRIES):
            try:
                contents = urllib2.urlopen(request, timeout=30).read()
            except urllib2.HTTPError, err:
                if err.code == 404:
                    self.ERROR_RESPONSE["failure_type"] = "404 Not Found"
                    return
                elif err.code == 504:
                    self.ERROR_RESPONSE["failure_type"] = "504 Gateway Timeout"
                    continue
                else:
                    raise
            except urllib2.URLError, err:
                if str(err) == '<urlopen error timed out>':
                    self.ERROR_RESPONSE["failure_type"] = "Timeout"
                    continue
                else:
                    raise
            except socket.timeout, err:
                self.ERROR_RESPONSE["failure_type"] = "Timeout"
                continue

            break

        if self.ERROR_RESPONSE["failure_type"]:
            return

        contents = self._clean_null(contents).decode("utf8")
        self.page_raw_text = contents
        self.tree_html = html.fromstring(contents)

        return

    def check_url_format(self):
        if re.match('^http://www\.petco\.com/shop/en/petcostore/.+$', self.product_page_url):
            return True
        return False

    def not_a_product(self):
        if self.ERROR_RESPONSE["failure_type"]:
            return True

        if 'Generic Error' in self.tree_html.xpath('//title/text()')[0]:
            self.ERROR_RESPONSE["failure_type"] = '404 Not Found'
            return True

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        return self._prod_jsons()[self._catentry_id()]['catalogEntryIdentifier']['externalIdentifier']['partNumber']

    # specific to petco
    def _catentry_id(self):
        return self.tree_html.xpath('//input[@name="firstAvailableSkuCatentryId_avl"]/@value')[0]

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//div[contains(@class,"product-name")]/h1/text()')[0]

    def _product_title(self):
        return self._product_name()

    def _title_seo(self):
        return self.tree_html.xpath('//title/text()')[0].strip()

    def _features(self):
        return None

    def _feature_count(self):
        return None

    def _description(self):
        description = ''

        description_elements = self.tree_html.xpath('//div[@id="description"]/div/*')

        for element in description_elements:
            if element.get('class') == 'row spacer-sm-top':
                continue

            description += self._clean_html(html.tostring(element))

        if description:
            return description

    def _long_description(self):
        long_description = ''

        description_elements = self.tree_html.xpath('//div[@id="shipping-returns_1"]/div/*')

        for element in description_elements:
            long_description += self._clean_html(html.tostring(element))

        if long_description:
            return long_description

    def _variants(self):
        variants = []

        for item in self._items_json():
            item_json = self._prod_jsons()[item['catentry_id']]

            if not item['Attributes']:
                continue

            item_attribute = item['Attributes'].keys()[0]

            v = {
                'properties' : {
                    item_attribute.split('_')[0] : item_attribute.split('_')[1]
                    },
                'image_url' : item['ItemImage'],
                'price' : float(item_json['offerPrice'][1:]),
                'selected' : item['catentry_id'] == self._catentry_id(),
                'in_stock' : item_json['inventory']['onlineInventory']['status'] == 'In-Stock',
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
        return None

    def _htags(self):
        htags_dict = {}

        htags_dict['h1'] = map(lambda t: self._clean_text(t), self.tree_html.xpath('//h1//text()[normalize-space()!=""]'))
        htags_dict['h2'] = map(lambda t: self._clean_text(t), self.tree_html.xpath('//h2//text()[normalize-space()!=""]'))

        return htags_dict

    def _canonical_link(self):
        return self.tree_html.xpath('//link[@rel="canonical"]/@href')[0]

    def _image_urls(self):
        image_urls = []

        image_inputs = self.tree_html.xpath('//input[starts-with(@id,"img_")]')

        for input in image_inputs:
            if self._product_id() in input.get('id') and not input.get('value') in image_urls:
                image_urls.append(input.get('value'))

        if self._items_json():
            for item in self._items_json():
                if item['catentry_id'] == self._catentry_id():
                    if not item['ItemImage'] in image_urls:
                        image_urls.append(item['ItemImage'])

        if image_urls:
            return image_urls

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())
        return 0

    def _video_urls(self):
        return None

    def _video_count(self):
        return None

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
        # Check if reviews are on page
        if not self.tree_html.xpath('//span[@id="comments_span"]'):
            # if they are not, return nothing
            return

        if not self.reviews_checked:
            self.reviews_checked = True

            product_part_no = self.tree_html.xpath('//input[@id="productPartNo"]/@value')[0]

            reviews_url = 'http://api.bazaarvoice.com/data/batch.json?passkey=dpaqzblnfzrludzy2s7v27ehz&apiversion=5.5&displaycode=3554-en_us&resource.q0=products&filter.q0=id%3Aeq%3A' + product_part_no + '&stats.q0=reviews'

            reviews_response = json.loads(requests.get(reviews_url).content)

            self.reviews_json = reviews_response['BatchedResults']['q0']['Results'][0]['ReviewStatistics']

    def _average_review(self):
        self._load_reviews()
        if self.reviews_json['AverageOverallRating']:
            return round(self.reviews_json['AverageOverallRating'], 1)

    def _review_count(self):
        self._load_reviews()
        return self.reviews_json['TotalReviewCount']

    def _max_review(self):
        if self._reviews():
            for review in self._reviews():
                if not review[1] == 0:
                    return review[0]

    def _min_review(self):
        if self._reviews():
            for review in reversed(self._reviews()):
                if not review[1] == 0:
                    return review[0]

    def _reviews(self):
        self._load_reviews()

        reviews = []

        ratings_distribution = self.reviews_json['RatingDistribution']

        if ratings_distribution:
            for i in reversed(range(1,6)):
                ratingFound = False

                for rating in ratings_distribution:
                    if rating['RatingValue'] == i:
                        reviews.append([rating['RatingValue'], rating['Count']])
                        ratingFound = True
                        break

                if not ratingFound:
                    reviews.append([i, 0])

            return reviews

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _prod_jsons(self):
        if not self.prod_jsons_checked:
            self.prod_jsons_checked = True

            self.prod_jsons = {}

            if self._items_json():
                iterate_over = self._items_json()
            else:
                iterate_over = [{'catentry_id' : self._catentry_id()}]

            for item in iterate_over:
                catentry_id = item['catentry_id']

                prod_json_url = 'http://www.petco.com/shop/GetCatalogEntryDetailsByIDView?catalogEntryId=' + catentry_id + '&catalogId=10051&langId=-1&storeId=10151'

                prod_json = requests.get(prod_json_url).content
                prod_json = re.search('{[^\*]*}', prod_json).group(0)
                prod_json = re.sub(',\s*\]', ']', prod_json)

                self.prod_jsons[catentry_id] = json.loads(prod_json)['catalogEntry']

                inventory_url = 'http://www.petco.com/shop/en/petcostore/GetInventoryStatusByIDView?catalogId=10051&itemId=' + catentry_id + '&langId=-1&storeId=10151'

                inventory_json = requests.get(inventory_url).content
                inventory_json = re.search('{[^\*]*}', inventory_json).group(0)
                inventory_json = re.sub('(\w+):', r'"\1":', inventory_json)

                self.prod_jsons[catentry_id]['inventory'] = json.loads(inventory_json)

        return self.prod_jsons

    def _price(self):
        # If the item with the main catentry id has no attributes, then use displayed price
        for item in self._items_json():
            if item['catentry_id'] == self._catentry_id() and not item['Attributes']:
                return self._clean_text(self.tree_html.xpath('//span[@itemprop="price"]/text()')[0])

        if self._prod_jsons()[self._catentry_id()]['offerPrice']:
            return self._prod_jsons()[self._catentry_id()]['offerPrice']

    def _price_amount(self):
        if self._price():
            # split in case of price range and remove intial '$'
            price_amount = self._price().split(' to ')[0][1:]
            return float(price_amount.replace(',', ''))

    def _price_currency(self):
        if self._price() and self._price()[0] == '$':
            return 'USD'

    def _temp_price_cut(self):
        if self._prod_jsons()[self._catentry_id()]['listPriced'] == 'true':
            return 1
        return 0

    def _site_online(self):
        if re.search('In Store Only', self.page_raw_text):
            return 0
        return 1

    def _site_online_out_of_stock(self):
        if self.tree_html.xpath('//span[@itemprop="availability"]/@content')[0] == 'in_stock':
            return 0
        return 1

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        return self.tree_html.xpath('//ol[@class="breadcrumb"]/li/a/text()')

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        return self.tree_html.xpath('//input[@id="tel_product_brand"]/@value')[0]

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        return re.sub('\s+', ' ', text).strip()

    def _clean_html(self, html):
        html = re.sub('<(\w+)[^>]*>', r'<\1>', html)
        return self._clean_text(html)
    
    def _items_json(self):
        return json.loads(self.tree_html.xpath('//div[starts-with(@id,"entitledItem")]/text()')[0])

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

