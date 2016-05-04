#!/usr/bin/python

import urllib
import re
import sys
import json
import copy

from lxml import html, etree
import time
import requests
from extract_data import Scraper


class HomeDepotScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.homedepot.com/p/<product-name>/<product-id>"
    REVIEW_URL = "http://homedepot.ugc.bazaarvoice.com/1999aa/{0}/reviews.djs?format=embeddedhtml"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.product_json = None
        # whether product has any webcollage media
        self.review_json = None
        self.review_list = None
        self.is_review_checked = False

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^http://www.homedepot.com/p/.*?$", self.product_page_url)
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
            itemtype = self.tree_html.xpath('//meta[@property="og:type"]/@content')[0].strip()

            if itemtype != "product":
                raise Exception()

        except Exception:
            return True

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _extract_product_json(self):
        if self.product_json:
            return

        try:
            product_json_text = re.search('product: ({.*}),\s*channel:', html.tostring(self.tree_html), re.DOTALL).group(1)
            self.product_json = json.loads(product_json_text)
        except:
            self.product_json = None

    def _canonical_link(self):
        canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

        return canonical_link

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        product_id = self.tree_html.xpath('//h2[@class="product_details"]//span[@itemprop="productID"]/text()')[0]
        return product_id

    def _site_id(self):
        return None

    def _status(self):
        return "success"

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//meta[@itemprop="name"]/@content')[0]

    def _product_title(self):
        return self.tree_html.xpath("//h1[@class='product_title']/text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//meta[@property='og:title']/@content")[0].strip()

    def _model(self):
        self._extract_product_json()

        return self.product_json["info"]["modelNumber"]

    def _upc(self):
        scripts = self.tree_html.xpath('//script//text()')
        for script in scripts:
            var = re.findall(r'CI_ItemUPC=(.*?);', script)
            if len(var) > 0:
                var = var[0]
                break
        var = re.findall(r'[0-9]+', str(var))[0]
        return var

    def _features(self):
        features_td_list = self.tree_html.xpath('//table[contains(@class, "tablePod tableSplit")]//td')
        features_list = []

        for index, val in enumerate(features_td_list):
            if (index + 1) % 2 == 0 and features_td_list[index - 1].xpath(".//text()")[0].strip():
                features_list.append(features_td_list[index - 1].xpath(".//text()")[0].strip() + " " + features_td_list[index].xpath(".//text()")[0].strip())

        if features_list:
            return features_list

        return None

    def _feature_count(self):
        if self._features():
            return len(self._features())

        return None

    def _model_meta(self):
        return None

    def _description(self):
        description_block = self.tree_html.xpath("//div[contains(@class, 'main_description')]")[0]
        short_description = ""

        for description_item in description_block:
            if description_item.tag == "ul":
                break

            short_description = short_description + html.tostring(description_item)

        short_description = short_description.strip()

        if short_description:
            return short_description

        return None

    def _long_description(self):
        description_block = self.tree_html.xpath("//div[contains(@class, 'main_description')]")[0]
        long_description = ""
        long_description_start = False

        for description_item in description_block:
            if description_item.tag == "ul":
                long_description_start = True

            if long_description_start:
                long_description = long_description + html.tostring(description_item)

        long_description = long_description.strip()

        if long_description:
            return long_description

        return None

    def _swatches(self):
        swatches = []

        for img in self.tree_html.xpath('//div[contains(@class, "sku_variant")]/ul/li/a/img'):
            swatch = {
                'color' : img.get('title'),
                'hero' : 1,
                'hero_image' : img.get('src')
            }
            swatches.append(swatch)

        if swatches:
            return swatches

    def _variants(self):
        variants = []

        first_sku_variant = True

        for sku_variant in self.tree_html.xpath('//div[contains(@class, "sku_variant")]'):
            variants = []

            for option in sku_variant.xpath('ul/li'):
                if 'product_sku_Overlay_ColorSwatch' in sku_variant.get('class'):
                    v = {
                        'selected' : False,
                        'properties' : {
                            'color' : option.xpath('a/img/@title')[0]
                        }
                    }

                    if option.get('class') and 'selected' in option.get('class'):
                        v['selected'] = True

                else:
                    custom_label = sku_variant.xpath('a[@class="customLabel"]/text()')[0]
                    selected_value = sku_variant.xpath('a[@class="customLabel"]/span[contains(@class,"select")]/text()')[0]

                    value = option.xpath('a/text()')[0]

                    v = {
                        'selected' : selected_value == value,
                        'properties' : {
                            custom_label : value
                        }
                    }

                if not first_sku_variant:
                    for variant in original_variants:
                        variant_copy = copy.deepcopy(variant)
                        variant_copy['properties'].update(v['properties'])
                        if not v['selected']:
                            variant_copy['selected'] = False
                        variants.append(variant_copy)

                else:
                    variants.append(v)

            original_variants = copy.deepcopy(variants)
            first_sku_variant = False

        if variants:
            return variants

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):        
        self._extract_product_json()
        media_list = self.product_json["media"]["mediaList"]
        image_list = []

        for media_item in media_list:
            if media_item["mediaType"].startswith("IMAGE") and int(media_item["width"]) == 400:
                image_list.append(media_item["location"])

        if image_list:
            return image_list

        return None

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def _video_urls(self):
        self._extract_product_json()
        media_list = self.product_json["media"]["mediaList"]
        video_list = []

        for media_item in media_list:
            if "video" in media_item:
                video_list.append(media_item["video"])

        if video_list:
            return video_list

        return None

    def _video_count(self):
        self._extract_product_json()
        videos = self._video_urls()

        media_list = self.product_json["media"]["mediaList"]
        video_count = len( filter(lambda m: 'videoId' in m, media_list))

        if videos:
            return len(videos)

        return video_count

    def _pdf_urls(self):
        moreinfo = self.tree_html.xpath('//div[@id="moreinfo_wrapper"]')[0]
        html = etree.tostring(moreinfo)
        pdf_url_list = re.findall(r'(http://.*?\.pdf)', html)

        if pdf_url_list:
            return pdf_url_list

        return None

    def _pdf_count(self):
        if self._pdf_urls():
            return len(self._pdf_urls())

        return 0

    def _webcollage(self):
        return None

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

    def _average_review(self):
        if self._review_count() == 0:
            return None

        average_review = round(float(self.review_json["jsonData"]["attributes"]["avgRating"]), 1)

        if str(average_review).split('.')[1] == '0':
            return int(average_review)
        else:
            return float(average_review)

    def _review_count(self):
        self._reviews()

        if not self.review_json:
            return 0

        return int(self.review_json["jsonData"]["attributes"]["numReviews"])

    def _max_review(self):
        if self._review_count() == 0:
            return None

        for i, review in enumerate(self.review_list):
            if review[1] > 0:
                return 5 - i

    def _min_review(self):
        if self._review_count() == 0:
            return None

        for i, review in enumerate(reversed(self.review_list)):
            if review[1] > 0:
                return i + 1

    def _reviews(self):
        if self.is_review_checked:
            return self.review_list

        self.is_review_checked = True

        h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        b = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        s.mount('https://', b)
        contents = s.get(self.REVIEW_URL.format(self._product_id()), headers=h, timeout=5).text

        try:
            start_index = contents.find("webAnalyticsConfig:") + len("webAnalyticsConfig:")
            end_index = contents.find(",\nwidgetInitializers:initializers", start_index)

            self.review_json = contents[start_index:end_index]
            self.review_json = json.loads(self.review_json)
        except:
            self.review_json = None

        review_html = html.fromstring(re.search('"BVRRSecondaryRatingSummarySourceID":" (.+?)"},\ninitializers={', contents).group(1))
        reviews_by_mark = review_html.xpath("//*[contains(@class, 'BVRRHistAbsLabel')]/text()")
        reviews_by_mark = reviews_by_mark[:5]
        review_list = [[5 - i, int(re.findall('\d+', mark)[0])] for i, mark in enumerate(reviews_by_mark)]

        if not review_list:
            review_list = None

        self.review_list = review_list

        return self.review_list

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        ajax_price = self.tree_html.xpath('//div[not(@class="bulk_wrapper")]/span[@id="ajaxPrice"]/text()')

        if ajax_price:
            return self._clean_text( ajax_price[0])

        return self._clean_text( self.tree_html.xpath('//span[@id="ajaxPriceAlt"]/text()')[0])

    def _price_amount(self):
        return float( self._price()[1:].replace(',',''))

    def _price_currency(self):
        return self.tree_html.xpath("//meta[@itemprop='priceCurrency']/@content")[0]

    def _temp_price_cut(self):
        return self.product_json["itemExtension"]["localStoreSku"]["pricing"]["itemOnSale"]

    def _in_stores(self):
        self._extract_product_json()

        if self.product_json["itemAvailability"]["availableInStore"] == True:
            return 1

        return 0

    def _site_online(self):
        self._extract_product_json()
        '''
        if self.product_json["itemAvailability"]["availableOnlineStore"] == True:
            return 1
        '''
        return 1

    def _site_online_out_of_stock(self):
        self._extract_product_json()

        for message in self.product_json["storeSkus"][0]["storeAvailability"]["itemAvilabilityMessages"]:
            if message["messageValue"] == u'Out Of Stock Online':
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
        scripts = self.tree_html.xpath('//script//text()')
        for script in scripts:
            jsonvar = re.findall(r'BREADCRUMB_JSON = (.*?});', script)
            if len(jsonvar) > 0:
                jsonvar = jsonvar[0]
                break
        jsonvar = json.loads(jsonvar)
        all = jsonvar['bcEnsightenData']['contentSubCategory'].split(u'\u003e')
        return all

    def _category_name(self):
        return self._categories()[-1]
    
    def _brand(self):
        self._extract_product_json()

        return self.product_json["info"]["brandName"]


    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        return re.sub("[\n\t]", "", text).strip()


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
        "swatches" : _swatches, \
        "variants" : _variants, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
        "pdf_count" : _pdf_count, \
        "pdf_urls" : _pdf_urls, \
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
        "temp_price_cut" : _temp_price_cut, \
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
