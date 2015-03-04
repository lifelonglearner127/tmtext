#!/usr/bin/python

import urllib
import re
import sys
import json

from lxml import html, etree
import lxml
import urllib
import lxml.html
import time
import requests
from selenium.webdriver.common.by import By

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

            BASE_URL_VIDEOREQ_WEBCOLLAGE (string):
            BASE_URL_PDFREQ_WEBCOLLAGE (string):
            BASE_URL_REVIEWSREQ (string):   strings containing necessary hardcoded URLs for extracting walmart
                                            videos, pdfs and reviews
    """

    # base URL for request containing video URL from webcollage
    BASE_URL_VIDEOREQ_WEBCOLLAGE = "http://json.webcollage.net/apps/json/walmart?callback=jsonCallback&environment-id=live&cpi="
    # base URL for request containing video URL from sellpoints
    BASE_URL_VIDEOREQ_SELLPOINTS = "http://www.walmart.com/product/idml/video/%s/SellPointsVideos"
    # base URL for request containing pdf URL from webcollage
    BASE_URL_PDFREQ_WEBCOLLAGE = "http://content.webcollage.net/walmart/smart-button?ignore-jsp=true&ird=true&channel-product-id="
    # base URL for request for product reviews - formatted string
    BASE_URL_REVIEWSREQ = 'http://walmart.ugc.bazaarvoice.com/1336a/%20{0}/reviews.djs?format=embeddedhtml'


    INVALID_URL_MESSAGE = "Expected URL format is http://www.walmart.com/ip[/<optional-part-of-product-name>]/<product_id>"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.has_webcollage_media = False
        # whether product has any sellpoints media
        self.has_sellpoints_media = False
        # product videos (to be used for "video_urls", "video_count", and "webcollage")
        self.video_urls = None
        # whether videos were extracted
        self.extracted_video_urls = False
        # product pdfs (to be used for "pdf_urls", "pdf_count", and "webcollage")
        self.pdf_urls = None
        # whether videos were extracted
        self.extracted_pdf_urls = False

        # whether product has any pdfs
        self.has_pdf = False
        # whether product has any videos
        self.has_video = False

        # javascript function found in a script tag
        # containing various info on the product.
        # Currently used for seller info (but useful for others as well)
        self.js_entry_function_body = None

        #whether the page has loaded in phantom
        self.is_page_loaded_in_phantom = False
    # checks input format
    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match("http://www\.walmart\.com(/.*)?/[0-9]+(\?www=true)?$", self.product_page_url)
        return not not m

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """

        try:
            page_title = self.tree_html.xpath("//title/text()")[0]
        except Exception:
            page_title = None

        if page_title == " - Walmart":
            return True

        else:
            return False

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

    def _extract_video_urls(self):
        """Extracts video URL for a given walmart product
        and puts them in instance variable.
        """

        # set flag that videos where attemtped to be extracted
        self.extracted_video_urls = True

        # if there is no video button, return no video
        if not self._has_video_button():
            return None

        request_url = self.BASE_URL_VIDEOREQ_WEBCOLLAGE + self._extract_product_id()

        self.video_urls = []

        #TODO: handle errors
        response_text = urllib.urlopen(request_url).read()

        # get first "src" value in response
        # # webcollage videos
        video_url_candidates = re.findall("src: \"([^\"]+)\"", response_text)
        if video_url_candidates:
            # remove escapes
            #TODO: better way to do this?
            for video_url_item in video_url_candidates:
                video_url_candidate = re.sub('\\\\', "", video_url_item)

                # if it ends in flv, it's a video, ok
                if video_url_candidate.endswith(".flv"):
                    self.has_webcollage_media = True
                    self.has_video = True
                    self.video_urls.append(video_url_candidate)
                    break

                # if it doesn't, it may be a url to make another request to, to get customer reviews video
                if "client.expotv.com" in video_url_candidate:
                    new_response = urllib.urlopen(video_url_candidate).read()
                    video_id_candidates = re.findall("param name=\"video\" value=\"(.*)\"", new_response)

                    if video_id_candidates:
                        video_id = video_id_candidates[0]

                        video_url_req = "http://client.expotv.com/vurl/%s?output=mp4" % video_id
                        video_url = urllib.urlopen(video_url_req).url
                        self.has_video = True
                        self.video_urls.append(video_url)

        # check sellpoints media if webcollage media doesn't exist
        request_url = self.BASE_URL_VIDEOREQ_SELLPOINTS % self._extract_product_id()
        #TODO: handle errors
        response_text = urllib.urlopen(request_url).read()

        # get first "src" value in response
        # # webcollage videos
        video_url_candidates = re.findall("'file': '([^']+)'", response_text)
        if video_url_candidates:
            # remove escapes
            #TODO: better way to do this?
            for video_url_item in video_url_candidates:
                video_url_candidate = re.sub('\\\\', "", video_url_item)

                # if it ends in flv, it's a video, ok
                if video_url_candidate.endswith(".mp4") or video_url_candidate.endswith(".flv"):
                    self.has_sellpoints_media = True
                    self.has_video = True
                    self.video_urls.append(video_url_candidate)
                    break

        if len(self.video_urls) == 0:
            if self.tree_html.xpath("//div[starts-with(@class,'js-idml-video-container')]"):
                contents = requests.get("http://www.walmart.com/product/idml/video/" +
                                        str(self._extract_product_id()) + "/WebcollageVideos").text

                tree = html.fromstring(contents)
                video_json = json.loads(tree.xpath("//div[@class='wc-json-data']/text()")[0])
                video_relative_path = video_json["videos"][0]["sources"][0]["src"]
                video_base_path = tree.xpath("//table[@class='wc-gallery-table']/@data-resources-base")[0]
                self.video_urls.append(video_base_path + video_relative_path)
                self.has_video = True
            else:
                self.video_urls = None


    def _video_urls(self):
        """Extracts video URLs for a given walmart product
        Returns:
            list of strings containing the video urls
            or None if none found
        """

        if not self.extracted_video_urls:
            self._extract_video_urls()

        return self.video_urls

    def _pdf_urls(self):
        """Extracts pdf URLs for a given walmart product, puts them in an instance variable
        Returns:
            list of strings containing the pdf urls
            or None if not found
        """

        if self.extracted_pdf_urls:
            return self.pdf_urls

        self.extracted_pdf_urls = True
        self.pdf_urls = []

        pdf_links = self.tree_html.xpath("//a[contains(@href,'.pdf')]/@href")

        for item in pdf_links:
            if item.strip().endswith(".pdf"):
                self.pdf_urls.append(item.strip()) if item.strip() not in self.pdf_urls else None

        if self.tree_html.xpath("//iframe[contains(@class, 'js-marketing-content-iframe')]/@src"):
            request_url = self.tree_html.xpath("//iframe[contains(@class, 'js-marketing-content-iframe')]/@src")[0]
            request_url = "http:" + request_url.strip()

            response_text = urllib.urlopen(request_url).read().decode('string-escape')

            pdf_url_candidates = re.findall('(?<=")http[^"]*media\.webcollage\.net[^"]*[^"]+\.[pP][dD][fF](?=")', response_text)

            if pdf_url_candidates:
                self.has_webcollage_media = True
                for item in pdf_url_candidates:
                    # remove escapes
                    pdf_url = re.sub('\\\\', "", item.strip())
                    self.pdf_urls.append(pdf_url) if pdf_url not in self.pdf_urls else None

        if self.pdf_urls:
            self.has_pdf = True
        else:
            self.pdf_urls = None

        return self.pdf_urls

    # deprecated
    # TODO: flatten returned object
    def reviews_for_url(self):
        """Extracts and returns reviews data for a walmart product
        using additional requests (other than page source).
        Works for old walmart page structure.
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

    def _has_webcollage_iframe(self):
        """Extracts webcollage links from an iframe on the page.
        (Example: http://www.walmart.com/ip/Trix-Wildberry-Red-Swirls-Cereal-22.7-oz/25847976
            has some webcollage images)
        Returns:
            1 if page has iframe with webcollage images, 0 otherwise
        """

        # assume only 1 iframe
        # TODO: identify it by class or smth?
        try:
            iframe_link = self.tree_html.xpath("//iframe/@src")[0]
            if iframe_link.startswith("/"):
                # append scheme
                iframe_link = "http:" + iframe_link

            # get contents of iframe
            contents = urllib.urlopen(iframe_link).read()
            # get webcollage content from iframe
            # TODO: what if they are in comments?
            if "media.webcollage.net" in contents:
                return 1

        except Exception, e:
            return 0

        return 0

    def _product_has_webcollage(self):
        """Uses video and pdf information
        to check whether product has any media from webcollage.
        Returns:
            1 if there is webcollage media
            0 otherwise
        """

        if not self.extracted_video_urls:
            self._extract_video_urls()

        if not self.extracted_pdf_urls:
            self._pdf_urls()

        if self.has_webcollage_media:
            return 1

        if self._has_webcollage_iframe():
            return 1

        return 0

    def _product_has_sellpoints(self):
        """Uses video and pdf information
        to check whether product has any media from sellpoints.
        Returns:
            1 if there is sellpoints media
            0 otherwise
        """

        if not self.extracted_video_urls:
            self._extract_video_urls()

#        if not self.extracted_pdf_urls:
#            self._pdf_urls()

        if self.has_sellpoints_media:
            return 1

#        if self._has_sellpoints_iframe():
#            return 1

        return 0

    def _product_has_video(self):
        """Whether product has video
        To be replaced with function that actually counts
        number of videos for this product
        Returns:
            1 if product has video
            0 if product doesn't have video
        """

        if not self.extracted_video_urls:
            self._extract_video_urls()

        if self.has_video:
            return 1
        else:
            return 0

    def _pdf_count(self):
        """Returns the number of pdf
        """

        return len(self.pdf_urls)

    def _product_has_pdf(self):
        """Whether product has pdf
        To be replaced with function that actually counts
        number of pdfs for this product
        Returns:
            1 if product has pdf
            0 if product doesn't have pdf
        """

        if not self.extracted_pdf_urls:
            self._pdf_urls()

        if self.has_pdf:
            return 1
        else:
            return 0

    # extract product name from its product page tree
    # ! may throw exception if not found
    # TODO: improve, filter by tag class or something
    def _product_name_from_tree(self):
        """Extracts product name.
        Supports both old and new page design.
        Returns:
            string containing product name, or None
        """

        # assume new design
        product_name_node = self.tree_html.xpath("//h1[contains(@class, 'product-name')]")

        if not product_name_node:
            # assume old design
            product_name_node = self.tree_html.xpath("//h1[contains(@class, 'productTitle')]")

        if self.stringify_children(product_name_node[0]).strip() == '':
            self.load_page_in_phantom()
            product_name_node = self.driver.find_element(By.XPATH, "//h1[contains(@class, 'product-name')]").text
            return product_name_node

        return self.stringify_children(product_name_node[0]).strip()

    # extract meta "keywords" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_keywords_from_tree(self):
        """Extracts meta 'kewyords' tag for a walmart product.
        Works for both old or new version of walmart pages
        Returns:
            string containing the tag's content, or None
        """

        # supports both new and old version of walmart pages
        return self.tree_html.xpath("//meta[@name='keywords']/@content | //meta[@name='Keywords']/@content")[0]

    # extract meta tags exclude http-equiv
    def _meta_tags(self):
        tags = map(lambda x:x.values() ,self.tree_html.xpath('//meta[not(@http-equiv)]'))
        return tags

    def _meta_tag_count(self):
        tags = self._meta_tags()
        return len(tags)

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

        short_description = "".join(map(lambda li_element: etree.tostring(li_element), \
            self.tree_html.xpath("//div[@class='product-short-description module']//li | " +\
                "//div[starts-with(@class, 'choice-short-description')]//li")\
            ))

        # try with just the text
        if not short_description.strip():
            short_description = " ".join(self.tree_html.xpath("//div[@class='product-short-description module']//text() | " + \
                "//div[starts-with(@class, 'choice-short-description')]//text()"))

        # try to extract from old page structure - in case walmart is
        # returning an old type of page
        if not short_description:
            short_description = " ".join(self.tree_html.xpath("//span[@class='ql-details-short-desc']//text()")).strip()

        # if no short description, return the long description
        if not short_description.strip():
            return None

        return short_description.strip()

    def _short_description_wrapper(self):
        """Extracts product short description.
        If not found, returns long description instead,
        or the first, bulletted part of the long description, if found.
        Returns:
            string containing the text content of the product's description, or None
        """

        # TODO: maybe these extractor functions are being called too many times.
        #       maybe reimplement this using state - an instance variable containing
        #       both descriptions (extracted at once)
        try:
            short_description = self._short_description_from_tree()
        except:
            short_description = None

        if not short_description:
            # get everything before and including <li> tags from long description.
            short_description = " ".join(self.tree_html.xpath("//div[@class='js-ellipsis module']//*[following-sibling::li|self::li|following-sibling::ul]//text()")).strip()

            # hack: remove everything after "Ingredients", cause sometimes they're still there...
            try:
                ingredients_index = short_description.index("Ingredients:")
                short_description = short_description[: ingredients_index].strip()
            except Exception:
                pass

        if not short_description.strip():
            # if there are no bullets either, get the entire long description text
            short_description = self._long_description()

        return short_description

    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description_from_tree_old(self):
        """Extracts product long description.
        Works on old design for walmart pages.
        Returns:
            string containing the text content of the product's description, or None
        """

        # select text in nodes under @itemprop='description' that don't have an ancestor @class='ql-details-short-desc' (that's where short description is)
        full_description = " ".join(self.tree_html.xpath("//div[@itemprop='description']//text()[not(ancestor::*[@class='ql-details-short-desc'])]")).strip()
        # return None if empty
        if not full_description:
            return None
        return full_description

    # ! may throw exception if not found
    def _long_description_from_tree(self):
        """Extracts product long description.
        Works on latest design for walmart pages.
        Returns:
            string containing the text content of the product's description, or None
        """

        description_elements = self.tree_html.xpath("//*[starts-with(@class, 'product-about js-about')]"
                                                    "/div[contains(@class, 'js-ellipsis')]")[0]
        full_description = ""

        for description_element in description_elements:
            full_description += lxml.html.tostring(description_element)

        # return None if empty
        if not full_description:
            return None
        return full_description

    def _long_description(self):
        """Extracts product long description.
        Wrapper function that uses extractor functions to try extracting assuming
        either old walmart page design, or new. Works for both.
        Returns:
            string containing the text content of the product's description, or None
        """

        # assume new page format
        # extractor function may throw exception if extraction fails
        try:
            long_description_new = self._long_description_from_tree()
        except Exception:
            long_description_new = None

        # try assuming old page structure now
        if long_description_new is None:
            long_description = self._long_description_from_tree_old()
        else:
            long_description = long_description_new

        return long_description

    def _long_description_wrapper(self):
        """Extracts product long description.
        Wrapper function that uses extractor functions to try extracting assuming
        either old walmart page design, or new. Works for both.
        If short description is equal to long description, returns None, because
        long description text will be returned by the short description function.
        Returns:
            string containing the text content of the product's description, or None
        """

        # if short description is null, it probably returned some part of long description
        # so change strategy for returning long description
        short_description = self._short_description_from_tree()
        long_description = self._long_description()

        if short_description is None:

            # get all long description text that is not in long description
            all_long_description_text = " ".join(self.tree_html.xpath("//div[@class='js-ellipsis module']//text()")).strip()
            short_description_text = self._short_description_wrapper()

            # normalize spaces
            all_long_description_text = re.sub("\s+", " ", all_long_description_text)
            short_description_text = re.sub("\s+", " ", short_description_text)

            # substract the 2 strings
            long_description = "".join(all_long_description_text.rsplit(short_description_text)).strip()

        return long_description

    # extract product price from its product product page tree
    def _price_from_tree(self):
        """Extracts product price
        Returns:
            string containing the product price, with decimals, no currency
        """
        try:
            body_raw = "" . join(self.tree_html.xpath("//form[@name='SelectProductForm']//script/text()")).strip()
            body_clean = re.sub("\n", " ", body_raw)
            body_jpart = re.findall("\{\ itemId.*?\}\s*\] }", body_clean)[0]
            sIndex = body_jpart.find("price:") + len("price:") + 1
            eIndex = body_jpart.find("',", sIndex)

            if "camelPrice" not in body_jpart[sIndex:eIndex] and not self._in_stock():
                return "out of stock - no price given"

            if "camelPrice" not in body_jpart[sIndex:eIndex] and self._in_stores_only():
                return "in stores only - no online price"
        except Exception:
            pass


        meta_price = self.tree_html.xpath("//meta[@itemprop='price']/@content")

        if meta_price:
            return meta_price[0]
        else:
            if not self._in_stock():
                return "out of stock - no price given"
            else:
                return None

    def _price_amount(self):
        """Extracts numercial value of product price in
        Returns:
            the numerical value of the price - floating-point number (null if there is no price)
        """

        price_info = self._price_from_tree()

        if price_info is None or price_info == "out of stock - no price given" or price_info == \
                "in stores only - no online price":
            return None
        else:
            if price_info[0] == '$':
                return float(price_info[1:])
            else:
                return float(price_info)

    def _price_currency(self):
        """Extracts currency of product price in
        Returns:
            price currency symbol
        """
        price_info = self._price_from_tree()

        if price_info is None or price_info == "out of stock - no price given" or price_info == \
                "in stores only - no online price":
            return None
        else:
            meta_currency = self.tree_html.xpath("//meta[@itemprop='priceCurrency']/@content")[0]
            return meta_currency

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
        """Extracts product model.
        Works for both old and new walmart page structure.
        Returns:
            string containing the product model, or None
        """

        # extract features table for new page version:
        # might cause exception if table node not found (and premature exit of function)
        try:
            table_node = self.tree_html.xpath("//div[@class='specs-table']/table")[0]
        except Exception:
            table_node = None

        if not table_node:
            # old page version:
            table_node = self.tree_html.xpath("//table[@class='SpecTable']")[0]

        return table_node.xpath(".//td[contains(text(),'Model')]/following-sibling::*/text()")[0].strip()

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
        it belongs to, to its top level department.
        Works for both old and new page design
        Returns:
            list of strings containing full path of categories
            (from highest-most general to lowest-most specific)
            or None if list is empty of not found
        """

        # assume new page design
        categories_list = self.tree_html.xpath("//li[@class='breadcrumb']/a/span/text()")
        if categories_list:
            return categories_list
        else:
            # assume old page design
            try:
                return self._categories_hierarchy_old()
            except Exception:
                return None

    # ! may throw exception if not found
    def _categories_hierarchy_old(self):
        """Extracts full path of hierarchy of categories
        this product belongs to, from the lowest level category
        it belongs to, to its top level department.
        For old page design
        Returns:
            list of strings containing full path of categories
            (from highest-most general to lowest-most specific)
            or None if list is empty of not found
        """

        js_breadcrumb_text = self.tree_html.xpath("""//script[@type='text/javascript' and
         contains(text(), 'adsDefinitionObject.ads.push')]/text()""")[0]

        # extract relevant part from js function text
        js_breadcrumb_text = re.sub("\n", " ", js_breadcrumb_text)
        m = re.match('.*(\{.*"unitName".*\}).*', js_breadcrumb_text)
        json_object = json.loads(m.group(1))
        categories_string = json_object["unitName"]
        categories_list = categories_string.split("/")
        # remove first irrelevant part
        catalog_index = categories_list.index("catalog")
        categories_list = categories_list[catalog_index + 1 :]

        # clean categories names
        def clean_category(category_name):
            import string
            # capitalize every word, separated by "_", replace "_" with spaces
            return re.sub("_", " ", string.capwords(category_name, "_"))

        categories_list = map(clean_category, categories_list)
        categories_list, "CATEGORIES LIST*******"
        return categories_list

    # ! may throw exception of not found
    def _category(self):
        """Extracts lowest level (most specific) category this product
        belongs to.
        Works for both old and new pages
        Returns:
            string containing product category
        """

        # return last element of the categories list

        # assume new design
        try:
            category = self.tree_html.xpath("//li[@class='breadcrumb']/a/span/text()")[-1]
        except Exception:
            category = None

        if category:
            return category
        else:
            # asume old design
            category = self._categories_hierarchy_old()[-1]

            return category

    # extract product features list from its product product page tree, return as string
    def _features_from_tree(self):
        """Extracts product features
        Returns:
            dictionary with 2 values:
            features_list - value is string containing text of product features
            nr_features - value is int containing number of features
        """

        # join all text in spec table; separate rows by newlines and eliminate spaces between cells
        # new page version:
        rows = self.tree_html.xpath("//div[@class='specs-table']/table//tr")
        if not rows:
            # old page version:
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
        """Extracts number of product features.
        Works for both old and new walmart page structure
        Returns:
            int containing number of features
        """

        # select table rows with more than 2 cells (the others are just headers), count them
        # new page version:
        rows = self.tree_html.xpath("//div[@class='specs-table']/table//tr")
        if not rows:
            # old page version:
            rows = self.tree_html.xpath("//table[@class='SpecTable']//tr")

        return len(filter(lambda row: len(row.xpath(".//td"))>1, rows))

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
        return self.tree_html.xpath("//meta[@itemprop='productID']/@content")[0]

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
    def _nr_reviews_new(self):
        """Extracts total nr of reviews info for walmart product using page source
        Works for new walmart page structure
        Returns:
            int containing total nr of reviews
        """

        nr_reviews_str = self.tree_html.xpath("//div[@class='review-summary grid grid-padded']\
            //p[@class='heading-e']/span[1]/text()")
        nr_reviews = int(nr_reviews_str[0])

        return nr_reviews

    # extract max review information from its product page tree
    # ! may return None if not found or no review
    def _max_review(self):
        review_rating_list_text = self.tree_html.xpath('//div[contains(@class, "review-summary")]//div[contains(@class, "js-rating-filter")]/span/text()')
        review_rating_list_int = []

        if not review_rating_list_text:
            return None

        for index in range(5):
            if int(review_rating_list_text[index]) > 0:
                review_rating_list_int.append(5 - index)

        if not review_rating_list_int:
            return None

        return float(max(review_rating_list_int))

    # extract min review information from its product page tree
    # ! may return None if not found or no review
    def _min_review(self):
        review_rating_list_text = self.tree_html.xpath('//div[contains(@class, "review-summary")]//div[contains(@class, "js-rating-filter")]/span/text()')
        review_rating_list_int = []

        if not review_rating_list_text:
            return None

        for index in range(5):
            if int(review_rating_list_text[index]) > 0:
                review_rating_list_int.append(5 - index)

        if not review_rating_list_int:
            return None

        return float(min(review_rating_list_int))

    # extract revew list information from its product page tree
    # ! may return None if not found or no reviews
    def _reviews(self):
        review_rating_list_text = self.tree_html.xpath('//div[contains(@class, "review-summary")]//div[contains(@class, "js-rating-filter")]/span/text()')
        review_rating_list_int = []

        if not review_rating_list_text:
            return None

        for index in range(5):
            if int(review_rating_list_text[index]) > 0:
                review_rating_list_int.append([5 - index, int(review_rating_list_text[index])])

        if not review_rating_list_int:
            return None

        return review_rating_list_int

    # extract average product reviews information from its product page
    # ! may throw exception if not found
    def _avg_review_new(self):
        """Extracts average review info for walmart product using page source
        Works for new walmart page structure
        Returns:
            float containing average value of reviews
        """

        average_review_str = self.tree_html.xpath("//div[@class='review-summary grid grid-padded']\
            //p[@class='heading-e']/span[2]/text()")
        average_review = float(average_review_str[0])

        return average_review

    # ! may throw exception if not found
    def _avg_review_old(self):
        """Extracts average review info for walmart product using page source
        Works for old walmart page structure
        Returns:
            float containing average value of reviews
        """
        reviews_info_node = self.tree_html.xpath("//div[@id='BVReviewsContainer']//span[@itemprop='aggregateRating']")[0]
        average_review = float(reviews_info_node.xpath("span[@itemprop='ratingValue']/text()")[0])
        return average_review

    # ! may throw exception if not found
    def _nr_reviews_old(self):
        """Extracts total nr of reviews info for walmart product using page source
        Works for old walmart page structure
        Returns:
            int containing total nr of reviews
        """
        reviews_info_node = self.tree_html.xpath("//div[@id='BVReviewsContainer']//span[@itemprop='aggregateRating']")[0]
        nr_reviews = int(reviews_info_node.xpath("span[@itemprop='reviewCount']/text()")[0])
        return nr_reviews

    def _avg_review(self):
        """Extracts average review value for walmart product
        Works for both new and old walmart page structure
        (uses the extractor function relevant for this page)
        Returns:
            float containing average value of reviews
        """

        # assume new page structure
        # extractor function may throw exception if extraction failed
        try:
            average_review = self._avg_review_new()
        except Exception:
            average_review = None

        # extractor for new page structure failed. try with old
        if average_review is None:
            return self._avg_review_old()

        return average_review

    def _nr_reviews(self):
        """Extracts total nr of reviews info for walmart product using page source
        Works for both new and old walmart page structure
        (uses the extractor function relevant for this page)
        Returns:
            int containing total nr of reviews
        """

        # assume new page structure
        # extractor function may throw exception if extraction failed
        try:
            nr_reviews = self._nr_reviews_new()
        except Exception:
            nr_reviews = None

        # extractor for new page structure failed. try with old
        if nr_reviews is None:
            return self._nr_reviews_old()

        return nr_reviews

    def _no_image(self, url):
        """Overwrites the _no_image
        in the base class with an additional test.
        Then calls the base class no_image.

        Returns True if image in url is a "no image"
        image, False if not
        """

        # if image name is "no_image", return True
        if re.match(".*no.image\..*", url):
            return True
        else:
            return Scraper._no_image(self, url)

    def _image_count(self):
        """Counts number of (valid) images found
        for this product (not including images saying "no image available")
        Returns:
            int representing number of images
        """

        try:
            images = self._image_urls()
        except Exception:
            images = None
            pass

        if not images:
            return 0
        else:
            return len(images)

    def _image_urls_old(self):
        """Extracts image urls for this product.
        Works on old version of walmart pages.
        Returns:
            list of strings representing image urls
        """

        scripts = self.tree_html.xpath("//script//text()")
        for script in scripts:
            # TODO: is str() below needed?
            #       it sometimes throws an exception for non-ascii text
            try:
                find = re.findall(r'posterImages\.push\(\'(.*)\'\);', str(script))
            except:
                find = []
            if len(find)>0:
                return self._qualify_image_urls(find)

        # It should only return this img when there's no img carousel
        pic = [self.tree_html.xpath('//div[@class="LargeItemPhoto215"]/a/@href')[0]]
        if pic:
            # check if it's a "no image" image
            # this may return a decoder not found error
            try:
                if self._no_image(pic[0]):
                    return None
            except Exception, e:
                # TODO: how to get this printed in the logs
                print "WARNING: ", e.message

            return self._qualify_image_urls(pic)
        else:
            return None

    def _qualify_image_urls(self, image_list):
        """Remove no image urls in image list
        """
        qualified_image_list = []

        for image in image_list:
            if not re.match(".*no.image\..*", image):
                qualified_image_list.append(image)

        if len(qualified_image_list) == 0:
            return None
        else:
            return qualified_image_list

    def _image_urls_new(self):
        """Extracts image urls for this product.
        Works on new version of walmart pages.
        Returns:
            list of strings representing image urls
        """

        def _fix_relative_url(relative_url):
            """Fixes relative image urls by prepending
            the domain. First checks if url is relative
            """

            if not relative_url.startswith("http"):
                return "http://www.walmart.com" + relative_url
            else:
                return relative_url

        images_carousel = self.tree_html.xpath("//div[contains(@class,'product-carousel-wrapper')]//a/@href")
        if images_carousel:
            # fix relative urls
            images_carousel = map(_fix_relative_url, images_carousel)

            # if there's only one image, check to see if it's a "no image"
            if len(images_carousel) == 1:
                try:
                    if self._no_image(images_carousel[0]):
                        return None
                except Exception, e:
                    print "WARNING: ", e.message

            return self._qualify_image_urls(images_carousel)

        # It should only return this img when there's no img carousel
        main_image = self.tree_html.xpath("//img[@class='product-image js-product-image js-product-primary-image']/@src")
        if main_image:
            # check if this is a "no image" image
            # this may return a decoder not found error
            try:
                if self._no_image(main_image[0]):
                    return None
            except Exception, e:
                print "WARNING: ", e.message

            return self._qualify_image_urls(main_image)

        # bundle product images
        images_bundle = self.tree_html.xpath("//div[contains(@class, 'choice-hero-imagery-components')]//" + \
                                             "img[contains(@class, 'media-object')]/@src")

        if not images_bundle:
            images_bundle = self.tree_html.xpath("//div[contains(@class, 'non-choice-hero-components')]//" + \
                                                 "img[contains(@class, 'media-object')]/@src")

        if images_bundle:
            # fix relative urls
            images_bundle = map(_fix_relative_url, images_bundle)
            return self._qualify_image_urls(images_bundle)

        # nothing found
        return None

    def _image_urls(self):
        """Extracts image urls for this product.
        Works on both old and new version of walmart pages.
        Returns:
            list of strings representing image urls
        """

        # assume new version
        image_list = self._image_urls_new()
        if image_list is None:
            return self._image_urls_old()

        return image_list

    # 1 if mobile image is same as pc image, 0 otherwise, and None if it can't grab images from one site
    # might be outdated? (since walmart site redesign)
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

    # ! may throw exception if json object not decoded properly
    def _extract_productinfo_json_from_jsfunction_body_new(self):
        """Extracts body of javascript function
        found in a script tag on each new product page,
        that contains various usable information about product.
        Stores function body as json decoded dictionary in instance variable.
        Returns:
            function body as dictionary (containing various info on product)
        """

        body_raw = "".join(self.tree_html.xpath("//section[@class='center']/script//text()"))
        body_clean = re.sub("\n", " ", body_raw)
        # extract json part of function body
        body_jpart = re.findall("\{\"productName.*?\}\s*\);", body_clean)[0]
        body_jpart = body_jpart[:-2].strip()

        body_dict = json.loads(body_jpart)

        self.js_entry_function_body = body_dict
        return body_dict

    # ! may throw exception if json object not decoded properly
    def _extract_productinfo_json_from_jsfunction_body_old(self):
        """Extracts body of javascript function
        found in a script tag on each old product page,
        that contains various usable information about product.
        Stores function body as json decoded dictionary in instance variable.
        Returns:
            function body as dictionary (containing various info on product)
        """

        body_raw = "" . join(self.tree_html.xpath("//form[@name='SelectProductForm']//script/text()")).strip()
        body_clean = re.sub("\n", " ", body_raw)
        body_jpart = re.findall("\{\ itemId.*?\}\s*\] }", body_clean)[0]

        body_dict = {}

        sIndex = body_jpart.find("isInStore") + len("isInStore") + 2
        if body_jpart[sIndex:sIndex + 1] == "t":
            body_dict['isInStore'] = True
        else:
            body_dict['isInStore'] = False

        sIndex = body_jpart.find("isInStock") + len("isInStock") + 2
        if body_jpart[sIndex:sIndex + 1] == "t":
            body_dict['isInStock'] = True
        else:
            body_dict['isInStock'] = False

        sIndex = body_jpart.find("isRunout") + len("isRunout") + 2
        if body_jpart[sIndex:sIndex + 1] == "t":
            body_dict['isRunout'] = True
        else:
            body_dict['isRunout'] = False

        sIndex = body_jpart.find("canAddtoCart") + len("canAddtoCart") + 2
        if body_jpart[sIndex:sIndex + 1] == "t":
            body_dict['canAddtoCart'] = True
        else:
            body_dict['canAddtoCart'] = False

        sIndex = body_jpart.find("isEmailMe") + len("isEmailMe") + 2
        if body_jpart[sIndex:sIndex + 1] == "t":
            body_dict['isEmailMe'] = True
        else:
            body_dict['isEmailMe'] = False

        sIndex = body_jpart.find("isPreOrder") + len("isPreOrder") + 2
        if body_jpart[sIndex:sIndex + 1] == "t":
            body_dict['isPreOrder'] = True
        else:
            body_dict['isPreOrder'] = False

        sIndex = body_jpart.find("isPreOrderOOS") + len("isPreOrderOOS") + 2
        if body_jpart[sIndex:sIndex + 1] == "t":
            body_dict['isPreOrderOOS'] = True
        else:
            body_dict['isPreOrderOOS'] = False

        sIndex = body_jpart.find("isComingSoon") + len("isComingSoon") + 2
        if body_jpart[sIndex:sIndex + 1] == "t":
            body_dict['isComingSoon'] = True
        else:
            body_dict['isComingSoon'] = False

        sIndex = body_jpart.find("isDisplayable") + len("isDisplayable") + 2
        if body_jpart[sIndex:sIndex + 1] == "t":
            body_dict['isDisplayable'] = True
        else:
            body_dict['isDisplayable'] = False

        return body_dict

    # ! may throw exception if not found
    def _owned_from_script(self):
        """Extracts 'owned' (by walmart) info on product
        from script tag content (using an object in a js function).
        Returns:
            1/0 (product owned/not owned)
        """

        if not self.js_entry_function_body:
            pinfo_dict = self._extract_productinfo_json_from_jsfunction_body_new()
        else:
            pinfo_dict = self.js_entry_function_body

        seller = pinfo_dict['analyticsData']['sellerName']

        # TODO: what if walmart is not primary seller?
        if (seller == "Walmart.com"):
            return 1
        else:
            return 0

    # ! may throw exception if not found
    def _marketplace_from_script(self):
        """Extracts 'marketplace' sellers info on product
        from script tag content (using an object in a js function).
        Returns:
            1/0 (product has marketplace sellers/has not)
        """

        if not self.js_entry_function_body:
            pinfo_dict = self._extract_productinfo_json_from_jsfunction_body_new()
        else:
            pinfo_dict = self.js_entry_function_body

        # TODO: what to do when there is no 'marketplaceOptions'?
        #       e.g. http://www.walmart.com/ip/23149039
        try:
            marketplace_seller_info = pinfo_dict['buyingOptions']['marketplaceOptions']

            if not marketplace_seller_info:
                if pinfo_dict["buyingOptions"]["seller"]["walmartOnline"]:
                    marketplace_seller_info = None
                elif not pinfo_dict["buyingOptions"]["seller"]["walmartOnline"]:
                    marketplace_seller_info = pinfo_dict["buyingOptions"]["seller"]["name"]
        except Exception:
            # if 'marketplaceOptions' key was not found,
            # check if product is owned and has no other sellers
            owned = self._owned_from_script()
            other_sellers = pinfo_dict['buyingOptions']['otherSellersCount']
            if owned and not other_sellers:
                return 0
            else:
                # didn't find info on this
                return None

        # if list is empty, then product is not available on marketplace
        if marketplace_seller_info:
            return 1
        else:
            return 0

    def _in_stores(self):
        """Extracts whether product is available in stores.
        Returns 1/0
        """
        in_stores = 0

        try:
            if self._in_stores_only() == 1:
                return 1

            in_stores = self._stores_available_from_script_old_page()
            return in_stores
        except Exception:
            pass

        try:
            in_stores = self._stores_available_from_script_new_page()

            if in_stores:
                return in_stores
            else:
                body_raw = "".join(self.tree_html.xpath("//script//text()"))
                body_clean = re.sub("\n", " ", body_raw)
                # extract json part of function body
#                body_jpart = re.findall("\{\ itemId.*?\}\s*\] }", body_clean)[0]

                body_jpart = re.findall("\{\"query.*?\}", body_clean)[0]
                body_dict = json.loads(body_jpart)

                if body_dict["inStore"] is True:
                    return 1
        except Exception:
            pass

        return in_stores


    def _in_stores_only(self):
        '''General function for setting value of field "in_stores_only".
        It will be inferred from other sellers fields.
        Method can be overwritten by scraper class if different implementation is available.
        '''

        onlinePriceText = ""

        try:
            onlinePriceText = "".join(self.tree_html.xpath("//div[@class='onlinePriceWM']//text()"))
            if "In stores only" in onlinePriceText:
                return 1
        except Exception:
            pass

        try:
            onlinePriceText = "".join(self.tree_html.xpath("//div[@class='onlinePriceMP']//text()"))
            if "In stores only" in onlinePriceText:
                return 1
        except Exception:
            pass

        return 0

    def _in_stores_out_of_stock(self):
        '''General function for setting value of field "in_stores_out_of_stock".
        It will be inferred from other sellers fields.
        Method can be overwritten by scraper class if different implementation is available.
        '''

        try:
            # old version
            self.load_page_in_phantom()
            WMNotAvailableLine_style = self.driver.find_element(By.XPATH, "//p[@id='WMNotAvailableLine']").\
                get_attribute("style").strip()

            if "display: block;" in WMNotAvailableLine_style or "display: none;" not in WMNotAvailableLine_style:
                WMNotAvailableLine_text = self.tree_html.xpath("//p[@id='WMNotAvailableLine']//text()")[0].strip()

                if "Not Available" in WMNotAvailableLine_text:
                    return 1
        except Exception:
            pass

        return None

    def load_page_in_phantom(self):
        if not self.is_page_loaded_in_phantom:
            self.driver.get(self.product_page_url)
            self.is_page_loaded_in_phantom = True

    def _stores_available_from_script_old_page(self):
        """Extracts whether product is available in stores.
        Works on old page version.
        Returns 1/0
        """

        body_raw = "" . join(self.tree_html.xpath("//form[@name='SelectProductForm']//script/text()")).strip()
        body_clean = re.sub("\n", " ", body_raw)
        body_jpart = re.findall("\{\ itemId.*?\}\s*\] }", body_clean)[0]

#        body_dict = json.loads(body_jpart)

        sIndex = body_jpart.find("isInStore") + len("isInStore") + 2
        eIndex = body_jpart.find(",", sIndex)

        if body_jpart[sIndex:eIndex] == "true":
            return 1
        else:
            return 0

    # ! may throw exception if not found
    def _stores_available_from_script_new_page(self):
        """Extracts whether product is available in stores.
        Works on new page version.
        Returns 1/0
        """

#        if self._site_online():
#           return 1

        if not self.js_entry_function_body:
            pinfo_dict = self._extract_productinfo_json_from_jsfunction_body_new()
        else:
            pinfo_dict = self.js_entry_function_body

        available = pinfo_dict["analyticsData"]["storesAvail"]

        return 1 if available else 0

    # ! may throw exception if not found
    def _marketplace_sellers_from_script(self):
        """Extracts list of marketplace sellers for this product.
        Works on new page version.
        Returns:
            list of strings representing marketplace sellers,
            or None if none found / not relevant
        """

        if not self.js_entry_function_body:
            pinfo_dict = self._extract_productinfo_json_from_jsfunction_body_new()
        else:
            pinfo_dict = self.js_entry_function_body

        sellers_dict = pinfo_dict["analyticsData"]["productSellersMap"]
        sellers = map(lambda d: d["sellerName"], sellers_dict)

        return sellers

    # ! may throw exception if not found
    def _in_stock_from_script(self):
        """Extracts info on whether product is available to be
        bought on the site, from any seller (marketplace or owned).
        Works on new page design
        Returns:
            1/0 (available/not available)
        """

        if not self.js_entry_function_body:
            pinfo_dict = self._extract_productinfo_json_from_jsfunction_body_new()
        else:
            pinfo_dict = self.js_entry_function_body

        available = pinfo_dict["analyticsData"]["onlineAvail"]

        return 1 if available else 0

    def _in_stock_old(self):
        """Extracts info on whether product is available to be
        bought on the site, from any seller (marketplace or owned).
        Works on old page design
        Returns:
            1/0 (available/not available)
        """

        sellers = self._seller_meta_from_tree()

        try:
            mp_seller_na_msg_3 = self.tree_html.xpath("//span[@id='MP_SELLER_NA_MSG_3']/@style")[0].replace(" ", "")

            if mp_seller_na_msg_3 == "display:block;":
                return 0
        except Exception:
            pass

        available = any(sellers.values())

        return 1 if available else 0

    def _owned(self):
        """Extracts info on whether product is ownedby Walmart.com.
        Uses functions that work on both old page design and new design.
        Will choose whichever gives results.
        Returns:
            1/0 (owned/not owned)
        """

        # assume new design
        # _owned_from_script() may throw exception if extraction fails
        # (causing the service to return None for "owned")
        try:
            owned_new = self._owned_from_script()
        except Exception:
            owned_new = None

        if owned_new is None:
            # try to extract assuming old page structure
            return self._owned_meta_from_tree()

        return owned_new

    def _marketplace(self):
        """Extracts info on whether product is found on marketplace
        Uses functions that work on both old page design and new design.
        Will choose whichever gives results.
        Returns:
            1/0 (marketplace sellers / no marketplace sellers)
        """

        # assume new design
        # _owned_from_script() may throw exception if extraction fails
        # (causing the service to return None for "owned")
        try:
            marketplace_new = self._marketplace_from_script()
        except Exception:
            marketplace_new = None

        if marketplace_new is None:
            # try to extract assuming old page structure
            return self._marketplace_meta_from_tree()

        return marketplace_new

    def _marketplace_sellers(self):
        """Extracts list of marketplace sellers for this product
        Works for both old and new page version
        Returns:
            list of strings representing marketplace sellers,
            or None if none found / not relevant
        """

        # assume new page version
        try:
            sellers = self._marketplace_sellers_from_script()
            # filter out walmart
            sellers = filter(lambda s: s!="Walmart.com", sellers)
            return sellers if sellers else None
        except:
            sellers = None

        if not sellers:
            # assume old page version
            sellers = self._seller_meta_from_tree().keys()
            # filter out walmart
            sellers = filter(lambda s: s!="Walmart.com", sellers)
            return sellers if sellers else None

    def _marketplace_out_of_stock(self):
        """Extracts info on whether currently unavailable from any marketplace seller - binary
        Uses functions that work on both old page design and new design.
        Will choose whichever gives results.
        Returns:
            1/0
        """
        if self._marketplace() == 1:
            if self._in_stock() == 0:
                return 1
            else:
                return 0

        return None

    def _in_stock(self):
        """Extracts info on whether product is available to be
        bought on the site, from any seller (marketplace or owned).
        Works on both old and new page design
        Returns:
            1/0 (available/not available)
        """

        # assume new page version
        try:
            in_stock_new = self._in_stock_from_script()
            return in_stock_new
        except:
            in_stock_new = None

        # assume old page design
        if not in_stock_new:
            in_stock_old = self._in_stock_old()

        return in_stock_old

    def _owned_out_of_stock(self):
        """Extracts whether product is owned and out of stock.
        Works on both old and new page version.
        Returns 1/0
        """

        owned = self._owned()
        in_stock = self._in_stock()

        if owned==1 and in_stock==0:
            return 1
        else:
            return 0

    def _site_online(self):
        """Extracts whether the item is sold by the site and delivered directly
        Works on both old and new page version.
        Returns 1/0
        """

        # TODO: what to do when there is no 'marketplaceOptions'?
        #       e.g. http://www.walmart.com/ip/23149039
        try:
            #       new design
            if not self.js_entry_function_body:
                pinfo_dict = self._extract_productinfo_json_from_jsfunction_body_new()
            else:
                pinfo_dict = self.js_entry_function_body

            marketplace_seller_info = pinfo_dict['buyingOptions']['marketplaceOptions']

            if pinfo_dict["buyingOptions"]["seller"]["walmartOnline"]:
                return 1
        except Exception:
            self.load_page_in_phantom()
            onlinePriceLabel_style = (self.driver.find_element(By.XPATH, "//div[@id='onlinePriceLabel']")).get_attribute("style").strip()

            if "display: block;" in onlinePriceLabel_style or "display: none;" not in onlinePriceLabel_style:
                return 1
            '''
            #       old design
            productinfo = self._extract_productinfo_json_from_jsfunction_body_old()

            if productinfo["isInStock"] and not productinfo["isRunout"]:
                A = "Instock";

            if productinfo["isInStock"] and productinfo["isRunout"]:
                A = "InstockRunout";

            if not productinfo["isInStock"] and not productinfo["canAddtoCart"]:
                A = "OutOfStock";

            if productinfo["isEmailMe"]:
                A = "EmailMe";

            if productinfo["isPreOrder"]:
                A = "PreorderInstock";

            if productinfo["isPreOrderOOS"]:
                A = "PreorderOutOfStock";

            if productinfo["isComingSoon"]:
                A = "ComingSoon";

            if not productinfo["isDisplayable"]:
                A = "OutOfStock";

            if A == "Instock":
                if productinfo["isInStock"]:
                    return 1

                if productinfo["isInStore"] and not productinfo["isInStock"]:
                    return 1

            if A == "OutOfStock":
                return 1

            if A == "PreorderInstock":
                return 1

            if A == "InstockRunout":
                return 1

            if A == "EmailMe":
                return 1

            if A == "ComingSoon":
                return 1

            if A == "PreorderOutOfStock":
                return 1
            '''
        return 0

    def _site_online_out_of_stock(self):
        """Extracts whether currently unavailable from the site - binary
        Works on both old and new page version.
        Returns 1/0
        """

        if self._site_online():
            try:
                site_online_out_of_stock = self.tree_html.xpath("//meta[@itemprop='availability']/@content")[0]

                if "InStock" in site_online_out_of_stock:
                    return 0
                elif "OutOfStock" in site_online_out_of_stock:
                    return 1
            except Exception:
                pass

        return None

    def _version(self):
        """Determines if walmart page being read (and version of extractor functions
            being used) is old or new design.
        Returns:
            "Walmart v1" for old design
            "Walmart v2" for new design
        """

        # using the "keywords" tag to distinguish between page versions.
        # In old version, it was capitalized, in new version it's not
        if self.tree_html.xpath("//meta[@name='keywords']/@content"):
            return "Walmart v2"
        if self.tree_html.xpath("//meta[@name='Keywords']/@content"):
            return "Walmart v1"

        # we could not decide
        return None


    def  _ingredients(self):
        # list of ingredients - list of strings
        ingr=self.tree_html.xpath("//section[contains(@class,'ingredients')]/p[2]//text()")
        if len(ingr) > 0:
            res = []
            w = ''
            br = 0
            for s in ingr[0]:
                if s == "," and br == 0:
                    if w != "":
                        res.append(w.strip())
                    w = ""
                elif s == "[" or s == "(":
                    w += s
                    br = 1
                elif s == "]" or s == ")":
                    w += s
                    br = 0
                else:
                    w += s
            if w != '':
                res.append(w.strip())
            self.ing_count = len(res)
            return res
        self.ing_count = None
        return None


    def  _ingredient_count(self):
        # number of ingredients - integer
        return  self.ing_count

    def  _nutrition_facts(self):
        # nutrition facts - list of tuples ((key,value) pairs, values could be dictionaries)
        # containing nutrition facts
        res=[]
        nutr=self.tree_html.xpath("//div[@class='nutrition-section']//div[@class='serving']//div")
        for i, n in enumerate(nutr):
            nt = n.text_content()
            if i == 0:
                res.append([nt[0:13].strip(),nt[13:].strip()])
            if i == 1:
                res.append([nt[0:22].strip(),nt[22:].strip()])
        nutr=self.tree_html.xpath("//div[@class='nutrition-section']//table[contains(@class,'table')]//tr")
        _digits = re.compile('\d')
        for i, n in enumerate(nutr):
            pr = n.xpath(".//*[self::th or self::td]//text()")
            if len(pr)>0 and pr[0].find("B6") < 0:
                m = _digits.search(pr[0])
                if m != None and m.start() > 1:
                    p0 = pr[0][0:m.start()-1]
                    p1 = pr[0][m.start()-1:]
                    pr[0] = p1.strip()
                    pr.insert(0,p0.strip())
            if len(pr)==2 :
                res.append(pr)
            elif len(pr)==3 and pr[2].strip()!="":
                res.append([pr[0].strip(),{"absolute":pr[1].strip(),"relative":pr[2].strip()}])
            elif len(pr) == 3 and pr[2].strip() == "":
                res.append([pr[0].strip(),pr[1].strip()])
        if len(res) > 0:
            self.nutr_count = len(res)
            return res
        self.nutr_count = None
        return None


    def  _nutrition_fact_count(self):
        # number of nutrition facts (of elements in the nutrition_facts list) - integer
        return self.nutr_count


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
        "meta_tags": _meta_tags,\
        "meta_tag_count": _meta_tag_count,\
        "brand" : _meta_brand_from_tree, \
        "description" : _short_description_wrapper, \
        # TODO: check if descriptions work right
        "long_description" : _long_description_wrapper, \
        "ingredients": _ingredients, \
        "ingredient_count": _ingredient_count, \
        "nutrition_facts": _nutrition_facts, \
        "nutrition_fact_count": _nutrition_fact_count, \
        "price" : _price_from_tree, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "htags" : _htags_from_tree, \
        "model" : _model_from_tree, \
        "model_meta" : _meta_model_from_tree, \
        "features" : _features_from_tree, \
        "feature_count" : _nr_features_from_tree, \
        "title_seo" : _title_from_tree, \
        # TODO: I think this causes the method to be called twice and is inoptimal
        "product_title" : _product_name_from_tree, \
        "owned": _owned, \
        "owned_out_of_stock": _owned_out_of_stock, \
        "in_stores" : _in_stores, \
        "in_stores_out_of_stock" : _in_stores_out_of_stock,
        "in_stores_only" : _in_stores_only, \
        "marketplace": _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_out_of_stock": _marketplace_out_of_stock, \
        "in_stock": _in_stock, \
        "site_online": _site_online, \
        "site_online_out_of_stock": _site_online_out_of_stock, \
        "review_count": _nr_reviews, \
        "average_review": _avg_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \
        # video needs both page source and separate requests
        "video_count" : _product_has_video, \
        "video_urls" : _video_urls, \
        "webcollage" : _product_has_webcollage, \
        "sellpoints" : _product_has_sellpoints, \

        "image_count" : _image_count, \
        "image_urls" : _image_urls, \

        "categories" : _categories_hierarchy, \
        "category_name" : _category, \

        "scraper" : _version, \
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
        "pdf_count" : _pdf_count, \
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
