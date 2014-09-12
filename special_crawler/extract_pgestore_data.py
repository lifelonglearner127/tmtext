#!/usr/bin/python

import urllib
import re
import sys
import json
import os.path
import urllib, cStringIO
from io import BytesIO
from PIL import Image
import mmh3 as MurmurHash
from lxml import html
import time
import requests
from extract_data import Scraper

class PGEStore(Scraper):
    '''
    '''
    
    INVALID_URL_MESSAGE = "Expected URL format is http://www.pgestore.com/[0-9a-zA-Z,/-]+\.html"
    
    #Holds a JSON variable that contains information scraped from a query which Tesco makes through javascript
    reviews_tree = None
    
    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match("^http://www.pgestore.com/[0-9a-zA-Z,/-]+\.html$", self.product_page_url)
        return not not m
    
    # TODO:
    #      better way of extracting id now that URL format is more permissive
    #      though this method still seems to work...
    def _extract_product_id(self):
        product_id = self.tree_html.xpath('//div[contains(@class, "productid")]//text()')[0]
        
        product_id = re.findall("([0-9]+)", product_id)[0]
        return product_id

    # return dictionary with one element containing the video url
    def video_for_url(self):
        base = 'http://www.pgestore.com'
        video_url = self.tree_html.xpath('//img[contains(@class, "productaltvideo")]/following-sibling::script//text()')[0]
        video_url = re.findall('showProductVideo\(\"(.+?)\"\)', video_url)
        return base+video_url[0]

    # return dictionary with one element containing the PDF
    def pdf_for_url(self):
        url = "http://content.webcollage.net/pgstore/smart-button?ird=true&channel-product-id=%s"%(self._extract_product_id())
        contents = urllib.urlopen(url).read()
        pdf = re.findall(r'wcobj=\\\"(http:\\/\\/.+?\.pdf)\\\"', str(contents))
        
        if pdf:
            return re.sub(r'\\', '', pdf[0])
        else:
            return None
    #populate the reviews_tree variable for use by other functions
    def load_reviews(self, url):
        try:
            contents = urllib.urlopen(url).read()
            self.reviews_tree = html.fromstring(contents)
        except:
            pass
        
    def _image_url(self):
        image_url = self.tree_html.xpath("//img[contains(@class, 'productaltimage')]/@fullsizesrc")

        return image_url
        
    def manufacturer_content_body(self):
        full_description = " ".join(self.tree_html.xpath("//div[@class='tabContent']//text()")).strip()

        return full_description
    
    #extract average review, and total reviews  
    def reviews_for_url(self):
        if not self.reviews_tree:
            url = "http://reviews.pgestore.com/3300/PG_00%s/reviews.htm?format=embedded"
            self.load_reviews(url%(self._extract_product_id()))
        rating = self.reviews_tree.xpath('//span[@class="BVRRNumber BVRRRatingNumber"]/text()')[0]
        return rating

    def nr_reviews(self):
        if not self.reviews_tree:
            url = "http://reviews.pgestore.com/3300/PG_00%s/reviews.htm?format=embedded"
            self.load_reviews(url%(self._extract_product_id()))
        nr = self.reviews_tree.xpath('//span[@class="BVRRCount BVRRNonZeroCount"]/span[@class="BVRRNumber"]/text()')[0]
        return nr        
    
    # extract product name from its product page tree
    # ! may throw exception if not found
    def _product_name_from_tree(self):
        return self.tree_html.xpath("//h1[@class='productname']//text()")[0]

    # extract meta "keywords" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_keywords_from_tree(self):
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0]

    # extract meta "brand" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_brand_from_tree(self):
        return self.tree_html.xpath('//span[contains(@class, "brand")]//text()')[0]


    # extract product short description from its product page tree
    # ! may throw exception if not found
    def _short_description_from_tree(self):
        short_description = " ".join(self.tree_html.xpath("//div[@class='tabContent']//text()")).strip()
        return short_description

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description_from_tree(self):
        full_description = " ".join(self.tree_html.xpath("//div[@class='tabContent']//text()")).strip()
        
        return full_description


    # extract product price from its product product page tree
    def _price_from_tree(self):
        meta_price = self.tree_html.xpath("//meta[@name='pgeprice']/@content")
        if meta_price:
            return meta_price[0].strip()
        else:
            return None

    # extract product price from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - test
    #      - is format ok?
    def _anchors_from_tree(self):
        # get all links found in the description text
        description_node = self.tree_html.xpath("//div[@class='tabContent']")[0]
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
        return None

    # extract number of features from tree
    # ! may throw exception if not found
    def _nr_features_from_tree(self):
        return None

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

    def _upc(self):
        return self.tree_html.xpath('//div[@id="prodSku"]//text()')[0]
    
    def _product_images(self):
        image_url = self.tree_html.xpath("//img[contains(@class, 'productaltimage')]/@fullsizesrc")

        return len(image_url)

    def _dept(self):
        dept = " ".join(self.tree_html.xpath("//div[@id='breadcrumb']//a[3]//text()")).strip()
        return dept
    
    def _super_dept(self):
        dept = " ".join(self.tree_html.xpath("//div[@id='breadcrumb']//a[2]//text()")).strip()
        return dept
    
    def _all_depts(self):
        all = self.tree_html.xpath("//div[@id='breadcrumb']//a//text()")
        return all
    
    def _no_image(self):
        #get image urls
        head = 'http://tesco.scene7.com/is/image/'
        image_url = self.tree_html.xpath("//section[@class='main-details']//script//text()")[1]
        image_url = re.findall("scene7PdpData\.s7ImageSet = '(.*)';", image_url)[0]
        image_url = image_url.split(',')
        image_url = [head+link for link in image_url]
        
        path = 'no_img_list.json'
        no_img_list = []
        
        if os.path.isfile(path):
            f = open(path, 'r')
            s = f.read()
            if len(s) > 1:
                no_img_list = json.loads(s)    
            f.close()
            
        first_hash = str(MurmurHash.hash(self.fetch_bytes(image_url[0])))

        if first_hash in no_img_list:
            return True
        else:
            return False
        
    
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
            sys.stderr.write("ERROR: No product URL provided.\nUsage:\n\tpython crawler_service.py <tesco_product_url>\n")
            sys.exit(1)
    
        product_page_url = args[1]
    
        # check format of page url
        if not check_url_format(product_page_url):
            sys.stderr.write("ERROR: Invalid URL " + str(product_page_url) + "\nFormat of product URL should be\n\t http://www.tesco.com/direct/<part-of-product-name>/<product_id>.prd\n")
            sys.exit(1)
    
        return json.dumps(product_info(sys.argv[1], ["name", "short_desc", "keywords", "price", "load_time", "anchors", "long_desc"]))



    '''#toggle printer
    x = self.tree_html.xpath('//div[contains(@class, "prod_features")]//li//text()')
    print "\n\nXXXXXXXXXXXXXXXXXXXXXXXX\n\n%s\n\nXXXXXXXXXXXXXXXXXXXXXXXX\n\n" % (x)
    #'''

    '''PGEStore
    pdf example
        http://www.pgestore.com/health/oral-care/replacement-brush-heads/oral-b-flossaction-refills-3-ct/069055842010,default,pd.html
    video example
        http://www.pgestore.com/men/shaving/electric-shavers/braun-series-5-590-system/069055853139,default,pd.html?start=1&cgid=braun-electric-shavers-1
        
                x "name" 
                x "keywords"
                x "short_desc" - same as long_desc, there's no apparent separate long and short desc
                x "long_desc" - same as short_desc, there's no apparent separate long and short desc
                x "price" 
                x "anchors" 
                x "htags" 
                x "features"  - None
                x "nr_features" - None
                x "title" 
                x "seller"
                x "product_id"
                x "image_url" 
                x "video_url"
                x "upc" - getting the product sku 
                x "product_images" 
                x "dept" 
                x "super_dept" 
                x "all_depts" 
                x "no_image"  - no "no images" found
                x "load_time"
         
                x "brand" 
                x "model"  - no models found on PGEStore
                x "manufacturer_content_body" - same as the other descriptions
                x "pdf_url" 
                x "average_review" 
                x "total_reviews" 
    


        
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
        "image_url" : _image_url, \
        "video_url" : video_for_url, \
        
        "upc" : _upc,\
        "product_images" : _product_images, \
        "dept" : _dept,\
        "super_dept" : _super_dept,\
        "all_depts" : _all_depts,\
        "no_image" : _no_image,\
        
        "brand" : _meta_brand_from_tree, \

        
        "load_time": None\
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
    TS = TescoScraper()
    print TS.main(sys.argv)
