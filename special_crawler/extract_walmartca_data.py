#!/usr/bin/python

import re
import lxml
import lxml.html
import requests
import json

from itertools import groupby

from lxml import html, etree
from extract_data import Scraper
from spiders_shared_code.walmartca_variants import WalmartCAVariants

is_empty = lambda x, y="": x[0] if x else y

class WalmartCAScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www\.walmart\.ca/(en|fr)/ip/[product-name]/[product-id]$"
    PRODUCT_INFO_URL = "http://api.bazaarvoice.com/data/batch.json?passkey=e6wzzmz844l2kk3v6v7igfl6i&" \
                      "apiversion=5.5&displaycode=2036-en_ca&resource.q0=products&" \
                      "filter.q0=id%3Aeq%3A{product_id}&" \
                      "stats.q0=questions%2Creviews&filteredstats.q0=questions%2Creviews&" \
                      "filter_questions.q0=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_answers.q0=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_reviews.q0=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "resource.q1=questions&" \
                      "filter.q1=productid%3Aeq%3A{product_id}&" \
                      "filter.q1=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "sort.q1=hasstaffanswers%3Adesc&stats.q1=questions&" \
                      "filteredstats.q1=questions&include.q1=authors%2Cproducts%2Canswers&" \
                      "filter_questions.q1=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_answers.q1=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "sort_answers.q1=submissiontime%3Aasc&limit.q1=10&offset.q1=0&" \
                      "limit_answers.q1=10&resource.q2=reviews&filter.q2=isratingsonly%3Aeq%3Afalse&" \
                      "filter.q2=productid%3Aeq%3A{product_id}&filter.q2=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "sort.q2=helpfulness%3Adesc%2Ctotalpositivefeedbackcount%3Adesc&" \
                      "stats.q2=reviews&filteredstats.q2=reviews&include.q2=authors%2Cproducts%2Ccomments&" \
                      "filter_reviews.q2=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_reviewcomments.q2=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_comments.q2=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&limit.q2=6&offset.q2=0&" \
                      "limit_comments.q2=3&resource.q3=reviews&filter.q3=productid%3Aeq%3A{product_id}&" \
                      "filter.q3=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&limit.q3=1&resource.q4=reviews&" \
                      "filter.q4=productid%3Aeq%3A{product_id}&filter.q4=isratingsonly%3Aeq%3Afalse&" \
                      "filter.q4=rating%3Agt%3A3&filter.q4=totalpositivefeedbackcount%3Agte%3A3&" \
                      "filter.q4=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&sort.q4=totalpositivefeedbackcount%3Adesc&" \
                      "stats.q4=reviews&filteredstats.q4=reviews&include.q4=authors%2Creviews&" \
                      "filter_reviews.q4=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_reviewcomments.q4=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "limit.q4=1&resource.q5=reviews&filter.q5=productid%3Aeq%3A{product_id}&" \
                      "filter.q5=isratingsonly%3Aeq%3Afalse&filter.q5=rating%3Alte%3A3&" \
                      "filter.q5=totalpositivefeedbackcount%3Agte%3A3&" \
                      "filter.q5=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "sort.q5=totalpositivefeedbackcount%3Adesc&stats.q5=reviews&" \
                      "filteredstats.q5=reviews&include.q5=authors%2Creviews&" \
                      "filter_reviews.q5=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_reviewcomments.q5=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&limit.q5=1"

    IN_STOCK_URL = "https://om.ordergroove.com/offer/af0a84f8847311e3b233bc764e1107f2/pdp?" \
                   "session_id=af0a84f8847311e3b233bc764e1107f2.262633.1436277025&" \
                   "page_type=1&p=%5B%22{product_id}%22%5D&module_view=%5B%22regular%22%5D"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        self.product_info_json = None

        self.failure_type = None

        self.wcv = WalmartCAVariants()

        self.review_json = None
        self.review_list = None
        self.is_review_checked = False
        self.product_json = None
        self.variant_json = None
        self.list_out_of_stock = ['70', '80', '85', '87', '90']
        self.list_not_sold_online = ['85', '87', '90']

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match(r"^http://www\.walmart\.ca/(en|fr)/ip/.*/[0-9]+$", self.product_page_url)

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
            if self.tree_html.xpath("//meta[@property='og:type']")[0] == "product":
                raise Exception()
        except Exception:
            return True

        self._load_product_json()
        self.wcv.setupCH(self.variant_json, self.tree_html)

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _load_product_json(self):
        try:
            skuid = self._sku()

            # Extract base product info from JS
            data = re.findall(
                    r'productPurchaseCartridgeData\["\d+"\]\s*=\s*(\{(.|\n)*?\});',
                    html.tostring(self.tree_html)
            )

            if data:
                data = list(data)[0]
                data = data[0].replace('numberOfVariants', '"numberOfVariants"').replace('variantDataRaw', '"variantDataRaw"')
                data = data.decode('utf-8').replace(' :', ':')

                try:
                    self.variant_json = product_data = json.loads(data)
                except ValueError:
                    return
            else:
                return

            product_data['baseProdInfo'] = product_data['variantDataRaw'][0]

            # Set variants
            number_of_variants = product_data.get('numberOfVariants', 0)
            data_variants = product_data['variantDataRaw']
            skus = []

            if number_of_variants:
                try:
                    variants = {}

                    for var in data_variants:
                        variant = dict()
                        properties = dict()

                        sku_id = is_empty(
                            var.get('sku_id', ''),
                            ''
                        )
                        skus.append({"skuid": sku_id})

                        price = var.get('price_store_price')
                        if price:
                            price = is_empty(price, None)
                            price = price.replace(',', '')
                            price = format(float(price), '.2f')
                        variant['price'] = price

                        color = is_empty(var.get('variantKey_en_Colour', []))
                        size = is_empty(var.get('variantKey_en_Size', []))

                        if size:
                            properties['size'] = size
                        if color:
                            properties['color'] = color
                        variant['properties'] = properties

                        variants[sku_id] = variant
                except (KeyError, ValueError):
                    variants = []

            else:
                skus = [{"skuid": skuid}]

            headers={
                'X-Requested-With': 'XMLHttpRequest'
            }
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries=3)
            b = requests.adapters.HTTPAdapter(max_retries=3)
            s.mount('http://', a)
            s.mount('https://', b)

            request_data = [{
                "productid": self._product_id(),
                "skus": [skus]
            }]

            request_data = json.dumps(request_data).replace(' ', '')
            contents = s.post("http://www.walmart.ca/ws/online/products", data={"products": request_data}, headers=headers, timeout=5).text

            self.product_json = json.loads(contents)
        except:
            self.product_json = None

    def _canonical_link(self):
        canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

        return canonical_link

    def _sku(self):
        try:
            return self.tree_html.xpath("//form[@data-product-id]/@data-sku-id")[0]
        except:
            return None

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        product_id = self.product_page_url.split('/')[-1]
        return product_id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//h1[@data-analytics-type="productPage-productName"]/text()')[0].strip()

    def _product_title(self):
        return self.tree_html.xpath('//h1[@data-analytics-type="productPage-productName"]/text()')[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath('//h1[@data-analytics-type="productPage-productName"]/text()')[0].strip()

    def _model(self):
        return None

    def _features(self):
        if not self.tree_html.xpath("//div[@id='specGroup']"):
            return None

        if self._sku():
            feature_name_list = self.tree_html.xpath("//div[@id='specGroup']/div[@data-sku-id={}]//div[contains(@class, 'name')]".format(self._sku()))
            feature_value_list = self.tree_html.xpath("//div[@id='specGroup']/div[@data-sku-id={}]//div[contains(@class, 'value')]".format(self._sku()))
        else:
            feature_name_list = self.tree_html.xpath("//div[@id='specGroup']//div[contains(@class, 'name')]")
            feature_value_list = self.tree_html.xpath("//div[@id='specGroup']//div[contains(@class, 'value')]")

        feature_list = []

        for index, feature_name in enumerate(feature_name_list):
            feature_list.append(feature_name.text_content().strip() + " " + feature_value_list[index].text_content().strip())

        if not feature_list:
            return None

        return feature_list

    def _feature_count(self):
        features = self._features()

        if not features:
            return 0

        return len(features)

    def _description(self):
        return self.tree_html.xpath("//div[@itemprop='description']/div[contains(@class, 'description')]")[0].text_content().strip()

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description(self):
        return self.tree_html.xpath("//div[@itemprop='description']/div[contains(@class, 'bullets')]")[0].text_content().strip()

    def _ingredients(self):
        return None

    def _ingredients_count(self):
        return 0

    def _variants(self):
        return self.wcv._variants()

    def _rollback(self):
        if self.product_json["products"][0]["isRollback"]:
            return 1

        return 0

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        pass
        
    def _image_urls(self):
        slider_images = self.tree_html.xpath("//div[@id='carousel']//ul[@class='slides']//img/@src")

        if slider_images:
            for index, image in enumerate(slider_images):
                if image.startswith("http:") or image.startswith("https:"):
                    continue

                slider_images[index] = "http:" + image

            return slider_images

        main_image = self.tree_html.xpath("//div[@id='product-images']//div[@class='centered-img-wrap']//img/@src")

        if main_image:
            return main_image

        return None

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
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0].strip()

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################

    def _average_review(self):
        average_review = float(self.tree_html.xpath("//span[@itemprop='ratingValue']/text()")[0])

        if average_review.is_integer():
            average_review = int(average_review)
        else:
            average_review = "%.1f" % float(average_review)

        return average_review

    def _review_count(self):
        review_count = self.tree_html.xpath("//button[@data-analytics-type='product-reviews']/@data-analytics-value")[0]
        review_count = [int(s) for s in review_count.split() if s.isdigit()]
        review_count = review_count[0]

        return review_count

    def _max_review(self):
        reviews = self._reviews()

        if not reviews:
            return None

        max_review = None

        for rating in reviews:
            if (max_review < rating[0] and rating[1] > 0) or max_review is None:
                max_review = rating[0]

        return max_review

    def _min_review(self):
        reviews = self._reviews()

        if not reviews:
            return None

        min_review = None

        for rating in reviews:
            if (min_review > rating[0] and rating[1] > 0) or min_review is None:
                min_review = rating[0]

        return min_review

    def _reviews(self):
        if self.is_review_checked:
            return self.review_list

        self.is_review_checked = True

        h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        b = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        s.mount('https://', b)
        contents = s.get(self.PRODUCT_INFO_URL.format(product_id=self._product_id()), headers=h, timeout=5).text

        try:
            self.review_json = json.loads(contents)
            self.review_list = []

            for rating in self.review_json["BatchedResults"]["q0"]["Results"][0]["ReviewStatistics"]["RatingDistribution"]:
                self.review_list.append([int(rating['RatingValue']), int(rating['Count'])])

            if self.review_list:
                return self.review_list

            self.review_list = None
        except:
            pass

        return None

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        try:
            return self.tree_html.xpath("//span[@itemprop='price']/text()")[0]
        except:
            return self.tree_html.xpath("//span[@itemprop='lowPrice']/text()")[0] + " to " + self.tree_html.xpath("//span[@itemprop='highPrice']/text()")[0]

    def _price_amount(self):
        return float(self.tree_html.xpath("//span[@itemprop='price']/text()")[0][1:])

    def _price_currency(self):
        return self.tree_html.xpath("//meta[@itemprop='priceCurrency']/@content")[0]

    def _site_online(self):
        if self.product_json["products"][0]["availability"] in self.list_not_sold_online:
            return 0

        return 1

    def _in_stores(self):
        if "sorry, this item is currently not available in stores." in html.tostring(self.tree_html).lower():
            return 0

        return 1

    def _site_online_out_of_stock(self):
        if self.product_json["products"][0]["availability"] in self.list_out_of_stock:
            return 1

        return 0

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
        categories = self.tree_html.xpath("//nav[@id='breadcrumb']/ul/li//span[@itemprop='title']/text()")

        return categories[1:]

    def _category_name(self):
        categories = self.tree_html.xpath("//nav[@id='breadcrumb']/ul/li//span[@itemprop='title']/text()")

        return categories[-1].strip()

    def _brand(self):
        return self.tree_html.xpath("//span[@itemprop='brand']/text()")[0].strip()

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
