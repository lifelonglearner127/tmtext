#!/usr/bin/python
#  -*- coding: utf-8 -*-

import urllib
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


class MaplinScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.maplin.co.uk/p/<product-id>"

    max_score = None
    min_score = None
    review_count = 0
    average_review = None
    reviews = None

    def check_url_format(self):
        #for ex: http://www.maplin.co.uk/p/black-heated-socks-1-pair-n57ds
        m = re.match(r"^http://www\.maplin\.co\.uk/p/([a-zA-Z0-9\-]+)?$", self.product_page_url)
        return not not m

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        product_id = self.product_page_url.split('/')[-1]
        return product_id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//h1[@itemprop='name']")[0].text

    def _product_title(self):
        return self.tree_html.xpath("//h1[@itemprop='name']")[0].text

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()
    
    def _model(self):
        return None

    def _upc(self):
        return self.tree_html.xpath("//span[@itemprop='sku']//text()")[0].strip()

    def _features(self):
        rows = self.tree_html.xpath("//table[@class='product-specs']//tr")
        
        # list of lists of cells (by rows)
        cells = map(lambda row: row.xpath(".//*//text()"), rows)
        # list of text in each row
        cells = cells[1:]
        rows_text = map(\
            lambda row: ":".join(\
                map(lambda cell: cell.strip(), row)\
                ), \
            cells)
        all_features_text = rows_text
        all_features_text = [r for r in all_features_text if len(self._clean_text(r)) > 0]
        # return dict with all features info
        return all_features_text

    def _feature_count(self):
        features = self._features()
        if features:
            return len(features)
        return 0

    def _model_meta(self):
        return None

    def _description_helper(self):
        description = "\n".join(self.tree_html.xpath("(//div[@class='product-summary']//ul)[2]//li//text()")).strip()
        return description

    def _description(self):
        description = self._description_helper()
        if len(description) < 1:
            return self._long_description_helper()
        return description

    def _long_description_helper(self):
        long_description = "\n".join(self.tree_html.xpath("//div[@class='productDescription']//text()")).strip()
        script = "\n".join(self.tree_html.xpath("//div[@class='productDescription']//script//text()")).strip()
        h4_txt = "\n".join(self.tree_html.xpath("//div[@id='tab_overview']//h4//text()")).strip()
        long_description = long_description.replace(script, "")
        if len(h4_txt) > 0:
            long_description = h4_txt + "\n" + long_description
        return long_description

    def _long_description(self):
        description = self._description_helper()
        if len(description) < 1:
            return None
        return self._long_description_helper()

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_urls = []
        rows = self.tree_html.xpath("//ul[@id='carousel_alternate']//li/a/@data-cloudzoom")
        for row in rows:
            jsn = json.loads(row)
            try:
                image_urls.append(jsn["zoomImage"])
            except:
                pass
        # image_url = self.tree_html.xpath("//ul[@id='carousel_alternate']//img/@src")
        return image_urls

    def _image_count(self):
        image_urls = self._image_urls()
        return len(image_urls)

    def _video_urls(self):
        video_url = self.tree_html.xpath("//ul[@id='carousel_alternate']//a[@class='gallery-video']/@href")
        if len(video_url) == 0:
            return None
        return video_url

    def _video_count(self):
        urls = self._video_urls()
        if urls:
            return len(urls)
        return 0

    def _pdf_urls(self):
        pdfs = self.tree_html.xpath("//a[contains(@href,'.pdf')]")
        pdf_hrefs = []
        for pdf in pdfs:
            try:
                if pdf.attrib['title'] == 'Terms & Conditions':
                    continue
            except KeyError:
                pass
            pdf_hrefs.append("http://www.maplin.co.uk%s" % pdf.attrib['href'])
        if len(pdf_hrefs) == 0:
            return None
        return pdf_hrefs

    def _pdf_count(self):
        urls = self._pdf_urls()
        if urls is not None:
            return len(urls)
        return 0

    def _webcollage(self):
        return 0

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
    def _load_reviews(self):
        try:
            if not self.max_score or not self.min_score:
                # for ex: http://samsclub.ugc.bazaarvoice.com/1337/prod12250457/reviews.djs?format=embeddedhtml
                url = "http://api.bazaarvoice.com/data/batch.json?passkey=p8bkgbkwhg9r9mcerwvg75ebc&apiversion=5.5" \
                      "&displaycode=19113-en_gb&resource.q0=products&filter.q0=id%3Aeq%3A"
                url = url + self.tree_html.xpath("//input[@name='productCodePost']//@value")[0].strip()
                url = url + "&stats.q0=questions%2Creviews&filteredstats.q0=questions%2Creviews" \
                            "&filter_questions.q0=contentlocale%3Aeq%3Aen_GB%2Cen_US" \
                            "&filter_answers.q0=contentlocale%3Aeq%3Aen_GB%2Cen_US" \
                            "&filter_reviews.q0=contentlocale%3Aeq%3Aen_GB%2Cen_US" \
                            "&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_GB%2Cen_US"
                contents = urllib.urlopen(url).read()
                jsn = json.loads(contents)
                jsn = jsn["BatchedResults"]
                jsn = jsn["q0"]["Results"][0]["FilteredReviewStatistics"]
                self.review_count = int(jsn["TotalReviewCount"])
                self.reviews = []
                for item in jsn["RatingDistribution"]:
                    try:
                        score = item['RatingValue']
                        score_cnt = item['Count']
                        self.reviews.append([int(score), int(score_cnt)])
                    except:
                        pass
                reviews = self.reviews
                for idx in range(1,6,1):
                    flag = False
                    for k, v in reviews:
                        if k == idx:
                            flag = True
                            break
                    if flag == False:
                        self.reviews.insert(idx-1, [idx, 0])

                for k, v in reversed(self.reviews):
                    if int(v) > 0:
                        self.max_score = k
                        break

                for k, v in self.reviews:
                    if int(v) > 0:
                        self.min_score = k
                        break
                self.average_review = float(jsn["AverageOverallRating"])
        except:
            pass

    def _average_review(self):
        self._load_reviews()
        return "%.2f" % self.average_review

    def _review_count(self):
        self._load_reviews()
        return self.review_count

    def _max_review(self):
        self._load_reviews()
        return self.max_score

    def _min_review(self):
        self._load_reviews()
        return self.min_score

    def _reviews(self):
        self._load_reviews()
        if len(self.reviews) < 1:
            return None
        return self.reviews

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        price = self.tree_html.xpath("//meta[@itemprop='price']/@content")[0].strip()
        currency = self.tree_html.xpath("//meta[@itemprop='priceCurrency']/@content")[0].strip()
        if price and currency:
            return "%s %s" % (currency, price)
        else:
            return None

    def _price_amount(self):
        price = self._price()
        price = price.replace(",", "")
        price_amount = re.findall(r"[\d\.]+", price)[0]
        return float(price_amount)

    def _price_currency(self):
        price = self._price()
        price = price.replace(",", "")
        price_amount = re.findall(r"[\d\.]+", price)[0]
        price_currency = price.replace(price_amount, "")
        if price_currency == "$":
            return "USD"
        elif price_currency == "£":
            return "GBP"
        return price_currency

    def _in_stores(self):
        # available to purchase in stores, 1/0
        rows = self.tree_html.xpath("//input[contains(@class,'grey discontinued')]")
        if len(rows) > 0:
            return 0
        rows = self.tree_html.xpath("//div[contains(@class,'prod_add_to_cart')]//input[contains(@class,'emailwhenstock')]")
        if len(rows) > 0:
            return 0
        return 1

    def _marketplace(self):
        '''marketplace: the product is sold by a third party and the site is just establishing the connection
        between buyer and seller. E.g., "Sold by X and fulfilled by Amazon" is also a marketplace item,
        since Amazon is not the seller.
        '''
        return 0

    def _marketplace_sellers(self):
        '''marketplace_sellers - the list of marketplace sellers - list of strings (["seller1", "seller2"])
        '''
        return None

    def _marketplace_lowest_price(self):
        # marketplace_lowest_price - the lowest of marketplace prices - floating-point number
        return None

    def _marketplace_out_of_stock(self):
        """Extracts info on whether currently unavailable from any marketplace seller - binary
        Uses functions that work on both old page design and new design.
        Will choose whichever gives results.
        Returns:
            1/0
        """
        return None

    def _site_online(self):
        # site_online: the item is sold by the site (e.g. "sold by Amazon") and delivered directly, without a physical store.
        rows = self.tree_html.xpath("//input[contains(@class,'grey discontinued')]")
        if len(rows) > 0:
            return 1
        rows = self.tree_html.xpath("//div[contains(@class,'prod_add_to_cart')]//input[contains(@class,'emailwhenstock')]")
        if len(rows) > 0:
            return 1
        lis = self.tree_html.xpath("//ul[contains(@class,'stock-status')]//li")
        for li in lis:
            txt = li.xpath(".//text()")[0].strip()
            i_class = li.xpath(".//i/@class")[0].strip()
            if txt == "Home Delivery" and i_class == "icon-ok-sign":
                return 1
            elif txt == "Home Delivery" and i_class == "icon-remove-sign":
                return 0
        return 1

    def _site_online_out_of_stock(self):
        #  site_online_out_of_stock - currently unavailable from the site - binary
        if self._site_online() == 0:
            return None
        rows = self.tree_html.xpath("//input[contains(@class,'grey discontinued')]")
        if len(rows) > 0:
            return 1
        rows = self.tree_html.xpath("//div[contains(@class,'prod_add_to_cart')]//input[contains(@class,'emailwhenstock')]")
        if len(rows) > 0:
            return 1
        lis = self.tree_html.xpath("//ul[contains(@class,'stock-status')]//li")
        for li in lis:
            txt = li.xpath(".//text()")[0].strip()
            i_class = li.xpath(".//i/@class")[0].strip()
            if txt == "Home Delivery" and i_class == "icon-ok-sign":
                return 0
            elif txt == "Home Delivery" and i_class == "icon-remove-sign":
                return 1
        return 0

    def _in_stores_out_of_stock(self):
        '''in_stores_out_of_stock - currently unavailable for pickup from a physical store - binary
        (null should be used for items that can not be ordered online and the availability may depend on location of the store)
        '''
        return None

    def _web_only(self):
        txts = self.tree_html.xpath("//div[contains(@class,'product-images')]//p[contains(@class,'tab-webonly')]//text()")
        if "Web only" in txts:
            return 1
        return 0

    def _home_delivery(self):
        rows = self.tree_html.xpath("//ul[contains(@class,'stock-status')]//li")
        for row in rows:
            txt = row.xpath(".//text()")[0].strip()
            if "Home Delivery" in txt:
                i_tag = row.xpath(".//i[contains(@class,'icon-ok-sign')]")
                if len(i_tag) > 0:
                    return 1
        return 0

    def _click_and_collect(self):
        rows = self.tree_html.xpath("//ul[contains(@class,'stock-status')]//li")
        for row in rows:
            txt = row.xpath(".//text()")[0].strip()
            if "Click & Collect" in txt:
                i_tag = row.xpath(".//i[contains(@class,'icon-ok-sign')]")
                if len(i_tag) > 0:
                    return 1
        return 0

    def _dsv(self):
        txts = self.tree_html.xpath("//div[@id='product-ctas']//div//text()")
        if "Shipped from an alternative warehouse" in txts:
            return 1
        return 0

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        all = self.tree_html.xpath("//ul[contains(@class, 'breadcrumb')]//li//span/text()")
        out = all[1:-1]#the last value is the product itself, and the first value is "home"
        out = [self._clean_text(r) for r in out]
        #out = out[::-1]
        return out

    def _category_name(self):
        return self._categories()[-1]

    def load_universal_variable(self):
        js_content = ' '.join(self.tree_html.xpath('//script//text()'))

        universal_variable = {}
        universal_variable["manufacturer"] = re.findall(r'"manufacturer": "(.*?)"', js_content)[0]
        return universal_variable

    def _brand(self):
        return self.load_universal_variable()["manufacturer"]

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

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "model" : _model, \
        "long_description" : _long_description, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "mobile_image_same" : _mobile_image_same, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "web_only" : _web_only, \
        "home_delivery" : _home_delivery, \
        "click_and_collect" : _click_and_collect, \
        "dsv" : _dsv, \
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
        "loaded_in_seconds": None \
        }


    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        # CONTAINER : CLASSIFICATION
        "brand" : _brand, \

        # CONTAINER : REVIEWS
        "average_review" : _average_review, \
        "review_count" : _review_count, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \
    }

