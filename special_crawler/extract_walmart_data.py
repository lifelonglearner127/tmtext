#!/usr/bin/python

import re
import sys
import json

from lxml import html, etree
import lxml
import lxml.html
import requests
import random
import yaml

from extract_data import Scraper
from compare_images import compare_images
from spiders_shared_code.walmart_variants import WalmartVariants

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

            BASE_URL_REQ_WEBCOLLAGE (string):
            BASE_URL_PDFREQ_WEBCOLLAGE (string):
            BASE_URL_REVIEWSREQ (string):   strings containing necessary hardcoded URLs for extracting walmart
                                            videos, pdfs and reviews
    """

    # base URL for request containing video URL from webcollage
    BASE_URL_VIDEOREQ_WEBCOLLAGE = "http://json.webcollage.net/apps/json/walmart?callback=jsonCallback&environment-id=live&cpi="
    # base URL for request containing video URL from webcollage
    BASE_URL_VIDEOREQ_WEBCOLLAGE_NEW = "http://www.walmart-content.com/product/idml/video/%s/WebcollageVideos"
    # base URL for request containing video URL from sellpoints
    BASE_URL_VIDEOREQ_SELLPOINTS = "http://www.walmart.com/product/idml/video/%s/SellPointsVideos"
    # base URL for request containing video URL from sellpoints
    BASE_URL_VIDEOREQ_SELLPOINTS_NEW = "http://www.walmart-content.com/product/idml/video/%s/SellPointsVideos"
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

        # whether webcollage 360 view were extracted
        self.extracted_webcollage_360_view = False
        # whether product has webcollage 360 view
        self.has_webcollage_360_view = False

        # whether webcollage emc view were extracted
        self.extracted_webcollage_emc_view = False
        # whether product has webcollage emc view
        self.has_webcollage_emc_view = False

        # whether webcollage video view were extracted
        self.extracted_webcollage_video_view = False
        # whether product has webcollage video view
        self.has_webcollage_video_view = False

        # whether webcollage pdf view were extracted
        self.extracted_webcollage_pdf = False
        # whether product has webcollage pdf view
        self.has_webcollage_pdf = False

        # whether webcollage product tour view were extracted
        self.extracted_webcollage_product_tour_view = False
        # whether product has webcollage product tour view
        self.has_webcollage_product_tour_view = False

        # javascript function found in a script tag
        # containing various info on the product.
        # Currently used for seller info (but useful for others as well)
        self.product_info_json = None

        self.failure_type = None

        self.review_json = None
        self.review_list = None
        self.is_review_checked = False
        self.is_legacy_review = False
        self.wv = WalmartVariants()
        self.is_bundle_product = False

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
            self.wv.setupCH(self.tree_html)
        except:
            pass

        self._failure_type()

        if self.failure_type:
            self.ERROR_RESPONSE["failure_type"] = self.failure_type

            return True

        return False

    def _extract_product_id(self):
        """Extracts product id of walmart product from its URL
        Returns:
            string containing only product id
        """
        if self._version() == "Walmart v1":
            product_id = self.product_page_url.split('/')[-1]
            return product_id
        elif self._version() == "Walmart v2":
            product_id = self.product_page_url.split('/')[-1]
            return product_id

        return None

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
            has_video = any(map(lambda el: "video')" in el, elements_onclick))

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

        if self._version() == "Walmart v2" and self.is_bundle_product:
            return

        # if there is no video button, return no video
        if not self._has_video_button():
            return

        self.video_urls = []

        if self._version() == "Walmart v1" and not self.tree_html.xpath("""//script[@type='text/javascript' and contains(text(), 'productVideoContent')]/text()"""):
            self.video_urls = None
            return

        if self._version() == "Walmart v2":
            emc_link = self.tree_html.xpath("//iframe[contains(@class,'js-marketing-content-iframe')]/@src")

            if emc_link:
                emc_link = "http:" + emc_link[0]
#                contents = requests.get(emc_link).text
                h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
                s = requests.Session()
                a = requests.adapters.HTTPAdapter(max_retries=3)
                b = requests.adapters.HTTPAdapter(max_retries=3)
                s.mount('http://', a)
                s.mount('https://', b)
                contents = s.get(emc_link, headers=h, timeout=5).text
                tree = html.fromstring(contents)
                wcobj_links = tree.xpath("//img[contains(@class, 'wc-media')]/@wcobj")

                if wcobj_links:
                    for wcobj_link in wcobj_links:
                        if wcobj_link.endswith(".flv"):
                            self.video_urls.append(wcobj_link)

        # webcollage video info
        request_url = self.BASE_URL_VIDEOREQ_WEBCOLLAGE_NEW % self._extract_product_id()
#        response_text = urllib.urlopen(request_url).read()
        h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        b = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        s.mount('https://', b)
        response_text = s.get(request_url, headers=h, timeout=5).text
        tree = html.fromstring(response_text)

        if tree.xpath("//div[@id='iframe-video-content']") and \
                tree.xpath("//table[contains(@class, 'wc-gallery-table')]/@data-resources-base"):
            video_base_path = tree.xpath("//table[contains(@class, 'wc-gallery-table')]/@data-resources-base")[0]
            sIndex = 0
            eIndex = 0

            while sIndex >= 0:
                sIndex = response_text.find('{"videos":[', sIndex)
                eIndex = response_text.find('}]}', sIndex) + 3

                if sIndex < 0:
                    break

                jsonVideo = response_text[sIndex:eIndex]
                jsonVideo = json.loads(jsonVideo)

                if len(jsonVideo['videos']) > 0:
                    for video_info in jsonVideo['videos']:
                        self.video_urls.append(video_base_path + video_info['src']['src'])

                sIndex = eIndex

        # check sellpoints media if webcollage media doesn't exist
        request_url = self.BASE_URL_VIDEOREQ_SELLPOINTS % self._extract_product_id()
        #TODO: handle errors
#        response_text = urllib.urlopen(request_url).read()
        h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        b = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        s.mount('https://', b)
        response_text = s.get(request_url, headers=h, timeout=5).text
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

        # check sellpoints media if webcollage media doesn't exist
        request_url = self.BASE_URL_VIDEOREQ_SELLPOINTS_NEW % self._extract_product_id()
        # TODO: handle errors
#        response_text = urllib.urlopen(request_url).read()
        h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        b = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        s.mount('https://', b)
        response_text = s.get(request_url, headers=h, timeout=5).text
        tree = html.fromstring(response_text)
        if tree.xpath("//div[@id='iframe-video-content']//div[@id='player-holder']"):
            self.has_video = True
            self.has_sellpoints_media = True

        if len(self.video_urls) == 0:
            if self.tree_html.xpath("//div[starts-with(@class,'js-idml-video-container')]"):
#                contents = requests.get("http://www.walmart.com/product/idml/video/" +
#                                        str(self._extract_product_id()) + "/WebcollageVideos").text
                h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
                s = requests.Session()
                a = requests.adapters.HTTPAdapter(max_retries=3)
                b = requests.adapters.HTTPAdapter(max_retries=3)
                s.mount('http://', a)
                s.mount('https://', b)
                contents = s.get("http://www.walmart.com/product/idml/video/" +
                                 str(self._extract_product_id()) + "/WebcollageVideos", headers=h, timeout=5).text

                if not contents:
                    self.video_urls = None
                    return

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

    def _wc_360(self):
        """Return 360view existence for a given walmart product in new walmart design
        Returns:
            1 if 360view exists
            or 0 if none found
        """

        self.extracted_webcollage_360_view = True

        if self.is_bundle_product:
            return 0

#        contents = requests.get("http://www.walmart-content.com/product/idml/video/" +
#                                str(self._extract_product_id()) + "/Webcollage360View").text
        h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        b = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        s.mount('https://', b)
        contents = s.get("http://www.walmart-content.com/product/idml/video/" +
                         str(self._extract_product_id()) + "/Webcollage360View", headers=h, timeout=5).text

        tree = html.fromstring(contents)
        existance_360view = tree.xpath("//div[@class='wc-360']")

        if not existance_360view:
            return 0
        else:
            if self._version() == "Walmart v1" and not self.tree_html.xpath("""//script[@type='text/javascript' and contains(text(), 'productVideoContent')]/text()""") and not self.tree_html.xpath("//li[contains(@class, 'sp95_BTN_btn_360degree')]"):
                return 0

            self.has_webcollage_360_view = True
            return 1

    def _wc_emc(self):
        """Return EMC (Extended Manufacturer Content) existence for a given walmart product in new walmart design
        Returns:
            1 if EMC exists
            or 0 if none found
        """
        self.extracted_webcollage_emc_view = True

        if self.is_bundle_product:
            return 0

        if self._version() == "Walmart v2":
            emc = self.tree_html.xpath("//iframe[contains(@class,'js-marketing-content-iframe')]")

        if self._version() == "Walmart v1":
            emc = self.tree_html.xpath("//div[@id='manufacturer-content']")

        if not emc:
            return 0
        else:
            self.has_webcollage_emc_view = True
            return 1

    def _wc_video(self):
        """Return video existence for a given walmart product in new walmart design
        Returns:
            1 if video exists
            or 0 if none found
        """

        self.extracted_webcollage_video_view = True

        if self.is_bundle_product:
            return 0

#        contents = requests.get("http://www.walmart-content.com/product/idml/video/" +
#                                str(self._extract_product_id()) + "/WebcollageVideos").text
        h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        b = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        s.mount('https://', b)
        contents = s.get("http://www.walmart-content.com/product/idml/video/" +
                         str(self._extract_product_id()) + "/WebcollageVideos", headers=h, timeout=5).text

        tree = html.fromstring(contents)
        existance_webcollage_video = tree.xpath("//div[@class='wc-fragment']")

        if not existance_webcollage_video:
            return 0
        else:
            if self._version() == "Walmart v1" and not self.tree_html.xpath("""//script[@type='text/javascript' and contains(text(), 'productVideoContent')]/text()"""):
                return 0

            self.has_webcollage_video_view = True
            return 1

    def _wc_pdf(self):
        """Return pdf existence for a given walmart product in new walmart design
        Returns:
            1 if pdf exists
            or 0 if none found
        """

        self.extracted_webcollage_pdf = True

        if self.is_bundle_product:
            return 0

        pdf_urls = self._pdf_urls()

        if pdf_urls:
            for item in pdf_urls:
                if "webcollage" in item.lower():
                    self.has_webcollage_pdf = True
                    return 1

        return 0

    def _wc_prodtour(self):
        """Return product tour existence for a given walmart product in new walmart design
        Returns:
            1 if product tour exists
            or 0 if none found
        """

        self.extracted_webcollage_product_tour_view = True

        if self.is_bundle_product:
            return 0

#        contents = requests.get("http://www.walmart-content.com/product/idml/video/" +
#                                str(self._extract_product_id()) + "/WebcollageInteractiveTour").text
        h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        b = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        s.mount('https://', b)
        contents = s.get("http://www.walmart-content.com/product/idml/video/" +
                         str(self._extract_product_id()) + "/WebcollageInteractiveTour", headers=h, timeout=5).text

        tree = html.fromstring(contents)
        existance_product_tour = tree.xpath("//div[contains(@class, 'wc-aplus-body')]")

        if not existance_product_tour:
            return 0
        else:
            if self._version() == "Walmart v1" and not self.tree_html.xpath("""//script[@type='text/javascript' and contains(text(), 'productVideoContent')]/text()"""):
                return 0

            self.has_webcollage_product_tour_view = True
            return 1

    def _flixmedia(self):
        if "media.flix" in etree.tostring(self.tree_html):
            return 1
        else:
            return 0

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

        if self._version() == "Walmart v1":
            """Extracts pdf URL for a given walmart product
            and puts them in instance variable.
            """

            pdf_links = self.tree_html.xpath("//a[contains(@href,'.pdf')]/@href")
            for item in pdf_links:
                if item.strip().endswith(".pdf"):
                    self.pdf_urls.append("http://www.walmart.com" + item.strip()) if item.strip() not in self.pdf_urls else None

            request_url = self.BASE_URL_PDFREQ_WEBCOLLAGE + self._extract_product_id()

#            response_text = urllib.urlopen(request_url).read().decode('string-escape')
            h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries=3)
            b = requests.adapters.HTTPAdapter(max_retries=3)
            s.mount('http://', a)
            s.mount('https://', b)
            response_text = s.get(request_url, headers=h, timeout=5).text.decode('string-escape')

            pdf_url_candidates = re.findall('(?<=")http[^"]*media\.webcollage\.net[^"]*[^"]+\.[pP][dD][fF](?=")',
                                            response_text)
            if pdf_url_candidates:
                # remove escapes
                for pdf_url in pdf_url_candidates:
                    pdf_url = re.sub('\\\\', "", pdf_url)
                    self.has_webcollage_media = True
                    self.has_pdf = True
                    self.pdf_urls.append(pdf_url)

        if self._version() == "Walmart v2":
            pdf_links = self.tree_html.xpath("//a[contains(@href,'.pdf')]/@href")
            for item in pdf_links:
                if item.strip().endswith(".pdf"):
                    self.pdf_urls.append(item.strip()) if item.strip() not in self.pdf_urls else None

            if self.tree_html.xpath("//iframe[contains(@class, 'js-marketing-content-iframe')]/@src"):
                request_url = self.tree_html.xpath("//iframe[contains(@class, 'js-marketing-content-iframe')]/@src")[0]
                request_url = "http:" + request_url.strip()

#                response_text = urllib.urlopen(request_url).read().decode('string-escape')
                h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
                s = requests.Session()
                a = requests.adapters.HTTPAdapter(max_retries=3)
                b = requests.adapters.HTTPAdapter(max_retries=3)
                s.mount('http://', a)
                s.mount('https://', b)
                response_text = s.get(request_url, headers=h, timeout=5).text.decode('string-escape')

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
        h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        request_url = self.BASE_URL_REVIEWSREQ.format(self._extract_product_id())
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        b = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        s.mount('https://', b)
        content = s.get(request_url, headers=h, timeout=5).text

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

        if not self.extracted_webcollage_360_view:
            self._wc_360()

        if not self.extracted_webcollage_product_tour_view:
            self._wc_prodtour()

        if not self.extracted_webcollage_pdf:
            self._wc_pdf()

        if not self.extracted_webcollage_emc_view:
            self._wc_emc()

        if not self.extracted_webcollage_video_view:
            self._wc_video()

        if self.has_webcollage_product_tour_view or self.has_webcollage_pdf or self.has_webcollage_video_view or self.has_webcollage_emc_view or self.has_webcollage_360_view:
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

    def _video_count(self):
        """Whether product has video
        To be replaced with function that actually counts
        number of videos for this product
        Returns:
            1 if product has video
            0 if product doesn't have video
        """

        if not self.extracted_video_urls:
            self._extract_video_urls()

        if not self.video_urls:
            if self.has_video:
                return 1
            else:
                return 0
        else:
            return len(self.video_urls)

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

        return product_name_node[0].text_content().strip()

    # extract walmart no
    def _site_id(self):
        if self._version() == "Walmart v2" and self.is_bundle_product:
            product_info_json = self._extract_product_info_json()
            return product_info_json["analyticsData"]["productId"]
        else:
            return self.tree_html.xpath("//tr[@class='js-product-specs-row']/td[text() = 'Walmart No.:']/following-sibling::td/text()")[0].strip()

    # extract walmart no
    def _walmart_no(self):
        if self._version() == "Walmart v2" and self.is_bundle_product:
            product_info_json = self._extract_product_info_json()
            return product_info_json["analyticsData"]["productId"]
        else:
            return self.tree_html.xpath("//tr[@class='js-product-specs-row']/td[text() = 'Walmart No.:']/following-sibling::td/text()")[0].strip()

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

        if self._version() == "Walmart v1":
            return self.tree_html.xpath("//meta[@itemprop='brand']/@content")[0]

        if self._version() == "Walmart v2":
            if self.is_bundle_product:
                product_info_json = self._extract_product_info_json()
                return product_info_json["analyticsData"]["brand"]
            else:
                return self.tree_html.xpath("//span[@itemprop='brand']/text()")[0]

        return None

    # extract product short description from its product page tree
    # ! may throw exception if not found
    def _short_description_from_tree(self):
        """Extracts product short description
        Returns:
            string containing the text content of the product's description, or None
        """

        if self._version() == "Walmart v2" and self.is_bundle_product:
            if not self._long_description():
                try:
                    return self.tree_html.xpath("//*[starts-with(@class, 'product-about js-about')]/div[contains(@class, 'js-ellipsis')]")[0].text_content().strip()
                except:
                    return None

        description_elements = self.tree_html.xpath("//*[starts-with(@class, 'product-about js-about')]"
                                                    "/div[contains(@class, 'js-ellipsis')]")

        short_description = ""
        short_description_end_index = -1
        sub_description = ""

        if description_elements:
            description_elements = description_elements[0]

            if description_elements.getparent().getparent().getparent().tag == "td":
                return None

            for description_element in description_elements:
                sub_description = lxml.html.tostring(description_element)

                if "<b>" in sub_description or "<ul>" in sub_description or "<dl>" in sub_description or "<li>" in sub_description or '<section class="product-about js-ingredients health-about">' in sub_description:
                    innerText = ""

                    try:
                        tree = html.fromstring(short_description)
                        innerText = tree.xpath("//text()")
                    except Exception:
                        pass

                    if not innerText:
                        short_description = ""

                    if "<b>" in sub_description:
                        short_description_end_index = sub_description.find("<b>")
                    elif "<ul>" in sub_description:
                        short_description_end_index = sub_description.find("<ul>")
                    elif "<dl>" in sub_description:
                        short_description_end_index = sub_description.find("<dl>")
                    elif "<li>" in sub_description:
                        short_description_end_index = sub_description.find("<li>")
                    elif '<section class="product-about js-ingredients health-about">' in sub_description:
                        short_description_end_index = sub_description.find('<section class="product-about js-ingredients health-about">')

                    break

                short_description += sub_description

            if short_description_end_index > 0:
                short_description = sub_description[:short_description_end_index] + short_description

            # if no short description, return the long description
            if not short_description.strip():
                return None
        else:
            # try to extract from old page structure - in case walmart is
            # returning an old type of page
            if not short_description:
                short_description = " ".join(self.tree_html.xpath("//span[@class='ql-details-short-desc']//text()")).strip()

            long_description_existence = self.tree_html.xpath('//*[contains(@class, "ItemSectionContent")]'
                                                              '//*[contains(@itemprop, "description")]//li')

            if not short_description and not long_description_existence:
                _desc = self.tree_html.xpath(
                    '//*[contains(@class, "ItemSectionContent")]'
                    '//*[contains(@itemprop, "description")]//text()'
                )
                if _desc:
                    short_description = " ".join(_desc).strip()

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

        return self._exclude_javascript_from_description(short_description)

    def _exclude_javascript_from_description(self, description):
        description = re.subn(r'<(script).*?</\1>(?s)', '', description)[0]
#        description = re.sub(r"<script type=.+</script>", "", description)
#       description = re.sub(r"<script>.+</script>", "", description)
#
        return description

    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description_from_tree_old(self):
        """Extracts product long description.
        Works on old design for walmart pages.
        Returns:
            string containing the text content of the product's description, or None
        """

        li_long_description_existence = self.tree_html.xpath('//*[contains(@class, "ItemSectionContent")]'
                                                  '//*[contains(@itemprop, "description")]//li')

        p_long_description_existence = None

        if len(self.tree_html.xpath("//div[@itemprop='description']/div")) > 0 and self.tree_html.xpath("//div[@itemprop='description']/div")[1].xpath(".//p"):
            p_long_description_existence = self.tree_html.xpath("//div[@itemprop='description']/div")[1].xpath(".//p")

        if not li_long_description_existence and not p_long_description_existence:
            return None

        long_description_elements = self.tree_html.xpath("//div[@itemprop='description']/div")[1]
        full_description = ""

        for description_element in long_description_elements:
            full_description += lxml.html.tostring(description_element)

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
                                                    "/div[contains(@class, 'js-ellipsis')]")
        full_description = ""

        if description_elements:
            description_elements = description_elements[0]

            if description_elements.getparent().getparent().getparent().tag == "td":
                return None

            long_description_start = False
            ingredients_description = False
            long_description_start_index = -2

            for description_element in description_elements:
                if (not long_description_start and "<b>" in lxml.html.tostring(description_element)) or \
                        (not long_description_start and ("<ul>" in lxml.html.tostring(description_element) or "<dl>" in lxml.html.tostring(description_element) or "<li>" in lxml.html.tostring(description_element))):
                    long_description_start = True

                    sub_description = lxml.html.tostring(description_element)

                    if long_description_start_index == -2:
                        if "<b>" in lxml.html.tostring(description_element):
                            long_description_start_index = sub_description.find("<b>")
                        elif "<ul>" in lxml.html.tostring(description_element):
                            long_description_start_index = sub_description.find("<ul>")
                        elif "<dl>" in lxml.html.tostring(description_element):
                            long_description_start_index = sub_description.find("<dl>")
                        elif "<li>" in lxml.html.tostring(description_element):
                            long_description_start_index = sub_description.find("<li>")

                if "<strong>Ingredients:" in lxml.html.tostring(description_element) or "<b>Ingredients:" in \
                        lxml.html.tostring(description_element):
                    ingredients_description = True
                else:
                    ingredients_description = False

                if long_description_start:
                    sub_description = lxml.html.tostring(description_element)

                    if not ingredients_description:
                        if long_description_start_index > 0:
                            full_description += sub_description[long_description_start_index:]
                            long_description_start_index = -1
                        else:
                            full_description += sub_description
                    else:
                        description_start_index = sub_description.find('<section class="product-about js-ingredients health-about">')
                        description_end_index = sub_description.find("</section>", description_start_index) + 10
                        full_description += (sub_description[:description_start_index] + sub_description[description_end_index:])

        if self.product_page_url[self.product_page_url.rfind("/") + 1:].isnumeric():
            url = "http://www.walmart-content.com/product/idml/emc/" + \
                  self.product_page_url[self.product_page_url.rfind("/") + 1:]
#            contents = requests.get(url).text
            h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries=3)
            b = requests.adapters.HTTPAdapter(max_retries=3)
            s.mount('http://', a)
            s.mount('https://', b)
            contents = s.get(url, headers=h, timeout=5).text

            tree = html.fromstring(contents)
            description_elements = tree.xpath("//div[@id='js-marketing-content']//*")

            long_description_start = False

            for description_element in description_elements:
                if not long_description_start and "<h2>Product Description</h2>" in \
                        lxml.html.tostring(description_element):
                    long_description_start = True

                if long_description_start and "<h2>Product Description</h2>" not in lxml.html.tostring(description_element) \
                        and (description_element.tag == "p" or description_element.tag == "h2" or (description_element.tag == "ul" and not description_element.get("class"))):
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
        long_description = self._long_description()

        return self._exclude_javascript_from_description(long_description)

    def _shelf_description(self):
        shelf_description_li_list = self.tree_html.xpath("//div[@class='product-short-description module']/li")
        shelf_description = ""

        if shelf_description_li_list:
            for li in shelf_description_li_list:
                shelf_description = shelf_description + html.tostring(li)

            return shelf_description

        return None

    def _variants(self):
        return self.wv._variants()

    def _swatches(self):
        return self.wv._swatches()

    def _related_product_urls(self):
        page_raw_text = lxml.html.tostring(self.tree_html)
        startIndex = page_raw_text.find('"variantProducts":') + len('"variantProducts":')

        if startIndex == -1:
            return None

        endIndex = page_raw_text.find(',"primaryProductId":', startIndex)

        json_text = page_raw_text[startIndex:endIndex]
        variants_json = json.loads(json_text)
        item_id_list = []

        for item in variants_json:
            item_id_list.append(item["buyingOptions"]["usItemId"])

        item_id_list = list(set(item_id_list))

        related_product_urls = []
        url = self.product_page_url

        for variant_id in item_id_list:
            related_product_url = url[:url.rfind("/")] + "/" + str(variant_id)
            related_product_urls.append(related_product_url)

        related_product_urls.remove(self.product_page_url)

        if related_product_urls:
            return related_product_urls

        return None

    def _style(self):
        return self.wv._style()

    # extract product price from its product product page tree
    def _price_from_tree(self):
        """Extracts product price
        Returns:
            string containing the product price, with decimals, no currency
        """
        if self._version() == "Walmart v1":
            try:
                if self.is_bundle_product:
                    return "$" + re.findall("\d+.\d+", self.tree_html.xpath("//div[@class='PricingInfo']")[0].text_content())[0]

                body_raw = "" . join(self.tree_html.xpath("//form[@name='SelectProductForm']//script/text()")).strip()
                body_clean = re.sub("\n", " ", body_raw)
                body_jpart = re.findall("\{\ itemId.*?\}\s*\] }", body_clean)[0]
                sIndex = body_jpart.find("price:") + len("price:") + 1
                eIndex = body_jpart.find("',", sIndex)

                if "camelPrice" not in body_jpart[sIndex:eIndex] and not self._in_stock():
                    return "out of stock - no price given"

                if "camelPrice" not in body_jpart[sIndex:eIndex] and self._in_stores_only():
                    return "in stores only - no online price"

                try:
                    return self.tree_html.xpath("//span[contains(@class, 'camelPrice')]")[0].text_content().strip()
                except:
                    pass

                try:
                    script_bodies = self.tree_html.xpath("//script/text()")
                    price_html = None

                    for script in script_bodies:
                        if "var DefaultItem =" in script or "var DefaultItemWidget =" in script:
                            price_html = script
                            break

                    if not price_html:
                        raise Exception

                    start_index = end_index = 0

                    start_index = price_html.find(",\nprice: '") + len(",\nprice: '")
                    end_index = price_html.find("',\nprice4SAC:")
                    price_html = price_html[start_index:end_index]
                    price_html = html.fromstring(price_html)
                    price = price_html.text_content()
                    price = re.findall("\$\d+.\d+", price_html.text_content())

                    if not price:
                        raise Exception

                    return price[0]
                except:
                    pass

                return None
            except:
                pass

        if self._version() == "Walmart v2":
            try:
                if self.is_bundle_product:
                    product_info_json = self._extract_product_info_json()

                    if product_info_json["buyingOptions"]["maxPrice"]["currencyAmount"] == product_info_json["buyingOptions"]["minPrice"]["currencyAmount"]:
                        return "${0}".format(product_info_json["buyingOptions"]["minPrice"]["currencyAmount"])
                    elif product_info_json["buyingOptions"]["maxPrice"]["currencyAmount"] > product_info_json["buyingOptions"]["minPrice"]["currencyAmount"]:
                        return "${0}-${1}".format(product_info_json["buyingOptions"]["minPrice"]["currencyAmount"], product_info_json["buyingOptions"]["maxPrice"]["currencyAmount"])
                    else:
                        return "${0}".format(product_info_json["buyingOptions"]["minPrice"]["currencyAmount"])
                else:
                    price = self.tree_html.xpath("//div[@itemprop='price']")[0].text_content().strip()

                    if price:
                        return price
                    else:
                        if not self._in_stock():
                            return "out of stock - no price given"
                        else:
                            return None
            except:
                pass

            try:
                return self.product_info_json["buyingOptions"]["price"]["currencyUnitSymbol"] + str(self.product_info_json["buyingOptions"]["price"]["currencyAmount"])
            except:
                pass

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
            price = re.findall("\d+.\d+", price_info)
            return price[0]

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
            if self._version() == "Walmart v1":
                meta_currency = self.tree_html.xpath("//meta[@itemprop='priceCurrency']/@content")[0]
                return meta_currency

            if self._version() == "Walmart v2":
                if self.is_bundle_product:
                    return "USD"
                else:
                    product_info_json = self._extract_product_info_json()

                    return product_info_json["buyingOptions"]["price"]["currencyUnit"]

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
        """Extracts product model.
        Works for both old and new walmart page structure.
        Returns:
            string containing the product model, or None
        """

        # extract features table for new page version:
        # might cause exception if table node not found (and premature exit of function)
        try:
            table_node = self.tree_html.xpath("//div[contains(@class, 'specs-table')]/table")[0]
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
        if self._version() == "Walmart v2":
            if self.is_bundle_product:
                product_info_json = self._extract_product_info_json()
                return product_info_json["analyticsData"]["catPath"].split("/")
            else:
                categories_list = self.tree_html.xpath("//li[@class='breadcrumb']/a/span/text()")
                if categories_list:
                    return categories_list

        if self._version() == "Walmart v1":
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
        if self._version() == "Walmart v2":
            if self.is_bundle_product:
                return self._categories_hierarchy()[-1]
            else:
                try:
                    category = self.tree_html.xpath("//li[@class='breadcrumb']/a/span/text()")[-1]
                except Exception:
                    category = None

                if category:
                    return category

        if self._version() == "Walmart v1":
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
        rows = self.tree_html.xpath("//div[contains(@class, 'js-specs-table')]/table//tr")
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
        rows = self.tree_html.xpath("//div[contains(@class, 'js-specs-table')]/table//tr")
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
        if self._version() == "Walmart v1":
            return self._find_between(html.tostring(self.tree_html), "upc: '", "'").strip()

        if self._version() == "Walmart v2":
            if self.is_bundle_product:
                product_info_json = self._extract_product_info_json()
                return product_info_json["analyticsData"]["upc"]
            else:
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
        # seller_info['marketplace'] = 1 if (len(sellers.keys()) > 0 and any(sellers.values())) else 0
        seller_info['marketplace'] = 1 if len(sellers.keys()) > 0 else 0

        return seller_info

    def _average_review(self):
        if self._review_count() == 0:
            return None

        if self.is_legacy_review:
            average_review_str = self.tree_html.xpath("//div[@class='review-summary Grid']\
                //p[@class='heading-e']/text()")[0]
            average_review = re.search('reviews \| (.+?) out of ', average_review_str).group(1)
            average_review = float(average_review)

            return average_review

        average_review = round(float(self.review_json["jsonData"]["attributes"]["avgRating"]), 1)

        if str(average_review).split('.')[1] == '0':
            return int(average_review)
        else:
            return float(average_review)

    def _review_count(self):
        self._reviews()

        if self.is_legacy_review:
            nr_reviews = 0

            nr_reviews_str = self.tree_html.xpath("//span[@itemprop='ratingCount']/text()")

            if not nr_reviews_str:
                return 0

            nr_reviews = int(nr_reviews_str[0])

            return nr_reviews

        if not self.review_json:
            return 0

        return int(self.review_json["jsonData"]["attributes"]["numReviews"])

    def _max_review(self):
        if self._review_count() == 0:
            return None

        for i, review in enumerate(self.review_list):
            if review[1] > 0:
                return 5 - i

    def _min_review(self):
        if self._review_count() == 0:
            return None

        for i, review in enumerate(reversed(self.review_list)):
            if review[1] > 0:
                return i + 1

    def _reviews(self):
        if self.is_review_checked:
            return self.review_list

        self.is_review_checked = True

        if self._version() == "Walmart v1":
            og_url_id = self.tree_html.xpath("//meta[@property='og:url']/@content")[0]
            og_url_id = og_url_id[og_url_id.rfind("/") + 1:]
            h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries=3)
            b = requests.adapters.HTTPAdapter(max_retries=3)
            s.mount('http://', a)
            s.mount('https://', b)
            contents = s.get(self.BASE_URL_REVIEWSREQ.format(og_url_id), headers=h, timeout=5).text

            try:
                start_index = contents.find("webAnalyticsConfig:") + len("webAnalyticsConfig:")
                end_index = contents.find("}},", start_index) + 2

                self.review_json = contents[start_index:end_index]
                self.review_json = json.loads(self.review_json)
            except:
                self.review_json = None

            review_html = html.fromstring(re.search('"BVRRSecondaryRatingSummarySourceID":" (.+?)"},\ninitializers={', contents).group(1))
            reviews_by_mark = review_html.xpath("//*[contains(@class, 'BVRRHistAbsLabel')]/text()")
            reviews_by_mark = reviews_by_mark[:5]
            review_list = [[5 - i, int(re.findall('\d+', mark)[0])] for i, mark in enumerate(reviews_by_mark)]

            if review_list:
                self.review_list = review_list
                return review_list

        if self._version() == "Walmart v2":
            try:
                review_list = self.legacy_reviews_v2()
            except:
                pass

            if review_list:
                self.is_legacy_review = True
                self.review_list = review_list
                return review_list

        return None

    def legacy_reviews_v2(self):
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

    def _rollback(self):
        if self._version() == "Walmart v1":
            rollback = self.tree_html.xpath("//div[@class='ItemFlagRow']/img[@alt='Rollback']")
        elif self._version() == "Walmart v2":
            rollback = self.tree_html.xpath('//div[@class="js-product-offer-summary"]//'
                                            'span[contains(@class,"flag-rollback")]')

        if not rollback:
            return 0
        else:
            return 1

    def _no_longer_available(self):
        try:
            if "This Item is no longer available" in self.tree_html.xpath("//div[@class='prod-no-buying-option']/div[@class='heading-d']/text()")[0]:
                return True
        except:
            pass

        return False

    def _shipping(self):
        flag = 'not available'

        if self.tree_html.xpath('//meta[@name="Keywords"]'):
            if not flag in html.tostring(self.tree_html):
                return False
            else:
                return True
        else:
            shipping = self.tree_html.xpath(
                '//div[@class="product-no-fulfillment Grid-col '
                'u-size-6-12-l active"][1]/span/text()'
                '[contains(.,"not available")] |'
                '//span[@class="js-shipping-delivery-date-msg '
                'delivery-date-msg"]/text()[contains(., "Not available")]'
            )

            if len(shipping) > 0:
                return False
            else:
                return True

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
            if len(find) > 0:
                return self._qualify_image_urls(find)

        if self.tree_html.xpath("//link[@rel='image_src']/@href"):
            if self._no_image(self.tree_html.xpath("//link[@rel='image_src']/@href")[0]):
                return None
            else:
                return self.tree_html.xpath("//link[@rel='image_src']/@href")

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

        if self._version() == "Walmart v2" and self.is_bundle_product:
            return self.tree_html.xpath("//div[contains(@class, 'choice-hero-non-carousel')]//img/@src")
        else:
            def _fix_relative_url(relative_url):
                """Fixes relative image urls by prepending
                the domain. First checks if url is relative
                """

                if not relative_url.startswith("http"):
                    return "http://www.walmart.com" + relative_url
                else:
                    return relative_url

            if not self.product_info_json:
                pinfo_dict = self._extract_product_info_json()
            else:
                pinfo_dict = self.product_info_json

            images_carousel = []

            for item in pinfo_dict['imageAssets']:
                images_carousel.append(item['versions']['hero'])

            if images_carousel:
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

        if self._version() == "Walmart v1":
            return self._image_urls_old()

        if self._version() == "Walmart v2":
            return self._image_urls_new()

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
            if len(mobile_img) > 0 and len(img) > 0:
                try:
                    similarity = compare_images(img[0], mobile_img[0])
                    return similarity
                except:
                    return None
            else:
                return None
        else:
            return None # no images found to compare

    # ! may throw exception if json object not decoded properly
    def _extract_product_info_json(self):
        """Extracts body of javascript function
        found in a script tag on each product page,
        that contains various usable information about product.
        Stores function body as json decoded dictionary in instance variable.
        Returns:
            function body as dictionary (containing various info on product)
        """
        if self.product_info_json:
            return self.product_info_json

        if self._version() == "Walmart v2" and self.is_bundle_product:
            product_info_json = self._find_between(html.tostring(self.tree_html), 'define("product/data",', ");\n")
            product_info_json = json.loads(product_info_json)
            self.product_info_json = product_info_json

            return self.product_info_json
        else:
            page_raw_text = html.tostring(self.tree_html)
            product_info_json = json.loads(re.search('define\("product\/data",\n(.+?)\n', page_raw_text).group(1))

            self.product_info_json = product_info_json

            return self.product_info_json

    # ! may throw exception if not found
    def _owned_from_script(self):
        """Extracts 'owned' (by walmart) info on product
        from script tag content (using an object in a js function).
        Returns:
            1/0 (product owned/not owned)
        """

        if not self.product_info_json:
            pinfo_dict = self._extract_product_info_json()
        else:
            pinfo_dict = self.product_info_json

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

        if not self.product_info_json:
            pinfo_dict = self._extract_product_info_json()
        else:
            pinfo_dict = self.product_info_json

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

        if self._version() == "Walmart v1":
            return self._in_stores_v1()

        if self._version() == "Walmart v2":
            return self._in_stores_v2()

    def _in_stores_v1(self):
        try:
            if self._find_between(html.tostring(self.tree_html), "isBuyableInStore:", ",").strip() == "true":
                return 1

            try:
                onlinePriceText = "".join(self.tree_html.xpath("//tr[@id='WM_ROW']//div[@class='onlinePriceWM']//text()"))
                if "In stores only" in onlinePriceText:
                    return 1
            except:
                pass
        except:
            pass

        return 0

    def _in_stores_v2(self):
        try:
            if not self.product_info_json:
                pinfo_dict = self._extract_product_info_json()
            else:
                pinfo_dict = self.product_info_json

            for store in pinfo_dict["analyticsData"]["storesAvail"]:
                if int(store["isAvail"]) == 1:
                    return 1

            if self._version() == "Walmart v2" and self.is_bundle_product:
                body_dict = json.loads(self._find_between(html.tostring(self.tree_html), 'define("ads/data",', ');\n'))

                if body_dict["inStore"] is True:
                    return 1
            else:
                body_raw = "".join(self.tree_html.xpath("//script//text()"))
                body_clean = re.sub("\n", " ", body_raw)
                body_jpart = re.findall("\{\"query.*?\}", body_clean)[0]
                body_dict = json.loads(body_jpart)

                if body_dict["inStore"] is True:
                    return 1
        except Exception:
            pass

        return 0

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
    def _marketplace_sellers_from_script(self):
        """Extracts list of marketplace sellers for this product.
        Works on new page version.
        Returns:
            list of strings representing marketplace sellers,
            or None if none found / not relevant
        """

        if not self.product_info_json:
            pinfo_dict = self._extract_product_info_json()
        else:
            pinfo_dict = self.product_info_json

#        sellers_dict = pinfo_dict["analyticsData"]["productSellersMap"]
#        sellers = map(lambda d: d["sellerName"], sellers_dict)

        sellers_dict = pinfo_dict["buyingOptions"]["marketplaceOptions"]
        sellers = map(lambda d: d["seller"]["displayName"], sellers_dict)

        return sellers

    # ! may throw exception if not found
    def _marketplace_prices_from_script(self):
        """Extracts list of marketplace sellers for this product.
        Works on new page version.
        Returns:
            list of strings representing marketplace sellers,
            or None if none found / not relevant
        """

        if not self.product_info_json:
            pinfo_dict = self._extract_product_info_json()
        else:
            pinfo_dict = self.product_info_json

        prices = []
        sellers_dict = pinfo_dict["analyticsData"]["productSellersMap"]

        if self._primary_seller().lower() == "walmart.com":
            for seller in sellers_dict:
                if seller["sellerName"] != "Walmart.com":
                    prices.append(float(seller["price"]))
        else:
            for seller in sellers_dict:
                prices.append(float(seller["price"]))

        return prices

    def _marketplace_lowest_price(self):
        marketplace_prices = self._marketplace_prices()

        if marketplace_prices is None:
            return None

        return min(marketplace_prices)

    # ! may throw exception if not found
    def _in_stock_from_script(self):
        """Extracts info on whether product is available to be
        bought on the site, from any seller (marketplace or owned).
        Works on new page design
        Returns:
            1/0 (available/not available)
        """

        if not self.product_info_json:
            pinfo_dict = self._extract_product_info_json()
        else:
            pinfo_dict = self.product_info_json

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
            try:
                # try to extract assuming old page structure
                marketplace_new = self._marketplace_meta_from_tree()
            except Exception:
                marketplace_new = None

        if marketplace_new is None:
            marketplace_new = 0

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
            if self._primary_seller().lower() == "walmart.com":
                sellers = filter(lambda s: s != "Walmart.com", sellers)

            return sellers if sellers else None
        except:
            sellers = None

        if not sellers:
            # assume old page version
            sellers = self._seller_meta_from_tree().keys()
            # filter out walmart
            if self._primary_seller().lower() == "walmart.com":
                sellers = filter(lambda s: s != "Walmart.com", sellers)
            return sellers if sellers else None

    def _marketplace_prices(self):
        """Extracts list of marketplace sellers for this product
        Works for both old and new page version
        Returns:
            list of strings representing marketplace sellers,
            or None if none found / not relevant
        """

        # assume new page version
        try:
            prices = self._marketplace_prices_from_script()

            if not prices:
                return None

            return prices if prices else None
        except:
            prices = None

        if not prices:
            # assume old page version
            sellers = self._marketplace_sellers()
            product_info_json_text = self._find_between(html.tostring(self.tree_html), "var DefaultItemWidget =", "addMethodsToDefaultItem(DefaultItemWidget);").strip()

            if not product_info_json_text:
                product_info_json_text = self._find_between(html.tostring(self.tree_html), "var DefaultItem =", "addMethodsToDefaultItem(DefaultItem);")

            if not sellers:
                return None

            if not "sellerName: '" + sellers[0] + "'," in product_info_json_text:
                return None

            price_html = html.fromstring(self._find_between(product_info_json_text, ",\nprice: '", "',\nprice4SAC:"))

            prices = [price_html.text_content()]

            prices = [float(price) for price in prices]

            if not prices:
                return None

            return prices

    def _find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""


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

    def _primary_seller(self):
        if self._version() == "Walmart v1":
            return self.tree_html.xpath("//meta[@itemprop='seller']/@content")[0]

        if self._version() == "Walmart v2":
            self._extract_product_info_json()
            return self.product_info_json["buyingOptions"]["seller"]["displayName"]

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

    def _site_online(self):
        """Extracts whether the item is sold by the site and delivered directly
        Works on both old and new page version.
        Returns 1/0
        """

        if self._version() == "Walmart v1":
            return self._site_online_v1()

        if self._version() == "Walmart v2":
            return self._site_online_v2()

    def _site_online_v1(self):
        try:
            try:
                onlinePriceText = "".join(self.tree_html.xpath("//tr[@id='WM_ROW']//div[@class='onlinePriceWM']//text()"))
                if "In stores only" in onlinePriceText:
                    return 0
            except:
                pass

            if "walmart.com" in self._find_between(html.tostring(self.tree_html), "sellerName:", ",").lower() and \
                            self._find_between(html.tostring(self.tree_html), "isBuyableOnWWW:", ",").strip() == "true":
                return 1

            if "WalmartMainBody DynamicMode wmBundleItemPage" in html.tostring(self.tree_html):
                if "online" in (" " . join(self.tree_html.xpath("//tr[@id='WM_ROW']//div[@id='onlinePriceLabel']/text()"))).lower():
                    return 1
        except:
            pass

        return 0

    def _site_online_v2(self):
        if self.is_bundle_product:
            pinfo_dict = self._extract_product_info_json()

            if pinfo_dict["buyingOptions"]["seller"]["walmartOnline"]:
                return 1
        else:
            try:
                modal_texts = self.tree_html.xpath("//*[@class='js-pure-soi-flyout-header']")[0].text_content()

                if "This item is only sold at a Walmart store." in modal_texts:
                    return 0
            except Exception:
                pass

            try:
                if not self.product_info_json:
                    pinfo_dict = self._extract_product_info_json()
                else:
                    pinfo_dict = self.product_info_json

                if pinfo_dict["buyingOptions"]["seller"]["walmartOnline"]:
                    return 1

                marketplace_seller_names = self.tree_html.xpath("//div[contains(@data-automation-id, 'product-mp-seller-name')]/text()")

                if marketplace_seller_names:
                    for marketplace in marketplace_seller_names:
                        if marketplace.lower().strip() == "walmart.com":
                            return 1

                return 0
            except:
                pass

            return 0

    def _site_online_out_of_stock(self):
        """Extracts whether currently unavailable from the site - binary
        Works on both old and new page version.
        Returns 1/0
        """

        if self._site_online():
            try:
                if self._version() == "Walmart v2" and self.is_bundle_product:
                    if not self.product_info_json["analyticsData"]["onlineAvail"]:
                        return 1
                    else:
                        return 0

                site_online_out_of_stock = self.tree_html.xpath("//meta[@itemprop='availability']/@content")[0]

                if "InStock" in site_online_out_of_stock:
                    return 0
                elif "OutOfStock" in site_online_out_of_stock:
                    return 1
            except Exception:
                return 1

        return 0

    def _failure_type(self):
        # we ignore bundle product
        if self.tree_html.xpath("//div[@class='js-about-bundle-wrapper']") or \
                        "WalmartMainBody DynamicMode wmBundleItemPage" in html.tostring(self.tree_html):
            self.is_bundle_product = True

        # we ignore video product
        if self.tree_html.xpath("//div[@class='VuduItemBox']"):
            self.failure_type = "Video on Demand"

        # we ignore non standard product(v1) like gift card for now
        if self.tree_html.xpath("//body[@id='WalmartBodyId']") and not self.tree_html.xpath\
                        ("//form[@name='SelectProductForm']"):
            if self.tree_html.xpath("//div[@class='PageTitle']/h1/text()") and "eGift Card" in self.tree_html.xpath("//div[@class='PageTitle']/h1/text()")[0]:
                self.failure_type = "E-Card"

        # we ignore incomplete product like http://www.walmart.com/ip/39783867
        if re.findall(r"<!(-+) preparation (-+)>", html.tostring(self.tree_html)):
            self.failure_type = "Incomplete"

        try:
            if "/cp/" in self._canonical_link():
                self.failure_type = "Category page"
        except:
            if "/cp/" in self.product_page_url:
                self.failure_type = "Category page"

        # check existence of "We can't find the product you are looking for, but we have similar items for you to consider."
        text_list = self.tree_html.xpath("//body//text()")
        text_contents = " " .join(text_list)

        if "We can't find the product you are looking for, but we have similar items for you to consider." in text_contents:
            self.failure_type = "404 Error"

        return self.failure_type

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

    def _ingredients(self):
        # list of ingredients - list of strings
        ingr = self.tree_html.xpath("//section[contains(@class,'ingredients')]/p[2]//text()")

        if not ingr:
            ingr = self.tree_html.xpath("//section[contains(@class,'js-ingredients')]/p[1]//text()")

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
        ingr=self.tree_html.xpath("//p[@class='ProductIngredients']//text()")
        if len(ingr) >0 :
            res = ingr[0].split(',')
            self.ing_count = len(res)
            return res
        ingr = self.tree_html.xpath("//b[contains(text(),'Ingredients:')]")
        if len(ingr) > 0:
            ingr = ingr[0].tail
            ingr = ingr.split(",")
            ingr = map(lambda e: e.strip(), ingr)
            self.ing_count = len(ingr)
            return ingr
        self.ing_count = None
        return None

    def _ingredient_count(self):
        # number of ingredients - integer
        ingredients = self._ingredients()

        if not ingredients:
            return 0

        return len(ingredients)

    def _canonical_link(self):
        canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

        if canonical_link.startswith("http://www.walmart.com"):
            return canonical_link
        else:
            return "http://www.walmart.com" + canonical_link

    def _nutrition_facts(self):
        # nutrition facts - list of tuples ((key,value) pairs, values could be dictionaries)
        # containing nutrition facts
        if self._version() == "Walmart v1":
            if not self.tree_html.xpath("//div[@class='NutFactsSIPT']"):
                return None

            res = []
            serving_info = self.tree_html.xpath("//div[@class='NutFactsSIPT']//tr[@class='ServingInfo']/td/text()")
            res.append([serving_info[0][0:13].strip(),serving_info[0][13:].strip()])
            res.append([serving_info[1][0:22].strip(),serving_info[1][22:].strip()])
            calories_info_cals = self.tree_html.xpath("//div[@class='NutFactsSIPT']//tr[@class='Calories']/td/div[@class='Cals']//text()")

            if calories_info_cals:
                res.append(calories_info_cals)

            calories_info_cals_fat = self.tree_html.xpath("//div[@class='NutFactsSIPT']//tr[@class='Calories']/td/div[@class='CalsFat']//text()")

            if calories_info_cals_fat:
                res.append([calories_info_cals_fat[0][:17].strip(), calories_info_cals_fat[0][17:].strip()])

            nutrition_info_list = self.tree_html.xpath("//div[@class='NutFactsSIPT']//tr[child::*[@class='AttrName'] and child::*[@class='AttrValue']]")

            for nutrition_info in nutrition_info_list:
                values = nutrition_info.xpath("./td//text()")
                pass

                if len(values) == 1:
                    if not re.search("\d", values[0]):
                        res.append([values[0], ""])
                    else:
                        nDigitIndex = re.search("\d", values[0]).start()
                        res.append([values[0][:nDigitIndex].strip(), values[0][nDigitIndex:].strip()])
                if len(values) == 2:
                    res.append([values[0].strip(), values[1].strip()])
                elif len(values) == 3:
                    res.append([values[0].strip(), {"absolute": values[1].strip(), "relative": values[2].strip()}])

            if not res:
                return None

            return res
        elif self._version() == "Walmart v2":
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
                return res

            return None

        return None

    def _nutrition_fact_count(self):
        # number of nutrition facts (of elements in the nutrition_facts list) - integer
        nutrition_facts = self._nutrition_facts()

        if nutrition_facts:
            return len(nutrition_facts)

        return 0

    def _nutrition_fact_text_health(self):
        try:
            if self._version() == "Walmart v1":
                nutrition_facts = self._nutrition_facts()

                if not nutrition_facts:
                    return 0

                calories_info_count = 0

                for nutrition_fact in nutrition_facts:
                    if "Calories" in nutrition_fact[0]:
                        calories_info_count = calories_info_count + 1

                if calories_info_count == 0 or len(nutrition_facts) - calories_info_count < 3:
                    return 1

                nutrition_facts_in_text = html.tostring(self.tree_html.xpath("//div[@class='NutFactsSIPT']")[0]).lower()

                if not re.search('percent daily values are based on(.+?)your daily values may be higher or lower depending', nutrition_facts_in_text):
                    return 1

                return 2
            elif self._version() == "Walmart v2":
                nutrition_facts = self._nutrition_facts()

                if not nutrition_facts:
                    return 0

                nutrition_facts_tr_list = self.tree_html.xpath("//div[@class='nutrition-section']//table[@class='nutrient-table']//tr")
                calories_facts_tr_list = self.tree_html.xpath("//div[@class='nutrition-section']//table[@class='calories-table']//tr")
                vitamins_facts_tr_list = self.tree_html.xpath("//div[@class='nutrition-section']//table[@class='vitamins-table']//tr")
                nutrition_facts_in_text = html.tostring(self.tree_html.xpath("//div[@class='nutrition-section']")[0]).lower()

                if len(nutrition_facts_tr_list) < 2 or len(calories_facts_tr_list) < 2:
                    return 1

                if not re.search('percent daily values are based on(.+?)your daily values may be higher or lower depending', nutrition_facts_in_text):
                    return 1

                return 2
        except:
            return 0

    def _drug_facts(self):
        drug_facts = {}
        active_ingredient_list = []
        warnings_list = []
        directions_list = []
        inactive_ingredients = []
        questions_list = []

        try:
            div_active_ingredients = self.tree_html.xpath("//section[@class='active-ingredients']/div[@class='ingredient clearfix']")

            if div_active_ingredients:
                for div_active_ingredient in div_active_ingredients:
                    active_ingredient_list.append({"ingredients": div_active_ingredient.xpath("./div[@class='column1']")[0].text_content().strip(), "purpose": div_active_ingredient.xpath("./div[@class='column2']")[0].text_content().strip()})
                drug_facts["Active Ingredients"] = active_ingredient_list
        except:
            pass

        try:
            ul_warnings = self.tree_html.xpath("//h6[@class='section-heading warnings']/following-sibling::*[1]")

            if ul_warnings:
                warnings_title_list = ul_warnings[0].xpath("./li/strong/text()")
                warnings_text_list = ul_warnings[0].xpath("./li/text()")

                for index, warning_title in enumerate(warnings_title_list):
                    warnings_list.append([warning_title.strip(), warnings_text_list[index].strip()])

                if warnings_list:
                    drug_facts["Warnings"] = warnings_list
        except:
            pass

        try:
            p_directions = self.tree_html.xpath("//h6[@class='section-heading' and contains(text(), 'Directions')]/following-sibling::*[1]")

            if p_directions:
                directions_text = p_directions[0].text_content().strip()
                drug_facts["Directions"] = directions_text
        except:
            pass

        try:
            p_inactive_ingredients = self.tree_html.xpath("//h6[@class='section-heading' and contains(text(), 'Inactive Ingredients')]/following-sibling::*[1]")

            if p_inactive_ingredients:
                inactive_ingredients = p_inactive_ingredients[0].text_content().strip().split(", ")

                if inactive_ingredients:
                    drug_facts["Inactive Ingredients"] = inactive_ingredients
        except:
            pass

        try:
            p_questions = self.tree_html.xpath("//h6[@class='section-heading' and contains(text(), 'Questions?')]/following-sibling::*[1]")

            if p_questions:
                questions_text = p_questions[0].text_content().strip()
                drug_facts["Questions?"] = questions_text
        except:
            pass

        if not drug_facts:
            return None

        return drug_facts

    def _drug_fact_count(self):
        drug_fact_key_list = ["Active Ingredients", "Directions", "Inactive Ingredients", "Questions?", "Warnings"]

        drug_facts = self._drug_facts()

        try:
            count = 0

            for key in drug_fact_key_list:
                if key in drug_facts:
                    if isinstance(drug_facts[key], str):
                        count = count + 1
                    else:
                        count = count + len(drug_facts[key])

            return count
        except:
            return 0

        return 0

    def _drug_fact_text_health(self):
        drug_fact_main_key_list = ["Active Ingredients", "Directions", "Inactive Ingredients", "Warnings"]

        drug_facts = self._drug_facts()

        if not drug_facts:
            return 0

        for key in drug_fact_main_key_list:
            if key not in drug_facts:
                return 1
            else:
               if len(drug_facts[key]) == 0:
                   return 1

        return 2

    def _supplement_facts(self):
        supplement_facts = None

        if not self.tree_html.xpath("//div[@class='supplement-section']"):
            return None

        supplement_facts = {"supplement-header": None, "supplement-facts": None}

        supplement_head_block = self.tree_html.xpath("//div[@class='supplement-header']/div")
        supplement_head = []

        for item in supplement_head_block:
            head_string = item.text_content().strip()

            if not head_string:
                continue

            index = re.search("\d", head_string)

            if index:
                key = head_string[:index.start()].strip()
                value = head_string[index.start():].strip()
            else:
                key = head_string
                value = None

            supplement_head.append([key, value])

        supplement_facts["supplement-header"] = supplement_head

        supplement_table_block = self.tree_html.xpath("//table[@class='supplement-table']/tbody/tr")
        supplement_table_info = []

        for item in supplement_table_block:
            data = item.xpath("./td/text()")

            try:
                key = item.xpath("./td[1]/text()")[0].strip()

                if not key:
                    continue

                absolute_value = item.xpath("./td[2]/text()")
                relative_value = item.xpath("./td[3]/text()")

                if absolute_value:
                    absolute_value = absolute_value[0].strip()
                else:
                    absolute_value = ""

                if relative_value:
                    relative_value = relative_value[0].strip()
                else:
                    relative_value = ""

                supplement_table_info.append([data[0], {"absolute": absolute_value, "relative": relative_value}])
            except:
                continue

        supplement_facts["supplement-facts"] = supplement_table_info

        return supplement_facts

    def _supplement_fact_count(self):
        supplement_facts = self._supplement_facts()

        if not supplement_facts:
            return 0

        return len(supplement_facts["supplement-header"]) + len(supplement_facts["supplement-facts"])

    def _supplement_fact_text_health(self):
        if not self.tree_html.xpath("//div[@class='supplement-section']"):
            return 0

        supplement_fact_count = self._supplement_fact_count()
        element_count = len(self.tree_html.xpath("//div[@class='supplement-header']/div")) + len(self.tree_html.xpath("//table[@class='supplement-table']/tbody/tr"))

        if supplement_fact_count != element_count:
            return 1

        supplement_facts = self._supplement_facts()

        if len(supplement_facts["supplement-header"]) < 2:
            return 1

        for header in supplement_facts["supplement-header"]:
            if not header[1].strip():
                return 1

        for fact in supplement_facts["supplement-facts"]:
            if not fact[1]["absolute"].strip():
                return 1

        return 2

    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        """Cleans a piece of text of html entities
        Args:
            original text (string)
        Returns:
            text stripped of html entities
        """

        return re.sub("&nbsp;", " ", text).strip()

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
        "upc": _upc_from_tree, \
        "product_name": _product_name_from_tree, \
        "site_id": _site_id, \
        "product_id": _extract_product_id, \
        "walmart_no": _walmart_no, \
        "keywords": _meta_keywords_from_tree, \
        "meta_tags": _meta_tags,\
        "meta_tag_count": _meta_tag_count,\
        "canonical_link": _canonical_link,
        "brand": _meta_brand_from_tree, \
        "description": _short_description_wrapper, \
        # TODO: check if descriptions work right
        "long_description": _long_description_wrapper, \
        "shelf_description": _shelf_description, \
        "variants": _variants, \
        "swatches": _swatches, \
        "related_products_urls":  _related_product_urls, \
        "ingredients": _ingredients, \
        "ingredient_count": _ingredient_count, \
        "nutrition_facts": _nutrition_facts, \
        "nutrition_fact_count": _nutrition_fact_count, \
        "nutrition_fact_text_health": _nutrition_fact_text_health, \
        "drug_facts": _drug_facts, \
        "drug_fact_count": _drug_fact_count, \
        "drug_fact_text_health": _drug_fact_text_health, \
        "supplement_facts": _supplement_facts, \
        "supplement_fact_count": _supplement_fact_count, \
        "supplement_fact_text_health": _supplement_fact_text_health, \
        "price": _price_from_tree, \
        "price_amount": _price_amount, \
        "price_currency": _price_currency, \
        "htags": _htags_from_tree, \
        "model": _model_from_tree, \
        "model_meta": _meta_model_from_tree, \
        "features": _features_from_tree, \
        "feature_count": _nr_features_from_tree, \
        "title_seo": _title_from_tree, \
        "rollback": _rollback, \
        "shipping": _shipping, \
        # TODO: I think this causes the method to be called twice and is inoptimal
        "product_title": _product_name_from_tree, \
        "in_stores": _in_stores, \
        "marketplace": _marketplace, \
        "marketplace_prices" : _marketplace_prices, \
        "marketplace_sellers": _marketplace_sellers, \
        "marketplace_out_of_stock": _marketplace_out_of_stock, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \
        "primary_seller": _primary_seller, \
        "in_stock": _in_stock, \
        "site_online": _site_online, \
        "site_online_out_of_stock": _site_online_out_of_stock, \
        "review_count": _review_count, \
        "average_review": _average_review, \
        "max_review": _max_review, \
        "min_review": _min_review, \
        "reviews": _reviews, \
        "no_longer_available": _no_longer_available, \
        # video needs both page source and separate requests
        "video_count": _video_count, \
        "video_urls": _video_urls, \
        "wc_360": _wc_360, \
        "wc_emc": _wc_emc, \
        "wc_video": _wc_video, \
        "wc_pdf": _wc_pdf, \
        "wc_prodtour": _wc_prodtour, \
        "flixmedia": _flixmedia, \
        "webcollage": _product_has_webcollage, \
        "sellpoints": _product_has_sellpoints, \

        "image_count": _image_count, \
        "image_urls": _image_urls, \

        "categories": _categories_hierarchy, \
        "category_name": _category, \

        "scraper": _version, \
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
