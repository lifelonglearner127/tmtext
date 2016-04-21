#!/usr/bin/python

import urllib
import re
import sys
import json
import ast
from lxml import html, etree
import time
import yaml
import requests
from extract_data import Scraper
from compare_images import compare_images


class MicrosoftScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.microsoftstore.com/store/msusa/en_US/pdp/<product-title>/productID.<product-id>"

    REVIEW_URL = 'http://api.bazaarvoice.com/data/batch.json?passkey=291coa9o5ghbv573x7ercim80&apiversion=5.5&displaycode=5681-en_us&resource.q0=products&filter.q0=id%3Aeq%3A{0}&stats.q0=questions%2Creviews&filteredstats.q0=questions%2Creviews'

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.product_json = None
        # whether product has any webcollage media
        self.review_json = None
        self.review_list = None
        self.is_review_checked = False

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^http://www\.microsoftstore\.com/store/msusa/en_US/pdp/(.*/)?productID\.[0-9]+(\?icid=.*)?$", self.product_page_url)
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
            itemtype = self.tree_html.xpath('//meta[@property="og:type"]/@content')[0].strip()

            if itemtype != "product":
                raise Exception()

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

    def _event(self):
        return None

    def _product_id(self):
        product_id = self.tree_html.xpath('//div[@data-basepproductid]/@data-basepproductid')[0]
        return product_id

    def _site_id(self):
        product_id = self.tree_html.xpath('//div[@data-basepproductid]/@data-basepproductid')[0]
        return product_id

    def _status(self):
        return "success"

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//div[@class="title-block title-desktop"]/h1/text()')[0].strip()

    def _product_title(self):
        return self.tree_html.xpath('//div[@class="title-block title-desktop"]/h1/text()')[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath('//div[@class="title-block title-desktop"]/h1/text()')[0].strip()

    def _model(self):
        return None

    def _upc(self):
        upc_list = re.search( 'upc : (\[[^\]]*\])', html.tostring(self.tree_html)).group(1)
        upc_list = ast.literal_eval(upc_list)
        return upc_list[0]

    def _features(self):
        features_block_list = self.tree_html.xpath("//section[@id='techspecs']//div[contains(@class, 'grid-row')]")
        features_list = []

        if features_block_list:
            for feature_block in features_block_list:
                feature_title = feature_block.xpath(".//div[contains(@class, 'grid-unit')]")[0].text_content().strip()
                feature_text = feature_block.xpath(".//div[contains(@class, 'grid-unit')]")[1].text_content().strip()
                features_list.append(feature_title + ": " + feature_text)

            if features_list:
                return features_list

        return None

    def _feature_count(self):
        if self._features():
            return len(self._features())

        return None

    def _model_meta(self):
        return None

    def _description(self):
        description = self.tree_html.xpath("//div[@class='description-block description-desktop']/div[contains(@class, 'short-desc')]")

        if description and len(description[0].text_content().strip()) > 0:
            return description[0].text_content().strip()

        return None

    def _long_description(self):
        description = self.tree_html.xpath("//section[@id='overview']")

        if description and len(self._clean_text(description[0].text_content().strip())) > 0:
            return self._clean_text(description[0].text_content().strip())

        return None

    def _variants(self):
        variants = []
        for li in self.tree_html.xpath('//div[contains(@class,"variation-container")]/ul[contains(@class,"option-list")]/li'):
            v = { 'variant' : self._clean_text(li.xpath('a/span/text()')[0]) }

            if li.get('class') == 'active':
                v['selected'] = True
            else:
                v['selected'] = False

            variants.append(v)

        i = 0
        for price in self.tree_html.xpath('//p[@itemprop="price"]'):
            variants[i]['price'] = self._clean_text(price.text_content())
            i += 1

        if variants:
            return variants


    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):        
        url_list = self.tree_html.xpath("//div[contains(@class, 'grid-row media-container')]/ul[contains(@class, 'product-hero')]//img/@src")

        if url_list:
            for index, url in enumerate(url_list):
                if not url.startswith("https://"):
                    url_list[index] = "https:" + url

            image_urls = []

            for url in url_list:
                if "360_Overlay.png" not in url \
                    and "/Spin/" not in url \
                    and not re.search( '(VID|Video-)\d+', url) \
                    and url not in image_urls:

                    image_urls.append(url)

            if image_urls:
                return image_urls

        return None

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def _video_urls(self):
        video_urls = []

        video_sources = self.tree_html.xpath('//div[contains(@class,"video-container")]/@data-video-sources')
        for source in video_sources:
            for video in source.split(';'):
                if '.mp4' in video and not video in video_urls:
                    video_urls.append(video)

        # Add youtube videos
        for video in self.tree_html.xpath('//div[contains(@class,"youtube-container")]/@data-src'):
            if not video.split('?')[0] in video_urls:
                video_urls.append(video.split('?')[0])

        if video_urls:
            return video_urls

    def _video_count(self):
        videos = self._video_urls()

        if videos:
            return len(videos)

        return 0

    def _pdf_urls(self):
        return None

    def _pdf_count(self):
        if self._pdf_urls():
            return len(self._pdf_urls())

        return 0

    def _webcollage(self):
        return None

    def _htags(self):
        htags_dict = {}
        # add h1 tags text to the list corresponding to the "h1" key in the dict
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        # add h2 tags text to the list corresponding to the "h2" key in the dict
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    def _keywords(self):
        return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]

    
    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################

    def _average_review(self):
        if self._review_count() > 0:
            average_review = float(self.tree_html.xpath("//div[@id='bvseo-aggregateRatingSection']//span[@class='bvseo-ratingValue' and @itemprop='ratingValue']/text()")[0])
            return average_review

        return None

    def _review_count(self):
        try:
            review_count = int(self.tree_html.xpath("//div[@id='bvseo-aggregateRatingSection']//span[@class='bvseo-reviewCount' and @itemprop='reviewCount']/text()")[0].replace(',',''))

            if review_count > 0:
                return review_count
        except:
            pass

        return 0

    def _max_review(self):
        if self._review_count() > 0:
            reviews = self._reviews()
            max_review = reviews[0]

            for review in reviews:
                if max_review[0] < review[0]:
                    max_review = review

            return int(max_review[0])

        return None

    def _min_review(self):
        if self._review_count() > 0:
            reviews = self._reviews()
            min_review = reviews[0]

            for review in reviews:
                if min_review[0] > review[0]:
                    min_review = review

            return int(min_review[0])

        return None

    def _reviews(self):
        if self._review_count() > 0:
            review_list = []
            review_json = self.load_page_from_url_with_number_of_retries(self.REVIEW_URL.format(self._product_id()))
            review_json = json.loads(review_json)

            for i in range(5):
                review_list.append([5-i, 0])

            for review in review_json["BatchedResults"]["q0"]["Results"][0]["FilteredReviewStatistics"]["RatingDistribution"]:
                review_list[5 - int(review["RatingValue"])] = [int(review["RatingValue"]), int(review["Count"])]

            if review_list:
                return review_list

        return None

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        price = self.tree_html.xpath("//div[@class='product-data-container']//div[@class='price-block']//p[@class='current-price' and @itemprop='price']")[0].text_content().strip()
        return price

    def _price_amount(self):
        return float(re.findall(r"\d*\.\d+|\d+", self._price().replace(",", ""))[0])

    def _price_currency(self):
        return self.tree_html.xpath("//meta[@itemprop='priceCurrency']/@content")[0]

    def _in_stores(self):
        return 0

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):
        return 0

    def _in_stores_out_of_stock(self):
        return 0

    def _marketplace(self):
        return 0

    def _seller_from_tree(self):
        return None

    def _marketplace_sellers(self):
        return None

    def _marketplace_lowest_price(self):
        return None


    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        return None

    def _category_name(self):
        return None
    
    def _brand(self):
        return None


    ##########################################
    ################ RETURN TYPES
    ##########################################

    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service

    DATA_TYPES = { \
        # CONTAINER : NONE
        "url" : _url, \
        "event" : _event, \
        "product_id" : _product_id, \
        "site_id" : _site_id, \
        "status" : _status, \

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "model" : _model, \
        "upc" : _upc,\
        "features" : _features, \
        "feature_count" : _feature_count, \
        "model_meta" : _model_meta, \
        "description" : _description, \
        "long_description" : _long_description, \
        "variants" : _variants, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
        "pdf_count" : _pdf_count, \
        "pdf_urls" : _pdf_urls, \
        "webcollage" : _webcollage, \
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
        "in_stores" : _in_stores, \
        "site_online": _site_online, \
        "site_online_out_of_stock": _site_online_out_of_stock, \
        "in_stores_out_of_stock": _in_stores_out_of_stock, \
        "marketplace" : _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \

        "loaded_in_seconds" : None, \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "mobile_image_same" : _mobile_image_same, \
    }
