#!/usr/bin/python

import re
import lxml
import lxml.html
import requests
import json

from itertools import groupby

from lxml import html, etree
from extract_data import Scraper


class UltaScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.ulta.com/ulta/browse/productDetail.jsp?productId=<product-id> or http://www.ulta.com/<product-name>?productId=xlsImpprod<product-id>"

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^http://www\.ulta\.com/ulta/browse/productDetail\.jsp\?productId=.+$", self.product_page_url)

        m1 = re.match(r"^http://www\.ulta\.com/.+\?productId=xlsImpprod\d+$", self.product_page_url)

        return m or m1

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
    def _url(self):
        return self.product_page_url

    def _product_id(self):
        product_id = self.tree_html.xpath("//input[@id='pinProduct']/@value")[0].strip()

        return product_id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//input[@id="pinDisplay"]/@value')[0].strip()

    def _product_title(self):
        return self.tree_html.xpath('//title/text()')[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath('//meta[@name="title"]/@content')[0].strip()

    def _model(self):
        return None

    def _features(self):
        return None

    def _feature_count(self):
        return 0

    def _description(self):

        description_elements = self.tree_html.xpath('//div[@id="product-first-catalog"]/div[contains(@class,"product-catalog-content")]')

        text_elements = self.tree_html.xpath('//div[@id="product-first-catalog"]/div[contains(@class,"product-catalog-content")]/text()')

        short_description = "" . join(text_elements)

        if description_elements:
            description_elements = description_elements[0]

            for description_element in description_elements:
                if "<iframe " in lxml.html.tostring(description_element):
                    continue

                short_description += lxml.html.tostring(description_element)

        short_description = short_description.strip()

        if not short_description:
            return None
        else:
            return short_description

    def _variants(self):
        current_sku = re.search("currentSkuId = '(\d+)'", html.tostring(self.tree_html)).group(1)

        variants = []

        variant_data = re.findall('productSkus\[\d+\] =\s+({[^}]+});', html.tostring(self.tree_html))

        for d in variant_data:
            variant_json = json.loads(d)

            if current_sku == variant_json['id']:
                continue

            price_html = html.fromstring( self.load_page_from_url_with_number_of_retries('http://www.ulta.com/common/inc/productDetail_price.jsp?skuId=%s&productId=%s&fromPDP=true' % (variant_json['id'], self._product_id())))

            variants.append( {
                'variant' : variant_json.get('displayName'),
                'item_no' : variant_json['id'],
                'price' : float( price_html.xpath('//p')[0].text[1:]), # remove leading $ and convert to float
                'image_url' : variant_json['imgUrl'].split('?')[0],
                'selected' : False,
            } )

        if variants:
            return variants

        return None

    '''
    def _swatches(self):
        swatches = []

        swatch_els = self.tree_html.xpath('//a[contains(@class,"product-swatch")]/img')

        for e in swatch_els:
            swatches.append( {
                'name' : e.get('alt'),
                'img' : e.get('data-blzsrc').split('?')[0],
            } )

        if swatches:
            return swatches

        return None
    '''

    def _no_longer_available(self):
        if re.search('Sorry, this product is no longer available.', self.page_raw_text):
            return 1
        return 0

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description(self):
        description_elements = self.tree_html.xpath('//div[contains(@class,"product-catalog")]')

        for description_element in description_elements:
            if description_element.xpath("div[contains(@class,'product-catalog-head')]") and \
                            "How to Use" in description_element.xpath("div[contains(@class,'product-catalog-head')]")[0].text_content():
                return re.sub('<div class="product-catalog-content.*>', '', \
                    lxml.html.tostring(description_element.xpath("div[contains(@class,'product-catalog-content')]")[0])).\
                    replace('</div>', '').strip()

        return None

    def _ingredients(self):
        product_catalog_list = self.tree_html.xpath('//div[contains(@class,"product-catalog")]')

        for product_catalog in product_catalog_list:
            pch = product_catalog.xpath("div[contains(@class,'product-catalog-head')]")

            if pch:
                head_text = pch[0].text_content()

                if "Ingredients" in head_text:
                    ingredients = product_catalog.xpath("div[contains(@class,'product-catalog-content')]")[0].text_content().strip()

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

        for url in self.tree_html.xpath('//div[@class="product-detail-thumbnail-image"]//img/@data-blzsrc'):
            if not url.split('?')[0] in thumb_image_urls:
                thumb_image_urls.append(url.split('?')[0])

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
        video_urls = []

        for url in self.tree_html.xpath('//iframe/@src'):
            if "www.youtube.com" in url and not url in video_urls:
                video_urls.append(url)

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
        "variants": _variants,
        "no_longer_available": _no_longer_available,

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
