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
import mechanize
import cookielib

from no_img_hash import fetch_bytes

from lxml import html
import time

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
    br = None

    # List containing all data types returned by the crawler (that will appear in responses of requests to service in crawler_service.py)
    # In practice, all returned data types for all crawlers should be defined here
    # The final list containing actual implementing methods for each data type will be defined in the constructor
    # using the declarations in the subclasses (for data types that have support in each subclass)

    BASE_DATA_TYPES_LIST = {
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
            "webcollage", # whether page contains webcollage content, 1/0
            "sellpoints", # whether page contains sellpoint content, 1/0
            "htags", # h1 and h2 tags, dictionary like: {"h1" : [], "h2": ["text in tag"]}
            "loaded_in_seconds", # load time of product page in seconds, float
            "keywords", # keywords for this product, usually from meta tag, string
            "meta_tags",# a list of pairs of meta tag keys and values
            "meta_tag_count", # the number of meta tags in the source of the page

            "image_hashes", # list of hash values of images as returned by _image_hash() function - list of strings (the same order as image_urls)
            "thumbnail", # thumbnail of the main product image on the page - tbd

            
            # reviews
            "review_count", # total number of reviews, int
            "average_review", # average value of review, float
            "max_review", # highest review score, float
            "min_review", # lowest review score, float
            "reviews", # review list
            
            # sellers
            "price", # price, string including currency
            "price_amount", # price, float
            "price_currency", # currency for price, string of max 3 chars
            "in_stores", # available to purchase in stores, 1/0
            "in_stores_only", # whether product can be found in stores only, 1/0
            "marketplace", # whether product can be found on marketplace, 1/0
            "marketplace_sellers", # sellers on marketplace (or equivalent) selling item, list of strings
            "marketplace_lowest_price", # string
            "in_stock", # binary (0/1), whether product can be bought from the site, from any seller
            "site_online", # the item is sold by the site and delivered directly, irrespective of availability - binary
            "site_online_in_stock", # currently available from the site - binary
            "site_online_out_of_stock", # currently unavailable from the site - binary
            "marketplace_in_stock", # currently available from at least one marketplace seller - binary
            "marketplace_out_of_stock", # currently unavailable from any marketplace seller - binary
            "marketplace_prices", # the list of marketplace prices - list of floating-point numbers ([0.00, 0.00], needs to be in the same order as list of marketplace_sellers)
            "in_stores_in_stock", # currently available for pickup from a physical store - binary (null should be used for items that can not be ordered online and the availability may depend on location of the store)
            "in_stores_out_of_stock", # currently unavailable for pickup from a physical store - binary (null should be used for items that can not be ordered online and the availability may depend on location of the store)
            "online_only", # site_online or marketplace but not in_stores - binary
            # legacy
            "owned", # whether product is owned by site, 1/0
            "owned_out_of_stock", # whether product is owned and out of stock, 1/0
            
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
    # TODO: add one for root? to make sure nothing new appears in root either?
    DICT_STRUCTURE = {
        "product_info": ["product_name", "product_title", "title_seo", "model", "upc", \
                        "features", "feature_count", "model_meta", "description", "long_description"],
        "page_attributes": ["mobile_image_same", "image_count", "image_urls", "video_count", "video_urls",\
                            "pdf_count", "pdf_urls", "webcollage", "htags", "loaded_in_seconds", "keywords",\
                            "meta_tags","meta_tag_count", \
                            "image_hashes", "thumbnail", "sellpoints"], \
        "reviews": ["review_count", "average_review", "max_review", "min_review", "reviews"], \
        "sellers": ["price", "price_amount", "price_currency", "in_stores_only", "in_stores", "owned", "owned_out_of_stock", \
                    "marketplace", "marketplace_sellers", "marketplace_lowest_price", "in_stock", \
                    "site_online", "site_online_in_stock", "site_online_out_of_stock", "marketplace_in_stock", \
                    "marketplace_out_of_stock", "marketplace_prices", "in_stores_in_stock", \
                    "in_stores_out_of_stock", "online_only"],
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

    def load_image_hashes():
        '''Read file with image hashes list
        Return list of image hashes found in file
        '''
        path = 'no_img_list.json'
        no_img_list = []
        if os.path.isfile(path):
            f = open(path, 'r')
            s = f.read()
            if len(s) > 1:
                no_img_list = json.loads(s)    
            f.close()
        return no_img_list

    '''Static class variable that holds list of image hashes
    that are "no image" images.
    Should be loaded once when service is started, and subsequently
    used whenever needed, by _no_image(), in any sub-scraper.
    '''
    NO_IMAGE_HASHES = load_image_hashes()

    def __init__(self, **kwargs):
        self.product_page_url = kwargs['url']
        self.bot_type = kwargs['bot']

        # Set generic fields
        # directly (don't need to be computed by the scrapers)

        # Note: This needs to be done before merging with DATA_TYPES, below,
        # so that BASE_DATA_TYPES values can be overwritten by DATA_TYPES values
        # if needed. (more specifically overwrite functions for extracting certain data
        # (especially sellers-related fields))
        self._pre_set_fields()

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

    def _pre_set_fields(self):
        '''Before the scraping for the particular site is started,
        some general fields are set directly.
        Fields set: date, url, status
        '''

        current_date = time.strftime("%Y-%m-%d %H:%M:%S")

        # Set fields for success respose

        # Generic fields
        # Set date
        self.BASE_DATA_TYPES['date'] = lambda x: current_date
        # Set url
        self.BASE_DATA_TYPES['url'] = lambda x: self.product_page_url
        # Set status
        self.BASE_DATA_TYPES['status'] = lambda x: "success"

        # Deprecated fields
        self.BASE_DATA_TYPES['owned'] = lambda c: c._owned()
        self.BASE_DATA_TYPES['owned_out_of_stock'] = lambda c: c._owned_out_of_stock()
        # Inferred fields
        self.BASE_DATA_TYPES['site_online_in_stock'] = lambda c: c._site_online_in_stock()
        self.BASE_DATA_TYPES['marketplace_in_stock'] = lambda c: c._marketplace_in_stock()
        self.BASE_DATA_TYPES['in_stores_in_stock'] = lambda c: c._in_stores_in_stock()

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
        # Browser
        self.br = mechanize.Browser()

        # Cookie Jar
        cj = cookielib.LWPCookieJar()
        self.br.set_cookiejar(cj)

        # Browser options
        self.br.set_handle_equiv(True)
        self.br.set_handle_gzip(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

        # Follows refresh 0 but not hangs on refresh > 0
        # br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        # Want debugging messages?
        #br.set_debug_http(True)
        #br.set_debug_redirects(True)
        #br.set_debug_responses(True)

        # User-Agent (this is cheating, ok?)
        # self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20140319 Firefox/24.0 Iceweasel/24.4.0')]

        # request = urllib2.Request(self.product_page_url)
        # # set user agent to avoid blocking
        # agent = ''
        # if self.bot_type == "google":
        #     print 'GOOOOOOOOOOOOOGGGGGGGLEEEE'
        #     agent = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        # else:
        #     agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20140319 Firefox/24.0 Iceweasel/24.4.0'
        # request.add_header('User-Agent', agent)

        for i in range(self.MAX_RETRIES):
            try:
                r = self.br.open(self.product_page_url)
                contents = r.read()
                # contents = urllib2.urlopen(request).read()

            # handle urls with special characters
            except UnicodeEncodeError, e:

                r = br.open(self.product_page_url.encode("utf-8"))
                contents = r.read()
                # request = urllib2.Request(self.product_page_url.encode("utf-8"))
                # request.add_header('User-Agent', agent)
                # contents = urllib2.urlopen(request).read()

            except IncompleteRead, e:
                continue


            try:
                self.tree_html = html.fromstring(contents.decode("utf8"))
            except UnicodeError, e:
                # if string was not utf8, don't deocde it
                print "Warning creating html tree from page content: ", e.message

                self.tree_html = html.fromstring(contents)

            # if we got it we can exit the loop and stop retrying
            return


            # try getting it again, without catching exception.
            # if it had worked by now, it would have returned.
            # if it still doesn't work, it will throw exception.
            # TODO: catch in crawler_service so it returns an "Error communicating with server" as well
            r = self.br.open(self.product_page_url)
            contents = r.read()
            # contents = urllib2.urlopen(request).read()
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

    def _image_hash(self, image_url):
        """Computes hash for an image.
        To be used in _no_image, and for value of _image_hashes
        returned by scraper.
        Returns string representing hash of image.

        :param image_url: url of image to be hashed
        """
        return str(MurmurHash.hash(fetch_bytes(image_url)))
    
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

        first_hash = self._image_hash(image_url)
        if first_hash in self.NO_IMAGE_HASHES:
            print "not an image"
            return True
        else:
            return False

    def _owned(self):
        '''General function for setting value of legacy field "owned".
        It will be inferred from value of "site_online_in_stock" field.
        Method can be overwritten by scraper class if different implementation
        is available.
        '''

        # set extractor function for owned
        # to be same as for site_online_in_stock
        return self.DATA_TYPES['site_online_in_stock']

    def _owned_out_of_stock(self):
        '''General function for setting value of legacy field "owned_out_of_stock".
        It will be inferred from value of "site_online_out_of_stock" field.
        Method can be overwritten by scraper class if different implementation
        is available.
        '''

        # set extractor function for owned_out_of_stock
        # to be same as for site_online_out_of_stock
        return self.DATA_TYPES['site_online_out_of_stock']

    def _site_online_in_stock(self):
        '''General function for setting value of field "site_online_in_stock".
        It will be inferred from other sellers fields.
        Method can be overwritten by scraper class if different implementation
        is available.
        '''

        # compute necessary fields
        # Note: might lead to calling these functions twice.
        # But they should be inexpensive
        try:
            site_online = self.ALL_DATA_TYPES['site_online'](self)
        except:
            site_online = None

        try:
            site_online_out_of_stock = self.ALL_DATA_TYPES['site_online_out_of_stock'](self)
        except:
            site_online_out_of_stock = None

        # site_online is 1 and site_online_out_of_stock is 0
        if site_online == 1 and site_online_out_of_stock == 0:
            return 1

        return 0

    def _in_stores_in_stock(self):
        '''General function for setting value of field "in_stores_in_stock".
        It will be inferred from other sellers fields.
        Method can be overwritten by scraper class if different implementation
        is available.
        '''

        # compute necessary fields
        # Note: might lead to calling these functions twice.
        # But they should be inexpensive
        try:
            in_stores = self.ALL_DATA_TYPES['in_stores'](self)
        except:
            in_stores = None

        try:
            in_stores_out_of_stock = self.ALL_DATA_TYPES['in_stores_out_of_stock'](self)
        except:
            in_stores_out_of_stock = None

        # in_stores is 1 and in_stores_out_of_stock is 0
        if in_stores == 1 and in_stores_out_of_stock == 0:
            return 1

        return 0

    def _marketplace_in_stock(self):
        '''General function for setting value of field "in_stores_in_stock".
        It will be inferred from other sellers fields.
        Method can be overwritten by scraper class if different implementation
        is available.
        '''

        # compute necessary fields
        # Note: might lead to calling these functions twice.
        # But they should be inexpensive
        try:
            marketplace = self.ALL_DATA_TYPES['marketplace'](self)
        except:
            marketplace = None

        try:
            marketplace_out_of_stock = self.ALL_DATA_TYPES['marketplace_out_of_stock'](self)
        except:
            marketplace_out_of_stock = None

        # marketplace is 1 and marketplace_out_of_stock is 0
        if marketplace == 1 and marketplace_out_of_stock == 0:
            return 1

        return 0


    
if __name__=="__main__":
    print main(sys.argv)
