#!/usr/bin/python

from lxml import html

import re
import json
import requests
import mmh3 as MurmurHash
import os

from special_crawler.no_img_hash import fetch_bytes
from special_crawler.extract_data import Scraper

class WalmartExtraData(object):

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
    # base URL for product API
    BASE_URL_PRODUCT_API = "http://www.walmart.com/product/api/{0}"

    INVALID_URL_MESSAGE = "Expected URL format is http://www.walmart.com/ip[/<optional-part-of-product-name>]/<product_id>"

    def __init__(self, *args, **kwargs):
        self.product_page_url = kwargs['url']
        self.tree_html = kwargs['response']

        # no image hash values
        self.NO_IMAGE_HASHES = self.load_image_hashes()
        # whether product has any sellpoints media
        self.has_sellpoints_media = False
        # product videos (to be used for "video_urls", "video_count", and "webcollage")
        self.video_urls = None
        # whether videos were extracted
        self.extracted_video_urls = False
        # whether product has any videos
        self.has_video = False
        # product json embeded in page html
        self.product_info_json = None

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

    def _is_bundle_product(self):
        if self.tree_html.xpath("//div[@class='js-about-bundle-wrapper']") or \
                        "WalmartMainBody DynamicMode wmBundleItemPage" in html.tostring(self.tree_html):
            return True

        return False

    def _image_urls_new(self):
        """Extracts image urls for this product.
        Works on new version of walmart pages.
        Returns:
            list of strings representing image urls
        """

        if self._version() == "Walmart v2" and self._is_bundle_product():
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
            first_hash = self._image_hash(url)
            if first_hash in self.NO_IMAGE_HASHES:
                print "not an image"
                return True
            else:
                return False

    def _image_hash(self, image_url):
        """Computes hash for an image.
        To be used in _no_image, and for value of _image_hashes
        returned by scraper.
        Returns string representing hash of image.

        :param image_url: url of image to be hashed
        """
        return str(MurmurHash.hash(fetch_bytes(image_url)))

    def load_image_hashes(self):
        '''Read file with image hashes list
        Return list of image hashes found in file
        '''
        path = '../special_crawler/no_img_list.json'
        no_img_list = []
        if os.path.isfile(path):
            f = open(path, 'r')
            s = f.read()
            if len(s) > 1:
                no_img_list = json.loads(s)
            f.close()
        return no_img_list

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

        if self._version() == "Walmart v2" and self._is_bundle_product():
            product_info_json = self._find_between(html.tostring(self.tree_html), 'define("product/data",', ");\n")
            product_info_json = json.loads(product_info_json)
            self.product_info_json = product_info_json

            return self.product_info_json
        else:
            page_raw_text = html.tostring(self.tree_html)
            product_info_json = json.loads(re.search('define\("product\/data",\n(.+?)\n', page_raw_text).group(1))

            self.product_info_json = product_info_json

            return self.product_info_json

    def _video_count(self):
        """Whether product has video
        To be replaced with function that actually counts
        number of videos for this product
        Returns:
            1 if product has video
            0 if product doesn't have video
        """

        self._extract_video_urls()

        if not self.video_urls:
            if self.has_video:
                return 1
            else:
                return 0
        else:
            return len(self.video_urls)

    def _extract_video_urls(self):
        """Extracts video URL for a given walmart product
        and puts them in instance variable.
        """

        if self.extracted_video_urls:
            return

        # set flag that videos where attemtped to be extracted
        self.extracted_video_urls = True

        if self._version() == "Walmart v2" and self._is_bundle_product():
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

    def _video_urls(self):
        """Extracts video URLs for a given walmart product
        Returns:
            list of strings containing the video urls
            or None if none found
        """

        self._extract_video_urls()

        return self.video_urls

    #TODO: To alter the structure of the module. The call requests only from spiders, query processing module.