#!/usr/bin/python

import urllib
import re
import sys
import json

from lxml import html
import time
import requests

from extract_data import Scraper

class WalmartScraper(Scraper):

    """Implements methods that each extract an individual piece of data for walmart.com
        Attributes:
            product_page_url (inherited): the URL for the product page being scraped
        Static attributes:
            DATA_TYPES (dict): 
            DATA_TYPES_SPECIAL (dict):  structures containing the supported data types to be extracted as keys
                                        and the methods that implement them as values

            INVALID_URL_MESSAGE: string that will be used in the "InvalidUsage" error message,
                                 should contain information on what the expected format for the
                                 input URL is.

            BASE_URL_VIDEOREQ (string):
            BASE_URL_PDFREQ (string):
            BASE_URL_REVIEWSREQ (string):   strings containing necessary hardcoded URLs for extracting walmart
                                            videos, pdfs and reviews
    """

    # base URL for request containing video URL
    BASE_URL_VIDEOREQ = "http://json.webcollage.net/apps/json/walmart?callback=jsonCallback&environment-id=live&cpi="
    # base URL for request containing pdf URL
    BASE_URL_PDFREQ = "http://content.webcollage.net/walmart/smart-button?ignore-jsp=true&ird=true&channel-product-id="
    # base URL for request for product reviews - formatted string
    BASE_URL_REVIEWSREQ = 'http://walmart.ugc.bazaarvoice.com/1336a/%20{0}/reviews.djs?format=embeddedhtml'


    INVALID_URL_MESSAGE = "Expected URL format is http://www.walmart.com/ip[/<optional-part-of-product-name>]/<product_id>"

    def __init__(self, product_page_url):
        Scraper.__init__(self, product_page_url)

        # whether product has any webcollage media
        self.has_webcollage_media = False

    # checks input format
    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match("http://www\.walmart\.com(/.*)?/[0-9]+$", self.product_page_url)
        return not not m

    # TODO:
    #      better way of extracting id now that URL format is more permissive
    #      though this method still seems to work...
    def _extract_product_id(self):
        """Extracts product id of walmart product from its URL
        Returns:
            string containing only product id
        """

        product_id = self.product_page_url.split('/')[-1]
        return product_id

    # check if there is a "Video" button available on the product page
    def _has_video_button(self):
        """Checks if a certain product page has a visible 'Video' button,
        using the page source tree.
        Returns:
            True if video button found (or if video button presence can't be determined)
            False if video button not present
        """

        richMedia_elements = self.tree_html.xpath("//div[@id='richMedia']")
        if richMedia_elements:
            richMedia_element = richMedia_elements[0]
            elements_onclick = richMedia_element.xpath(".//li/@onclick")
            # any of the "onclick" attributes of the richMedia <li> tags contains "video')"
            has_video =  any(map(lambda el: "video')" in el, elements_onclick))

            return has_video

        # if no rich media div found, assume a possible error in extraction and return True for further analysis
        # TODO:
        #      return false cause no rich media at all?
        return True

    def _video_urls(self):
        """Extracts video URL for a given walmart product
        Returns:
            list containing the video's URLs
        """

        # if there is no video button, return no video
        if not self._has_video_button():
            return None

        request_url = self.BASE_URL_VIDEOREQ + self._extract_product_id()

        #TODO: handle errors
        response_text = urllib.urlopen(request_url).read()

        # get first "src" value in response
        # # webcollage videos
        video_url_candidates = re.findall("src: \"([^\"]+)\"", response_text)
        if video_url_candidates:
            # remove escapes
            #TODO: better way to do this?
            video_url_candidate = re.sub('\\\\', "", video_url_candidates[0])

            # if it ends in flv, it's a video, ok
            if video_url_candidate.endswith(".flv"):
                self.has_webcollage_media = True
                return [video_url_candidate]

            # if it doesn't, it may be a url to make another request to, to get customer reviews video
            new_response = urllib.urlopen(video_url_candidate).read()
            video_id_candidates = re.findall("param name=\"video\" value=\"(.*)\"", new_response)

            if video_id_candidates:
                video_id = video_id_candidates[0]

                video_url_req = "http://client.expotv.com/vurl/%s?output=mp4" % video_id
                video_url = urllib.urlopen(video_url_req).url

                return [video_url]

        return None

    def _pdf_urls(self):
        """Extracts pdf URL for a given walmart product
        Returns:
            list containing the pdf's URLs
        """

        request_url = self.BASE_URL_PDFREQ + self._extract_product_id()

        response_text = urllib.urlopen(request_url).read().decode('string-escape')

        pdf_url_candidates = re.findall('(?<=")http[^"]*media\.webcollage\.net[^"]*[^"]+\.[pP][dD][fF](?=")', response_text)
        if pdf_url_candidates:
            # remove escapes
            pdf_url = re.sub('\\\\', "", pdf_url_candidates[0])
            self.has_webcollage_media = True

            return [pdf_url]

        else:
            return None

    # TODO: flatten returned object
    def reviews_for_url(self):
        """Extracts and returns reviews data for a walmart product
        using additional requests (other than page source)
        Returns:
            nested dictionary with 'reviews' as first-level key,
            pointing to another dictionary with following keys:
            'total_reviews' - value is int
            'average_review' - value is float
        """

        request_url = self.BASE_URL_REVIEWSREQ.format(self._extract_product_id())
        content = urllib.urlopen(request_url).read()
        try:
            reviews_count = re.findall(r"BVRRNonZeroCount\\\"><span class=\\\"BVRRNumber\\\">([0-9,]+)<", content)[0]
            average_review = re.findall(r"class=\\\"BVRRRatingNormalOutOf\\\"> <span class=\\\"BVRRNumber BVRRRatingNumber\\\">([0-9\.]+)<", content)[0]
        except Exception, e:
            return {"reviews" : {"total_reviews": None, "average_review": None}}
        return {"reviews" : {"total_reviews": reviews_count, "average_review": average_review}}

    def _product_has_webcollage(self):
        """Uses video and pdf information
        to check whether product has any media from webcollage.
        Returns:
            1 if there is webcollage media
            0 otherwise
        """
        if self.has_webcollage_media:
            return 1
        return 0

    # extract product name from its product page tree
    # ! may throw exception if not found
    # TODO: improve, filter by tag class or something
    def _product_name_from_tree(self):
        """Extracts product name
        Returns:
            string containing product name, or None
        """

        return self.tree_html.xpath("//h1")[0].text

    # extract meta "keywords" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_keywords_from_tree(self):
        """Extracts meta 'kewyords' tag for a walmart product
        Returns:
            string containing the tag's content, or None
        """

        return self.tree_html.xpath("//meta[@name='Keywords']/@content")[0]

    # extract meta "brand" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_brand_from_tree(self):
        """Extracts meta 'brand' tag for a walmart product
        Returns:
            string containing the tag's content, or None
        """

        return self.tree_html.xpath("//meta[@itemprop='brand']/@content")[0]


    # extract product short description from its product page tree
    # ! may throw exception if not found
    def _short_description_from_tree(self):
        """Extracts product short description
        Returns:
            string containing the text content of the product's description, or None
        """

        short_description = " ".join(self.tree_html.xpath("//span[@class='ql-details-short-desc']//text()")).strip()
        # TODO: return None if no description
        return short_description

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description_from_tree(self):
        """Extracts product long description
        Returns:
            string containing the text content of the product's description, or None
        """
        
        full_description = " ".join(self.tree_html.xpath("//div[@itemprop='description']//text()")).strip()
        # TODO: return None if no description
        return full_description

    # extract product price from its product product page tree
    def _price_from_tree(self):
        """Extracts product price
        Returns:
            string containing the product price, with decimals, no currency
        """

        meta_price = self.tree_html.xpath("//meta[@itemprop='price']/@content")
        if meta_price:
            return meta_price[0]
        else:
            return None

    # extract htags (h1, h2) from its product product page tree
    def _htags_from_tree(self):
        """Extracts 'h' tags in product page
        Returns:
            dictionary with 2 keys:
            h1 - value is list of strings containing text in each h1 tag on page
            h2 - value is list of strings containing text in each h2 tag on page
        """

        htags_dict = {}

        # add h1 tags text to the list corresponding to the "h1" key in the dict
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        # add h2 tags text to the list corresponding to the "h2" key in the dict
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))

        return htags_dict

    # extract product model from its product product page tree
    # ! may throw exception if not found
    def _model_from_tree(self):
        """Extracts product model
        Returns:
            string containing the product model, or None
        """

        return self.tree_html.xpath("//table[@class='SpecTable']//td[contains(text(),'Model')]/following-sibling::*/text()")[0]

    # extract product model from its product product page tree (meta tag)
    # ! may throw exception if not found
    def _meta_model_from_tree(self):
        """Extracts product model from meta tag
        Returns:
            string containing the meta model
        """

        return self.tree_html.xpath("//meta[@itemprop='model']/@content")[0]

    def _categories_hierarchy(self):
        """Extracts full path of hierarchy of categories
        this product belongs to, from the lowest level category
        it belongs to, to its top level department
        Returns:
            list of strings containing full path of categories
            (from highest-most general to lowest-most specific)
            or None if list is empty of not found
        """

        categories_list = self.tree_html.xpath("//li[@class='breadcrumb']/a/span/text()")
        if categories_list:
            return categories_list
        else:
            return None

    # ! may throw exception of not found
    def _category(self):
        """Extracts lowest level (most specific) category this product
        belongs to.
        Returns:
            string containing product category
        """

        # return last element of the categories list
        return self.tree_html.xpath("//li[@class='breadcrumb']/a/span/text()")[-1]

    # extract product features list from its product product page tree, return as string
    def _features_from_tree(self):
        """Extracts product features
        Returns:
            dictionary with 2 values:
            features_list - value is string containing text of product features
            nr_features - value is int containing number of features
        """

        # join all text in spec table; separate rows by newlines and eliminate spaces between cells
        rows = self.tree_html.xpath("//table[@class='SpecTable']//tr")
        # list of lists of cells (by rows)
        cells = map(lambda row: row.xpath(".//td//text()"), rows)
        # list of text in each row
        rows_text = map(\
            lambda row: "".join(\
                map(lambda cell: cell.strip(), row)\
                ), \
            cells)
        all_features_text = "\n".join(rows_text)

        # return string with all features text
        return all_features_text

    # extract number of features from tree
    # ! may throw exception if not found
    def _nr_features_from_tree(self):
        """Extracts number of product features
        Returns:
            int containing number of features
        """

        # select table rows with more than 2 cells (the others are just headers), count them
        return len(filter(lambda row: len(row.xpath(".//td"))>1, self.tree_html.xpath("//table[@class='SpecTable']//tr")))

    # extract page title from its product product page tree
    # ! may throw exception if not found
    def _title_from_tree(self):
        """Extracts page title
        Returns:
            string containing page title, or None
        """

        return self.tree_html.xpath("//title//text()")[0].strip()

    # extract product seller meta tag content from its product product page tree
    # ! may throw exception if not found
    def _seller_meta_from_tree(self):
        """Extracts sellers of product extracted from 'seller' meta tag, and their availability
        Returns:
            dictionary with sellers as keys and availability (true/false) as values
        """

        sellers = self.tree_html.xpath("//div[@itemprop='offers']")

        sellers_dict = {}
        for seller in sellers:
            # try to get seller if any, otherwise ignore this div
            try:
                avail = (seller.xpath(".//meta[@itemprop='availability']/@content")[0] == "http://schema.org/InStock")
                sellers_dict[seller.xpath(".//meta[@itemprop='seller']/@content")[0]] = avail
            except IndexError:
                pass

        return sellers_dict

    # TODO: more optimal - don't extract this twice
    # TODO: add docstring
    def _owned_meta_from_tree(self):
        seller_dict = self._seller_from_tree()
        owned = seller_dict['owned']
        return owned

    # TODO: more optimal - don't extract this twice
    # TODO: add docstring
    def _marketplace_meta_from_tree(self):
        seller_dict = self._seller_from_tree()
        marketplace = seller_dict['marketplace']
        return marketplace     

    # ! may throw exception if not found
    # TODO: is this the right UPC? there are versions of it in the page, some with leading "00" before it
    def _upc_from_tree(self):
        """Extracts UPC of product from meta tag
        Returns:
            string containing upc
        """
        return self.tree_html.xpath("//meta[@property='og:upc']/@content")[0]   


    # extract product seller information from its product product page tree
    def _seller_from_tree(self):
        """Extracts seller info of product extracted from 'Buy from ...' elements on page
        Returns:
            dictionary with 2 values:
            owned - True if owned by walmart.com, False otherwise
            marketplace - True if available on marketplace, False otherwise
        """

        seller_info = {}
        sellers = self._seller_meta_from_tree()

        # owned if has seller Walmart.com and availability for it is true
        seller_info['owned'] = 1 if ('Walmart.com' in sellers.keys() and sellers['Walmart.com']) else 0
        # found on marketplace if there are other keys other than walmart and they are in stock
        # TODO:
        #      more sophisticated checking of availability for marketplace? (values are more than just InStock/OutOfStock)
        #      (because for walmart they should only be available when in stock) 
        # remove Walmart key as we already checked for it
        if 'Walmart.com' in sellers.keys():
            del sellers['Walmart.com']
        seller_info['marketplace'] = 1 if (len(sellers.keys()) > 0 and any(sellers.values())) else 0

        return seller_info

    # extract nr of product reviews information from its product page
    # ! may throw exception if not found
    def _nr_reviews_from_tree(self):
        """Extracts total nr of reviews info for walmart product using page source
        Returns:
            int containing total nr of reviews
        """

        reviews_info_node = self.tree_html.xpath("//div[@id='BVReviewsContainer']//span[@itemprop='aggregateRating']")[0]
        nr_reviews = int(reviews_info_node.xpath("span[@itemprop='reviewCount']/text()")[0])

        return nr_reviews

    # extract average product reviews information from its product page
    # ! may throw exception if not found
    def _avg_review_from_tree(self):
        """Extracts average review info for walmart product using page source
        Returns:
            float containing average value of reviews
        """

        reviews_info_node = self.tree_html.xpath("//div[@id='BVReviewsContainer']//span[@itemprop='aggregateRating']")[0]
        average_review = float(reviews_info_node.xpath("span[@itemprop='ratingValue']/text()")[0])

        return average_review

    def _image_count(self):
        return len(self._image_urls())

    def _image_urls(self):
        scripts = self.tree_html.xpath("//script//text()")
        for script in scripts:
            find = re.findall(r'posterImages\.push\(\'(.*)\'\);', str(script)) 
            if len(find)>0:
                return find
        
        # It should only return this img when there's no img carousel    
        pic = [self.tree_html.xpath('//div[@class="LargeItemPhoto215"]/a/@href')[0]]
        return pic
    
    # 1 if mobile image is same as pc image, 0 otherwise, and None if it can't grab images from one site
    def _mobile_image_same(self):
        url = self.product_page_url
        url = re.sub('http://www', 'http://mobile', url)
        mobile_headers = {"User-Agent" : "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5"}
        contents = requests.get(url, headers=mobile_headers).text
        tree = html.fromstring(contents)
        mobile_img = tree.xpath('.//*[contains(@class,"carousel ")]//*[contains(@class, "carousel-item")]/@data-model-id')
        img = self._image_urls()
        
        if mobile_img and img:
            if mobile_img[0] == img[0]:
                return 1
            else:
                return 0
        else:
            return None # no images found to compare
    

    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        """Cleans a piece of text of html entities
        Args:
            original text (string)
        Returns:
            text stripped of html entities
        """

        return re.sub("&nbsp;", " ", text).strip()
    



    # TODO: fix to work with restructured code
    def main(args):
        # check if there is an argument
        if len(args) <= 1:
            sys.stderr.write("ERROR: No product URL provided.\nUsage:\n\tpython extract_walmart_media.py <walmart_product_url>\n")
            sys.exit(1)

        product_page_url = args[1]

        # check format of page url
        if not check_url_format(product_page_url):
            sys.stderr.write("ERROR: Invalid URL " + str(product_page_url) + "\nFormat of product URL should be\n\t http://www.walmart.com/ip/<product_id>\n")
            sys.exit(1)

        return json.dumps(product_info(sys.argv[1], ["name", "short_desc", "keywords", "price", "load_time", "anchors", "long_desc"]))

        # create json object with video and pdf urls
        #return json.dumps(media_for_url(product_page_url))
    #    return json.dumps(reviews_for_url(product_page_url))



    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service
    # 
    # data extracted from product page
    # their associated methods return the raw data
    """Contains as keys all data types that can be extracted by this class
    Their corresponding values are the methods of this class that handle the extraction of
    the respective data types. All these methods must be defined (except for 'load_time' value)

    The keys of this structure are data types that can be extracted solely from the page source
    of the product page.
    """

    DATA_TYPES = { \
        # Info extracted from product page
        "upc" : _upc_from_tree, \
        "product_name" : _product_name_from_tree, \
        "keywords" : _meta_keywords_from_tree, \
        "brand" : _meta_brand_from_tree, \
        "description" : _short_description_from_tree, \
        # TODO: check if descriptions work right
        "long_description" : _long_description_from_tree, \
        "price" : _price_from_tree, \
        "htags" : _htags_from_tree, \
        "model" : _model_from_tree, \
        "model_meta" : _meta_model_from_tree, \
        "features" : _features_from_tree, \
        "feature_count" : _nr_features_from_tree, \
        "title_seo" : _title_from_tree, \
        # TODO: I think this causes the method to be called twice and is inoptimal
        "product_title" : _product_name_from_tree, \
        "owned": _owned_meta_from_tree, \
        "marketplace": _marketplace_meta_from_tree, \
        "review_count": _nr_reviews_from_tree, \
        "average_review": _avg_review_from_tree, \
        # video needs both page source and separate requests
        "video_urls" : _video_urls, \
        "webcollage" : _product_has_webcollage, \
        
        "image_count" : _image_count, \
        "image_urls" : _image_urls, \

        "categories" : _categories_hierarchy, \
        "category_name" : _category, \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    """Contains as keys all data types that can be extracted by this class
    Their corresponding values are the methods of this class that handle the extraction of
    the respective data types. All these methods must be defined (except for 'load_time' value)

    The keys of this structure are data types that can't be extracted from the page source
    of the product page and need additional requests.
    """

    DATA_TYPES_SPECIAL = { \
        "pdf_urls" : _pdf_urls, \
        "mobile_image_same" : _mobile_image_same \

    #    "reviews" : reviews_for_url \
    }


if __name__=="__main__":
    WD = WalmartScraper()
    print WD.main(sys.argv)

## TODO:
## Implemented:
##     - name
##  - meta keywords
##  - short description
##  - long description
##  - price
##  - url of video
##  - url of pdf
##  - anchors (?)
##  - H tags 
##  - page load time (?)
##  - number of reviews
##  - model
##  - list of features
##  - meta brand tag
##  - page title
##  - number of features
##  - sold by walmart / sold by marketplace sellers

##  
## To implement:
##     - number of images, URLs of images
##  - number of videos, URLs of videos if more than 1
##  - number of pdfs
##  - category info (name, code, parents)
##  - minimum review value, maximum review value
