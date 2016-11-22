#!/usr/bin/python

import HTMLParser
import itertools
import json
import re
import requests

from lxml import html, etree
import xml.etree.ElementTree as ET
from extract_data import Scraper
from spiders_shared_code.verizonwireless_variants import VerizonWirelessVariants

class VerizonWirelessScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is https?://www.verizonwireless.com/<product-category>/<product-name>$"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.wc_360 = 0
        self.wc_emc = 0
        self.wc_video = 0
        self.wc_pdf = 0
        self.wc_prodtour = 0

        self.features = None
        self.ingredients = None
        self.images = None
        self.videos = None
        self.json_data = None
        self.review_json = None
        self.review_list = None
        self.REVIEW_URL = "http://api.bazaarvoice.com/data/batch.json?passkey=e8bg3vobqj42squnih3a60fui&apiversion=5.5&displaycode=6543-en_us&resource.q0=products&filter.q0=id%3Aeq%3A{0}&stats.q0=questions%2Creviews&filteredstats.q0=questions%2Creviews"
        self.av = VerizonWirelessVariants()

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match('^https?://www.verizonwireless.com/.*$', self.product_page_url)
        return not not m

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        if not (self.tree_html.xpath('//*[@itemtype="http://schema.org/Product"]') \
            or self.tree_html.xpath('//script[@id="accessoryPdpJson"]')):
            return True
        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _canonical_link(self):
        return self.tree_html.xpath('//link[@rel="canonical"]/@href')[0]

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        sku_text = self.tree_html.xpath('//*[@id="sku-id"]/text()')
        if sku_text:
            search_sku = re.search('\#(.*)', sku_text[0])
            return search_sku.group(1).strip() if search_sku else None

        return None

    def _site_id(self):
        return None

    def _status(self):
        return "success"

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self._product_title()

    def _product_title(self):
        title = self.tree_html.xpath('//*[@itemprop="name"]/text()')
        return title[0].strip() if title else None

    def _title_seo(self):
        return self._product_title()

    def _model(self):
        model = re.search('deviceModel":"(.*?)"', html.tostring(self.tree_html))
        return model.group(1) if model else None        

    def _manufacturer(self):
        model = re.search('deviceManufacturer":"(.*?)"', html.tostring(self.tree_html))  
        return model.group(1) if model else None        

    def _upc(self):
        return None

    def _features(self):
        features = self.tree_html.xpath(
            '//h2[@class="margin36 onlyTopMargin"]/text()')
        features += self.tree_html.xpath(
            '//*[@class="features"]//ul/li/text()')

        features = filter(None, map((lambda x: x.strip()), features))

        return features if features else None

    def _feature_count(self):
        features = self._features()
        return len(features) if features else 0

    def _model_meta(self):
        return None

    def _description(self):
        description = self.tree_html.xpath(
            '//*[@itemprop="description" and '
            '@class="is-hidden"]//text()')

        return ''.join(filter(None, map((lambda x: x.strip()),description))).strip() if description else None

    def _long_description(self):
        return None

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _load_json_data(self):
        image_urls = self.tree_html.xpath(
            '//*[@property="og:image"]/@content')[0].split('?')[0]
        image_urls += "-mms?req=set,json,UTF-8&labelkey=label"
        response = requests.get(image_urls)
        json_text = re.findall('s7jsonResponse\((.*),"', response.text)
        self.json_data = json.loads(json_text[0])

    def _image_urls(self):
        if self.images:
            return self.images

        self.images = []

        try:
            main_image_url = self.tree_html.xpath('//input[@id="MainProductImageURL"]/@value')[0].split('?')[0]

            c = requests.get(main_image_url + '?req=set').content
            x = ET.fromstring(c)

            for item in x:
                self.images.append('https://ss7.vzw.com/is/image/' + item[0].get('n'))

            if self.images:
                return self.images

        except:
            pass

        try:
            if not self.images:
                if not self.json_data:
                    self._load_json_data()

                data = self.json_data.get('set', {})
                self.images = []
                images = []
                if data.get('type', None) == 'media_set':
                    try:
                        images += list(itertools.chain.from_iterable([x.get(
                            'set', {}).get('item') for x in data[
                                'item'] if x.get('type') == 'img_set']))
                        images = [x for x in data['item'] if x.get('dx')] + images

                    except:
                        data = self.json_data['set']['item']

                if data.get('set', {}).get('type', None) == 'img_set':
                    images += data.get('set', {}).get('item', [])

                for img in images:
                    self.images.append(
                        "https://ss7.vzw.com/is/image/" + img['i']['n'])

        except:
            self.images = [self.tree_html.xpath(
                '//*[@property="og:image"]/@content')[0].split('?')[0]]

        return self.images if self.images else [self.tree_html.xpath(
            '//*[@property="og:image"]/@content')[0].split('?')[0]]

    def _image_count(self):
        if not self.images:
            self.images = self._image_urls()

        return len(self.images) if self.images else None

    def _video_urls(self):
        if not self.videos:
            if not self.json_data:
                self._load_json_data()

            data = self.json_data.get('set', {})
            videos = []

            if data.get('type', None) == 'media_set':
                try:
                    videos += [x.get('set', {}).get('item', [])[-1] for x in data['item'] if x.get('type')=='video_set']
                    videos += [x for x in data['item'] if x.get('type') == 'video']
                except:
                    pass

            self.videos = []
            for video in videos:
                self.videos.append(
                    "https://ss7.vzw.com/is/content/" + video['i']['n'])

        return self.videos

    def _video_count(self):
        videos = self._video_urls()
        return len(videos) if videos else 0

    def _pdf_urls(self):
        return None

    def _pdf_count(self):
        return 0

    def _webcollage(self):
        """Uses video and pdf information
        to check whether product has any media from webcollage.
        Returns:
            1 if there is webcollage media
            0 otherwise
        """
        if self.wc_360 + self.wc_emc + self.wc_pdf + self.wc_prodtour + self.wc_video > 0:
            return 1

        return 0

    def _wc_360(self):
        if not self.json_data:
            self._load_json_data()

        try:
            data = self.json_data.get('set', {})
            self.wc_360 = 1 if len(filter((lambda x: x.get('type') == 'spin'),
                                   data.get('item'))) else 0
        except:
            self.wc_360 = 0

        return self.wc_360

    def _wc_emc(self):
        self._webcollage()

        return self.wc_emc

    def _wc_pdf(self):
        self._webcollage()

        return self.wc_pdf

    def _wc_prodtour(self):
        self._webcollage()

        return self.wc_prodtour

    def _wc_video(self):
        self._webcollage()

        return self.wc_video

    def _htags(self):
        htags_dict = {}

        htags_dict['h1'] = map(lambda t: self._clean_text(t), self.tree_html.xpath('//h1//text()[normalize-space()!=""]'))
        htags_dict['h2'] = map(lambda t: self._clean_text(t), self.tree_html.xpath('//h2//text()[normalize-space()!=""]'))

        return htags_dict

    def _keywords(self):
        keywords = self.tree_html.xpath('//meta[@name="keywords"]/@content')
        return keywords[0] if keywords else None

    def _variants(self):
        self.av.setupCH(self.tree_html)
        return self.av._variants()

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    def _average_review(self):
        average_review = self.review_json["BatchedResults"]["q0"][
            "Results"][0]["FilteredReviewStatistics"]["AverageOverallRating"]
        return round(float(average_review), 1) if average_review else None

    def _review_count(self):
        if not self.review_json:
            self._load_review_json()

        review_count = self.review_json["BatchedResults"]["q0"]["Results"][0][
            "FilteredReviewStatistics"]["TotalReviewCount"]
        return review_count

    def _max_review(self):
        if not self.review_json:
            self._load_review_json()

        if not self.review_list:
            self._reviews()

        not_zero_reviews = filter((lambda x: x[1]), self.review_list)
        max_review = max(not_zero_reviews, key=(lambda x: x[0]))

        return int(max_review[0])

        return None

    def _min_review(self):
        if not self.review_json:
            self._load_review_json()

        if not self.review_list:
            self._reviews()

        not_zero_reviews = filter((lambda x: x[1]), self.review_list)
        min_review = min(not_zero_reviews, key=(lambda x: x[0]))

        return int(min_review[0])

        return None

    def _reviews(self):
        if not self.review_json:
            self._load_review_json()

        if not self.review_list:
            review_list = []
            for i in range(5):
                review_list.append([5 - i, 0])

            for review in self.review_json["BatchedResults"]["q0"]["Results"][0]["FilteredReviewStatistics"]["RatingDistribution"]:
                review_list[5 - int(review["RatingValue"])] = [int(review["RatingValue"]), int(review["Count"])]

            if review_list:
                self.review_list = review_list

        return self.review_list

    def _load_review_json(self):
        content = html.tostring(self.tree_html)
        device_prod_id_search = re.search('deviceProdId=(.*?)&', content)

        if device_prod_id_search:
            id = device_prod_id_search.group(1)

        else:
            id = self.tree_html.xpath('//input[@id="isProductId"]/@value')[0]

        self.review_json = self.load_page_from_url_with_number_of_retries(
            self.REVIEW_URL.format(id))
        self.review_json = json.loads(self.review_json)


    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _in_stock(self):
        in_stock = self.tree_html.xpath(
            '//*[@itemprop="availability" and @href="//schema.org/InStock"]')
        return int(bool(in_stock))

    def _price(self):
        price = re.search(
            'price"\s*:\s*"\$?(.*?)"', html.tostring(self.tree_html))
        return price.group(1) if price else None

    def _price_amount(self):
        return float(self._price())

    def _price_currency(self):
        currency = self.tree_html.xpath('//*[@itemprop="priceCurrency"]/@content')
        return currency[0] if currency else None

    def _in_stores(self):
        return None

    def _site_online(self):
        return 1

    def _site_online_out_of_stock(self):
        availability = self.tree_html.xpath('//link[@itemprop="availability"]/@href')[0]
        return 1 if availability != 'http://schema.org/InStock' else 0

    def _in_stores_out_of_stock(self):
        return None

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
        devices = ['/tablets/', '/smartphones/', '/basic-phones/']
        url = self.product_page_url
        categories = self.tree_html.xpath(
            '//*[@itemtype="https://data-vocabulary.org/Breadcrumb"]'
            '//span[@itemprop="title"]/text()')
        if categories and any([x in url for x in devices]):
            categories.insert(1, 'Devices')
        return categories

    def _category_name(self):
        categories = self._categories()
        return categories[-1] if categories else None

    def _brand(self):
        brand = self.tree_html.xpath('//*[@itemprop="brand"]/text()')
        return brand[0].strip() if brand else None

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################  
    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        text = HTMLParser.HTMLParser().unescape(text)
        text = re.sub('[\r\n]', '', text)
        return text.strip()

    ##########################################
    ################ RETURN TYPES
    ##########################################

    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service

    DATA_TYPES = {
        # CONTAINER : NONE
        "url": _url,
        "event": _event,
        "product_id": _product_id,
        "site_id": _site_id,
        "status": _status,

        # CONTAINER : PRODUCT_INFO
        "product_name": _product_name,
        "product_title": _product_title,
        "title_seo": _title_seo,
        "model": _model,
        "upc": _upc,\
        "manufacturer": _manufacturer,
        "features": _features,
        "feature_count": _feature_count,
        "model_meta": _model_meta,
        "description": _description,
        "long_description": _long_description,
        "variants": _variants,

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count": _image_count,
        "image_urls": _image_urls,
        "video_count": _video_count,
        "video_urls": _video_urls,
        "pdf_count": _pdf_count,
        "pdf_urls": _pdf_urls,
        "wc_360": _wc_360,
        "wc_emc": _wc_emc,
        "wc_video": _wc_video,
        "wc_pdf": _wc_pdf,
        "wc_prodtour": _wc_prodtour,
        "webcollage": _webcollage,
        "htags": _htags,
        "keywords": _keywords,
        "canonical_link": _canonical_link,

        # CONTAINER : REVIEWS
        "review_count": _review_count,
        "average_review": _average_review,
        "max_review": _max_review,
        "min_review": _min_review,
        "reviews": _reviews,

        # CONTAINER : SELLERS
        "in_stock": _in_stock,
        "price": _price,
        "price_amount": _price_amount,
        "price_currency": _price_currency,
        "in_stores": _in_stores,
        "site_online": _site_online,
        "site_online_out_of_stock": _site_online_out_of_stock,
        "in_stores_out_of_stock": _in_stores_out_of_stock,
        "marketplace": _marketplace,
        "marketplace_sellers": _marketplace_sellers,
        "marketplace_lowest_price": _marketplace_lowest_price,

        # CONTAINER : CLASSIFICATION
        "categories": _categories,
        "category_name": _category_name,
        "brand": _brand,

        "loaded_in_seconds": None}

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = {"mobile_image_same": _mobile_image_same}
