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
    
    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^http://www.homedepot.com/.*?$", self.product_page_url)
        return not not m



    ##########################################
    ############### CONTAINER : NONE
    ##########################################
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
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _title_seo(self):
        return None

    def _model(self):
        model = self.tree_html.xpath('//h2[contains(@class, "product_details modelNo")]//text()')[0].strip()
        return model

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
        rows = self.tree_html.xpath('//div[contains(@class, "main_description")]//ul[@class="bulletList"]//li')
        # list of lists of cells (by rows)
        cells = map(lambda row: row.xpath(".//text()"), rows)
        # list of text in each row
        rows_text = map(\
            lambda row: ":".join(\
                map(lambda cell: cell.strip(), row)\
                ), \
            cells)
        all_features_text = "\n".join(rows_text)
        return all_features_text

    def _feature_count(self):
        return len(filter(lambda row: len(row.xpath(".//text()"))>0, self.tree_html.xpath('//div[contains(@class, "main_description")]//ul[@class="bulletList"]//li')))

    def _model_meta(self):
        return None

    def _description(self):
        short_description = " ".join(self.tree_html.xpath("//*[@id='feature-bullets']//text()")).strip()
        return short_description

    def _long_description(self):
        full_description = " ".join(self.tree_html.xpath('//div[contains(@class, "main_description")]//span[@itemprop="description"]//text()')).strip()
        return full_description



    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):        
        scripts = self.tree_html.xpath('//script//text()')
        for script in scripts:
            jsonvar = re.findall(r'JSON = (.*?);', script)
            if len(jsonvar) > 0:
                jsonvar = jsonvar[0]
                break
        jsonvar = json.loads(jsonvar)
        imageurl = []
        for row in jsonvar.items():
            imageurl.append(row[1][0]['mediaUrl'])
        return imageurl

    def _image_count(self):
        return len(self._image_urls())

    def _video_urls(self):
        return None

    def _video_count(self):
        urls = self._video_urls()
        if urls is not None:
            return len(urls)
        return None

    def _pdf_urls(self):
        moreinfo = self.tree_html.xpath('//div[@id="moreinfo_wrapper"]')[0]
        html = etree.tostring(moreinfo)
        pdfurl = re.findall(r'(http://.*?\.pdf)', html)[0]
        return pdfurl

    def _pdf_count(self):
        urls = self._pdf_urls()
        if urls is not None:
            return len(urls)
        return None

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
        average_review = self.tree_html.xpath('//meta[@itemprop="ratingValue"]/@content')[0]
        return average_review

    def _review_count(self):
        nr_reviews = self.tree_html.xpath('//meta[@itemprop="reviewCount"]/@content')[0]
        return nr_reviews

    def _max_review(self):
        return None

    def _min_review(self):
        return None




    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        price = self.tree_html.xpath("//span[@id='ajaxPrice']//text()")
        if price:
            return price[0].strip()
        return None

    def _in_stores_only(self):
        return None

    def _in_stores(self):
        return None

    def _owned(self):
        return 1
    
    def _marketplace(self):
        return 0

    def _seller_from_tree(self):
        return None
    
    def _owned_out_of_stock(self):
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
        all = self.tree_html.xpath("//div[@class='detailBreadcrumb']/li[@class='breadcrumb']/a//text()")
        all = map(lambda t: self._clean_text(t), all)
        return all[1]
    
    def _brand(self):
        return None



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

        # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "in_stores_only" : _in_stores_only, \
        "in_stores" : _in_stores, \
        "owned" : _owned, \
        "owned_out_of_stock" : _owned_out_of_stock, \
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
