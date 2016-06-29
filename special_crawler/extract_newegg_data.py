#!/usr/bin/python

import urllib
import re
import sys
import json

from lxml import html, etree
import time
import requests
from extract_data import Scraper
from lxml.etree import tostring


class NeweggScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.newegg.com/Product/Product.aspx?Item=<product-id>"
    WEBCOLLAGE_BASE_URL = "http://content.webcollage.net/newegg/power-page?ird=true&channel-product-id={0}"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        self.hdGroupItemModelString_json = None
        self.hdGroupItemsString_json = None
        self.related_item_id = None
        self.imgGalleryConfig_json = None
        self.overviewData_json = None
        self.availableMap_json = None
        self.review_json = None
        self.review_list = None
        self.is_review_checked = False
        self.webcollage_contents = None
        self.webcollage_json_data = None

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match(r"^http://www\.newegg\.com/Product/Product\.aspx\?Item=[a-zA-Z0-9\-]+$", self.product_page_url)
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
            if not self.tree_html.xpath('//div[@itemtype="http://schema.org/Product"]'):
                raise Exception()
        except Exception:
            return True

        self._extract_product_json()

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _primary_seller_info(self):
        seller_text_block = self.tree_html.xpath("//p[@class='grpNote-sold-by']")
        seller_name = ""

        if len(seller_text_block) > 1:
            seller_text_block = self.tree_html.xpath("//p[@class='grpNote-sold-by' and @id='grpNotesoldby_{0}']".format(self.related_item_id))

        if "newegg" in seller_text_block[0].text_content().lower():
            seller_name = "Newegg"
        else:
            seller_name = seller_text_block[0].xpath(".//a/text()")[0].strip()


        price = self._price_amount()

        return {seller_name: price}

    def _secondary_seller_list_info(self):
        secondary_sellers_list = {}

        secondary_sellers_block_list = self.tree_html.xpath("//div[@class='grpAction grpActionSecondary additional-sellers']")

        if len(secondary_sellers_block_list) > 1:
            secondary_sellers_block_list = self.tree_html.xpath("//div[@class='grpAction grpActionSecondary additional-sellers' and @id='MBO_{0}']".format(self.related_item_id))

        if secondary_sellers_block_list:
            for seller_block in secondary_sellers_block_list[0].xpath(".//ul[@class='sellers-list']/li[@class='sellers-list-item normal-available']"):
                seller_name = seller_block.xpath(".//div[@class='store']")[0].text_content().strip()
                price = seller_block.xpath(".//li[@class='price-current ']")[0].text_content()
                price = price[price.find("$"):]
                price = float(re.findall(r"\d*\.\d+|\d+", price.replace(",", ""))[0])
                secondary_sellers_list[seller_name] = price

            return secondary_sellers_list

        return None

    def _extract_product_json(self):
        try:
            self.hdGroupItemModelString_json = json.loads(self._find_between(html.tostring(self.tree_html), "var hdGroupItemModelString = ", ";\r"))

            for item in self.hdGroupItemModelString_json:
                if item["SellerItem"] == self._product_id():
                    self.related_item_id = item["ParentItem"]
                    break
        except:
            print "Issue(Newegg): product hdGroupItemModelString json loading"

        try:
            self.hdGroupItemsString_json = json.loads(self._find_between(html.tostring(self.tree_html), "var hdGroupItemsString = ", ";\r"))
        except:
            print "Issue(Newegg): product hdGroupItemsString json loading"

        try:
            self.imgGalleryConfig_json = json.loads(self._find_between(html.tostring(self.tree_html), "imgGalleryConfig.Items=", ";\r"))
        except:
            print "Issue(Newegg): product imgGalleryConfig json loading"

        try:
            self.overviewData_json = json.loads(self._find_between(html.tostring(self.tree_html), "\n                     var data = ", " || {}"))
        except:
            print "Issue(Newegg): product imgGalleryConfig json loading"

        try:
            self.availableMap_json = json.loads(self._find_between(html.tostring(self.tree_html), "availableMap:", ",\r"))
        except:
            print "Issue(Newegg): product availableMap json loading"

        try:
            self.flixcars = []

            flixcar = re.search('"(http://media.flixcar.com/delivery/js/inpage/[^"]+)"', tostring(self.tree_html))

            if flixcar:
                content = self.load_page_from_url_with_number_of_retries( flixcar.group(1))
                distributor_id = re.search( "distributor: '(\d+)'", content ).group(1)
                product_ids = re.findall( "product: '(\d+)'", content )

                for id in product_ids:
                    response = self.load_page_from_url_with_number_of_retries('http://media.flixcar.com/delivery/inpage/show/%s/us/%s/json?c=jsonpcar%sus%s&complimentary=0&type=.html' % (distributor_id, id, distributor_id, id))

                    self.flixcars.append(response)
        except:
            self.flixcars = None
            print "Issue(Newegg): flixcars loading"

        try:
            self.liveclicker = self.load_page_from_url_with_number_of_retries('http://sv.liveclicker.net/service/api?method=liveclicker.widget.getList&account_id=2437&&extra_options=%7B%22include_description%22%3A%22true%22%2C%22include_extra_images%22%3A%22true%22%2C%22return_dimensions%22%3A%226%22%7D&dim1=' + self._product_id() + '&order=recent&status=online&format=json&var=liveclicker.api_res[0]')
        except:
            self.liveclicker = None
            print "Issue(Newegg): liveclicker loading"

    def _canonical_link(self):
        canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

        return canonical_link

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        return self._canonical_link().split('=')[-1]

    def _site_id(self):
        return None

    def _status(self):
        return "success"

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//h1/span[@itemprop='name']/text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//h1/span[@itemprop='name']/text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//h1/span[@itemprop='name']/text()")[0].strip()

    def _model(self):
        for item in self.hdGroupItemModelString_json:
            if item["SellerItem"] == self._product_id():
                return item["Model"]

        return None

    def _upc(self):
        return None

    def _features(self):
        features_dl_list = self.tree_html.xpath('//div[@id="detailSpecContent"]//dl')
        features_list = []

        for feature in features_dl_list:
            features_list.append(feature.xpath("./dt")[0].text_content().strip() + ": " + feature.xpath("./dd")[0].text_content().strip())

        if features_list:
            return features_list

        return None

    def _feature_count(self):
        features = self._features()
        return len(features) if features else 0

    def _model_meta(self):
        return None

    def _description(self):
        if self.related_item_id:
            description_block = self.tree_html.xpath("//ul[@id='grpBullet_{0}']".format(self.related_item_id))
        else:
            description_block = self.tree_html.xpath("//ul[@id='grpBullet_']")

        if description_block:
            description_block = html.tostring(description_block[0])
            description_block = self._clean_text(self._exclude_javascript_from_description(description_block))
            return description_block if description_block else None

        return None

    def _long_description(self):
        long_description = None

        try:
            long_description = html.tostring(self.tree_html.xpath("//div[@id='Overview_Content']")[0])
            long_description = self._clean_text(html.fromstring(self._exclude_javascript_from_description(long_description)).text_content()).strip()

            if long_description and len(long_description) > 0:
                return long_description
        except:
            pass

        try:
            for overview in self.overviewData_json:
                if overview["ParentItem"] == self.related_item_id:
                    long_description = self._clean_text(html.fromstring(self._exclude_javascript_from_description(overview["Overview"])).text_content()).strip()

                    if long_description and len(long_description) > 0:
                        return long_description
        except:
            pass

        try:
            wc_rich_content_description_blocks= self.webcollage_contents.xpath("//div[contains(@class, 'wc-rich-content-description')]")
            long_description = ""

            for description in wc_rich_content_description_blocks:
                long_description += (description.text_content().strip() + "\n")

            long_description = self._clean_text(long_description).strip()

            if long_description and len(long_description) > 0:
                return long_description
        except:
            pass

        return None

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):        
        image_list = []

        base_url_for_s7 = "http://images17.newegg.com/is/image/newegg/"
        base_url_for_non_s7 = "http://images10.newegg.com/productimage/"

        for item in self.imgGalleryConfig_json:
            if item["itemNumber"] == self._product_id() or len(self.imgGalleryConfig_json) == 1:
                if item["normalImageInfo"]:
                    image_list = [base_url_for_non_s7 + img_name for img_name in item["normalImageInfo"]["imageNameList"].split(",")]
                elif item["scene7ImageInfo"]:
                    image_list = [base_url_for_s7 + img_name for img_name in item["scene7ImageInfo"]["imageSetImageList"].split(",")]
                break

        if image_list:
            return image_list

        return None

    def _image_count(self):
        image_urls = self._image_urls()
        return len(image_urls) if image_urls else 0

    def _video_urls(self):
        video_urls = []

        widget_id_results = re.search('widget_id" : "(\d+)', self.liveclicker)

        if widget_id_results:
            widget_id = widget_id_results.group(1)

            response = self.load_page_from_url_with_number_of_retries('http://sv.liveclicker.net/service/getEmbed?client_id=2437&widget_id=%s&width=320&height=180&bufferTime=0&container=LiveclickerVideoDiv&player_custom_id=1783&div_id=LiveclickerVideoDiv' % widget_id)

            for url in re.findall('http://ecdn.liveclicker.net[^"]+.mp4', response):
                if not url in video_urls:
                    video_urls.append(url)

        for flixcar in self.flixcars:
            for url in re.findall('media.flixcar.com.[^"]+.mp4', flixcar):
                if not url in video_urls:
                    video_urls.append(url)

        if video_urls:
            return map( lambda x: x.replace('\\', ''), video_urls)

        return None

    def _video_count(self):
        videos = self._video_urls()

        num_embed_videos = len( self.tree_html.xpath('//div[contains(@class,"video")]'))

        if videos:
            return len(videos) + num_embed_videos

        return num_embed_videos

    def _pdf_urls(self):
        pdf_urls = []

        for flixcar in self.flixcars:
            for url in re.findall('media.flixcar.com[^"]+.pdf', flixcar):
                if not url in pdf_urls:
                    pdf_urls.append(url)

        if pdf_urls:
            return map( lambda x: x.replace('\\', ''), pdf_urls)

        return None

    def _pdf_count(self):
        if self._pdf_urls():
            return len(self._pdf_urls())

        return 0

    def _webcollage(self):
        webcollage = self.tree_html.xpath("//div[@id='Overview_Content']//script[contains(@src, 'http://content.webcollage.net')]")
        return 1 if webcollage else 0

    def _htags(self):
        htags_dict = {}
        # add h1 tags text to the list corresponding to the "h1" key in the dict
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        # add h2 tags text to the list corresponding to the "h2" key in the dict
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    def _keywords(self):
        return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]

    def _no_image(self):
        return None
    
    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################

    def _average_review(self):
        rws = self._reviews()
        if rws:
            s = n = 0
            for r in rws:
                s += r[0] * r[1]
                n += r[1]
            if n > 0:
                return round(s/float(n),2)
        return None


    def _review_count(self):
        nr_reviews = self.tree_html.xpath('//*[@id="linkSumRangeAll"]/span//text()')
        return self._toint(nr_reviews[0].strip()[1:-1]) if len(nr_reviews) > 0 else 0

    def _reviews(self):
        res = []
        for i in range(1,6):
            rvm = self.tree_html.xpath('//span[@id="reviewNumber%s"]//text()' % i)
            if len(rvm) > 0 and  self._toint(rvm[0]) > 0:
                res.append([i, self._toint(rvm[0])])
        if len(res) > 0: return res
        return None

    def _tofloat(self,s):
        try:
            t=float(s)
            return t
        except ValueError:
            return 0.0

    def _toint(self,s):
        try:
            s = s.replace(',','')
            t=int(s)
            return t
        except ValueError:
            return 0

    def _max_review(self):
        rv = self._reviews()
        if rv !=None and len(rv)>0:
            return rv[-1][0]
        return None

    def _min_review(self):
        rv = self._reviews()
        if rv !=None and len(rv)>0:
            return rv[0][0]
        return None


    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        return "${0}".format(self._price_amount())

    def _price_amount(self):
        shipping_cost = float(self._find_between(html.tostring(self.tree_html), "product_default_shipping_cost:['", "'],"))
        sale_price = float(self._find_between(html.tostring(self.tree_html), "product_sale_price:['", "'],"))

        if shipping_cost > 0.01:
            return sale_price - shipping_cost

        return sale_price

    def _price_currency(self):
        return "USD"

    def _in_stores(self):
        return 0

    def _site_online(self):
        if "Newegg" in self._primary_seller_info() or "Newegg" in self._secondary_seller_list_info():
            return 1

        return 0

    def _site_online_out_of_stock(self):
        stock_status = int(self._find_between(html.tostring(self.tree_html), "product_instock:['", "'],"))

        if stock_status == 0 and self._site_online() == 1:
            return 1

        return 0

    def _in_stores_out_of_stock(self):
        return 0

    def _primary_seller(self):
        return self._primary_seller_info().keys()[0]

    def _marketplace(self):
        return 1 if self._marketplace_sellers() else 0

    def _marketplace_sellers(self):
        primary_sellers = self._primary_seller_info()

        if primary_sellers.keys()[0].lower() == "newegg":
            primary_sellers = {}

        secondary_sellers = self._secondary_seller_list_info()
        secondary_sellers = secondary_sellers if secondary_sellers else {}

        marketplace_sellers = primary_sellers.keys() + secondary_sellers.keys()

        if marketplace_sellers:
            return marketplace_sellers

        return None

    def _marketplace_lowest_price(self):
        marketplace_prices = self._marketplace_prices()
        return sorted(marketplace_prices)[0] if marketplace_prices else None

    def _marketplace_prices(self):
        primary_sellers = self._primary_seller_info()

        if primary_sellers.keys()[0].lower() == "newegg":
            primary_sellers = {}

        secondary_sellers = self._secondary_seller_list_info()
        secondary_sellers = secondary_sellers if secondary_sellers else {}

        marketplace_prices = primary_sellers.values() + secondary_sellers.values()

        if marketplace_prices:
            return marketplace_prices

        return None

    def _marketplace_out_of_stock(self):
        if self._marketplace() == 1:
            stock_status = int(self._find_between(html.tostring(self.tree_html), "product_instock:['", "'],"))

            if stock_status == 0:
                return 1

            return 0

        return None

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################

    def _categories(self):
        return self.tree_html.xpath("//div[@id='baBreadcrumbTop']//dd/a/text()")[1:]

    def _category_name(self):
        return self._categories()[-1]
    
    def _brand(self):
        for item in self.hdGroupItemModelString_json:
            if item["SellerItem"] == self._product_id():
                return item["Brand"]

        return None

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces


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

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
        "no_image" : _no_image, \
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
        "primary_seller": _primary_seller, \
        "marketplace" : _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \
        "marketplace_prices" : _marketplace_prices, \
        "marketplace_out_of_stock": _marketplace_out_of_stock, \
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
