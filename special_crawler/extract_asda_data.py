#!/usr/bin/python

import re
import lxml
import lxml.html
import requests

from itertools import groupby

from lxml import html, etree
from extract_data import Scraper


class AsdaScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.ulta.com/ulta/browse/productDetail.jsp?productId=<product-id>"

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match(r"^http://groceries\.asda\.com/asda-webstore/landing/home\.shtml\?cmpid=ahc-_-ghs-d1-_"
                     r"-asdacom-dsk-_-hp/search/.+$", self.product_page_url)

        return not not m

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        self._product_json()

        itemtype = self.tree_html.xpath('//div[@id="pd-cms-container"]')

        if not itemtype:
            return True

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################
    def _url(self):
        return self.product_page_url

    def _product_json(self):
        product_id_start_index = self.product_page_url.rfind("/", 0)
        product_id = self.product_page_url[product_id_start_index:]

        product_json_url = "http://groceries.asda.com/api/items/view?itemid=910001528811&responsegroup=extended&cacheable=true&storeid=4565&shipdate=currentDate&requestorigin=gi"

    def _product_id(self):
        product_id = self.tree_html.xpath("//div[@id='pd-wrapper']//div[@class='prod-code']/h3/span/text()")[0].strip()

        return product_id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//div[@id='pd-wrapper']//div[@id='itemDetails']/h1[class='prod-title']/text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//div[@id='pd-wrapper']//div[@id='itemDetails']/h1[class='prod-title']/text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//div[@id='pd-wrapper']//div[@id='itemDetails']/h1[class='prod-title']/text()")[0].strip()

    def _model(self):
        return None

    def _features(self):
        nutritional_values_table = self.tree_html.xpath("//div[@id='pd-wrapper']//"
                                                        "div[@class='nv-table']/table/tbody/tr")

        if not nutritional_values_table:
            return None

        features = []

        for nutritional_value in nutritional_values_table:
            feature = ""
            feature = " " . join(nutritional_value.xpath("./td/text()"))
            features.append(feature)

        return features

    def _feature_count(self):
        features = self._features()

        if not features:
            return 0

        return len(features)

    def _description(self):

        description_element = self.tree_html.xpath('//p[@id="prodDescription"]')

        if not description_element:
            return None

        return lxml.html.tostring(description_element)

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description(self):
        description_elements = self.tree_html.xpath('//div[@class="product-catalog"]')
        return None

    def _ingredients(self):
        product_catalog_list = self.tree_html.xpath('//div[@class="product-catalog"]')

        for product_catalog in product_catalog_list:
            head_text = product_catalog.xpath("div[@class='product-catalog-head']/text()")

            if head_text:
                head_text = head_text[0].strip()

                if "Ingredients" in head_text:
                    ingredients = product_catalog.xpath("div[@class='product-catalog-content']/text()")[0].strip()

                    return ingredients.split(', ')

        return None

    def _ingredients_count(self):
        if not self._ingredients():
            return 0

        return len(self._ingredients())

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        pass
        
    def _image_urls(self):
        main_image_url = self.tree_html.xpath('//meta[@property="og:image"]/@content')[0]
        thumb_image_urls = [main_image_url]
        thumb_image_urls.extend(self.tree_html.xpath('//div[@class="product-detail-thumbnail-image"]//img/@alt'))

        for idx, item in enumerate(thumb_image_urls):
            if "http:" in item:
                thumb_image_urls[idx] = item.strip()
            else:
                thumb_image_urls[idx] = "http:" + item.strip()

        return thumb_image_urls

    def _image_count(self):
        if not self._image_urls():
            return 0

        return len(self._image_urls())

    def _video_urls(self):
        video_urls = self.tree_html.xpath('//iframe/@src')
        video_urls = [url for url in video_urls if "www.youtube.com" in url]

        for idx, item in enumerate(video_urls):
            if "http:" in item:
                video_urls[idx] = item.strip()
            else:
                video_urls[idx] = "http:" + item.strip()

        if not video_urls:
            return None

        return video_urls

    def _video_count(self):
        if not self._video_urls():
            return 0

        return len(self._video_urls())

    # return dictionary with one element containing the PDF
    def _pdf_urls(self):
        return None

    def _pdf_count(self):
        return 0

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
        if not self.tree_html.xpath('//div[@id="product-review-container"]/a[@id="reviews"]'):
            return None

        return float(self.tree_html.xpath('//span[@class="pr-rating pr-rounded average"]/text()')[0])

    def _review_count(self):
        if not self.tree_html.xpath('//div[@id="product-review-container"]/a[@id="reviews"]'):
            return int(0)

        return int(self.tree_html.xpath('//p[@class="pr-snapshot-average-based-on-text"]/span[@class="count"]/text()')[0])

    def _max_review(self):
        '''
        if not self._reviews():
            return 0.0

        return max(self._reviews())
        '''
        return None

    def _min_review(self):
        '''
        if not self._reviews():
            return 0.0

        return min(self._reviews())
        '''
        return None

    def _reviews(self):
        '''
        if not self.tree_html.xpath('//div[@id="product-review-container"]/a[@id="reviews"]'):
            return None

        reviews = self.tree_html.xpath('//span[@class="pr-rating pr-rounded"]/text()')

        for idx, item in enumerate(reviews):
            reviews[idx] = float(item)

        reviews.sort()
        review_count = [len(list(group)) for key, group in groupby(reviews)]
        reviews = list(set(reviews))

        reviews = [list(a) for a in zip(reviews, review_count)]

        return reviews
        '''
        return None

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        currency = ""

        if self._price_currency() == "USD":
            currency = "$"

        return currency + "{0:.2f}".format(self._price_amount())

    def _price_amount(self):
        return float(self.tree_html.xpath("//meta[@property='product:price:amount']/@content")[0])

    def _price_currency(self):
        return self.tree_html.xpath("//meta[@property='product:price:currency']/@content")[0]

    def _owned(self):
        return 0

    def _marketplace(self):
        return 0

    def _site_online(self):
        if self._in_stores_only() == 1:
            return 0

        '''
        if self._site_online_only() == 1:
            return 1
        '''

        return 1

    def _site_online_only(self):

        skuDisplayName = self.tree_html.xpath('//h6[@id="skuDisplayName"]/text()')

        if skuDisplayName:
            skuDisplayName = skuDisplayName[0]

            if "Online Only" in skuDisplayName:
                return 1

        contents = requests.get(self.product_page_url).text
        tree = html.fromstring(contents)

        if tree.xpath('//div[@id="productBadge"]/img'):
            productBadge = " " . join(tree.xpath('//div[@id="productBadge"]/img/@src'))

            if "http://images.ulta.com/is/image/Ulta/badge-online-only" in productBadge:
                return 1

        return 0

    def _in_stores(self):
        if self._site_online_only() == 1:
            return 0

        '''
        if self._in_stores_only() == 1:
            return 1
        '''

        return 1

    def _in_stores_only(self):
        contents = requests.get(self.product_page_url).text
        tree = html.fromstring(contents)

        if tree.xpath('//div[@id="productBadge"]/img'):
            productBadge = " " . join(tree.xpath('//div[@id="productBadge"]/img/@src'))

            if "http://images.ulta.com/is/image/Ulta/badge-instore" in productBadge:
                return 1

        return 0

    def _site_online_out_of_stock(self):
        return 0

    def _owned_out_of_stock(self):
        return 0

    def _marketplace_sellers(self):
        return None

    def _marketplace_out_of_stock(self):
        return 0

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################    
    def _categories(self):
        categories_text = self.tree_html.xpath('//div[@class="makeup-breadcrumb"]/ul/li/a/text()')

        return categories_text[1:]

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        return self.tree_html.xpath('//input[@id="pinBrand"]/@value')[0].strip()

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
        "owned_out_of_stock": _owned_out_of_stock, \
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
