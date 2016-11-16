#!/usr/bin/python
#  -*- coding: utf-8 -*-

import re, json, requests
from lxml import html, etree
from extract_data import Scraper

class ChewyScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = 'Expected URL format is http(s)://www.chewy.com/<item-name>/dp/<item-id>'

    reviews_checked = False
    reviews_tree = None

    def check_url_format(self):
        if re.match('^https?://www\.chewy\.com/[\w-]+/dp/\d+$', self.product_page_url):
            return True
        return False

    def not_a_product(self):
        if self.tree_html.xpath('//div[@itemtype="http://schema.org/Product"]'):
            return False
        return True

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        return self.tree_html.xpath('//input[@id="productId"]/@value')[0]

    # specific to chewy.com
    def _item_id(self):
        return self.tree_html.xpath('//input[@id="itemId"]/@value')[0]

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//div[@id="product-title"]/h1/text()')[0].strip()

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

        description_elements = self.tree_html.xpath('//div[@class="longDescription"]/*')

        if not description_elements:
            description_elements = self.tree_html.xpath('//section[@class="descriptions-left"]/*')

        for element in description_elements:
            # do not include 'Product Description'
            if element.tag == 'h4':
                continue
            # end at the first strong element
            if element.xpath('strong'):
                break

            description += self._clean_text( html.tostring(element))

        if description:
            return description

    def _long_description(self):
        long_description = ''

        description_elements = self.tree_html.xpath('//div[@class="longDescription"]/*')

        if not description_elements:
            description_elements = self.tree_html.xpath('//section[@class="descriptions-left"]/*')

        for element in description_elements:
            if element.get('class') in ['see-all', 'view-all'] or element.xpath('em'):
                continue

            long_description += self._clean_text( html.tostring(element))

        if long_description and long_description != self._description():
            return long_description

    def _variant_data(self):
        item_data = re.search('itemData = ({[^;]*});', self.page_raw_text, re.DOTALL).group(1)
        item_data = item_data.replace("'", '"')
        item_data = re.sub('(\w+):', r'"\1":', item_data)
        item_data = re.sub(',\s+\]', ']', item_data)
        item_data = json.loads(item_data)

        return item_data

    def _variations_item_map(self):
        variations_item_map = re.search('variationsItemMap = ({[^;]*\});', self.page_raw_text, re.DOTALL).group(1)
        variations_item_map = variations_item_map.replace("'", '"')
        variations_item_map = json.loads(variations_item_map)

        return variations_item_map

    def _variants(self):
        variants = []

        item_data = self._variant_data()
        variations_item_map = self._variations_item_map()

        for li in self.tree_html.xpath('//div[starts-with(@id,"variation-")]/ul/li'):
            item_id = variations_item_map['_' + li.get('dim-value-id')]
            option = li.xpath('span/text()')

            property_name = self.tree_html.xpath('//div[starts-with(@id,"variation-")]/@dim-identifier')[0]

            for item_no in item_data:
                if item_no == item_id:
                    item = item_data[item_no]

                    v = {
                        'properties' : {
                            property_name : option
                            },
                        'price' : item['price'],
                        'selected' : item_no == self._item_id(),
                        'in_stock' : not self._site_online_out_of_stock(),
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

        for link in self.tree_html.xpath('//div[@id="media-selector"]//a/@href'):
            if not link == '#':
                image_urls.append('http:' + link)

        for link in self.tree_html.xpath('//div[@id="product-image"]//a/@href'):
            if link[2:] and not link[2:] in image_urls:
                image_urls.append('http:' + link)

        '''
        item_data = self._variant_data()

        # add variant image urls
        for item_no in item_data:
            item = item_data[item_no]

            for image in item['images']:
                image_id = re.search('_([^_]+)+_.jpg', image).group(1)

                # if there is a media selector, check for duplicates
                if self.tree_html.xpath('//div[@id="media-selector"]'):

                    duplicate = False

                    for image_url in image_urls:
                        if image_id in image_url:
                            duplicate = True

                    if not duplicate:
                        image_urls.append(image[2:])

                # otherwise, just add it
                else:
                    image_urls.append(image[2:])
        '''

        if image_urls:
            return image_urls

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())
        return 0

    def _video_urls(self):
        return None

    def _video_count(self):
        return len( self.tree_html.xpath('//a[contains(@class,"alt-vid")]'))

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    #populate the reviews_tree variable for use by other functions
    def _load_reviews(self):
        if not self.reviews_checked:
            self.reviews_checked = True

            reviews_product_id = re.search('productId: "(\d+)"', self.page_raw_text).group(1)

            reviews_response = requests.get('http://chewy.ugc.bazaarvoice.com/0090-en_us/' + reviews_product_id + '/reviews.djs?format=embeddedhtml').content

            xml_string = re.search('"BVRRRatingSummarySourceID":"(.*)","BVRRSecondaryRatingSummarySourceID', reviews_response).group(1)

            xml_string = xml_string.replace('\\n', '').replace('\\"', '"').replace('\\/', '/')
            xml_string = xml_string.replace('&nbsp;', ' ')

            self.reviews_tree = etree.fromstring(xml_string)

    def _average_review(self):
        self._load_reviews()

        average_review = self.reviews_tree.xpath('//span[@itemprop="ratingValue"]/text()')
        if average_review:
            return float(average_review[0])

    def _review_count(self):
        self._load_reviews()

        review_count = self.reviews_tree.xpath('//meta[@itemprop="reviewCount"]/@content')

        if review_count:
            return int(review_count[0])
        return 0

    def _max_review(self):
        self._load_reviews()

        if self._reviews():
            for review in self._reviews():
                if review[1] != 0:
                    return review[0]

    def _min_review(self):
        self._load_reviews()

        if self._reviews():
            for review in reversed(self._reviews()):
                if review[1] != 0:
                    return review[0]

    def _reviews(self):
        self._load_reviews()

        reviews = []

        try:
            for i in range(5):
                num_reviews = self.reviews_tree.xpath('//div[@class="BVRRHistogramContent"]/div/span[@class="BVRRHistAbsLabel"]/text()')[i]

                reviews.append([5 - i, int(num_reviews)])

            return reviews
        except:
            return None

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        #return self.tree_html.xpath('//span[@class="our-price"]/text()')[0].strip()
        return self.tree_html.xpath('//*[@class="price"]/span/text()')[0].strip()

    def _price_amount(self):
        price_amount = self.tree_html.xpath('//meta[@itemprop="price"]/@content')[0]
        return float(price_amount.replace(',', ''))

    def _price_currency(self):
        return self.tree_html.xpath('//meta[@itemprop="priceCurrency"]/@content')[0]

    def _temp_price_cut(self):
        if self.tree_html.xpath('//div[@class="sale-overlay"]'):
            return 1
        return 0

    def _web_only(self):
        return 1

    def _in_stores(self):
        return 0

    def _marketplace(self):
        return 0

    def _marketplace_sellers(self):
        return None

    def _marketplace_lowest_price(self):
        return None

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):
        if self.tree_html.xpath('//meta[@itemprop="availability"]/@content')[0] == 'http://schema.org/InStock':
            return 0
        return 1

    def _in_stores_out_of_stock(self):
        return None

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        return self.tree_html.xpath('//*[contains(@class,"breadcrumbs")]//a/text()')

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        return self.tree_html.xpath('//div[@id="brand"]/a/text()')[0]

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        return re.sub('\s+', ' ', text).strip()

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

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "temp_price_cut" : _temp_price_cut, \
        "web_only" : _web_only, \
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

