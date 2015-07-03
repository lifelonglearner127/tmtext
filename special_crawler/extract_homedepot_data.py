#!/usr/bin/python

import urllib
import re
import sys
import json

from lxml import html, etree
import time
import requests
from extract_data import Scraper


class HomeDepotScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.homedepot.com/p/<product-name>/<product-id>"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.product_json = None

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
            product_json_text = self.tree_html.xpath("//script[contains(text(), 'THD.PIP.products.primary')]/text()")[0]

            start_index = product_json_text.find("{")
            end_index = product_json_text.rfind("}") + 1

            product_json = product_json_text[start_index:end_index]
            self.product_json = json.loads(product_json)
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
        print '\n\n\n\n\n'
        scripts = self.tree_html.xpath('//script//text()')
        for script in scripts:
            var = re.findall(r'CI_ItemUPC=(.*?);', script)
            print var
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



    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):        
        scripts = self.tree_html.xpath('//script//text()')

        for script in scripts:
            jsonvar = re.findall(r'PRODUCT_INLINE_PLAYER_JSON = (.*?);', script)
            if len(jsonvar) > 0:
                jsonvar = jsonvar[0]
                break

        jsonvar = json.loads(jsonvar)
        imageurl = []

        for row in jsonvar.items():
            if "videoId" in row[1]:
                continue

            imageurl.append(row[1][0]['mediaUrl'])

        if imageurl:
            return imageurl

        return None

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def _video_urls(self):
        return None

    def _video_count(self):
        scripts = self.tree_html.xpath('//script//text()')

        for script in scripts:
            jsonvar = re.findall(r'PRODUCT_INLINE_PLAYER_JSON = (.*?);', script)
            if len(jsonvar) > 0:
                jsonvar = jsonvar[0]
                break

        jsonvar = json.loads(jsonvar)
        video_count = 0

        for row in jsonvar.items():
            if "videoId" in row[1]:
                video_count += 1

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

    def _no_image(self):
        return None
    






    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    def _average_review(self):
        self._extract_product_json()

        return float("%.1f" % float(self.product_json["ratingsReviews"]["averageRating"]))

    def _review_count(self):
        self._extract_product_json()

        return int(self.product_json["ratingsReviews"]["totalReviews"])

    def _max_review(self):
        return None

    def _min_review(self):
        return None




    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        price = self.tree_html.xpath("//div[contains(@class, 'product_containerprice c show')]//span[@id='ajaxPrice']/text()")

        if price:
            return price[0].strip()

        return None

    def _price_amount(self):
        self._extract_product_json()

        return float(self.product_json["itemExtension"]["displayPrice"])

    def _price_currency(self):
        price_currency = self.tree_html.xpath("//div[contains(@class, 'product_containerprice c show')]//meta[@itemprop='priceCurrency']/@content")

        if price_currency:
            return price_currency[0].strip()

        return None

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
            jsonvar = re.findall(r'BREADCRUMB_JSON = (.*?);', script)
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
        return re.sub("&nbsp;", " ", text).strip()



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

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
        "no_image" : _no_image, \
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
