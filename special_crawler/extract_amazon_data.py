#!/usr/bin/python

import urllib
import re
import sys
import json

from lxml import html
import time
import requests
from extract_data import Scraper

class AmazonScraper(Scraper):
    
#    http://www.amazon.com/dp/B000JMAVYO
    
    INVALID_URL_MESSAGE = "Expected URL format is http://www.amazon.com/dp/<product-id>"
    
    
    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        #m = re.match("^http://www.amazon.com/dp/[a-zA-Z0-9]+$", self.product_page_url)
        m = re.match(r"^http://www.amazon.com/([a-zA-Z0-9\-]+/)?(dp|gp/product)/[a-zA-Z0-9]+(/[a-zA-Z0-9_\-\?\&\=]+)?$", self.product_page_url)

        return not not m
    
    # TODO:
    #      better way of extracting id now that URL format is more permissive
    #      though this method still seems to work...
    def _extract_product_id(self):
        #product_id = self.product_page_url.split('/')[-1]
        product_id = re.match("^http://www.amazon.com/([a-zA-Z0-9\-]+/)?(dp|gp/product)/([a-zA-Z0-9]+)(/[a-zA-Z0-9_\-\?\&\=]+)?$", self.product_page_url).group(3)

        return product_id

    # return dictionary with one element containing the video url
    def video_for_url(self):
        #"url":"http://ecx.images-amazon.com/images/I/B1d2rrt0oJS.mp4"
        video_url = self.tree_html.xpath('//script[@type="text/javascript"]') 
        temp = []
        for v in video_url:
            r = re.findall("[\'\"]url[\'\"]:[\'\"](http://.+?\.mp4)[\'\"]", str(v.xpath('.//text()')))
            if r:
                temp.extend(r)
        return temp

    # return dictionary with one element containing the PDF
    def pdf_for_url(self):
        return None
    

    def _image_url(self):
        image_url = self.tree_html.xpath("//span[@class='a-button-text']//img/@src")
        return image_url
        
    def manufacturer_content_body(self):
        full_description = " ".join(self.tree_html.xpath('//*[@class="productDescriptionWrapper"]//text()')).strip()
        return full_description
    
    #extract average review, and total reviews  
    def reviews_for_url(self):
        average_review = self.tree_html.xpath("//span[@id='acrPopover']/@title")[0]
        average_review = re.findall("([0-9]\.?[0-9]?) out of 5 stars", average_review)[0]

        return average_review

    def nr_reviews(self):
        nr_reviews = self.tree_html.xpath("//span[@id='acrCustomerReviewText']//text()")[0]
        nr_reviews = re.findall("([0-9]+) customer reviews", nr_reviews)[0]
        return nr_reviews
        
    # extract product name from its product page tree
    # ! may throw exception if not found
    def _product_name_from_tree(self):
        return self.tree_html.xpath('//h1[@id="title"]/span[@id="productTitle"]')[0].text

    # extract meta "keywords" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_keywords_from_tree(self):
        
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0]
        
    # extract meta "brand" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_brand_from_tree(self):
        #<div id="mbc" data-asin="B000JMAVYO" data-brand="Spicy World"
        return self.tree_html.xpath('//div[@id="mbc"]/@data-brand')[0]


    # extract product short description from its product page tree
    # ! may throw exception if not found
    def _short_description_from_tree(self):
        
        short_description = " ".join(self.tree_html.xpath("//*[@id='feature-bullets']//text()")).strip()
        return short_description

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description_from_tree(self):
        full_description = " ".join(self.tree_html.xpath('//*[@class="productDescriptionWrapper"]//text()')).strip()
        
        return full_description


    # extract product price from its product product page tree
    def _price_from_tree(self):
        
        price = self.tree_html.xpath("//*[@id='priceblock_ourprice']//text()")
        if price:
            return price[0].strip()
        
        price = self.tree_html.xpath("//*[contains(@class, 'offer-price')]//text()")
        if price:
            return price[0].strip()
        
        return None

    # extract product price from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - test
    #      - is format ok?
    def _anchors_from_tree(self):
        # get all links found in the description text
        description_node = self.tree_html.xpath('//*[@class="productDescriptionWrapper"]')[0]
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
        model = self.tree_html.xpath("//tr[@class='item-model-number']/td[@class='value']//text()")[0]
        return model

    # extract product features list from its product product page tree, return as string
    # join all text in spec table; separate rows by newlines and eliminate spaces between cells
    def _features_from_tree(self):
        rows = self.tree_html.xpath("//div[@class='content pdClearfix']//tbody//tr")
        
        # list of lists of cells (by rows)
        cells = map(lambda row: row.xpath(".//*//text()"), rows)
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
        return len(filter(lambda row: len(row.xpath(".//td"))>0, self.tree_html.xpath("//div[@class='content pdClearfix']//tbody//tr")))

    # extract page title from its product product page tree
    # ! may throw exception if not found
    def _title_from_tree(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    # extract product seller meta keyword from its product product page tree
    # ! may throw exception if not found
    def _seller_meta_from_tree(self):
        return self.tree_html.xpath("//meta[@itemprop='brand']/@content")[0]

    # extract product seller information from its product product page tree (using h2 visible tags)
    # TODO:
    #      test this in conjuction with _seller_meta_from_tree; also test at least one of the values is 1
    def _seller_from_tree(self):
        seller_info = {}
        h5_tags = map(lambda text: self._clean_text(text), self.tree_html.xpath("//h5//text()[normalize-space()!='']"))
        acheckboxlabel = map(lambda text: self._clean_text(text), self.tree_html.xpath("//span[@class='a-checkbox-label']//text()[normalize-space()!='']"))
        
        seller_info['owned'] = 1 if "FREE Two-Day" in acheckboxlabel else 0
        seller_info['marketplace'] = 1 if "Other Sellers on Amazon" in h5_tags else 0

        return seller_info

    def _product_images(self):
        return len(self.tree_html.xpath("//span[@class='a-button-text']//img/@src"))
    
    def _no_image(self):
        return None


    def _dept(self):
        all = self.tree_html.xpath("//div[@class='detailBreadcrumb']/li[@class='breadcrumb']/a//text()")
        all = map(lambda t: self._clean_text(t), all)
        return all[1]
    
    def _super_dept(self):
        all = self.tree_html.xpath("//div[@class='detailBreadcrumb']/li[@class='breadcrumb']/a//text()")
        all = map(lambda t: self._clean_text(t), all)
        return all[0]
    
    def _all_depts(self):
        all = self.tree_html.xpath("//div[@class='detailBreadcrumb']/li[@class='breadcrumb']/a//text()")
        all = map(lambda t: self._clean_text(t), all)
        return all
    
    def _meta_description(self):
        return self.tree_html.xpath("//meta[@name='description']/@content")[0]
    
    def _meta_keywords(self):
        return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]
    
    def _asin(self):
        #<input type="hidden" id="ASIN" name="ASIN" value="B00G2Y4WNY"
        return self.tree_html.xpath("//input[@name='ASIN']/@value")[0]

    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        return re.sub("&nbsp;", " ", text).strip()
    def main(args):
        # check if there is an argument
        if len(args) <= 1:
            sys.stderr.write("ERROR: No product URL provided.\nUsage:\n\tpython crawler_service.py <amazon_product_url>\n")
            sys.exit(1)
    
        product_page_url = args[1]
    
        # check format of page url
        if not check_url_format(product_page_url):
            sys.stderr.write(INVALID_URL_MESSAGE)
            sys.exit(1)
    
        return json.dumps(product_info(sys.argv[1], ["name", "short_desc", "keywords", "price", "load_time", "anchors", "long_desc"]))


    '''
    
    x extra : all_depts = since dept/super_dept were deprecated and you wanted the whole breadcrumb, I added all_depts which is ordered in a hierarchy
    x UPC/EAN/ISBN - returns ASIN
    x product_images -  for given  url  it should be 1
    x super_dept - scraped from the breadcrumbs
    x dept - scraped from the breadcrumbs
    x model_title -  exists as "title_from_tree"
    x review_count - exists as "total_reviews"
    x meta description - 
    x meta keywords - 
    x model_meta  -  there's no meta for model, but there is a model in the source
    
    '''


    '''
    http://www.amazon.com/Dell-Inspiron-i3531-1200BK-15-6-Inch-Laptop/dp/B00KMRGF28/ref=sr_1_1?ie=UTF8&qid=1409586411&sr=8-1&keywords=dell
    
    x    name
    x    keywords
    x    short
    x    long
    x    price
    x    anchors
    x    htags
    x    features
    x    nr_features
    x    title
    x    seller  <-  Not sure, There are a lot of versions of owned vs merchant, I'll need to look into this more
    x    product_id
    x    load_time
    x    image_url
    x    video_url
    x    brand
    x    model
    x    manufacturer_content_body
        pdf_url
        no_image
    x    average_review
    x    total_reviews
    

    '''



    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service
    # 
    # data extracted from product page
    # their associated methods return the raw data
    DATA_TYPES = { \
        # Info extracted from product page
        "name" : _product_name_from_tree, \
        "keywords" : _meta_keywords_from_tree, \
        "short_desc" : _short_description_from_tree, \
        "long_desc" : _long_description_from_tree, \
        "manufacturer_content_body" : manufacturer_content_body, \
        "price" : _price_from_tree, \
        "anchors" : _anchors_from_tree, \
        "htags" : _htags_from_tree, \
        "features" : _features_from_tree, \
        "nr_features" : _nr_features_from_tree, \
        "title" : _title_from_tree, \
        "seller": _seller_from_tree, \
        "product_id" : _extract_product_id, \
        "brand" : _meta_brand_from_tree, \
        "image_url" : _image_url, \
        "video_url" : video_for_url, \
        "no_image" : _no_image, \
        
        "product_images" : _product_images,\
        "all_depts" : _all_depts,\
        "dept" : _dept,\
        "super_dept" : _super_dept,\
        "meta_description" : _meta_description,\
        "meta_keywords" : _meta_keywords,\
        "asin" : _asin,\
        
        "load_time": None \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "model" : _model_from_tree, \
        "pdf_url" : pdf_for_url, \
        "average_review" : reviews_for_url, \
        "total_reviews" : nr_reviews\
    }


if __name__=="__main__":
    AS = AmazonScraper()
    print AS.main(sys.argv)
