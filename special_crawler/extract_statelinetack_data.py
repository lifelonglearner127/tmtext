#!/usr/bin/python

import urllib
import re
import sys
import json

from lxml import html, etree
import time
import requests
from extract_data import Scraper


class StateLineTackScraper(Scraper):
    
    # holds a data from an external request for loading 
    bazaar = None
        
    INVALID_URL_MESSAGE = "Expected URL format is http://www.statelinetack.com/item/<product-name>/<product-id>/"
    
    
    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        #m = re.match("^http://www.amazon.com/dp/[a-zA-Z0-9]+$", self.product_page_url)
        m = re.match(r"^http://www.statelinetack.com/.*?$", self.product_page_url)

        return not not m
    
    # TODO:
    #      better way of extracting id now that URL format is more permissive
    #      though this method still seems to work...
    def _extract_product_id(self):
        #product_id = self.product_page_url.split('/')[-1]
        product_id = self.tree_html.xpath('//input[@id="ctl00_ctl00_CenterContentArea_MainContent_HidBaseNo"]/@value')[0]

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
        moreinfo = self.tree_html.xpath('//div[@class="ItemPageDownloadableResources"]//div//a/@href')
        pdfurl = []
        print '\n\n'
        for a in moreinfo:
            p = re.findall(r'(.*\.pdf)', a)
            pdfurl.extend(p)
        
        baseurl = 'http://www.statelinetack.com/'    
        pdfurl = [baseurl + x[1:] for x in pdfurl] 
        return pdfurl

    
    def _image_url(self):
        #metaimg comes from meta tag
        metaimg = self.tree_html.xpath('//meta[@property="og:image"]/@content')
        
        #imgurl comes from the carousel
        imageurl = self.tree_html.xpath('//img[@class="swatch"]/@src')
        imageurl.extend(metaimg)
        return imageurl
    
    # image count
    def _product_images(self):
        #metaimg comes from meta tag
        metaimg = self.tree_html.xpath('//meta[@property="og:image"]/@content')
        
        #imgurl comes from the carousel
        imageurl = self.tree_html.xpath('//img[@class="swatch"]/@src')
        imageurl.append(metaimg)
        return len(imageurl)
        
    def manufacturer_content_body(self):
        return None
    
    #bazaar for ratings
    def get_bazaar(self):
        if self.bazaar != None:
            return self.bazaar
        else:
            url = 'http://tabcomstatelinetack.ugc.bazaarvoice.com/3421-en_us/%s/reviews.djs?format=embeddedhtml'
            url = url % (self._extract_product_id())

            contents = urllib.urlopen(url).read()
            tree = re.findall(r'var materials=(\{.*?\})', contents)[0]
            tree = re.sub(r'\\(.)', r'\1', tree)
            tree = re.findall(r'(\<.*\>)', tree)[0]
            tree = html.fromstring(tree)

            return tree

    #extract average review, and total reviews  
    def reviews_for_url(self):
        bazaar = self.get_bazaar()
        avg = bazaar.xpath('//*[contains(@class, "BVRRRatingNumber")]//text()')
        return avg[0]

    def nr_reviews(self):
        bazaar = self.get_bazaar()
        num = bazaar.xpath('//*[contains(@class, "BVRRRatingRangeNumber")]//text()')
        return num[0]
        
    # extract product name from its product page tree
    # ! may throw exception if not found
    def _product_name_from_tree(self):
        return self.tree_html.xpath('//meta[@itemprop="name"]/@content')[0]

    # extract meta "keywords" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_keywords_from_tree(self):
        
        return None
        
    # extract meta "brand" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_brand_from_tree(self):
        return None


    # extract product short description from its product page tree
    # ! may throw exception if not found
    def _short_description_from_tree(self):
        return None

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description_from_tree(self):
        full_description = ([x.strip() for x in self.tree_html.xpath('//div[@id="ItemPageProductSummaryBoxMain"]//text()') if len(x.strip())>0])
        for row in range(0,4):
            if len(full_description[row]) > 60:
                return full_description[row]
        return ''

    # extract product price from its product product page tree.
    def _price_from_tree(self):
        
        price = self.tree_html.xpath("//span[@id='lowPrice']//text()")
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
        description_node = self.tree_html.xpath('//div[contains(@class, "GreyBoxMiddle")]/div/span/span/span/div[3]')[0]
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
        return None

    # extract product features list from its product product page tree, return as string
    # join all text in spec table; separate rows by newlines and eliminate spaces between cells
    def _features_from_tree(self):
        return self._feature_helper()

    # extract number of features from tree
    # ! may throw exception if not found
    def _nr_features_from_tree(self):
        return len(self._feature_helper())
        
    #this helper is specific to this site
    def _feature_helper(self):
        full_description = [x.strip() for x in self.tree_html.xpath('//div[@id="ItemPageProductSummaryBoxMain"]//text()') if len(x.strip())>0]
        full_description = [x for x in full_description if len(x)>3]
        
        feat_index = [i for i in range(len(full_description)) if re.findall(r'^.{0,10}(F|f)eatures.{0,4}$', full_description[i])]
        spec_index = [i for i in range(len(full_description)) if re.findall(r'^.{0,10}(S|s)pecifications.{0,4}$', full_description[i])]
        if len(feat_index)>0:
            feat_index = feat_index[0]
        else:
            feat_index = 0
            
        if len(spec_index)>0:
            spec_index = spec_index[0]
        else:
            spec_index = None

        if spec_index>0:
            return full_description[feat_index+1:spec_index]
        else:
            return full_description[feat_index+1:]
    
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
        # 
        all = self.tree_html.xpath('//div[@id="ItemPageBreadCrumb"]//a/text()')
        return all
    
    def _meta_description(self):
        return self.tree_html.xpath("//meta[@name='Description']/@content")[0]
    
    def _meta_keywords(self):
        return self.tree_html.xpath("//meta[@name='Keywords']/@content")[0]
    
    def _asin(self):
        return None
    

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
    
    
    x    pdf_url
    x    average_review
    x    total_reviews
    
    UPC/EAN/ISBN
    x    product_images
    x    all_depts
    x    meta description 
    x    meta keywords - may not ever be populated although the tag exists
    
    
    
    # 
    missing --------------------------------------
    mobile_image_same - haven't implemented yet
    noimage - haven't implemented yet
    short - doesn't exist
    video_url - couldn't find on stateline tack
    brand - couldn't find on stateline tack
    model - couldn't find on stateline tack
    manufacturer_content_body - no instances of this found on statelinetack
    

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
        "mobile_image_same" : _mobile_image_same \

        
    }
