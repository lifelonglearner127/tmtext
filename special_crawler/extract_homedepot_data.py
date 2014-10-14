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
    
#    http://www.amazon.com/dp/B000JMAVYO
    
    INVALID_URL_MESSAGE = "Expected URL format is http://www.homedepot.com/p/<product-name>/<product-id>"
    
    
    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        #m = re.match("^http://www.amazon.com/dp/[a-zA-Z0-9]+$", self.product_page_url)
        m = re.match(r"^http://www.homedepot.com/.*?$", self.product_page_url)

        return not not m
    
    # TODO:
    #      better way of extracting id now that URL format is more permissive
    #      though this method still seems to work...
    def _extract_product_id(self):
        #product_id = self.product_page_url.split('/')[-1]
        product_id = self.tree_html.xpath('//h2[@class="product_details"]//span[@itemprop="productID"]/text()')[0]

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
        moreinfo = self.tree_html.xpath('//div[@id="moreinfo_wrapper"]')[0]
        html = etree.tostring(moreinfo)
        pdfurl = re.findall(r'(http://.*?\.pdf)', html)[0]
        return pdfurl

    def _image_url(self):
        #image_url = self.tree_html.xpath('//div[@class="popup-content"]/img/@src')
        
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
        
    def manufacturer_content_body(self):
        full_description = " ".join(self.tree_html.xpath('//*[@class="productDescriptionWrapper"]//text()')).strip()
        return full_description
    
    #extract average review, and total reviews  
    def reviews_for_url(self):
        average_review = self.tree_html.xpath('//meta[@itemprop="ratingValue"]/@content')[0]
        return average_review

    def nr_reviews(self):
        nr_reviews = self.tree_html.xpath('//meta[@itemprop="reviewCount"]/@content')[0]
        return nr_reviews
        
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
        #<div id="mbc" data-asin="B000JMAVYO" data-brand="Spicy World"
        return self.tree_html.xpath('//span[@itemprop="brand"]//text()')[0].strip()


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
        full_description = " ".join(self.tree_html.xpath('//div[contains(@class, "main_description")]//span[@itemprop="description"]//text()')).strip()
        
        return full_description


    # extract product price from its product product page tree.
    def _price_from_tree(self):
        
        price = self.tree_html.xpath("//span[@id='ajaxPrice']//text()")
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
        description_node = self.tree_html.xpath('//div[contains(@class, "main_description")]//span[@itemprop="description"]')[0]
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
        model = self.tree_html.xpath('//h2[contains(@class, "product_details modelNo")]//text()')[0].strip()
        return model

    # extract product features list from its product product page tree, return as string
    # join all text in spec table; separate rows by newlines and eliminate spaces between cells
    def _features_from_tree(self):
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

        # return dict with all features info
        return all_features_text

    # extract number of features from tree
    # ! may throw exception if not found
    def _nr_features_from_tree(self):
        # select table rows with more than 2 cells (the others are just headers), count them
        return len(filter(lambda row: len(row.xpath(".//text()"))>0, self.tree_html.xpath('//div[contains(@class, "main_description")]//ul[@class="bulletList"]//li')))

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
        seller_info['owned'] = 1
        seller_info['marketplace'] = 0

        return seller_info

    def _product_images(self):
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
        return len(imageurl)
    
    def _no_image(self):
        return None

    def _mobile_image_same(self):
        pass

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
        scripts = self.tree_html.xpath('//script//text()')
        for script in scripts:
            jsonvar = re.findall(r'BREADCRUMB_JSON = (.*?);', script)
            if len(jsonvar) > 0:
                jsonvar = jsonvar[0]
                break
        jsonvar = json.loads(jsonvar)
        all = jsonvar['bcEnsightenData']['contentSubCategory'].split(u'\u003e')
        return all
    
    def _meta_description(self):
        return self.tree_html.xpath("//meta[@name='description']/@content")[0]
    
    def _meta_keywords(self):
        return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]
    
    def _asin(self):
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
    HOMEDEPOT --------------------
    
    x    name
    x    keywords
    short - doesn't exist
    x    long
    x    price
    x    anchors
    x    htags
    x    features
    x    nr_features
    x    title
    x    seller - hardcoded as just 'owned'
    x    product_id
    x    load_time
    x    image_url
    video_url
    x    brand
    x    model
    manufacturer_content_body - haven't found an instance of this
    x    pdf_url
    no_image
    x    average_review
    x    total_reviews
    
    x    UPC/EAN/ISBN
    x    product_images
    x    all_depts
    x    meta description 
    x    meta keywords 
    

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
        "meta_description" : _meta_description,\
        "meta_keywords" : _meta_keywords,\
        "upc" : _asin,\
        
        "model" : _model_from_tree, \
        "pdf_url" : pdf_for_url, \
        
        "average_review" : reviews_for_url, \
        "total_reviews" : nr_reviews, \
        
        "load_time": None \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "mobile_image_same" : _mobile_image_same, \

        
    }
