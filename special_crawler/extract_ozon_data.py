#!/usr/bin/python
 # -*- coding: utf-8 -*-

import urllib
import re
import sys
import json
import os.path
from lxml import html
from lxml import etree
import time
import requests
from extract_data import Scraper

class OzonScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################
    
    INVALID_URL_MESSAGE = "Expected URL format is http://www.ozon.ru/.*"

    feature_count = 0
    is_long_desc_is_none = False

    def check_url_format(self):
        m = re.match("^http://www\.ozon\.ru/.*$", self.product_page_url) 
        return (not not m)
    
    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        if len(self._categories()) < 1:
            return True
        else:
            return False
    ##########################################
    ############### CONTAINER : NONE
    ##########################################


    def _url(self):
        return self.product_page_url
    
    def _event(self):
        return None

    def _product_id(self):
        flag = False
        for item in self.product_page_url.split('/'):
            if flag:
                product_id = item
                break
            if item == "id":
                flag = True
        return product_id
        # product_id = self.tree_html.xpath('//div[@class="eDetail_ProductId"]//text()')[0]
        # return product_id

    def _site_id(self):
        return None

    def _status(self):
        return 'success'



    ##########################################
    ################ CONTAINER : PRODUCT_INFO
    ##########################################


    def _product_name(self):
        return self.tree_html.xpath("//h1")[0].text

    def _product_title(self):
        return self.tree_html.xpath("//h1")[0].text

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _model(self):
        isbn = self.tree_html.xpath("//p[@itemprop='isbn']//text()")[0].strip()
        if isbn and len(isbn) > 0:
            return isbn
        try:
            names = self.tree_html.xpath("//div[@class='bTechDescription']/div[starts-with(@class,'bTechCover')]/div[@class='bTechName']//text()")
            values = self.tree_html.xpath("//div[@class='bTechDescription']/div[starts-with(@class,'bTechCover')]/div[@class='bTechDescr']//text()")
            idx = 0
            model = None
            for name in names:
                if "Артикул" == name.encode('utf-8').strip():
                    model = values[idx].strip()
                    break
                idx += 1
            return model
        except IndexError:
            return None

        return None

    def _upc(self):
        return None

    def _features(self):
        rows = self.tree_html.xpath("//div[@class='bTechDescription']//div[contains(@class, 'bTechCover')]")
        cells = map(lambda row: row.xpath(".//*//text()"), rows)
        rows_text = map(\
            lambda row: ":".join(\
                map(lambda cell: cell.strip(), row)\
                ), \
            cells)
        if len(rows_text) < 1:
            # get from json
            script = " ".join(self.tree_html.xpath("//div[@class='bContentColumn']/script/text()"))
            m = re.findall(r"\.model_data = (.*?)};", script)
            script = m[0] + "}"
            jsn = json.loads(script)
            #jsn = jsn['Gallery']['Groups']
            rows_text = []
            for feature in jsn["Capabilities"]["Capabilities"]:
                try:
                    rows_text.append("%s: %s" % (feature["Name"], feature["Value"][0]["Text"]))
                except:
                    rows_text.append("%s: %s" % (feature["Name"], feature["Value"]))
            self.feature_count = len(rows_text)
            short_description = jsn["FirstComment"]["FirstComment"]["Text"]

        all_features_text = "\n".join(rows_text)
        return all_features_text

    def _feature_count(self):
        features = self._features()
        if self.feature_count > 0:
            return self.feature_count
        return len(filter(lambda row: len(row.xpath(".//text()"))>0, self.tree_html.xpath("//div[@class='bTechDescription']//div[contains(@class, 'bTechCover')]")))

    def _model_meta(self):
        return None

    def _description(self):
        short_description = " ".join(self.tree_html.xpath("//div[@class='bDetailLogoBlock']//text()")).strip()
        if len(short_description) < 1:
            # for ex: http://www.ozon.ru/context/detail/id/19966749/
            # short_description = " ".join(self.tree_html.xpath("//div[starts-with(@class,'eFirstDetailComment_textIn')]//text()"))
            # if len(short_description) < 1:
            # http://www.ozon.ru/context/detail/id/18467120/
            try:
                script = " ".join(self.tree_html.xpath("//div[@class='bContentColumn']/script/text()"))
                m = re.findall(r"\.model_data = (.*?)};", script)
                script = m[0] + "}"
                jsn = json.loads(script)
                # short_description = jsn["FirstComment"]["FirstComment"]["Text"]
                rows_text = []
                for row in jsn["Capabilities"]["MainCapabilities"]:
                    try:
                        rows_text.append("%s: %s" % (row["Name"], row["Value"]["Text"]))
                    except:
                        rows_text.append("%s: %s" % (row["Name"], row["Value"]))
                short_description = "\n".join(rows_text)
            except IndexError:
                short_description = ""

            if len(short_description) < 1:
                self.is_long_desc_is_none = True
                short_description = " ".join(self.tree_html.xpath("//div[@class='mDetail_SidePadding']/table//text()")).strip()
                if len(short_description) < 1:
                    short_description = self._clean_html(jsn["Description"]["ManufacturerDescription"] + "\n" + jsn["Description"]["OzonDescription"])
        return short_description

    def _long_description(self):
        description = self._description()
        if self.is_long_desc_is_none:
            return None
        description = " ".join(self.tree_html.xpath("//div[@class='mDetail_SidePadding']/table//text()")).strip()
        if len(description) < 1:
            # return  " ".join(self.tree_html.xpath("//div[@itemprop='description']//text()")).strip()
            try:
                script = " ".join(self.tree_html.xpath("//div[@class='bContentColumn']/script/text()"))
                m = re.findall(r"\.model_data = (.*?)};", script)
                script = m[0] + "}"
                jsn = json.loads(script)
                #jsn = jsn['Gallery']['Groups']
                description = self._clean_html(jsn["Description"]["ManufacturerDescription"] + "\n" + jsn["Description"]["OzonDescription"])
            except IndexError:
                description = None
        return description


    ##########################################
    ################ CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _meta_tags(self):
        tags = map(lambda x:x.values() ,self.tree_html.xpath('//meta[not(@http-equiv)]'))
        return tags

    def _meta_tag_count(self):
        tags = self._meta_tags()
        return len(tags)

    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        try:
            text = self.tree_html.xpath('//*[@class="bImageColumn"]//script//text()')
            text = re.findall(r'gallery_data \= (\[\{.*\}\]);', str(text))[0]
            jsn = json.loads(text)
        except IndexError:
            text = self.tree_html.xpath('//div[@class="bCombiningColumn"]//div[@class="bContentColumn"]//script//text()')
            text = re.findall(r'\.model_data = (\{.*\});', str(text))[0]
            text = ''.join(text)
            jsn = json.loads(text.decode("unicode_escape"))
            jsn = jsn['Gallery']['Groups']

        image_url = []
        for row in jsn:
            if 'Elements' in row:
                for element in row['Elements']:
                    if 'Original' in element:
                        if 'noimg_' not in element['Original']:
                            image_url.append(element['Original'])
        if len(image_url) < 1:
            return None
        return image_url

    def _image_count(self):
        image_url = self._image_urls()
        if not image_url:
            return 0
        return len(image_url)

    # return 1 if the "no image" image is found
    def _no_image(self):
        return None


    def _video_urls(self):
        """ example video pages:
        http://www.ozon.ru/context/detail/id/24920178/
        http://www.ozon.ru/context/detail/id/19090838/
        """
        iframes = self.tree_html.xpath("//iframe")
        video_url = []
        for iframe in iframes:
            src = str(iframe.xpath('.//@src'))
            find = re.findall(r'www\.youtube\.com/embed/.*$', src)
            if find:
                video_url.append(find[0])
        if len(video_url) < 1:
            return None
        return video_url

    def _video_count(self):
        video_urls = self._video_urls()
        if not video_urls:
            return 0
        return len(video_urls)

    def _pdf_urls(self):
        return None
        
    def _pdf_count(self):
        urls = self._pdf_urls()
        if urls is not None:
            return len(urls)
        return 0

    def _webcollage(self):
        return None

    def _htags(self):
        htags_dict = {}
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    def _loaded_in_seconds(self):
        return None

    def _keywords(self):
        return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]






    ##########################################
    ################ CONTAINER : REVIEWS
    ##########################################

    def _average_review(self):
        r = self.tree_html.xpath('//div[@itemprop="ratingValue"]//text()')[0]
        return r
    
    def _review_count(self):
        try:
            nr = self.tree_html.xpath('//div[@itemprop="aggregateRating"]//span//text()')[0]
            return re.findall(r'[0-9]+', nr)[0]
        except IndexError:
            return 0

    def _max_review(self):
        return None

    def _min_review(self):
        return None




    ##########################################
    ################ CONTAINER : SELLERS
    ##########################################

    def _price(self):
        try:
            price_txt = self.tree_html.xpath("//div[@class='bSale_BasePriceCover']//div[contains(@class, 'bOzonPrice mSaleBlock')]//span[contains(@class,'eOzonPrice_main')]//text()")[0].strip()
            price_sub_txt = self.tree_html.xpath("//div[@class='bSale_BasePriceCover']//div[contains(@class, 'bOzonPrice mSaleBlock')]//span[contains(@class,'eOzonPrice_submain')]//text()")[0].strip()
            currency_txt = self.tree_html.xpath("//div[@class='bSale_BasePriceCover']//div[contains(@class, 'bOzonPrice mSaleBlock')]//meta[@itemprop='priceCurrency']/@content")[0].strip()
            price_txt = price_txt.replace(u'\xa0', u'')
            return "%s.%s %s" % (price_txt, price_sub_txt, currency_txt)
        except IndexError:
            return None

    def _in_stores_only(self):
        return 0

    def _in_stores(self):
        return None

    def _owned(self):
        return 1

    def _owned_out_of_stock(self):
        try:
            text = self.tree_html.xpath("//div[starts-with(@class,'bSaleBlock')]/h3/text()")[0]
            text = text.encode("utf-8")
            if text.strip() == "Нет в продаже":
                return 1
        except IndexError:
            return 0
        return None

    def _marketplace(self):
        return 0
    
    def _marketplace_sellers(self):
        return None

    def _marketplace_lowest_price(self):
        return None





    ##########################################
    ################ CONTAINER : CLASSIFICATION
    ##########################################

    def _categories(self):
        all = self.tree_html.xpath("//ul[@class='navLine']/li//text()")
        #the last value is the product itself
        return all[0:-1]
   
    def _category_name(self):
        # dept = " ".join(self.tree_html.xpath("//ul[@class='navLine']/li[1]//text()")).strip()
        return self._categories()[-1]
   
    def _brand(self):
        #search for misc product brand
        brand_txt = self.tree_html.xpath("//div[@class='PageModule']//a[contains(@href, 'brand')]/text()")
        for brand in brand_txt:
            if len(brand.strip())>1:
                return brand.strip()

        #search for a books brand
        try:
            brand_txt = self.tree_html.xpath("//*[@itemprop='publisher']/a//text()")[0].strip()
            return brand_txt
        except:
            pass

        # try:
        #     brand_txt = self.tree_html.xpath("//div[@class='bContentBlock']//h1[@itemprop='name']//text()")[0].strip()
        #     brand_txt = brand_txt.split("//*[@itemprop='publisher'] ")[0]
        #     if len(brand_txt) == 0:
        #         return None
        #     return "C"+brand_txt
        # except IndexError:
        #     return None
        
    '''
    python curl_wrapper.py 'localhost/get_data?url=http://www.ozon.ru/context/detail/id/1434860/'
    "ФИЗМАТЛИТ"

    python curl_wrapper.py 'localhost/get_data?url=http://www.ozon.ru/context/detail/id/1435596/'
    None

    python curl_wrapper.py 'localhost/get_data?url=http://www.ozon.ru/context/detail/id/26422253/'
    Joan Rivers

    python curl_wrapper.py 'localhost/get_data?url=http://www.ozon.ru/context/detail/id/19550371/'
    ФК Зенит
    '''



    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################

    def _clean_text(self, text):
        return re.sub("&nbsp;", " ", text).strip()

    def _clean_html(self, raw_html):
        cleanr =re.compile('<.*?>')
        cleantext = re.sub(cleanr,'', raw_html)
        return cleantext

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
        "meta_tags": _meta_tags,\
        "meta_tag_count": _meta_tag_count,\

        # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "in_stores_only" : _in_stores_only, \
        "in_stores" : _in_stores, \
        "owned" : _owned, \
        "owned_out_of_stock" : _owned_out_of_stock, \
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

