#!/usr/bin/python

import re
import lxml
import lxml.html
import requests
import json
import ast

from itertools import groupby

from lxml import html, etree
from extract_data import Scraper
from spiders_shared_code.newlook_variants import NewlookVariants


class NewlookScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.newlook.com/shop/.*$"
    REVIEW_URL = "http://jcpenney.ugc.bazaarvoice.com/1573-en_us/{}/reviews.djs?format=embeddedhtml"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.review_json = None
        self.review_list = None
        self.is_review_checked = False
        self.price_json = None
        self.jv = NewlookVariants()
        self.is_analyze_media_contents = False
        self.video_urls = None
        self.video_count = 0
        self.pdf_urls = None
        self.pdf_count = 0
        self.wc_emc = 0
        self.wc_prodtour = 0
        self.wc_360 = 0
        self.wc_video = 0
        self.wc_pdf = 0

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match(r"^http://www.newlook.com/shop/.*$", self.product_page_url)

        return not not m

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        itemtype = self.tree_html.xpath('//div[@class="prod_info"]')
        if not itemtype:
            return True
        return False

    def _find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _canonical_link(self):
        canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

        return canonical_link

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        return self.tree_html.xpath('//*[@itemprop="productID"]//text()')[0].strip()

    def _site_id(self):
        return self.tree_html.xpath('//*[@itemprop="productID"]//text()')[0].strip()

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//*[@itemprop="name"]//text()')[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _model(self):
        return None

    def _features(self):
        return None

    def _feature_count(self):
        return 0

    def _description(self):
        description_block = self.tree_html.xpath("//span[@itemprop='description']")
        description = ""
        if len(description_block)>0:
            description = description_block[0].text_content().strip()

        return description

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description(self):
        try:
            description_block = self.tree_html.xpath("//div[@id='longCopyCont']//ul")[0]
            long_description = description_block.text_content().strip()

            if not long_description:
                return None
            else:
                long_description = re.sub('\\n+', ' ', long_description).strip()
                long_description = re.sub('\\t+', ' ', long_description).strip()
                long_description = re.sub('\\r+', ' ', long_description).strip()
                long_description = re.sub(' +', ' ', long_description).strip()

                return long_description
        except:
            pass

        return None

    def _ingredients(self):
        return None

    def _ingredients_count(self):
        return 0

    def _variants(self):
        return self.jv._variants()

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        pass

    def _image_urls(self):
        return ["http:"+b for b in self.tree_html.xpath("//div[@id='thumbs']//img/@src")]

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())
        return 0

    def analyze_media_contents(self):
        if self.is_analyze_media_contents:
            return

        self.is_analyze_media_contents = True

        page_raw_text = html.tostring(self.tree_html)

        #check pdf
        try:
            pdf_url = re.search('href="(.+\.pdf?)"', page_raw_text).group(1)

            if not pdf_url:
                raise Exception

            if not pdf_url.startswith("http://"):
                pdf_url = "http://www.jcpenney.com" + pdf_url

            self.pdf_urls = [pdf_url]
            self.pdf_count = len(self.pdf_urls)
        except:
            pass

        video_json = None

        try:
            video_json = ast.literal_eval(self._find_between(html.tostring(self.tree_html), "videoIds.push(", ");\nvar videoThumbsMap = "))
        except:
            video_json = None

        #check media contents window existence
        if self.tree_html.xpath("//a[@class='InvodoViewerLink']"):

            media_contents_window_link = self.tree_html.xpath("//a[@class='InvodoViewerLink']/@onclick")[0]
            media_contents_window_link = re.search("window\.open\('(.+?)',", media_contents_window_link).group(1)

            h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}

            contents = requests.get(media_contents_window_link, headers=h).text

            #check media contents
            if "webapps.easy2.com" in media_contents_window_link:
                try:
                    media_content_raw_text = re.search('Demo.instance.data =(.+?)};\n', contents).group(1) + "}"
                    media_content_json = json.loads(media_content_raw_text)

                    video_lists = re.findall('"Path":"(.*?)",', media_content_raw_text)

                    video_lists = [media_content_json["UrlAddOn"] + url for url in video_lists if url.strip().endswith(".flv") or url.strip().endswith(".mp4/")]
                    video_lists = list(set(video_lists))

                    if not video_lists:
                        raise Exception

                    self.video_urls = video_lists
                    self.video_count = len(self.video_urls)
                except:
                    pass
            elif "content.webcollage.net" in media_contents_window_link:
                webcollage_link = re.search("document\.location\.replace\('(.+?)'\);", contents).group(1)
                contents = requests.get(webcollage_link, headers=h).text
                webcollage_page_tree = html.fromstring(contents)

                try:
                    webcollage_media_base_url = re.search('<div data-resources-base="(.+?)"', contents).group(1)

                    videos_json = '{"videos":' + re.search('{"videos":(.*?)]}</div>', contents).group(1) + ']}'
                    videos_json = json.loads(videos_json)

                    video_lists = [webcollage_media_base_url + videos_json["videos"][0]["src"]["src"][1:]]
                    self.wc_video = 1
                    self.video_urls = video_lists
                    self.video_count = len(self.video_urls)
                except:
                    pass

                try:
                    if webcollage_page_tree.xpath("//div[@class='wc-ms-navbar']//span[text()='360 Rotation']") or webcollage_page_tree.xpath("//div[@class='wc-ms-navbar']//span[text()='360/Zoom']"):
                        self.wc_360 = 1
                except:
                    pass

                try:
                    if webcollage_page_tree.xpath("//ul[contains(@class, 'wc-rich-features')]"):
                        self.wc_emc = 1
                except:
                    pass

            elif "bcove.me" in media_contents_window_link:
                try:
                    brightcove_page_tree = html.fromstring(contents)
                    video_lists = [brightcove_page_tree.xpath("//meta[@property='og:video']/@content")[0]]
                    self.video_urls = video_lists
                    self.video_count = len(self.video_urls)
                except:
                    pass

        if video_json:
            if not self.video_urls:
                self.video_urls = [video_json['url']]
                self.video_count = 1
            else:
                self.video_urls.append(video_json["url"])
                self.video_count = self.video_count + 1

    def _video_urls(self):
        self.analyze_media_contents()
        return self.video_urls

    def _video_count(self):
        self.analyze_media_contents()
        return self.video_count

    # return dictionary with one element containing the PDF
    def _pdf_urls(self):
        self.analyze_media_contents()
        return self.pdf_urls

    def _pdf_count(self):
        self.analyze_media_contents()
        return self.pdf_count

    def _wc_emc(self):
        self.analyze_media_contents()
        return self.wc_emc

    def _wc_prodtour(self):
        self.analyze_media_contents()
        return self.wc_prodtour

    def _wc_360(self):
        self.analyze_media_contents()
        return self.wc_360

    def _wc_video(self):
        self.analyze_media_contents()
        return self.wc_video

    def _wc_pdf(self):
        return None

    def _webcollage(self):
        return 0

    def _htags(self):
        htags_dict = {}
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))

        return htags_dict

    def _keywords(self):
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0].strip()

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################


    def _average_review(self):
        return None

    def _review_count(self):
        return 0

    def _max_review(self):
        return None

    def _min_review(self):
        return None

    def _reviews(self):
        return None

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        return self.tree_html.xpath('//*[@itemprop="price"]//text()')[0].strip()


    def _price_amount(self):
        price = self._price()
        price = price.replace(",", "")
        price_amount = re.findall(r"[\d\.]+", price)[0]
        return float(price_amount)

    def _price_currency(self):
        return "GBP"

    def _owned(self):
        return 0

    def _marketplace(self):
        return 0

    def _site_online(self):
        return 1

    def _in_stores(self):
        return 1

    def _site_online_out_of_stock(self):
        return 0

    def _marketplace_sellers(self):
        return None

    def _marketplace_out_of_stock(self):
        return 0

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        return self.tree_html.xpath("//div[@class='breadcrumb']/ul//li/a/text()")[1:]

    def _category_name(self):
        return self.tree_html.xpath("//div[@class='breadcrumb']/ul//li/a/text()")[-1]

    def _brand(self):
        return None


    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    def _clean_text(self, text):
        return re.sub("&nbsp;", " ", text).strip()

    ##########################################
    ################ RETURN TYPES
    ##########################################

    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service

    DATA_TYPES = { \
        # CONTAINER : NONE
        "url" : _url, \
        "product_id" : _product_id, \
        "site_id" : _site_id, \
        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "model" : _model, \
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "long_description" : _long_description, \
        "ingredients": _ingredients, \
        "ingredient_count": _ingredients_count,
        "variants": _variants,

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
        "pdf_count" : _pdf_count, \
        "pdf_urls" : _pdf_urls, \
        "webcollage" : _webcollage, \
        "wc_360": _wc_360, \
        "wc_emc": _wc_emc, \
        "wc_pdf": _wc_pdf, \
        "wc_prodtour": _wc_prodtour, \
        "wc_video": _wc_video, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "canonical_link": _canonical_link,

        # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \
        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "owned" : _owned, \
        "marketplace" : _marketplace, \
        "site_online": _site_online, \
        "site_online_out_of_stock": _site_online_out_of_stock, \
        "in_stores" : _in_stores, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_out_of_stock": _marketplace_out_of_stock, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "mobile_image_same" : _mobile_image_same, \
    }

