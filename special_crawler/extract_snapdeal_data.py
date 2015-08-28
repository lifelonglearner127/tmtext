#!/usr/bin/python

import re
import lxml
import lxml.html
import requests
import json

from itertools import groupby

from lxml import html, etree
from extract_data import Scraper
from spiders_shared_code.snapdeal_variants import SnapdealVariants


class SnapdealScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.snapdeal.com/product/<product-name>/<product-id>"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.reviews = None
        self.average_review = 0
        self.max_review = 0
        self.min_review = 0
        self.review_count = 0
        self.is_review_checked = False

        self.sv = SnapdealVariants()

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match(r"^http://www\.snapdeal\.com/product/.*/[0-9]+$", self.product_page_url)

        return not not m

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """

        self.sv.setupCH(self.tree_html)

        try:
            if self.tree_html.xpath("//meta[@property='og:type']/@content")[0] != "snapdeallog:item":
                raise Exception
        except Exception:
            return True

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
        return self.product_page_url.split('/')[-1]

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//meta[@name='og_title']/@content")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//meta[@name='og_title']/@content")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//meta[@name='og_title']/@content")[0].strip()

    def _model(self):
        return None

    def _features(self):
        try:
            features_td_list = self.tree_html.xpath("//table[@class='product-spec']//tr/td")
            features = []

            for index, td in enumerate(features_td_list):
                if (index + 1) % 2 != 0:
                    continue

                features.append(features_td_list[index - 1].text_content() + " " + td.text_content())

            if not features:
                return None

            return features
        except:
            return None

    def _feature_count(self):
        features = self._features()

        if not features:
            return 0

        return len(features)

    def _description(self):
        description = None

        try:
            spec_title_list = self.tree_html.xpath("//h3[@class='spec-title']")
            short_description = None

            for spec_title in spec_title_list:
                if "Highlights" in spec_title.text_content():
                    short_description = spec_title.xpath("./../following-sibling::div[@class='spec-body']")[0].text_content().strip()
                    break

            if short_description:
                return short_description
        except:
            return None

        return None

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description(self):
        try:
            description = self.tree_html.xpath("//div[@itemprop='description' and @class='detailssubbox']")[0].text_content().strip()

            return description
        except:
            return None

        return None

    def _ingredients(self):
        return None

    def _ingredients_count(self):
        return None

    def _variants(self):
        return self.sv._variants()

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        pass
        
    def _image_urls(self):
        image_urls = self.tree_html.xpath("//div[@class='baseSliderPager']//img/@src")
        lazy_image_urls = self.tree_html.xpath("//div[@class='baseSliderPager']//img/@lazysrc")
        image_urls = image_urls + lazy_image_urls

        if not image_urls:
            image_urls = self.tree_html.xpath("//div[@id='bx-pager-left-image-panel']//img/@src")
            lazy_image_urls = self.tree_html.xpath("//div[@id='bx-pager-left-image-panel']//img/@lazysrc")
            image_urls = image_urls + lazy_image_urls

        if not image_urls:
            return None

        return image_urls

    def _image_count(self):
        image_urls = self._image_urls()

        if not image_urls:
            return 0

        return len(image_urls)

    def _video_urls(self):
        iframe_list = self.tree_html.xpath("//iframe")

        youtubu_iframes = []

        for iframe in iframe_list:
            if "www.youtube.com" in iframe.xpath("./@lazysrc")[0]:
                youtubu_iframes.append(iframe)

        if not youtubu_iframes:
            return None

        youtubu_urls = []

        for iframe in youtubu_iframes:
            youtubu_urls.append(iframe.xpath("./@lazysrc")[0].strip())

        return youtubu_urls

    def _video_count(self):
        video_urls = self._video_urls()

        if not video_urls:
            return 0

        return len(video_urls)

    # return dictionary with one element containing the PDF
    def _pdf_urls(self):
        return None

    def _pdf_count(self):
        return 0

    def _wc_emc(self):
        return 0

    def _wc_prodtour(self):
        return 0

    def _wc_360(self):
        return 0

    def _wc_video(self):
        return 0

    def _wc_pdf(self):
        return 0

    def _webcollage(self):
        if self._wc_360() == 1 or self._wc_prodtour() == 1 or self._wc_pdf() == 1 or self._wc_emc() == 1 or self._wc_360():
            return 1

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
        self._reviews()

        return self.average_review

    def _review_count(self):
        self._reviews()

        return self.review_count

    def _max_review(self):
        self._reviews()

        return self.max_review

    def _min_review(self):
        self._reviews()

        return self.min_review

    def _reviews(self):
        if self.is_review_checked:
            return self.reviews

        self.is_review_checked = True

        rating_blocks = self.tree_html.xpath("//ul[@itemprop='aggregateRating']//div[contains(@class, 'row')]")

        review_list = []
        max_review = None
        min_review = None

        for rating_block in rating_blocks:
            review_rate = int(rating_block.xpath(".//span[contains(@class, 'lfloat')]/text()")[0][0])
            review_count = int(rating_block.xpath(".//span[contains(@class, 'barover')]/following-sibling::span/text()")[0])
            review_list.append([review_rate, review_count])

            if not max_review:
                max_review = review_rate
            elif review_count > 0 and review_rate > max_review:
                max_review = review_rate

            if not min_review:
                min_review = review_rate
            elif review_count > 0 and review_rate < min_review:
                min_review = review_rate

        self.reviews = review_list
        self.average_review = float(self.tree_html.xpath("//span[@itemprop='ratingValue']/text()")[0].strip())
        self.review_count = int(self.tree_html.xpath("//span[@itemprop='ratingCount']/text()")[0].strip())
        self.max_review = max_review
        self.min_review = min_review

        return self.reviews

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        return "Rs " + self.tree_html.xpath("//span[@itemprop='price']/text()")[0]

    def _price_amount(self):
        price_amount = self.tree_html.xpath("//input[@id='productPrice']/@value")[0]

        if str(int(price_amount)) == price_amount:
            return int(price_amount)
        else:
            return float(price_amount)

        return None

    def _price_currency(self):
        return self.tree_html.xpath("//meta[@itemprop='priceCurrency']/@content")[0]

    def _site_online(self):
        return 1

    def _in_stores(self):
        return 1

    def _site_online_out_of_stock(self):
        if self.tree_html.xpath("//div[@class='container-fluid inStockNotify reset-padding ']"):
            return 1

        return 0

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################    
    def _categories(self):
        return self.tree_html.xpath("//div[@class='containerBreadcrumb']//span[@itemprop='title']/text()")

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        return self.tree_html.xpath("//input[@id='brandName']/@value")[0]

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
        "site_online": _site_online, \
        "site_online_out_of_stock": _site_online_out_of_stock, \
        "in_stores" : _in_stores, \

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
