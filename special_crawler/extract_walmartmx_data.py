#!/usr/bin/python

import re
import lxml
import requests
import json

from lxml import html
from extract_data import Scraper

is_empty = lambda x, y="": x[0] if x else y

class WalmartMXScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www\.walmart\.com\.mx/[product-categories]/[product-name]_[product-id]"


    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^http://www\.walmart\.com\.mx/([\w\d/-])+_\d+", self.product_page_url)
        return bool(m)

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        try:
            if self.tree_html.xpath("//meta[@property='og:type']/@content")[0].lower() != "product":
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

    def _product_id(self):
        product_id =  self.tree_html.xpath("//*[@id='lblUPC']/text()")
        return product_id[0] if product_id else None

    def _sku(self):
        return self._product_id()

    def _url(self):
        return self.product_page_url


    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//*[@id="lblTitle"]/text()')[0].strip()

    def _product_title(self):
        return self.tree_html.xpath('//*[@id="lblTitle"]/text()')[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath('//*[@id="lblTitle"]/text()')[0].strip()

    def _upc(self):
        return self._product_id()

    def _model(self):
        model = self.tree_html.xpath("//*[@itemprop='model']/@content")
        return model[0] if model else None

    # Not Done Yet
    def _features(self):
        features_ajax = requests.get("http://www.walmart.com.mx/WebControls/hlFacets.ashx?upc=%s" % self._product_id())
        return [ "%s: %s" % (x['Etiqueta'], x['Valor']) for x in  features_ajax.json()]

    # Not Done Yet
    def _feature_count(self):
        features = self._features()
        return len(features) if features else 0

    def _description(self):
        return ' '.join(self.tree_html.xpath('//*[@id="productoDescripcionTexto"]/text()'))

    def _long_description(self):
        return self._description()

    def _ingredients(self):
        return None

    def _ingredients_count(self):
        return 0

    def _variants(self):
        return None

    def _rollback(self):
        return None

    def _no_longer_available(self):
        return True if  "no disponible para su venta" in html.tostring(self.tree_html).lower() else False
    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################

    def _mobile_image_same(self):
        pass
        
    def _image_urls(self):
        # There is 1 to 3 images on this website.
        # It always will include 3 images URL on the page but sometimes URL 2 and 3 will not work and are hidden.
        # I can't decipher how does the website decide if images 2 and 3 are valid or not without downloading.
        return [self.tree_html.xpath('//*[@id="product-carousel"]//img/@src')[0]]

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def _video_urls(self):
        return None

    def _video_count(self):
        return 0

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
        keywords = self.tree_html.xpath('//meta[@name="keywords"]/@content')
        return keywords[0].strip() if keywords else None

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################

    def _average_review(self):
        average_review_img_url = self.tree_html.xpath('//*[@id="imgRatingGen"]/@src')[0]
        try:
            average_review = float(re.search('/images/ranking/rating(\d+)\.png', average_review_img_url).group(1))
            if average_review.is_integer():
                average_review = int(average_review)
            else:
                average_review = "%.1f" % float(average_review)

            return average_review
        except:
            return None


    def _review_count(self):
        review_count = self.tree_html.xpath('//*[@id="CountComment"]/text()')[0]
        review_count = [int(s) for s in review_count.split() if s.isdigit()]
        return review_count[0] if review_count else 0

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
        try:
            return self.tree_html.xpath("//*[@itemprop='price']/@content")[0]
        except:
            return None

    def _price_amount(self):
        return float(self.tree_html.xpath("//*[@itemprop='price']/@content")[0][1:])

    def _price_currency(self):
        return self.tree_html.xpath("//meta[@itemprop='priceCurrency']/@content")[0]

    def _site_online(self):
        return 1

    def _in_stores(self):
        if "sorry, this item is currently not available in stores." in html.tostring(self.tree_html).lower():
            return 0

        return 1

    def _site_online_out_of_stock(self):
        return 1 if self._no_longer_available() else 0

    def _marketplace_sellers(self):
        return None

    def _marketplace_out_of_stock(self):
        return 0

    def _marketplace(self):
        return 0

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################    

    def _categories(self):
        excluded_categories = ['inicio']
        raw_categories = self.tree_html.xpath("//*[@class='breadcrumb']//a/text()")
        categories = [re.sub('>|/','',x).strip() for x in raw_categories]
        return filter((lambda x: x.lower() not in excluded_categories), categories)

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        manufacturer = self.tree_html.xpath("//*[@itemprop='manufacturer']/@content")
        return manufacturer[0] if manufacturer else None

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
        "rollback": _rollback,
        "no_longer_available": _no_longer_available,
        "upc": _upc,
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
