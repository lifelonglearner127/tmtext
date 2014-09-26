#!/usr/bin/python

import urllib
import re
import sys
import json

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
    - implement check_url_format()

    Attributes:
        product_page_url (string): URL of the page of the product being scraped
        tree_html (lxml tree object): html tree of page source. This variable is initialized
        whenever a request is made for a piece of data in DATA_TYPES. So it can be used for methods
        extracting these types of data.
    """


    # List containing all data types returned by the crawler (that will appear in responses of requests to service in crawler_service.py)
    # In practice, all returned data types for all crawlers should be defined here
    # The final list containing actual implementing methods for each data type will be defined in the constructor
    # using the declarations in the subclasses (for data types that have support in each subclass)

    BASE_DATA_TYPES_LIST = {
            "name", # name of product, string
            "keywords", # keywords associated with product (usually from "meta" tag), string
            "short_desc", # short description, string
            "long_desc", # long description, string
            "price", # price (string, with or without currency)
            "anchors", # links found in the description, dictionary like {"links" : [], quantity: 0}
            "htags", # h1 and h2 tags, dictionary like: {"h1" : [], "h2": ["text in tag"]}
            "features", # features of product, string
            "nr_features", # number of features of product, int
            "title", # page title, string
            "seller", # seller of product, dictionary like: {"owned" : 1, "marketplace": 0}
            "marketplace", # whether product can be found on marketplace, 1/0
            "owned", # whether product is owned by site, 1/0
            "product_id", # product id (usually from page url), string
            "image_url", # urls of product images, list of strings
            "video_url", # urls of product videos, list of strings
            "upc", # UPC of product, string
            "product_images", # number of product images, int
            "categories", # info on product categories, dictionary like: {"super_dept": "string", "dept": "string", "full": ["full", "path", "to", "product"], "hostname": "string"}
            "dept", # product department
            "super_dept", # parent of department
            "all_depts", # full path of categories down to this product, list of strings
            "no_image", # whether product image is a "there is no image" image: true/false
            "product_in_stock", # whether product is in stock: true/false
            "in_stores_only", # whether product can be found in stores only: true/false
            "load_time", # load time of product page in seconds, float
            "mobile_image_same", # whether mobile image is same as desktop image: true/false
            "brand", # brand of product, string
            "model", # model of product, string
            "manufacturer_content_body", # special section of description by the manufacturer, string
            "pdf_url", # urls of product pdfs, list of strings
            "average_review", # average value of review, float?
            "total_reviews", # total number of reviews, int
            "meta_keywords", # "keywords" meta tag, string
            "meta_description", # description in meta tag, string
            "asin", 
    }

    # Structure containing data types returned by the crawler as keys
    # and the functions handling extraction of each data type as values
    # There will be dummy implementations for the functions in this base class
    # (to handle subclasses where the extraction is not implemented)
    # and their definition will be overwritten in subclasses where the extraction is implemented;
    # or data types will be added to the structure below
    # 
    # "load_time" needs to always have a value of None (no need to implement extraction)
    BASE_DATA_TYPES = {
        data_type : lambda x: None for data_type in BASE_DATA_TYPES_LIST # using argument for lambda because it will be used with "self"
    }


    def __init__(self, product_page_url):
        self.product_page_url = product_page_url

        # update data types dictionary to overwrite names of implementing methods for each data type
        # with implmenting function from subclass
        self.ALL_DATA_TYPES = dict(self.BASE_DATA_TYPES.items() + self.DATA_TYPES.items() + self.DATA_TYPES_SPECIAL.items())
        # remove data types that were not declared in this superclass
        # TODO: do this more efficiently?
        for key in list(self.ALL_DATA_TYPES.keys()):
            if key not in self.BASE_DATA_TYPES:
                print "*******EXTRA data type: ", key
                del self.ALL_DATA_TYPES[key]

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
        return_load_time = "load_time" in info_type_list_copy
        if return_load_time:
            info_type_list_copy.remove("load_time")

        ret_dict = self._extract_product_data(info_type_list_copy)
        # add load time to dictionary -- if it's in the list
        # TODO:
        #      - format for load_time?
        #      - what happens if there are requests to js info too? count that load time as well?
        if return_load_time:
            ret_dict["load_time"] = round(time_end - time_start, 2)

        return ret_dict

    # method that returns xml tree of page, to extract the desired elemets from
    def _extract_page_tree(self):
        """Builds and sets as instance variable the xml tree of the product page
        Returns:
            lxml tree object
        """

        contents = urllib.urlopen(self.product_page_url).read()
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

        results_dict = {}

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

    # base function to test input URL is valid.
    # always returns True, to be used for subclasses where it is not implemented
    # it should be implemented by subclasses with specific code to validate the URL for the specific site
    def check_url_format(self):
        return True

    
if __name__=="__main__":
    print main(sys.argv)
