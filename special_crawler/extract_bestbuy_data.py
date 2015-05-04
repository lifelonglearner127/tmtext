#!/usr/bin/python

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

class BestBuyScraper(Scraper):
    
    ##########################################
    ############### PREP
    ##########################################
    INVALID_URL_MESSAGE = "Expected URL format is http://www.bestbuy.com/site/<product-name>/<product-id>.*"

    feature_count = None
    features = None
    video_urls = None
    video_count = None
    pdf_urls = None
    pdf_count = None
    wc_content = None
    wc_video = None
    wc_pdf = None

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
        True if valid, False otherwise
        """
        m = re.match(r"^http://www.bestbuy.com/.*$", self.product_page_url)
        return not not m

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''

        txt = " ".join(self.tree_html.xpath("//div[contains(@class,'alert alert-warning')]//text()"))
        if "This item is no longer available" in txt:
            return True
        return False


    ##########################################
    ############### CONTAINER : NONE
    ##########################################
    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        prod_id = self.tree_html.xpath('//div[@id="pdp-model-data"]/@data-product-id')[0]
        return prod_id

    def _site_id(self):
        return None

    def _status(self):
        return "success"




    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//meta[@itemprop="name"]/@content')[0]
    
    def _product_title(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _model(self):
        return self.tree_html.xpath('//span[@id="model-value"]/text()')[0]

    def _upc(self):
        return self.tree_html.xpath('//div[@id="pdp-model-data"]/@data-sku-id')[0]

    def _features(self):
        if self.feature_count is not None:
            return self.features
        self.feature_count = 0

        # http://www.bestbuy.com/site/sony-65-class-64-1-2-diag--led-2160p-smart-3d-4k-ultra-hd-tv-black/5005015.p;template=_specificationsTab
        url = None
        data_tabs = self.tree_html.xpath("//div[@id='pdp-model-data']/@data-tabs")
        jsn = json.loads(data_tabs[0])
        for tab in jsn:
            if tab["id"] == "specifications":
                url = tab["fragmentUrl"]
                url = "http://www.bestbuy.com%s" % url
                break
        line_txts = []
        if url is not None:
            contents = urllib.urlopen(url).read()
            # document.location.replace('
            tree = html.fromstring(contents)
            rows = tree.xpath("//table//tbody//tr")
            for r in rows:
                th_txt = " ".join(r.xpath(".//th//text()"))
                td_txt = " ".join(r.xpath(".//td//text()"))
                if len(th_txt) > 0 and len(td_txt) > 0:
                    line = "%s: %s" % (th_txt, td_txt)
                    line_txts.append(line)
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

    def _description_helper(self):
        rows = self.tree_html.xpath("//div[@id='long-description']//text()")
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        description = "\n".join(rows)
        return description

    def _description(self):
        description = self._description_helper()
        if len(description) < 1:
            return self._long_description_helper()
        return description

    def _long_description_helper(self):
        rows = self.tree_html.xpath("//div[@id='features']//text()")
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        description = "\n".join(rows)
        return description

    def _long_description(self):
        description = self._description_helper()
        if len(description) < 1:
            return None
        return self._long_description_helper()




    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_url = self.tree_html.xpath('//div[@id="pdp-model-data"]/@data-gallery-images')[0]
        json_list = json.loads(image_url)
        image_url = []
        for i in json_list:
            image_url.append(i['url'])
        return image_url
    
    def _image_count(self):
        return len(self._image_urls())

    def _video_urls(self):
        if self.video_count is not None:
            return self.video_urls
        self.video_count = 0
        self.wc_video = 0

        url = self.tree_html.xpath("//ul[@id='media-links']//a/@href")
        if len(url) == 0:
            return None

        video_urls = []
        if "www.bestbuy.com" in url[0]:
            video_urls.append(url[0])
        elif "media.flixcar.com" in url[0]:
            contents = urllib.urlopen(url[0]).read()
            tree = html.fromstring(contents)
            rows = tree.xpath("//div[@id='minisite_multiple_videos']//object/@data")
            rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
            video_urls.append(rows)
        elif "content.webcollage.net" in url[0]:
            redirect_contents = self._wc_content()
            redirect_tree = html.fromstring(redirect_contents)
            tabs = redirect_tree.xpath("//div[@class='wc-ms-navbar']//li//a")
            for tab in tabs:
                tab_txt = ""
                try:
                    tab_txt = tab.xpath(".//span/text()")[0].strip()
                except IndexError:
                    continue
                if '360 view video' == tab_txt.lower() \
                        or 'videos' == tab_txt.lower() \
                        or 'video' == tab_txt.lower() \
                        or 'product tour' == tab_txt.lower():
                    redirect_link2 = tab.xpath("./@href")[0]
                    redirect_link2 = "http://content.webcollage.net" + redirect_link2
                    redirect_contents2 = urllib.urlopen(redirect_link2).read()
                    redirect_tree2 = html.fromstring(redirect_contents2)
                    jsn = json.loads(redirect_tree2.xpath("//div[contains(@class,'wc-json-data')]//text()")[0])
                    for video in jsn["videos"]:
                        try:
                            video_url = video["src"]["src"]
                            if len(video_url) > 0:
                                if not video_url.startswith("http"):
                                    video_url = "http://content.webcollage.net%s" % video_url
                                video_urls.append(video_url)
                                self.wc_video = 1
                        except KeyError:
                            continue
        elif "syndicate.sellpoint.net" in url[0]:
            # contents = urllib.urlopen(url[0]).read()
            # tree = html.fromstring(contents)
            # rows = tree.xpath("//div[@id='minisite_multiple_videos']//object/@data")
            # rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
            # video_urls.append(rows)
            self.video_count = 1

        if len(video_urls) < 1:
            return None
        self.video_urls = video_urls
        self.video_count = len(self.video_urls)
        return video_urls

    def _video_count(self):
        if self.video_count is None:
            self._video_urls()
        return self.video_count

    def _pdf_urls(self):
        if self.pdf_count is not None:
            return self.pdf_urls
        self.pdf_count = 0
        self.wc_pdf = 0
        pdfs = self.tree_html.xpath("//div[@id='pdp-content']//a[contains(@href,'.pdf')]")
        pdf_hrefs = []
        for pdf in pdfs:
            pdf_url_txts = [self._clean_text(r) for r in pdf.xpath(".//text()") if len(self._clean_text(r)) > 0]
            if len(pdf_url_txts) > 0:
                pdf_hrefs.append(pdf.attrib['href'])

        redirect_contents = self._wc_content()
        redirect_tree = html.fromstring(redirect_contents)
        tabs = redirect_tree.xpath("//div[@class='wc-ms-navbar']//li//a")
        for tab in tabs:
            tab_txt = ""
            try:
                tab_txt = tab.xpath(".//span/text()")[0].strip()
            except IndexError:
                continue
            if 'more info' == tab_txt.lower():
                redirect_link2 = tab.xpath("./@href")[0]
                redirect_link2 = "http://content.webcollage.net" + redirect_link2
                redirect_contents2 = urllib.urlopen(redirect_link2).read()
                redirect_tree2 = html.fromstring(redirect_contents2)
                rows = redirect_tree2.xpath("//div[@id='wc-pc-content']//a[contains(@class,'wc-document-view-link')]/@data-asset-url")
                rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
                rows = list(set(rows))
                rows = ["http://content.webcollage.net%s" % r for r in rows]
                if len(rows) > 0:
                    pdf_hrefs += rows
                    self.wc_pdf = 1

        if len(pdf_hrefs) < 1:
            return None
        self.pdf_count = len(pdf_hrefs)
        self.pdf_urls = pdf_hrefs
        return pdf_hrefs
    
    def _pdf_count(self):
        if self.pdf_count is None:
            self._pdf_urls()
        return self.pdf_count

    def _wc_content(self):
        if self.wc_content == None:
            url = self.tree_html.xpath("//ul[@id='media-links']//a/@href")
            if len(url) == 0:
                return ""
            if "webcollage.net" in url[0]:
                contents = urllib.urlopen(url[0]).read()
                tree = html.fromstring(contents)
                redirect_link = tree.xpath("//div[@id='slow-reporting-message']//a/@href")[0]
                redirect_contents = urllib.urlopen(redirect_link).read()
                self.wc_content = redirect_contents.replace("\\","")
                return self.wc_content
        return self.wc_content

    def _wc_360(self):
        content = self._wc_content()
        if "wc-360" in content: return 1
        return 0


    def _wc_pdf(self):
        if self.pdf_count is None:
            self._pdf_urls()
        return self.wc_pdf

    def _wc_video(self):
        if self.video_count is None:
            self._video_urls()
        return self.wc_video

    def _wc_emc(self):
        content = self._wc_content()
        if "wc-aplus" in content: return 1
        return 0

    def _wc_prodtour(self):
        content = self._wc_content()
        if "wc-tour" in content: return 1
        tree = html.fromstring(content)
        rows = tree.xpath("//div[@class='wc-ms-navbar']//li//a//text()")
        if "Reading Your Card" in rows: return 1
        return 0

    def _flixmedia(self):
        url = self.tree_html.xpath("//ul[@id='media-links']//a/@href")
        if len(url) > 0:
            if "flixcar.com" in url[0]:
                return 1
        return 0

    def _webcollage(self):
        content = self._wc_content()
        if content is not None and len(content) > 0:
            return 1
        return 0

    def _sellpoints(self):
        url = self.tree_html.xpath("//ul[@id='media-links']//a/@href")
        if len(url) > 0:
            if "sellpoint.net" in url[0]:
                return 1
        return 0


    def _htags(self):
        htags_dict = {}
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    def _keywords(self):
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0]

    # extracts whether the first product image is the "no-image" picture
    def _no_image(self):
        None

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    def _average_review(self):
        return self.tree_html.xpath('//span[@itemprop="ratingValue"]//text()')[0]

    def _review_count(self):
        return self.tree_html.xpath('//meta[@itemprop="reviewCount"]/@content')[0]
 
    def _max_review(self):
        return None

    def _min_review(self):
        return None

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        meta_price = self.tree_html.xpath('//meta[@itemprop="price"]//@content')
        if meta_price:
            return meta_price[0].strip()
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
        return price_currency

    def _in_stores(self):
        rows = self.tree_html.xpath("//a[contains(@title,'Add to Registry')]")
        if len(rows) > 0:
            return 1
        return 0

    def _marketplace(self):
        rows = self.tree_html.xpath("//div[contains(@class,'marketplace-puck')]//a//text()")
        rows = [r for r in rows if "Marketplace" in r]
        if len(rows) > 0:
            return 1
        return 0

    def _marketplace_sellers(self):
        if self._marketplace() == 1:
            rows = self.tree_html.xpath("//div[contains(@class,'marketplace-featured')]/a//text()")
            rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
            return rows
        return None

    def _marketplace_lowest_price(self):
        return self._price()

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
        return 1

    def _site_online_out_of_stock(self):
        #  site_online_out_of_stock - currently unavailable from the site - binary
        if self._site_online() == 0:
            return None
        rows = self.tree_html.xpath("//div[contains(@class,'cart-button')]/@data-add-to-cart-message")
        if "Sold Out Online" in rows:
            return 1
        return 0

    def _in_stores_out_of_stock(self):
        '''in_stores_out_of_stock - currently unavailable for pickup from a physical store - binary
        (null should be used for items that can not be ordered online and the availability may depend on location of the store)
        '''
        if self._in_stores() == 0:
            return None
        return 0

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################    
    def _categories(self):
        all = self.tree_html.xpath("//ul[@id='breadcrumb-list']/li/a/text()")
        return all

    def _category_name(self):
        dept = " ".join(self.tree_html.xpath("//ul[@id='breadcrumb-list']/li[1]/a/text()")).strip()
        return dept
    
    def _brand(self):
        return self.tree_html.xpath('//meta[@id="schemaorg-brand-name"]/@content')[0]
    



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
        "model_meta" : _model_meta, \
        "description" : _description, \
        "long_description" : _long_description, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "no_image" : _no_image, \
        "htags" : _htags, \
        "keywords" : _keywords, \

        # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "in_stores" : _in_stores, \
        "marketplace": _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \
        "marketplace_out_of_stock" : _marketplace_out_of_stock, \
        "site_online" : _site_online, \
        "site_online_out_of_stock" : _site_online_out_of_stock, \
        "in_stores_out_of_stock" : _in_stores_out_of_stock, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \



        "loaded_in_seconds" : None, \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        # CONTAINER : PRODUCT_INFO
        "features" : _features, \
        "feature_count" : _feature_count, \

        # CONTAINER : PAGE_ATTRIBUTES
        "mobile_image_same" : _mobile_image_same, \
        "webcollage" : _webcollage, \
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        "wc_emc" : _wc_emc, \
        "wc_video" : _wc_video, \
        "wc_pdf" : _wc_pdf, \
        "wc_prodtour" : _wc_prodtour, \
        "flixmedia" : _flixmedia, \
        "sellpoints": _sellpoints, \
    }



