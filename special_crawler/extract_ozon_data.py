#!/usr/bin/python

import urllib
import re
import sys
import json
import os.path
from lxml import html
from lxml import etree
import time
import requests
from extract_data import Scraper

class OzonScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################
    
    INVALID_URL_MESSAGE = "Expected URL format is http://www.ozon.ru/.*"
    
    def check_url_format(self):
        m = re.match("^http://www\.ozon\.ru/.*$", self.product_page_url) 
        return (not not m)
    
    ##########################################
    ############### CONTAINER : NONE
    ##########################################


    def _url(self):
        return self.product_page_url
    
    def _event(self):
        return None

    def _product_id(self):
        product_id = self.tree_html.xpath('//div[@class="eDetail_ProductId"]//text()')[0]
        return product_id

    def _site_id(self):
        return None

    def _status(self):
        return 'success'



    ##########################################
    ################ CONTAINER : PRODUCT_INFO
    ##########################################


    def _product_name(self):
        return self.tree_html.xpath("//h1")[0].text

    def _product_title(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _model(self):
        return None

    def _upc(self):
        return None

    def _features(self):
        rows = self.tree_html.xpath("//div[@class='bTechDescription']//div[contains(@class, 'bTechCover')]")
        cells = map(lambda row: row.xpath(".//*//text()"), rows)
        rows_text = map(\
            lambda row: ":".join(\
                map(lambda cell: cell.strip(), row)\
                ), \
            cells)
        all_features_text = "\n".join(rows_text)
        return all_features_text

    def _feature_count(self):
        return len(filter(lambda row: len(row.xpath(".//text()"))>0, self.tree_html.xpath("//div[@class='bTechDescription']//div[contains(@class, 'bTechCover')]")))

    def _model_meta(self):
        return None

    def _description(self):
        short_description = " ".join(self.tree_html.xpath("//div[@class='bDetailLogoBlock']//text()")).strip()
        return short_description

    def _long_description(self):
        return  " ".join(self.tree_html.xpath("//div[@class='mDetail_SidePadding']/table//text()")).strip()






    ##########################################
    ################ CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _meta_tags(self):
        tags = map(lambda x:x.values() ,self.tree_html.xpath('//meta[not(@http-equiv)]'))
        return tags

    def _meta_tag_count(self):
        tags = self._meta_tags()
        return len(tags)

    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        text = self.tree_html.xpath('//*[@class="bImageColumn"]/script//text()')
        text = re.findall(r'gallery_data \= (\[\{.*\}\]);', str(text))[0]
        jsn = json.loads(text)
        image_url = []
        for row in jsn:
            if 'Elements' in row:
                for element in row['Elements']:
                    if 'Original' in element:
                        image_url.append(element['Original'])
        return image_url

    def _image_count(self):
        image_url = self._image_urls()
        return len(image_url)

    # return 1 if the "no image" image is found
    def _no_image(self):
        return None


    def _video_urls(self):
        """ example video pages:
        http://www.ozon.ru/context/detail/id/24920178/
        http://www.ozon.ru/context/detail/id/19090838/
        """
        iframes = self.tree_html.xpath("//iframe")
        video_url = []
        for iframe in iframes:
            src = str(iframe.xpath('.//@src'))
            find = re.findall(r'www\.youtube\.com/embed/.*$', src)
            if find:
                video_url.append(find[0])
        return video_url

    def _video_count(self):
        return len(self._video_urls())

    def _pdf_urls(self):
        return None
        
    def _pdf_count(self):
        return len(self._pdf_urls())
        
    def _webcollage(self):
        return None

    def _htags(self):
        htags_dict = {}
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    def _loaded_in_seconds(self):
        return None

    def _keywords(self):
        return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]





    ##########################################
    ################ CONTAINER : REVIEWS
    ##########################################

    def _average_review(self):
        r = self.tree_html.xpath('//div[@itemprop="ratingValue"]//text()')[0]
        return r
    
    def _review_count(self):
        nr = self.tree_html.xpath('//div[@itemprop="aggregateRating"]//span//text()')[0]
        return re.findall(r'[0-9]+', nr)[0]

    def _max_review(self):
        return None

    def _min_review(self):
        return None





    ##########################################
    ################ CONTAINER : SELLERS
    ##########################################

    def _price(self):
        meta_price = self.tree_html.xpath("//div[@class='pages_set']//div[@class='price']//text()")
        if meta_price:
            return meta_price
        else:
            return None
    
    def _in_stores_only(self):
        return 0

    def _in_stores(self):
        return None

    def _owned(self):
        return 1

    def _owned_out_of_stock(self):
        s = " ".join(self.tree_html.xpath("//span[contains(@class, 'mInStock')]//text()"))
        if not not s:
            return not not re.findall(u"\u041D\u0430 \u0441\u043A\u043B\u0430\u0434\u0435", unicode(s))
        return None

    def _marketplace(self):
        return 0
    
    def _marketplace_sellers(self):
        return None

    def _marketplace_lowest_price(self):
        return None





    ##########################################
    ################ CONTAINER : CLASSIFICATION
    ##########################################

    def _categories(self):
        all = self.tree_html.xpath("//ul[@class='navLine']/li//text()")
        #the last value is the product itself
        return all[:-1]
   
    def _category_name(self):
        dept = " ".join(self.tree_html.xpath("//ul[@class='navLine']/li[1]//text()")).strip()
        return dept
   
    def _brand(self):
        return None



    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################

    def _clean_text(self, text):
        return re.sub("&nbsp;", " ", text).strip()


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
        "meta_tags": _meta_tags,\
        "meta_tag_count": _meta_tag_count,\

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

