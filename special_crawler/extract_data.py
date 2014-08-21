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

    Attributes:
        product_page_url (string): URL of the page of the product being scraped
    """

    def __init__(self, product_page_url):
        self.product_page_url = product_page_url

    # Inherited classes need to implement additionally:
    # - [NO] check_url_format
    # - [NO] check_url that will validate the input [after i move it]
    # - [deprecated] media_for_url
    # - methods defined as keys to self.DATA_TYPES and self.DATA_TYPES_SPECIAL (except for load_time)

    # extract product info from product page.
    # (note: this is for info that can be extracted directly from the product page, not content generated through javascript)
    # Additionally from _info_from_tree(), this method extracts page load time.
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

        if not info_type_list:
            info_type_list = self.DATA_TYPES.keys() + self.DATA_TYPES_SPECIAL.keys()
        
        # copy of info list to send to _info_from_tree
        info_type_list_copy = list(info_type_list)

        # build page xml tree. also measure time it took and assume it's page load time (the rest is neglijable)
        time_start = time.time()
        tree = self.page_tree()
        time_end = time.time()
        # don't pass load time as info to be extracted by _info_from_tree
        return_load_time = "load_time" in info_type_list_copy
        if return_load_time:
            info_type_list_copy.remove("load_time")

        # remove special info that is not to be extracted from the product page (and handled separately)
        for special_info in self.DATA_TYPES_SPECIAL.keys():
            if special_info in info_type_list_copy:
                info_type_list_copy.remove(special_info)
        ret_dict = self._info_from_tree(tree, info_type_list_copy)
        # add load time to dictionary -- if it's in the list
        # TODO:
        #      - format for load_time?
        #      - what happens if there are requests to js info too? count that load time as well?
        if return_load_time:
            ret_dict["load_time"] = round(time_end - time_start, 2)

        # add special data
        for special_info in self.DATA_TYPES_SPECIAL:
            if special_info in info_type_list:
                # TODO: do this differently
                ret_dict.update(self.DATA_TYPES_SPECIAL[special_info](self))

        return ret_dict

    # method that returns xml tree of page, to extract the desired elemets from
    def page_tree(self):
        """Builds and returns the xml tree of the product page
        Returns:
            lxml tree object
        """

        contents = urllib.urlopen(self.product_page_url).read()
        tree_html = html.fromstring(contents)
        return tree_html

    # Extract product info from its product page tree
    # given its tree and a list of the type of info needed.
    # Return dictionary containing type of info as keys and extracted info as values.
    # This method is intended to act as a unitary way of getting all data needed,
    # looking to avoid generating the html tree for each kind of data (if there is more than 1 requested).
    def _info_from_tree(self, tree_html, info_type_list):
        """Extracts data from page source given its xml tree
        Args:
            tree_html (lxml tree object): tree of source page
            info_type_list: list of strings containing the requested data
        Returns:
            dictionary containing the requested data types as keys
            and the scraped data as values
        """

        results_dict = {}

        for info in info_type_list:

            try:
                results = self.DATA_TYPES[info](self, tree_html)
            except IndexError, e:
                sys.stderr.write("ERROR: No " + info + " for " + self.product_page_url + ":\n" + str(e) + "\n")
                results = None
            except Exception, e:
                sys.stderr.write("ERROR: Unknown error extracting " + info + " for " + self.product_page_url + ":\n" + str(e) + "\n")
                results = None

            results_dict[info] = results

        return results_dict

    
if __name__=="__main__":
    print main(sys.argv)
