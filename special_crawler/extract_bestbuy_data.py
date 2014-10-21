#!/usr/bin/python

import urllib
import re
import sys
import json
import os.path
from lxml import html
import time
import requests
from extract_data import Scraper

class BestBuyScraper(Scraper):
    
    INVALID_URL_MESSAGE = "Expected URL format is http://www.bestbuy.com/site/<product-name>/<product-id>.*"
    
    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^http://www.bestbuy.com/.*$", self.product_page_url)
        return not not m

    def _url(self):
        return self.product_page_url

    def _extract_product_id(self):
        prod_id = self.tree_html.xpath('//div[@id="pdp-model-data"]/@data-product-id')[0]
        return prod_id

    def video_for_url(self):
        video_url = "\n".join(self.tree_html.xpath("//script//text()"))
        video_url = re.sub(r"\\", "", video_url)
        video_url = re.findall("url.+(http.+flv)\"", video_url)
        return video_url

    def pdf_for_url(self):
        return None
    
    def _image_url(self):
        image_url = self.tree_html.xpath('//div[@id="pdp-model-data"]/@data-gallery-images')[0]
        json_list = json.loads(image_url)
        image_url = []
        for i in json_list:
            image_url.append(i['url'])
        return image_url
    
    def _product_images(self):
        image_url = self.tree_html.xpath('//div[@id="pdp-model-data"]/@data-gallery-images')[0]
        json_list = json.loads(image_url)
        return len(json_list)
        
    def manufacturer_content_body(self):
        return None
    
    #extract average review, and total reviews  
    def reviews_for_url(self):
        return self.tree_html.xpath('//span[@itemprop="ratingValue"]//text()')[0]

    def nr_reviews(self):
        return self.tree_html.xpath('//meta[@itemprop="reviewCount"]/@content')[0]
        
    # extract product name from its product page tree
    # ! may throw exception if not found
    def _product_name_from_tree(self):
        return self.tree_html.xpath('//meta[@itemprop="name"]/@content')[0]

    # extract meta "keywords" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_keywords_from_tree(self):
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0]

    # extract meta "brand" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_brand_from_tree(self):
        return self.tree_html.xpath('//meta[@id="schemaorg-brand-name"]/@content')[0]


    # extract product short description from its product page tree
    # ! may throw exception if not found
    def _short_description_from_tree(self):
        return None

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    def _long_description_from_tree(self):
        full_description = self.tree_html.xpath('//div[@id="long-description"]//text()')[0]
        return full_description

    # extract product price from its product product page tree
    def _price_from_tree(self):
        meta_price = self.tree_html.xpath('//meta[@itemprop="price"]//@content')
        if meta_price:
            return meta_price[0].strip()
        else:
            return None

    # extract product price from its product product page tree
    # ! may throw exception if not found
    def _anchors_from_tree(self):
        # get all links found in the description text
        description_node = self.tree_html.xpath('//div[@id="long-description"]//text()')[0]
        links = description_node.xpath(".//a")
        nr_links = len(links)
        links_dicts = []
        for link in links:
            # TODO: 
            #       extract text even if nested in something?
            #       better error handling (on a per link basis)
            links_dicts.append({"href" : link.xpath("@href")[0], "text" : link.xpath("text()")[0]})
        ret = {"quantity" : nr_links, "links" : links_dicts}
        return ret


    # extract htags (h1, h2) from its product product page tree
    def _htags_from_tree(self):
        htags_dict = {}

        # add h1 tags text to the list corresponding to the "h1" key in the dict
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        # add h2 tags text to the list corresponding to the "h2" key in the dict
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))

        return htags_dict

    # extract product model from its product product page tree
    # ! may throw exception if not found
    def _model_from_tree(self):
        return self.tree_html.xpath('//span[@id="model-value"]/text()')[0]

    # extract product features list from its product product page tree, return as string
    # join all text in spec table; separate rows by newlines and eliminate spaces between cells
    def _features_from_tree(self):
        rows = self.tree_html.xpath("//div[@id='features']")
        # list of lists of cells (by rows)
        cells = map(lambda row: row.xpath(".//div[@class='feature']//text()"), rows)
        # list of text in each row
        rows_text = map(\
            lambda row: ":".join(\
                map(lambda cell: cell.strip(), row)\
                ), \
            cells)
        all_features_text = "\n".join(rows_text)
        # return dict with all features info
        return all_features_text

    # extract number of features from tree
    # ! may throw exception if not found
    def _nr_features_from_tree(self):
        # select table rows with more than 2 cells (the others are just headers), count them
        return len(filter(lambda row: len(row.xpath(".//text()"))>0, self.tree_html.xpath("//div[@id='features']/div[@class='feature']")))

    # extract page title from its product product page tree
    # ! may throw exception if not found
    def _title_from_tree(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    # extract product seller meta keyword from its product product page tree
    # ! may throw exception if not found
    def _seller_meta_from_tree(self):
        return self.tree_html.xpath("//meta[@itemprop='brand']/@content")[0]

    # extract product seller information from its product product page tree (using h2 visible tags)
    def _seller_from_tree(self):
        seller_info = {}
        seller_info['owned'] = 1
        seller_info['marketplace'] = 0
        return seller_info
    
    def _marketplace(self):
        return 0
    
    def _owned(self):
        return 1
    
    def _upc(self):
        return self.tree_html.xpath('//div[@id="pdp-model-data"]/@data-sku-id')[0]

    # extract the department which the product belongs to
    def _dept(self):
        dept = " ".join(self.tree_html.xpath("//ul[@id='breadcrumb-list']/li[2]/a/text()")).strip()
        return dept
    
    # extract the department's department, or super department
    def _super_dept(self):
        dept = " ".join(self.tree_html.xpath("//ul[@id='breadcrumb-list']/li[1]/a/text()")).strip()
        return dept
    
    # extract a hierarchical list of all the departments the product belongs to
    def _all_depts(self):
        all = self.tree_html.xpath("//ul[@id='breadcrumb-list']/li/a/text()")
        return all
    
    # extracts whether the first product image is the "no-image" picture
    def _no_image(self):
        None

    def _mobile_image_same(self):
        return None
    
    def fetch_bytes(self, url):
        file = cStringIO.StringIO(urllib.urlopen(url).read())
        img = Image.open(file)
        b = BytesIO()
        img.save(b, format='png')
        data = b.getvalue()
        return data

    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        return re.sub("&nbsp;", " ", text).strip()



    def main(args):
        # check if there is an argument
        if len(args) <= 1:
            sys.stderr.write("ERROR: No product URL provided.\nUsage:\n\tpython crawler_service.py <product_url>\n")
            sys.exit(1)
    
        product_page_url = args[1]
    
        # check format of page url
        if not check_url_format(product_page_url):
            sys.stderr.write(INVALID_URL_MESSAGE)
            sys.exit(1)
    
        return json.dumps(product_info(sys.argv[1], ["name", "short_desc", "keywords", "price", "load_time", "anchors", "long_desc"]))


    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service
    # 
    # data extracted from product page
    # their associated methods return the raw data
    DATA_TYPES = { \
        # Info extracted from product page
        "url" : _url, \
        "product_name" : _product_name_from_tree, \
        "keywords" : _meta_keywords_from_tree, \
        "description" : _short_description_from_tree, \
        "long_description" : _long_description_from_tree, \
        "price" : _price_from_tree, \
        "anchors" : _anchors_from_tree, \
        "htags" : _htags_from_tree, \
        "features" : _features_from_tree, \
        "feature_count" : _nr_features_from_tree, \
        "product_title" : _title_from_tree, \

        "marketplace" : _marketplace, \
        "owned" : _owned, \
        "product_id" : _extract_product_id, \
        "upc" : _upc,\
        "video_urls" : video_for_url, \
        
        "image_urls" : _image_url, \
        "image_count" : _product_images, \

        "category_name" : _dept,\
        "categories" : _all_depts,\

        "no_image" : _no_image,\
        "brand" : _meta_brand_from_tree, \
        "model" : _model_from_tree, \
        
        "average_review" : reviews_for_url, \
        "review_count" : nr_reviews, \

        
        "loaded_in_seconds": None\
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "mobile_image_same" : _mobile_image_same, \
        "manufacturer_content_body" : manufacturer_content_body, \
        "pdf_urls" : pdf_for_url
    }



