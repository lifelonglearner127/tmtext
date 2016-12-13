#!/usr/bin/python
#  -*- coding: utf-8 -*-

import urllib
import urllib2
import re
import sys
import json
import os.path
import urllib, cStringIO
from io import BytesIO
from PIL import Image
import mmh3 as MurmurHash
from lxml import html
from lxml import etree
import time
import requests
from extract_data import Scraper
from spiders_shared_code.macys_variants import MacysVariants, normalize_product_json_string
CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CWD, '../product-ranking'))
from product_ranking.guess_brand import guess_brand_from_first_words


class MacysScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www1\.macys\.com/shop/(.*)"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.review_json = None
        self.price_json = None
        self.mv = MacysVariants()

        self.reviews_tree = None
        self.max_score = None
        self.min_score = None
        self.review_count = None
        self.average_review = None
        self.reviews = None
        self.feature_count = None
        self.features = None
        self.video_urls = None
        self.video_count = None
        self.pdf_urls = None
        self.pdf_count = None
        self.is_review_checked = False
        self.product_info_json = None
        self.is_product_info_json_checked = False
        self.is_bundle = False

    def check_url_format(self):
        # for ex: http://www1.macys.com/shop/product/closeout-biddeford-comfort-knit-fleece-heated-king-blanket?ID=694761
        m = re.match(r"^http://www1\.macys\.com/shop/(.*)", self.product_page_url)
        return not not m

    def _extract_product_info_json(self):
        if self.is_product_info_json_checked:
            return self.product_info_json

        self.is_product_info_json_checked = True

        try:
            if self.is_bundle:
                product_info_json = self.tree_html.xpath("//script[@id='pdpMainData' and @type='application/json']/text()")

                if product_info_json:
                    product_info_json = json.loads(product_info_json[0])['productDetail']
            else:
                product_info_json = self.tree_html.xpath("//script[@id='productMainData' and @type='application/json']/text()")

                if product_info_json:
                    product_info_json = json.loads(normalize_product_json_string(product_info_json[0]))
        except:
            product_info_json = None

        self.product_info_json = product_info_json

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''

        #if len(self.tree_html.xpath("//div[@id='imageZoomer']//div[contains(@class,'main-view-holder')]/img")) < 1:
        #    return True
        if len(self.tree_html.xpath("//*[contains(@class, 'productTitle')]")) < 1:
            return True

        if len(self.tree_html.xpath("//div[@id='viewCollectionItemsButton']")) > 0:
            self.is_bundle = True

        self.mv.setupCH(self.tree_html, self.is_bundle)

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
        return self.mv._get_prod_id()

    def _site_id(self):
        # TODO: should this be the product ID?
        #site_id = self.tree_html.xpath("//input[@id='productId']/@value")[0].strip()
        site_id = None
        return site_id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        try:
            return self.tree_html.xpath("//h1[contains(@class, 'productName')]//text()")[0].strip()
        except:
            return self.tree_html.xpath("//h1[@id='productTitle']/text()")[0].strip()

    def _product_title(self):
        return self._product_name()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()
    
    def _model(self):
        return None

    def _upc(self):
        upc = None
        try:
            variants = self._variants()
        except:
            return self.product_info_json['upcMap'][self._product_id()][0]['upc']

        if not variants:
            upc = re.findall(r'"upc": "(.*?)",', html.tostring(self.tree_html), re.DOTALL)[0]
        elif len(variants) == 1:
            upc = variants[0]["upc"]

        return upc

    def _features(self):
        if self.feature_count is not None:
            return self.features
        self.feature_count = 0
        rows = self.tree_html.xpath("//div[@id='prdDesc']//ul[contains(@class,'bullets')]/li")
        line_txts = []
        for row in rows:
            txt = "".join([r for r in row.xpath(".//text()") if len(self._clean_text(r)) > 0]).strip()
            if len(txt) > 0:
                line_txts.append(txt)
        if len(line_txts) < 1:
            return None
        self.feature_count = len(line_txts)
        self.features = line_txts
        return self.features

    def _feature_count(self):
        if self.feature_count is None:
            self._features()
        return self.feature_count

    def _model_meta(self):
        return None

    def _description(self):
        description = self.tree_html.xpath("//div[@id='longDescription']")[0].text_content().strip()

        if description:
            return description

        return None

    def _description_helper(self):
        description = ""
        rows = self.tree_html.xpath("//div[@id='prdDesc']//div[@itemprop='description']/text()")
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        if len(rows) > 0:
            description += "\n".join(rows)
        if len(description) < 1:
            description = ""
            rows = self.tree_html.xpath("//div[@id='productDetails']//text()")
            rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
            if len(rows) > 0:
                description += "\n".join(rows)
            if len(description) < 1:
                return None
            if description.startswith("Product Details"):
                description = description.replace("Product Details\n", "")
        return description

    def _long_description(self):
        '''
        description = self._description_helper()
        if description is None or len(description) < 1:
            return None
        return self._long_description_helper()
        '''
        return html.tostring(self.tree_html.xpath("//ul[@id='bullets']")[0])

    def _long_description_helper(self):
        script = " ".join(self.tree_html.xpath("//script//text()"))
        link = re.findall(r"MACYS\.adLinkPopUp\.definePopup\('(.*?)'", script, re.DOTALL)
        try:
            link = "http://www1.macys.com/shop/media/popup/?popupFileName=%s" % link[0]
            req = urllib2.Request(link, headers={'User-Agent' : "Magic Browser"})
            contents = urllib2.urlopen(req).read()
            # document.location.replace('
            tree = html.fromstring(contents)
            rows = tree.xpath("//text()")
            line_txts = []
            txt = "\n".join([r for r in rows if len(self._clean_text(r)) > 0]).strip()
            if len(txt) > 0:
                line_txts.append(txt)
            if len(line_txts) < 1:
                return None
            description = "\n".join(line_txts)
            return description
        except IndexError:
            pass

    def _variants(self):
        return self.mv._variants()

    def _swatches(self):
        return self.mv._swatches()

    def _no_longer_available(self):
        try:
            currently_unavailable = self.tree_html.xpath("//span[contains(text(),'This product is currently unavailable')]")
            return bool(currently_unavailable)
        except:
            pass

        return False


    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        if not self.product_info_json:
            return self.tree_html.xpath('//div[@class="productImageSection"]/img/@src')

        image_url = self.product_info_json['imageUrl']

        try:
            if self._no_image(image_url):
                return None
        except Exception, e:
            print "WARNING: ", e.message

        if self.is_bundle:
            image_url_frags = []

            for additional_images in re.findall('MACYS.pdp.memberAdditionalImages\[\d+\] = "([^"]*)"', self.page_raw_text):
                image_url_frags += additional_images.split(',')

            for additional_images in re.findall('MACYS.pdp.additionalImages\[\d+\] = ({[^}]*})', self.page_raw_text):
                for frag_string in json.loads(additional_images).itervalues():
                    image_url_frags += frag_string.split(',')

        else:
            image_url_frags = [self.product_info_json['images']['imageSource']]
            
            image_url_frags += self.product_info_json['images']['additionalImages']
            
            image_url_frags += self.product_info_json['images']['colorwayPrimaryImages'].values()
            
            for c in self.product_info_json['images']['colorwayAdditionalImages'].values():
                image_url_frags += c.split(',')

        image_urls_tmp = map(lambda f: "http://slimages.macysassets.com/is/image/MCY/products/%s" % f, image_url_frags)

        image_urls = []

        # Remove duplicates
        for image_url in image_urls_tmp:
            if not image_url in image_urls:
                image_urls.append( image_url )

        return image_urls

    def _image_count(self):
        image_urls = self._image_urls()
        if image_urls is None:
            return 0
        return len(image_urls)

    def _video_urls(self):
        if self.video_count is not None:
            return self.video_urls
        self.video_count = 0
        video_urls = []
        rows = re.findall(r'videoid: "(.*?)"', " ".join(self.tree_html.xpath("//script//text()")), re.DOTALL)
        video_urls = rows

        url_template = "http://c.brightcove.com/services/viewer/federated_f9?&width=328&height=412&flashID={}_v&bgcolor=%23FFFFFF&playerID=34437976001&publisherID=24953835001&%40videoPlayer=ref%3A{}&isVid=true&isUI=true&wmode=transparent"
        video_urls = [url_template.format(r, r) for r in video_urls]

        for video_id in re.findall('"videoID": "([^"]+)"', html.tostring(self.tree_html)):
            videos_json = json.loads(requests.get('https://edge.api.brightcove.com/playback/v1/accounts/24953835001/videos/ref:' + video_id, headers={'Accept': 'application/json;pk=BCpkADawqM1zkb9gepUqJUigGl8BbTj-cvrHiWCc8KIrwo2ex89DkqokI_tsvGDhn2oB4dO9v8tyPUgiUaYoKJmqA8Ia7kzcrVVVAbd3VjZdjOCnHjyJbqTFvAw'}).content)

            max_size = None

            for source in videos_json['sources']:
                if source.get('src'):
                    if not max_size or source.get('size') > max_size:
                        max_size = source['size']

            for source in videos_json['sources']:
                if source['size'] == max_size and source.get('src'):
                    video_urls.append(source['src'].split('?')[0])
                    break

        self.video_count = len(video_urls)
        if video_urls:
            self.video_urls = video_urls
            return self.video_urls

    def _video_count(self):
        if self.video_count is None:
            self._video_urls()
        return self.video_count

    def _pdf_urls(self):
        if self.pdf_count is not None:
            return self.pdf_urls
        self.pdf_count = 0
        pdf_hrefs = []
        if len(pdf_hrefs) < 1:
            return None
        self.pdf_count = len(pdf_hrefs)
        return pdf_hrefs

    def _pdf_count(self):
        if self.pdf_count is None:
            self._pdf_urls()
        return self.pdf_count

    def _bundle(self):
        return self.is_bundle

    # extract htags (h1, h2) from its product product page tree
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
    #populate the reviews_tree variable for use by other functions
    def _load_reviews(self):
        try:
            if not self.is_review_checked:
                self.is_review_checked = True
                # http://macys.ugc.bazaarvoice.com/7129aa/694761/reviews.djs?format=embeddedhtml
                url = "http://macys.ugc.bazaarvoice.com/7129aa/%s/reviews.djs?format=embeddedhtml" % self._product_id()
                contents = urllib.urlopen(url).read()
                # contents = re.findall(r'"BVRRRatingSummarySourceID":"(.*?)"}', contents)[0]
                reviews = re.findall(r'<span class=\\"BVRRHistAbsLabel\\">(.*?)<\\/span>', contents)[:5]

                if reviews:
                    reviews = [review.replace(",", "") for review in reviews]

                score = 5
                for review in reviews:
                    if int(review) > 0:
                        self.max_score = score
                        break
                    score -= 1

                score = 1
                for review in reversed(reviews):
                    if int(review) > 0:
                        self.min_score = score
                        break
                    score += 1

                self.reviews = []
                score = 1
                for review in reversed(reviews):
                    self.reviews.append([score, int(review)])
                    score += 1

                if not self.reviews:
                    self.reviews = None
                # self.reviews_tree = html.fromstring(contents)
        except:
            self.reviews = None
            pass

    def _average_review(self):
        self._load_reviews()
        count = 0
        score = 0
        for review in self.reviews:
            count += review[1]
            score += review[0]*review[1]
        return round(1.0*score/count, 1)

    def _review_count(self):
        self._load_reviews()
        count = 0

        if not self.reviews:
            return 0

        for review in self.reviews:
            count += review[1]
        return count

    def _max_review(self):
        self._load_reviews()
        return self.max_score

    def _min_review(self):
        self._load_reviews()
        return self.min_score

    def _reviews(self):
        self._load_reviews()
        return self.reviews

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        if self._site_online_out_of_stock():
            return "out of stock - no price given"

        if self.is_bundle:
            price_range = self.tree_html.xpath('//span[contains(@class, "fullrange")]/text()')
            if price_range:
                return price_range[0].replace('\n', ' ').strip()

            if self.product_info_json.get('salePrice'):
                return '$' + self.product_info_json['salePrice']
            else:
                return '$' + self.product_info_json['regularPrice']

        return self.tree_html.xpath("//meta[@itemprop='price']/@content")[0].strip()

    def _price_amount(self):
        price = self._price()
        price = price.replace(",", "")
        price_amount = re.findall(r"[\d\.]+", price)[0]
        return float(price_amount)

    def _price_currency(self):
        price = self._price()
        if price and price[0] == "$":
            return "USD"
        else:
            return self.tree_html.xpath("//meta[@itemprop='priceCurrency']/@content")[0].strip()

    def _in_stores(self):
        # MACYS.pdp.productAvailable = "true";
        script = " ".join(self.tree_html.xpath("//script//text()"))
        available = re.findall(r"MACYS\.pdp\.productAvailable = \"(.*?)\"", script, re.DOTALL)
        if len(available) > 0:
            if available[0] == "true":
                return 1
        return 0

    def _marketplace(self):
        return 0

    def _marketplace_sellers(self):
        return None

    def _marketplace_lowest_price(self):
        return None

    def _site_online(self):
        # site_online: the item is sold by the site (e.g. "sold by Amazon") and delivered directly, without a physical store.
        if self._site_online_out_of_stock():
            return 0
        return 1

    def _site_online_out_of_stock(self):
        #  site_online_out_of_stock - currently unavailable from the site - binary
        '''
        if self._site_online() == 0:
            return None
        '''
        rows = self.tree_html.xpath("//ul[@class='similarItems']//li//text()")
        if "This product is currently unavailable" in rows:
            return 1
        return 0

    def _in_stores_out_of_stock(self):
        '''in_stores_out_of_stock - currently unavailable for pickup from a physical store - binary
        (null should be used for items that can not be ordered online and the availability may depend on location of the store)
        '''
        return None

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        if self.is_bundle:
            all = self.tree_html.xpath('//meta[@itemprop="breadcrumb"]/@content')[0].split('-')
        else:
            all = self.product_info_json['breadCrumbCategory'].split('-')

        out = [self._clean_text(r) for r in all]
        if len(out) < 1:
            return None
        return out

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        return guess_brand_from_first_words(self._product_name())

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces
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
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "model" : _model, \
        "upc" : _upc, \
        "long_description" : _long_description, \
        "variants" : _variants, \
        "swatches" : _swatches, \
        "no_longer_available": _no_longer_available, \

        # CONTAINER : PAGE_ATTRIBUTES
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "canonical_link": _canonical_link,
        "mobile_image_same" : _mobile_image_same, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        "bundle" : _bundle, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "in_stores" : _in_stores, \
        "marketplace": _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \
        "site_online" : _site_online, \
        "site_online_out_of_stock" : _site_online_out_of_stock, \
        "in_stores_out_of_stock" : _in_stores_out_of_stock, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \

        "loaded_in_seconds": None \
        }


    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        # CONTAINER : CLASSIFICATION
         # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \
    }

