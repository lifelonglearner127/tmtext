#!/usr/bin/python

import re
import lxml
import lxml.html
import requests
import json

from itertools import groupby

from lxml import html, etree
from extract_data import Scraper
from spiders_shared_code.kohls_variants import KohlsVariants


class KohlsScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.kohls.com/product/prd-<product-id>/<optional-part-of-product-name>.jsp"
    REVIEW_URL = "http://kohls.ugc.bazaarvoice.com/9025/{}/reviews.djs?format=embeddedhtml"
    WEBCOLLAGE_CHANNEL_URL = "http://content.webcollage.net/kohls/product-content-page?channel-product-id={0}"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.failure_type = None
        self.kv = KohlsVariants()

        self.review_json = None
        self.review_list = None
        self.is_review_checked = False

        self.variants = None
        self.is_variant_checked = False

        self.wc_360 = 0
        self.wc_emc = 0
        self.wc_video = 0
        self.wc_pdf = 0
        self.wc_prodtour = 0
        self.is_webcollage_contents_checked = False
        self.is_video_checked = False
        self.product_info_json = None
        self.is_product_info_json_checked = False
        self.video_urls = []

    def _extract_page_tree(self):
        Scraper._extract_page_tree(self)

        if self.ERROR_RESPONSE["failure_type"] == "HTTP 404 - Page Not Found":
            self.ERROR_RESPONSE["failure_type"] = None

            contents = self.load_page_from_url_with_number_of_retries(self.product_page_url)

            self.page_raw_text = contents
            self.tree_html = html.fromstring(contents)

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match(r"^http://www.kohls.com/product/prd-.+/.+\.jsp(\?.*)?$", self.product_page_url)

        return not not m

    def _extract_product_info_json(self):
        if self.is_product_info_json_checked:
            return self.product_info_json

        self.is_product_info_json_checked = True

        try:
            product_info_json = self.tree_html.xpath("//script[contains(text(), 'var productJsonData = {')]/text()")[0].strip()
            start_index = product_info_json.find("var productJsonData = ") + len("var productJsonData = ")
            end_index = product_info_json.rfind(";")
            product_info_json = product_info_json[start_index:end_index].strip()
            product_info_json = json.loads(product_info_json)
        except:
            product_info_json = None

        self.product_info_json = product_info_json

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """

        try:
            self.kv.setupCH(self.tree_html)
        except:
            pass

        try:
            self._failure_type()

            if self.failure_type:
                self.ERROR_RESPONSE["failure_type"] = self.failure_type
                return True
        except Exception:
            return True

        self._extract_product_info_json()

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _canonical_link(self):
        canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

        return canonical_link

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        product_id = re.search('prd-(.+)/', self._url()).group(1)

        return product_id

    def _is_out_of_stock(self):
        try:
            message = html.tostring(self.tree_html.xpath('//div[@id="content"]/p')[0])
            message = re.sub('[\r\n\t]', '', message)

            if re.match('<p><strong>We&#8217;re very sorry, this item</strong><b>.+</b><strong> is out of stock.</strong></p>', message):
                return True
        except:
            return False

    def _failure_type(self):
        itemtype = self.tree_html.xpath('//div[@itemtype="http://schema.org/Product"]')

        if self._is_out_of_stock():
            return

        if not itemtype:
            self.failure_type = "Not a product"
            return

        if "var page = 'collectionPDPPage';" in self.page_raw_text:
            self.failure_type = "Collection product"
            return

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _out_of_stock_product_name(self):
        return self.tree_html.xpath('//div[@id="content"]/p/b/text()')[0]

    def _product_name(self):
        if self._is_out_of_stock():
            return self._out_of_stock_product_name()
        return self.tree_html.xpath('//title/text()')[0].strip()

    def _product_title(self):
        return self._product_name()

    def _title_seo(self):
        return self._product_name()

    def _model(self):
        return None

    def _features(self):
        description_block = html.fromstring("<div>" + self.product_info_json["productItem"]["accordions"]["productDetails"]["content"] + "</div>")
        is_features_found = False
        features_title_list = ["Product Features:", "PRODUCT FEATURES", "Product Features", "Features"]

        for element_block in description_block:
            inner_text = "".join([t.strip() for t in element_block.itertext()])
            inner_text = inner_text.strip()

            if inner_text in features_title_list:
                is_features_found = True
                break

        if not is_features_found:
            return None

        try:
            features_block = element_block.xpath(".//following-sibling::ul")[0]
            features_list = []

            features_list = [x.text_content() for x in features_block.xpath(".//li")]

            return features_list
        except:
            return None

    def _feature_count(self):
        if self._features():
            return len(self._features())

        return 0

    def _description(self):
        description_block = html.fromstring("<div>" + self.product_info_json["productItem"]["accordions"]["productDetails"]["content"] + "</div>")
        short_description = ""
        features_title_list = ["Product Features:", "PRODUCT FEATURES", "Product Features", "Features"]

        if self._features():
            features_ul = 0

            for element_block in description_block:
                inner_text = "".join([t.strip() for t in element_block.itertext()])
                inner_text = inner_text.strip()

                if inner_text in features_title_list:
                    break

                if not element_block.xpath('./a'):
                    short_description += html.tostring(element_block)
        else:
            for element_block in description_block:
                if element_block.tag == "ul":
                    break

                short_description += html.tostring(element_block)

        if not short_description.strip():
            return None
        else:
            return short_description

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description(self):
        description_block = html.fromstring("<div>" + self.product_info_json["productItem"]["accordions"]["productDetails"]["content"] + "</div>")
        features_title_list = ["Product Features:", "PRODUCT FEATURES", "Product Features", "Features"]

        if not description_block:
            return None

        long_description = ""

        if self._features():
            features_ul = 0

            for element_block in description_block:
                if html.tostring(element_block).startswith("<!--"):
                    continue

                inner_text = "".join([t.strip() for t in element_block.itertext()])
                inner_text = inner_text.strip()

                if inner_text in features_title_list:
                    features_ul = 1
                    continue

                if features_ul == 1:
                    features_ul = 2
                    continue

                if features_ul == 2:
                    if not element_block.xpath('./em'):
                        long_description += html.tostring(element_block)
        else:
            is_long_description = False

            for element_block in description_block:
                if not is_long_description and element_block.tag == "ul":
                    is_long_description = True

                if is_long_description:
                    long_description += html.tostring(element_block)

        if not long_description.strip():
            return None
        else:
            return long_description

    def _ingredients(self):
        return None

    def _ingredients_count(self):
        return 0

    def _variants(self):
        if self.is_variant_checked:
            return self.variants

        self.is_variant_checked = True

        self.variants = self.kv._variants()

        return self.variants

    def _swatches(self):
        return self.kv.swatches()

    def _no_longer_available(self):
        if self._is_out_of_stock():
            return 1
        return 0

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        pass
        
    def _image_urls(self):
        image_urls = [self.product_info_json["productItem"]["media"]["defaultImage"]["largeImage"]]

        if self.product_info_json["productItem"]["media"].get("alternateImages", None):
            for alt_image in self.product_info_json["productItem"]["media"]["alternateImages"]:
                if not alt_image["largeImage"] in image_urls:
                    image_urls.append(alt_image["largeImage"])

        if image_urls:
            return image_urls

        return None

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def _video_urls(self):
        if self.is_video_checked:
            return self.video_urls

        self.is_video_checked = True

        self._extract_webcollage_contents()

        if self.product_info_json["productItem"]["media"].get("videoURL", None):
            video_page_html = html.fromstring(self.load_page_from_url_with_number_of_retries(self.product_info_json["productItem"]["media"]["videoURL"]))
            video_urls = video_page_html.xpath("//video[@id='product-video']/source[contains(@type, 'video')]/@src")

            if video_urls:
                self.video_urls.extend([video_urls[0]])

        if not self.video_urls:
            self.video_urls.extend(self.tree_html.xpath('//a[starts-with(@href, "http://netstorage.kohls.com/product_video")]/@href'))

        return self.video_urls if self.video_urls else None

    def _video_count(self):
        video_urls = self._video_urls()

        return len(video_urls) if video_urls else 0

    # return dictionary with one element containing the PDF
    def _pdf_urls(self):
        return None

    def _pdf_count(self):
        return 0

    def _extract_webcollage_contents(self):
        if self.is_webcollage_contents_checked:
            return

        self.is_webcollage_contents_checked = True

        try:
            webcollage_page_contents = self.load_page_from_url_with_number_of_retries(self.WEBCOLLAGE_CHANNEL_URL.format(self._product_id()))

            if webcollage_page_contents.startswith("<HTML><HEAD></HEAD><BODY><P>Product information is currently unavailable</P>"):
                raise Exception

            webcollage_page_contents = html.fromstring(webcollage_page_contents)

            video_gallery_element = webcollage_page_contents.xpath("//div[@data-resources-base and starts-with(@id, 'videoGallery')]")

            if video_gallery_element:
                video_gallery_element = video_gallery_element[0]
            else:
                raise Exception

            base_video_url = video_gallery_element.xpath("./@data-resources-base")[0]
            wc_json_data = json.loads(video_gallery_element.xpath(".//div[@class='wc-json-data']/text()")[0].strip())
            webcollage_video_list = []

            for video_info in wc_json_data["videos"]:
                if base_video_url[-1] == "/" and video_info["src"]["src"][0] == "/":
                    webcollage_video_list.append(base_video_url + video_info["src"]["src"][1:])
                else:
                    webcollage_video_list.append(base_video_url + video_info["src"]["src"])

            if webcollage_video_list:
                self.video_urls.extend(webcollage_video_list)
                self.wc_video = 1

            if webcollage_page_contents.xpath("//div[@id='navbar']//ul/li//span[text()='Interactive Tour']"):
                self.wc_prodtour = 1

            if webcollage_page_contents.xpath("//div[@id='navbar']//ul/li//span[text()='360 Zoom']"):
                self.wc_360 = 1

            return
        except:
            pass

        return

    def _webcollage(self):
        if self._wc_360() + self._wc_emc() + self._wc_pdf() + self._wc_prodtour() + self._wc_video() > 0:
            return 1

        return 0

    def _wc_360(self):
        self._extract_webcollage_contents()
        return self.wc_360

    def _wc_emc(self):
        self._extract_webcollage_contents()
        return self.wc_emc

    def _wc_video(self):
        self._extract_webcollage_contents()
        return self.wc_video

    def _wc_pdf(self):
        self._extract_webcollage_contents()
        return self.wc_pdf

    def _wc_prodtour(self):
        self._extract_webcollage_contents()
        return self.wc_prodtour

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
        if self._review_count() == 0:
            return None

        average_review = round(float(self.review_json["jsonData"]["attributes"]["avgRating"]), 1)

        if str(average_review).split('.')[1] == '0':
            return int(average_review)
        else:
            return float(average_review)

    def _review_count(self):
        self._reviews()

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

        contents = self.load_page_from_url_with_number_of_retries(self.REVIEW_URL.format(self._product_id()))

        try:
            start_index = contents.find("webAnalyticsConfig:") + len("webAnalyticsConfig:")
            end_index = contents.find(",\nwidgetInitializers:initializers", start_index)

            self.review_json = contents[start_index:end_index]
            self.review_json = json.loads(self.review_json)
        except:
            self.review_json = None

        review_html = html.fromstring(re.search('"BVRRSecondaryRatingSummarySourceID":" (.+?)"},\ninitializers={', contents).group(1))
        reviews_by_mark = review_html.xpath("//*[contains(@class, 'BVRRHistAbsLabel')]/text()")
        reviews_by_mark = reviews_by_mark[:5]
        review_list = [[5 - i, int(re.findall('\d+', mark)[0])] for i, mark in enumerate(reviews_by_mark)]

        if not review_list:
            review_list = None

        self.review_list = review_list

        return self.review_list

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        if self.product_info_json["productItem"]["pricing"].get("salePrice", None):
            return self.product_info_json["productItem"]["pricing"]["salePrice"]

        if self.product_info_json["productItem"]["pricing"].get("regularPrice", None):
            return self.product_info_json["productItem"]["pricing"]["regularPrice"]

        return "$" + self.tree_html.xpath("//meta[@property='og:product:price:amount']/@content")[0]

    def _price_amount(self):
        price_text = self._price()
        price = re.findall(r"\d*\.\d+|\d+", price_text.replace(",", ""))
        return float(price[0])

    def _price_currency(self):
        return "USD"

    def _marketplace(self):
        if self.product_info_json["productItem"]["productDetails"].get("isMarketPlaceItem", False):
            return 1

        return 0

    def _site_online(self):
        if self._is_out_of_stock():
            return 1

        if self._marketplace() == 1:
            return 0

        return 1

    def _in_stores(self):
        if self.product_info_json["productItem"]["productDetails"].get("isStorePickUpEligible", False):
            return 1

        return 0

    def _site_online_out_of_stock(self):
        if self._is_out_of_stock():
            return 1

        if self._marketplace() == 1:
            return None

        if not self.tree_html.xpath("//meta[@itemprop='availability' and @content='http://schema.org/InStock']"):
            return 1

        return 0

    def _marketplace_sellers(self):
        sellers = self.tree_html.xpath("//div[@class='marketplacePDP']//a[@id='pdp_vendor']/text()")

        if sellers:
            return sellers

        return None

    def _marketplace_lowest_price(self):
        marketplace_prices = self._marketplace_prices()

        if marketplace_prices:
            return min(marketplace_prices)

        return None

    def _marketplace_prices(self):
        if self._marketplace() == 1:
            return [self._price_amount()]

        return None

    def _marketplace_out_of_stock(self):
        if self._marketplace() == 1:
            if not self.tree_html.xpath("//meta[@itemprop='availability' and @content='http://schema.org/InStock']"):
                return 1
            else:
                return 0

        return None

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################    
    def _categories(self):
        return None

    def _category_name(self):
        return None

    def _brand(self):
        brand = re.search('googletag\.pubads\(\)\.setTargeting\("brd", "(.+?)"', self.page_raw_text).group(1)
        return brand

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
        "swatches": _swatches,
        "no_longer_available": _no_longer_available,

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
        "pdf_count" : _pdf_count, \
        "pdf_urls" : _pdf_urls, \
        "wc_360": _wc_360, \
        "wc_emc": _wc_emc, \
        "wc_video": _wc_video, \
        "wc_pdf": _wc_pdf, \
        "wc_prodtour": _wc_prodtour, \
        "webcollage": _webcollage, \
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
        "marketplace" : _marketplace, \
        "site_online": _site_online, \
        "site_online_out_of_stock": _site_online_out_of_stock, \
        "in_stores" : _in_stores, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_out_of_stock": _marketplace_out_of_stock, \
        "marketplace_prices" : _marketplace_prices, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \
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
