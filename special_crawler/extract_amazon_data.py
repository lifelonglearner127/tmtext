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
        
    INVALID_URL_MESSAGE = "Expected URL format is http://www.amazon.com/dp/<product-id>"
    
    
    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise.
        """
        m = re.match(r"^http://www.amazon.com/([a-zA-Z0-9\-]+/)?(dp|gp/product)/[a-zA-Z0-9]+(/[a-zA-Z0-9_\-\?\&\=]+)?$", self.product_page_url)
        return not not m
    
    def _extract_product_id(self):
        product_id = re.match("^http://www.amazon.com/([a-zA-Z0-9\-]+/)?(dp|gp/product)/([a-zA-Z0-9]+)(/[a-zA-Z0-9_\-\?\&\=]+)?$", self.product_page_url).group(3)

        return product_id

    def _url(self):
        return self.product_page_url

    def video_urls(self):
        video_url = self.tree_html.xpath('//script[@type="text/javascript"]') 
        temp = []
        for v in video_url:
            r = re.findall("[\'\"]url[\'\"]:[\'\"](http://.+?\.mp4)[\'\"]", str(v.xpath('.//text()')))
            if r:
                temp.extend(r)
        return ",".join(temp)

    def video_count(self):
        return len(self.video_urls().split(','))

    # return one element containing the PDF
    def pdf_for_url(self):
        return None
    
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        url = self.product_page_url
        mobile_headers = {"User-Agent" : "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5"}
        pc_headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        img_list = []
        for h in [mobile_headers, pc_headers]:
            contents = requests.get(url, headers=h).text
            tree = html.fromstring(contents)
            image_url = self._image_url(tree)
            print '\n\n\nImage URL:', image_url, '\n\n\n'
            img_list.extend(image_url)
        if len(img_list) == 2:
            return img_list[0] == img_list[1]
        return None

    def _image_url(self, tree = None):
        if tree == None:
            tree = self.tree_html
        image_url = tree.xpath("//span[@class='a-button-text']//img/@src")
        return image_url
    
    def _mobile_image_url(self, tree = None):
        if tree == None:
            tree = self.tree_html
        image_url = tree.xpath("//span[@class='a-button-text']//img/@src")
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

    def _anchors_from_tree(self):
        '''get all links found in the description text'''
        description_node = self.tree_html.xpath('//*[@class="productDescriptionWrapper"]')[0]
        links = description_node.xpath(".//a")
        nr_links = len(links)
        links_dicts = []
        for link in links:
            links_dicts.append({"href" : link.xpath("@href")[0], "text" : link.xpath("text()")[0]})
        ret = {"quantity" : nr_links, "links" : links_dicts}
        return ret


    # extract htags (h1, h2) from its product product page tree
    def _htags_from_tree(self):
        htags_dict = {}
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
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

    # extract product seller information from its product product page tree (using h2 visible tags)
    def _seller_from_tree(self):
        seller_info = {}
        h5_tags = map(lambda text: self._clean_text(text), self.tree_html.xpath("//h5//text()[normalize-space()!='']"))
        acheckboxlabel = map(lambda text: self._clean_text(text), self.tree_html.xpath("//span[@class='a-checkbox-label']//text()[normalize-space()!='']"))
        seller_info['owned'] = 1 if "FREE Two-Day" in acheckboxlabel else 0
        seller_info['marketplace'] = 1 if "Other Sellers on Amazon" in h5_tags else 0
        return seller_info

    def _owned(self):
        s = self._seller_from_tree()
        return s['owned']

    def _marketplace(self):
        s = self._seller_from_tree()
        return s['marketplace']

    def _product_images(self):
        return len(self.tree_html.xpath("//span[@class='a-button-text']//img/@src"))
    
    def _no_image(self):
        return None

    # extract the department which the product belongs to
    def _dept(self):
        all = self.tree_html.xpath("//div[@class='detailBreadcrumb']/li[@class='breadcrumb']/a//text()")
        all = map(lambda t: self._clean_text(t), all)
        return all[1]
    
    # extract the department's department, or super department
    def _super_dept(self):
        all = self.tree_html.xpath("//div[@class='detailBreadcrumb']/li[@class='breadcrumb']/a//text()")
        all = map(lambda t: self._clean_text(t), all)
        return all[0]
    
    # extract a hierarchical list of all the departments the product belongs to
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


    
    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service
    # 
    # data extracted from product page
    # their associated methods return the raw data
    DATA_TYPES = { \
        "url" : _url, \
        "product_name" : _product_name_from_tree, \
        "product_title" : _title_from_tree, \
        
        "keywords" : _meta_keywords_from_tree, \
        "descrtiption" : _short_description_from_tree, \
        "long_description" : _long_description_from_tree, \
        "manufacturer_content_body" : manufacturer_content_body, \
        "price" : _price_from_tree, \
        "anchors" : _anchors_from_tree, \
        "htags" : _htags_from_tree, \
        "features" : _features_from_tree, \
        "feature_count" : _nr_features_from_tree, \

        "owned" : _owned, \
        "marketplace" : _marketplace, \

        "product_id" : _extract_product_id, \
        "brand" : _meta_brand_from_tree, \
        
        "image_urls" : _image_url, \
        "image_count" : _product_images,\

        "video_urls" : video_urls, \
        "video_count" : video_count, \
        "no_image" : _no_image, \
        
        "categories" : _all_depts,\
        "category_name" : _dept,\
        "upc" : _asin,\
        
        "loaded_in_seconds": None \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "mobile_image_same" : _mobile_image_same, \
        "model" : _model_from_tree, \
        "pdf_urls" : pdf_for_url, \
        "average_review" : reviews_for_url, \
        "review_count" : nr_reviews\
    }

