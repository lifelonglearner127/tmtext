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
from lxml import etree
import time
import requests
from extract_data import Scraper

class OzonScraper(Scraper):
    
    INVALID_URL_MESSAGE = "Expected URL format is http://www.ozon.ru/.*"
    
    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match("^http://www\.ozon\.ru/.*$", self.product_page_url)
        
        return (not not m)
    
    # TODO:
    #      better way of extracting id now that URL format is more permissive
    #      though this method still seems to work...
    def _extract_product_id(self):
        product_id = self.tree_html.xpath('//div[@class="eDetail_ProductId"]//text()')[0]
        return product_id

    # return video urls
    def video_for_url(self):
        """ example video pages:
        http://www.ozon.ru/context/detail/id/24920178/
        http://www.ozon.ru/context/detail/id/19090838/
        """
        iframes = self.tree_html.xpath("//iframe")
        video_url = []
        for iframe in iframes:
            src = str(iframe.xpath('.//@src'))
            print(src)
            find = re.findall(r'www\.youtube\.com/embed/.*$', src)
            if find:
                video_url.append(find[0])
        
        return video_url

    # return dictionary with one element containing the PDF
    def pdf_for_url(self):
        return None
        
    def _image_url(self):
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
        
   
    
    #extract average review, and total reviews  
    def reviews_for_url(self):
        #div class="hidden" itemprop="ratingValue"
        r = self.tree_html.xpath('//div[@itemprop="ratingValue"]//text()')[0]

        return r
    
    def nr_reviews(self):
        nr = self.tree_html.xpath('//div[@itemprop="aggregateRating"]//span//text()')[0]
        return re.findall(r'[0-9]+', nr)[0]
        
    # extract product name from its product page tree
    # ! may throw exception if not found
    def _product_name_from_tree(self):
        return self.tree_html.xpath("//h1")[0].text

    # extract meta "keywords" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_keywords_from_tree(self):
        return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]

    # extract meta "brand" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_brand_from_tree(self):
        return None

    # extract product short description from its product page tree
    # ! may throw exception if not found
    def _short_description_from_tree(self):
        short_description = " ".join(self.tree_html.xpath("//div[@class='bDetailLogoBlock']//text()")).strip()
        return short_description

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description_from_tree(self):
        return  " ".join(self.tree_html.xpath("//div[@class='mDetail_SidePadding']/table//text()")).strip()
    
    def manufacturer_content_body(self):
       return None


    # extract product price from its product product page tree
    def _price_from_tree(self):
        meta_price = self.tree_html.xpath("//div[@class='pages_set']//div[@class='price']//text()")
        if meta_price:
            return meta_price
        else:
            return None

    # extract product price from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - test
    #      - is format ok?
    def _anchors_from_tree(self):
        # get all links found in the description text
        description_node = self.tree_html.xpath("//div[@class='mDetail_SidePadding']")[0]
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
        
        #TODO: Needs some logic for deciding when Tesco is displaying one format or the other, the following 2 lines are the currently encountered versions
        #rows = self.tree_html.xpath("//section[@class='detailWrapper']//tr")
        rows = self.tree_html.xpath("//div[@class='bTechDescription']//div[contains(@class, 'bTechCover')]")

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
        return len(filter(lambda row: len(row.xpath(".//text()"))>0, self.tree_html.xpath("//div[@class='bTechDescription']//div[contains(@class, 'bTechCover')]")))

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
    
    def _owned(self):
        return 1
    
    def _marketplace(self):
        return 0
    
    
    # extract the UPC number
    def _upc(self):
        return None
    
    #extract links for all images
    def _product_images(self):
        image_url = self._image_url()
        return len(image_url)

    # extract the department which the product belongs to
    def _dept(self):
        dept = " ".join(self.tree_html.xpath("//ul[@class='navLine']/li[2]//text()")).strip()
        return dept
    
    # extract the department's department, or super department
    def _super_dept(self):
        dept = " ".join(self.tree_html.xpath("//ul[@class='navLine']/li[1]//text()")).strip()
        return dept
    
    # extract a hierarchical list of all the departments the product belongs to
    def _all_depts(self):
        all = self.tree_html.xpath("//ul[@class='navLine']/li//text()")
        #the last value is the product itself
        return all[:-1]
    
    # returns departments encapsulated in a categories object
    def _categories(self):
        categories = {}
        categories["super_dept"] = self._super_dept()
        categories["dept"] = self._dept()
        categories["full"] = self._all_depts()
        categories["hostname"] = 'Ozon'
        
        return categories
    
    
    # return True if there is a no-image image and False otherwise
    # Certain products have an image that indicates "there is no image available"
    # a hash of these "no-images" is saved to a json file and new images are compared to see if they're the same
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
        
    
    # returns 1 if the product is in stock, 0 otherwise
    def _product_in_stock(self):
        s = " ".join(self.tree_html.xpath("//span[contains(@class, 'mInStock')]//text()"))
        if not not s:
            return not not re.findall(u"\u041D\u0430 \u0441\u043A\u043B\u0430\u0434\u0435", unicode(s))
        return None
    
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None
    
    #returns 1 if it's in stores only, 0 otherwise 
    def _in_stores_only(self):
        return 0
    
    
    #read the bytes of an image
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




    '''
    
        x    "name"
        x    "keywords"
        x    "short_desc"
        x    "long_desc"
        x    "price" - note : some products have multiple prices, so this returns a list (eg memory card size 8GB, 16GB, 32GB, etc.)
        x    "anchors"
        x    "htags"
        x    "features"
        x    "nr_features"
        x    "title"
        x    "seller" - note : seller is hardcoded for Ozon
        x    "marketplace"
        x    "owned"
        x    "product_id"
        x    "image_url"
    "video_url"
    "upc" - can't find an example of this on Ozon
        x    "product_images"
        x    "categories"
        x    "dept"
        x    "super_dept"
        x    "all_depts"
    "no_image" - not implemented
        x    "product_in_stock"
        x    "in_stores_only" - hard coded
        x    "load_time"
    "mobile_image_same" - not implemented
        x    "average_review"
        x    "total_reviews"
    
    "pdf_url" - can't find an example of this on Ozon
    "brand" - can't find an example of this on Ozon
    "model" - can't find an example of this on Ozon
    "manufacturer_content_body" - can't find an example of this on Ozon
    
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
        "price" : _price_from_tree, \
        "anchors" : _anchors_from_tree, \
        "htags" : _htags_from_tree, \
        "features" : _features_from_tree, \
        "nr_features" : _nr_features_from_tree, \
        "title" : _title_from_tree, \
        "seller": _seller_from_tree, \
        "marketplace": _marketplace, \
        "owned" : _owned, \
        
        "product_id" : _extract_product_id, \
        "image_url" : _image_url, \
        "video_url" : video_for_url, \
        
        "upc" : _upc,\
        "product_images" : _product_images, \
        
        "categories" : _categories, \
        "dept" : _dept,\
        "super_dept" : _super_dept,\
        "all_depts" : _all_depts,\
        
        "no_image" : _no_image,\
        
        "product_in_stock" : _product_in_stock, \
        "in_stores_only" : _in_stores_only, \
        
        "average_review" : reviews_for_url, \
        "total_reviews" : nr_reviews, \
        
        "load_time": None\
        }


    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "mobile_image_same" : _mobile_image_same, \
        "brand" : _meta_brand_from_tree, \
        "model" : _model_from_tree, \
        "manufacturer_content_body" : manufacturer_content_body, \
        "pdf_url" : pdf_for_url \
        
    }


