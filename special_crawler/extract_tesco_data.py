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

class TescoScraper(Scraper):
    '''
    no/broken image example:
        http://www.tesco.com/direct/torch-keychain-1-led/592-8399.prd
        
    hp no image: 
        http://www.tesco.com/direct/nvidia-nvs-310-graphics-card-512mb/436-0793.prd
    
    '''
    INVALID_URL_MESSAGE = "Expected URL format is http://www.tesco.com/direct/<part-of-product-name>/<product_id>.prd"
    
    #Holds a JSON variable that contains information scraped from a query which Tesco makes through javascript
    bazaarvoice = None
    
    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match("^http://www.tesco.com/direct/[0-9a-zA-Z-]+/[0-9-]+\.prd$", self.product_page_url)
        return not not m
    
    # TODO:
    #      better way of extracting id now that URL format is more permissive
    #      though this method still seems to work...
    def _extract_product_id(self):
        product_id = self.product_page_url.split('/')[-1]
        product_id = product_id.split('.')[0]
        return product_id

    # return dictionary with one element containing the video url
    def video_for_url(self):
        video_url = self.tree_html.xpath("//section[@class='main-details']//script//text()")[1]
        video_url = re.search("\['http://embed\.flixfacts\.com/.*\]", video_url.strip()).group()
        video_url = re.findall("'(.*?)'", video_url)
        return video_url

    # return dictionary with one element containing the PDF
    def pdf_for_url(self):
        return None
    
    #populate the bazaarvoice variable for use by other functions
    def load_bazaarvoice(self):
        url = "http://api.bazaarvoice.com/data/batch.json?passkey=asiwwvlu4jk00qyffn49sr7tb&apiversion=5.4&displaycode=1235-en_gb&resource.q0=products&filter.q0=id%3Aeq%3A" \
        + self._extract_product_id() + \
        "&stats.q0=reviews&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Aen_AU%2Cen_CA%2Cen_DE%2Cen_GB%2Cen_IE%2Cen_NZ%2Cen_US"
        req = requests.get(url)
        self.bazaarvoice = req.json()
        
    def _image_url(self):
        head = 'http://tesco.scene7.com/is/image/'
        image_url = self.tree_html.xpath("//section[@class='main-details']//script//text()")[1]
        image_url = re.findall("scene7PdpData\.s7ImageSet = '(.*)';", image_url)[0]
        image_url = image_url.split(',')
        image_url = [head+link for link in image_url]
        return image_url
        
   
    
    #extract average review, and total reviews  
    def reviews_for_url(self):
        if not self.bazaarvoice:
            self.load_bazaarvoice()
        average_review = self.bazaarvoice['BatchedResults']['q0']['Results'][0]['FilteredReviewStatistics']['AverageOverallRating']
    
        return average_review

    def nr_reviews(self):
        if not self.bazaarvoice:
            self.load_bazaarvoice()

        nr_reviews = self.bazaarvoice['BatchedResults']['q0']['Results'][0]['FilteredReviewStatistics']['TotalReviewCount']
        return nr_reviews
        
    # extract product name from its product page tree
    # ! may throw exception if not found
    def _product_name_from_tree(self):
        return self.tree_html.xpath("//h1")[0].text

    # extract meta "keywords" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_keywords_from_tree(self):
        return None

    # extract meta "brand" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_brand_from_tree(self):
        if not self.bazaarvoice:
            self.load_bazaarvoice()
        return self.bazaarvoice['BatchedResults']['q0']['Results'][0]['Brand']['Name']


    # extract product short description from its product page tree
    # ! may throw exception if not found
    def _short_description_from_tree(self):
        short_description = " ".join(self.tree_html.xpath("//ul[@class='features']/li//text()")).strip()
        return short_description

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description_from_tree(self):
        if not self.bazaarvoice:
           self.load_bazaarvoice()
        content = self.bazaarvoice['BatchedResults']['q0']['Results'][0]['Description']
        return content
    
    def manufacturer_content_body(self):
       return None


    # extract product price from its product product page tree
    def _price_from_tree(self):
        meta_price = self.tree_html.xpath("//p[@class='current-price']//text()")
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
        description_node = self.tree_html.xpath("//section[@class='detailWrapper']")[0]
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
        if not self.bazaarvoice:
            self.load_bazaarvoice()
        return self.bazaarvoice['BatchedResults']['q0']['Results'][0]['ModelNumbers'][0]

    # extract product features list from its product product page tree, return as string
    # join all text in spec table; separate rows by newlines and eliminate spaces between cells
    def _features_from_tree(self):
        
        #TODO: Needs some logic for deciding when Tesco is displaying one format or the other, the following 2 lines are the currently encountered versions
        #rows = self.tree_html.xpath("//section[@class='detailWrapper']//tr")
        rows = self.tree_html.xpath("//div[@class='product-spec-container']//tr")
        
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
        return len(filter(lambda row: len(row.xpath(".//td"))>0, self.tree_html.xpath("//div[@class='product-spec-container']//tr")))

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
        h2_tags = map(lambda text: self._clean_text(text), self.tree_html.xpath("//h2//text()"))
        seller_info['owned'] = 1 if "Buy on Tesco Direct from:" in h2_tags else 0
        seller_info['marketplace'] = 1 if "more buying option(s) from:" in h2_tags else 0

        return seller_info
    
    # extract the UPC number
    def _upc(self):
        return self.tree_html.xpath('//meta[@property="og:upc"]/@content')[0]
    
    #extract links for all images
    def _product_images(self):
        head = 'http://tesco.scene7.com/is/image/'
        image_url = self.tree_html.xpath("//section[@class='main-details']//script//text()")[1]
        image_url = re.findall("scene7PdpData\.s7ImageSet = '(.*)';", image_url)[0]
        image_url = image_url.split(',')
        return len(image_url)

    # extract the department which the product belongs to
    def _dept(self):
        dept = " ".join(self.tree_html.xpath("//div[@id='breadcrumb']//li[2]//text()")).strip()
        return dept
    
    # extract the department's department, or super department
    def _super_dept(self):
        dept = " ".join(self.tree_html.xpath("//div[@id='breadcrumb']//li[1]//text()")).strip()
        return dept
    
    # extract a hierarchical list of all the departments the product belongs to
    def _all_depts(self):
        all = self.tree_html.xpath("//div[@id='breadcrumb']//li//span/text()")
        #the last value is the product itself
        return all[:-1]
    
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
    def product_in_stock(self):
        return None
    
    #returns 1 if the mobile version is the same, 0 otherwise
    def mobile_image_same(self):
        return None
    
    #returns 1 if it's in stores only, 0 otherwise
    def in_stores_only(self):
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
            sys.stderr.write("ERROR: No product URL provided.\nUsage:\n\tpython crawler_service.py <tesco_product_url>\n")
            sys.exit(1)
    
        product_page_url = args[1]
    
        # check format of page url
        if not check_url_format(product_page_url):
            sys.stderr.write("ERROR: Invalid URL " + str(product_page_url) + "\nFormat of product URL should be\n\t http://www.tesco.com/direct/<part-of-product-name>/<product_id>.prd\n")
            sys.exit(1)
    
        return json.dumps(product_info(sys.argv[1], ["name", "short_desc", "keywords", "price", "load_time", "anchors", "long_desc"]))



    '''
    x extra : all_depts = since dept/super_dept were deprecated and you wanted the whole breadcrumb, I added all_depts which is ordered in a hierarchy
    x UPC/EAN/ISBN - found UPC
    x product_images
    x super_dept - scraped from the breadcrumbs
    x dept - scraped from the breadcrumbs
    x model_title -  exists as "title_from_tree", no other meta title
    x review_count - exists as "total_reviews"
    x meta description - doesn't exist in meta, but this is being pulled from the bazarr json file as "manufacturer_content_body"
    x model_meta  -  there's no meta for model, but there is a model that could (but usually doesn't) exist in the bazaar json file

    meta keywords - doesn't exist in html source, or in the bazaar json
    
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
        "product_id" : _extract_product_id, \
        "image_url" : _image_url, \
        "video_url" : video_for_url, \
        
        "upc" : _upc,\
        "product_images" : _product_images, \
        "dept" : _dept,\
        "super_dept" : _super_dept,\
        "all_depts" : _all_depts,\
        "no_image" : _no_image,\
        
        "product_in_stock" : product_in_stock, \
        "in_stores_only" : in_stores_only, \
        "mobile_image_same" : mobile_image_same, \
        
        "load_time": None\
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "brand" : _meta_brand_from_tree, \
        "model" : _model_from_tree, \
        "manufacturer_content_body" : manufacturer_content_body, \
        "pdf_url" : pdf_for_url, \
        "average_review" : reviews_for_url, \
        "total_reviews" : nr_reviews\
    }






if __name__=="__main__":
    TS = TescoScraper()
    print TS.main(sys.argv)
