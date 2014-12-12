#!/usr/bin/python

import urllib2
from httplib import IncompleteRead
import re
import sys
import json
from io import BytesIO
import cStringIO
from PIL import Image
import mmh3 as MurmurHash
import os

from no_img_hash import fetch_bytes

from lxml import html
import time
from crawlera_api_wrapper import CrawleraRequest
import requests

class Scraper():

    """Base class for scrapers
    Handles incoming requests and calls specific methods from subclasses
    for each requested type of data,
    making sure to minimize number of requests to the site being scraped

    Each subclass must implement:
    - define DATA_TYPES and DATA_TYPES_SPECIAL structures (see subclass docs)
    - implement each method found in the values of the structures above
    - implement checktree_html_format()

    Attributes:
        product_page_url (string): URL of the page of the product being scraped
        tree_html (lxml tree object): html tree of page source. This variable is initialized
        whenever a request is made for a piece of data in DATA_TYPES. So it can be used for methods
        extracting these types of data.
        MAX_RETRIES (int): number of retries before giving up fetching product page soruce (if errors encountered
            - usually IncompleteRead exceptions)
    """

    # number of retries for fetching product page source before giving up
    MAX_RETRIES = 3

    # List containing all data types returned by the crawler (that will appear in responses of requests to service in crawler_service.py)
    # In practice, all returned data types for all crawlers should be defined here
    # The final list containing actual implementing methods for each data type will be defined in the constructor
    # using the declarations in the subclasses (for data types that have support in each subclass)

    BASE_DATA_TYPES_LIST = {
            # TODO: set url globally
            "url", # url of product
            "event",
            "product_id",
            "site_id",
            "date",
            "status",
            "scraper", # version of scraper in effect. Relevant for Walmart old vs new pages.
                       # Only implemented for walmart. Possible values: "Walmart v1" or "Walmart v2"

            # product_info
            "product_name", # name of product, string
            "product_title", # page title, string
            "title_seo", # SEO title, string
            "model", # model of product, string
            "upc", # upc of product, string
            "features", # features of product, string
            "feature_count", # number of features of product, int
            "model_meta", # model from meta, string
            "description", # short description / entire description if no short available, string
            "long_description", # long description / null if description above is entire description, string

            # page_attributes
            "mobile_image_same", # whether mobile image is same as desktop image, 1/0
            "image_count", # number of product images, int
            "image_urls", # urls of product images, list of strings
            "video_count", # nr of videos, int
            "video_urls", # urls of product videos, list of strings
            "pdf_count", # nr of pdfs, string
            "pdf_urls", # urls of product pdfs, list of strings
            "webcollage", # whether video is from webcollage (?), 1/0
            "htags", # h1 and h2 tags, dictionary like: {"h1" : [], "h2": ["text in tag"]}
            "loaded_in_seconds", # load time of product page in seconds, float
            "keywords", # keywords for this product, usually from meta tag, string
            "meta_tags",# a list of pairs of meta tag keys and values
            "meta_tag_count", # the number of meta tags in the source of the page
            
            # reviews
            "review_count", # total number of reviews, int
            "average_review", # average value of review, float
            "max_review", # highest review score, float
            "min_review", # lowest review score, float
            "reviews", # review list
            
            # sellers
            "price", # price, string including currency
            "in_stores", # available to purchase in stores, 1/0
            "in_stores_only", # whether product can be found in stores only, 1/0
            "owned", # whether product is owned by site, 1/0
            "owned_out_of_stock", # whether product is owned and out of stock, 1/0
            "marketplace", # whether product can be found on marketplace, 1/0
            "marketplace_sellers", # sellers on marketplace (or equivalent) selling item, list of strings
            "marketplace_lowest_price", # string
            
            # classification
            "categories", # full path of categories down to this product's ["full", "path", "to", "product", "category"], list of strings
            "category_name", # category for this product, string
            "brand" # brand of product, string

            # Deprecated:
            # "anchors", # links found in the description, dictionary like {"links" : [], quantity: 0}
            # "product_id", # product id (usually from page url), string
            # "no_image", # whether product image is a "there is no image" image: 1/0
            # "manufacturer_content_body", # special section of description by the manufacturer, string
            # "asin",
    }

    # Structure containing data types returned by the crawler as keys
    # and the functions handling extraction of each data type as values
    # There will be dummy implementations for the functions in this base class
    # (to handle subclasses where the extraction is not implemented)
    # and their definition will be overwritten in subclasses where the extraction is implemented;
    # or data types will be added to the structure below
    # 
    # "loaded_in_seconds" needs to always have a value of None (no need to implement extraction)
    # TODO: date should be implemented here
    BASE_DATA_TYPES = {
        data_type : lambda x: None for data_type in BASE_DATA_TYPES_LIST # using argument for lambda because it will be used with "self"
    }

    # structure containing subdictionaries of returned object
    # and how they should be grouped.
    # keys are root object keys, values are lists of result object keys that should be nested
    # into these root keys
    # keys that should be left in the root are not included in this structure
    # TODO: make sure this is synchronized somehow with BASE_DATA_TYPES? like there should be no extra data types here
    #       maybe put it as an instance variable
    # TODO: what if only specific data was requested? will this still work?
    # TODO: add one for root? to make sure nothing new appears in root either?
    DICT_STRUCTURE = {
        "product_info": ["product_name", "product_title", "title_seo", "model", "upc", \
                        "features", "feature_count", "model_meta", "description", "long_description"],
        "page_attributes": ["mobile_image_same", "image_count", "image_urls", "video_count", "video_urls",\
                            "pdf_count", "pdf_urls", "webcollage", "htags", "loaded_in_seconds", "keywords",\
                            'meta_tags','meta_tag_count'], \
        "reviews": ["review_count", "average_review", "max_review", "min_review", "reviews"], \
        "sellers": ["price", "in_stores_only", "in_stores", "owned", "owned_out_of_stock", \
                    "marketplace", "marketplace_sellers", "marketplace_lowest_price"], \
        "classification": ["categories", "category_name", "brand"]
    }

    # response in case of error
    ERROR_RESPONSE = {
        "url" : None,
        "event" : None,
        "product_id" : None,
        "event" : None,
        "date": None,
        "status": None
    }


    def __init__(self, **kwargs):
        self.product_page_url = kwargs['url']
        self.bot_type = kwargs['bot']
        self.crawlera = kwargs['crawlera']
        if self.crawlera is not None:
            self.crawlera = int(self.crawlera)

        current_date = time.strftime("%Y-%m-%d %H:%M:%S")

        # Set fields for success response

        # Set date
        self.BASE_DATA_TYPES['date'] = lambda x: current_date
        # Set url
        self.BASE_DATA_TYPES['url'] = lambda x: self.product_page_url

        # Set status
        # TODO: handle error as well
        self.BASE_DATA_TYPES['status'] = lambda x: "success"

        # update data types dictionary to overwrite names of implementing methods for each data type
        # with implmenting function from subclass
        # precaution mesaure in case one of the dicts is not defined in a scraper
        if not hasattr(self, "DATA_TYPES"):
            self.DATA_TYPES = {}
        if not hasattr(self, "DATA_TYPES_SPECIAL"):
            self.DATA_TYPES_SPECIAL = {}
        self.ALL_DATA_TYPES = dict(self.BASE_DATA_TYPES.items() + self.DATA_TYPES.items() + self.DATA_TYPES_SPECIAL.items())
        # remove data types that were not declared in this superclass
    
        # TODO: do this more efficiently?
        for key in list(self.ALL_DATA_TYPES.keys()):
            if key not in self.BASE_DATA_TYPES:
                print "*******EXTRA data type: ", key
                del self.ALL_DATA_TYPES[key]

        # Set fields for error response
        
        # Set date
        self.ERROR_RESPONSE['date'] = current_date
        # Set url
        self.ERROR_RESPONSE['url'] = self.product_page_url
        # Set status
        self.ERROR_RESPONSE['status'] = "failure"

    # extract product info from product page.
    # (note: this is for info that can be extracted directly from the product page, not content generated through javascript)
    # Additionally from extract_product_data(), this method extracts page load time.
    # parameter: types of info to be extracted as a list of strings, or None for all info
    # return: dictionary with type of info as key and extracted info as value
    def product_info(self, info_type_list = None):
        """Extract all requested data for this product, using subclass extractor methods
        Args:
            info_type_list (list of strings) list containing the types of data requested
        Returns:
            dictionary containing the requested data types as keys
            and the scraped data as values
        """

        #TODO: does this make sure page source is not extracted if not necessary?
        #      if so, should all functions returning null (in every case) be in DATA_TYPES_SPECIAL?

        # if no specific data types were requested, assume all data types were requested
        if not info_type_list:
            info_type_list = self.ALL_DATA_TYPES.keys()

        
        # copy of info list to send to _extract_product_data
        info_type_list_copy = list(info_type_list)

        # build page xml tree. also measure time it took and assume it's page load time (the rest is neglijable)
        time_start = time.time()
        #TODO: only do this if something in DATA_TYPES was requested
        self._extract_page_tree()
        time_end = time.time()
        # don't pass load time as info to be extracted by _extract_product_data
        return_load_time = "loaded_in_seconds" in info_type_list_copy
        if return_load_time:
            info_type_list_copy.remove("loaded_in_seconds")

        ret_dict = self._extract_product_data(info_type_list_copy)
        # add load time to dictionary -- if it's in the list
        # TODO:
        #      - format for loaded_in_seconds?
        #      - what happens if there are requests to js info too? count that load time as well?
        if return_load_time:
            ret_dict["loaded_in_seconds"] = round(time_end - time_start, 2)

        # pack results into nested structure
        nested_results_dict = self._pack_returned_object(ret_dict)

        return nested_results_dict


    # method that returns xml tree of page, to extract the desired elemets from
    def _extract_page_tree(self):
        """Builds and sets as instance variable the xml tree of the product page
        Returns:
            lxml tree object
        """
        if self.crawlera == 1:
            cr = CrawleraRequest()
            contents = cr.get_page(self.product_page_url)
        else:
            request = urllib2.Request(self.product_page_url)
            # set user agent to avoid blocking
            agent = ''
            if self.bot_type == "google":
                agent = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
            else:
                agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20140319 Firefox/24.0 Iceweasel/24.4.0'
            request.add_header('User-Agent', agent)

            for i in range(self.MAX_RETRIES):
                try:
                    contents = urllib2.urlopen(request).read()

                    try:
                        self.tree_html = html.fromstring(contents.decode("utf8"))
                    except UnicodeError, e:
                        # if string was not utf8, don't deocde it
                        print "Warning creating html tree from page content: ", e.message

                        self.tree_html = html.fromstring(contents)

                    # if we got it we can exit the loop and stop retrying
                    return

                except IncompleteRead, e:
                    pass

                # try getting it again, without catching exception.
                # if it had worked by now, it would have returned.
                # if it still doesn't work, it will throw exception.
                # TODO: catch in crawler_service so it returns an "Error communicating with server" as well
            contents = urllib2.urlopen(request).read()
        self.tree_html = html.fromstring(contents)
            

    # Extract product info given a list of the type of info needed.
    # Return dictionary containing type of info as keys and extracted info as values.
    # This method is intended to act as a unitary way of getting all data needed,
    # looking to avoid generating the html tree for each kind of data (if there is more than 1 requested).
    def _extract_product_data(self, info_type_list):
        """Extracts data for current product:
        either from page source given its xml tree
        or using other requests defined in each specific function
        Args:
            info_type_list: list of strings containing the requested data
        Returns:
            dictionary containing the requested data types as keys
            and the scraped data as values
        """

        # _pre_scrape is especially useful for grabbing a related page that multiple fields need access to
        try:
            self._pre_scrape()
        except Exception as e:
            pass # not all websites need a pre_scrape

        results_dict = {}

        # if it's not a valid product page, abort
        if self.not_a_product():
            return self.ERROR_RESPONSE

        for info in info_type_list:

            try:
                results = self.ALL_DATA_TYPES[info](self)
            except IndexError, e:
                sys.stderr.write("ERROR: No " + info + " for " + self.product_page_url + ":\n" + str(e) + "\n")
                results = None
            except Exception, e:
                sys.stderr.write("ERROR: Unknown error extracting " + info + " for " + self.product_page_url + ":\n" + str(e) + "\n")
                results = None

            results_dict[info] = results

        #
        # Add the following calculations to all scrapes
        #
        
        results_dict['img_hashes'] = []
        
        if 'image_urls' in results_dict and results_dict['image_urls'] is not None:
            for image_url in results_dict['image_urls']:
                results_dict['img_hashes'].append( str(MurmurHash.hash(fetch_bytes(image_url))))

        return results_dict

    # pack returned object data types into nested dictionary according to specific format
    # arguments: data_types_dict - contains original flat response dictionary
    # returns: result nested response dictionary
    def _pack_returned_object(self, data_types_dict):

        # pack input object into nested structure according to structure above
        nested_object = {}
        for root_key in self.DICT_STRUCTURE.keys():
            for subkey in self.DICT_STRUCTURE[root_key]:
                # only add this if this data type was requested
                if subkey in data_types_dict:
                    if root_key not in nested_object:
                        nested_object[root_key] = {}

                    nested_object[root_key][subkey] = data_types_dict[subkey]
                    # print subkey
                    # print data_types_dict.keys()
                    del data_types_dict[subkey]
        # now add leftover keys to root level
        nested_object.update(data_types_dict)

        return nested_object

    # base function to test input URL is valid.
    # always returns True, to be used for subclasses where it is not implemented
    # it should be implemented by subclasses with specific code to validate the URL for the specific site
    def check_url_format(self):
        return True


    def not_a_product(self):
        """Abstract method.
        Checks if current page is not a valid product page
        (either an unavailable product page, or some other type of content)
        To be implemented by each scraper specifically for its site.
        Returns:
            True if not a product page,
            False otherwise
        """

        return False
    
    # Checks if image given as parameter is "no  image" image
    # To be used by subscrapers
    def _no_image(self, image_url):
        """Verifies if image with URL given as argument is
        a "no image" image.

        Certain products have an image that indicates "there is no image available"
        a hash of these "no-images" is saved to a json file 
        and new images are compared to see if they're the same.

        Uses "fetch_bytes" function from the script used to compute
        hashes that images here are compard against.

        Returns:
            True if it's a "no image" image, False otherwise
        """

        path = 'no_img_list.json'
        no_img_list = []
        if os.path.isfile(path):
            f = open(path, 'r')
            s = f.read()
            if len(s) > 1:
                no_img_list = json.loads(s)    
            f.close()
        first_hash = str(MurmurHash.hash(fetch_bytes(image_url)))
        if first_hash in no_img_list:
            return True
        else:
            return False

    
if __name__=="__main__":
    print main(sys.argv)
