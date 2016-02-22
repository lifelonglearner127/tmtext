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


class SamsclubScraper(Scraper):

    ##########################################
    ############### PREP+
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.samsclub.com/sams/(.+)?/(.+)"

    reviews_tree = None
    max_score = None
    min_score = None
    review_count = 0
    average_review = None
    reviews = None
    image_urls = None
    image_count = -1
    price = None
    price_amount = None
    price_currency = None
    video_count = None
    video_urls = None
    pdf_count = None
    pdf_urls = None

    def check_url_format(self):
        # for ex: http://www.samsclub.com/sams/dawson-fireplace-fall-2014/prod14520017.ip?origin=item_page.rr1&campaign=rr&sn=ClickCP&campaign_data=prod14170040
        m = re.match(r"^http://www\.samsclub\.com/sams/(.+)?/(.+)", self.product_page_url)
        return not not m

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''

        if len(self.tree_html.xpath("//div[contains(@class, 'imgCol')]//div[@id='plImageHolder']//img")) < 1:
            return True
        return False

    ##########################################
    #### ########### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        try:
            product_id = self.tree_html.xpath("//input[@name='/atg/commerce/order/purchase/CartModifierFormHandler.baseProductId']/@value")[0].strip()
            return product_id
        except:
            pass
        try:
            product_id = self.tree_html.xpath("//input[@id='mbxProductId']/@value")[0].strip()
        except IndexError:
            product_id = self.tree_html.xpath("//div[@id='myShoppingList']/@data-productid")[0].strip()
        return product_id
        # product_id = self.tree_html.xpath("//span[@itemprop='productID']//text()")[0].strip()
        # m = re.findall(r"[0-9]+", product_id)
        # if len(m) > 0:
        #     return m[0]
        # else:
        #     return None

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//span[@itemprop='name']//text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//span[@itemprop='name']//text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()
    
    def _model(self):
        return self.tree_html.xpath("//span[@itemprop='model']//text()")[0].strip()

    def _upc(self):
        return self.tree_html.xpath("//input[@id='mbxSkuId']/@value")[0].strip()

    def _features(self):
        lis = self.tree_html.xpath("//div[contains(@class,'itemFeatures')]//li")
        rows = []
        for li in lis:
            txt = "".join(li.xpath(".//text()"))
            rows.append(txt)
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        if len(rows) < 1:
            trs = self.tree_html.xpath("//div[contains(@class,'itemFeatures')]//table//tr")
            rows = []
            for tr in trs:
                tds = tr.xpath(".//td")
                if len(tds) > 0:
                    row_txt = " ".join([self._clean_text(r) for r in tr.xpath(".//text()") if len(self._clean_text(r)) > 0])
                    rows.append(row_txt)
            if len(rows) < 1:
                return None
        return rows

    def _feature_count(self):
        features = len(self._features())
        if features is None:
            return 0
        return len(self._features())

    def _model_meta(self):
        return None

    def _description(self):
        description = self._description_helper()
        if len(description) < 1:
            return self._long_description_helper()
        return description

    def _description_helper(self):
        description = html.tostring(self.tree_html.xpath("//div[contains(@class,'itemBullets')]")[0])
        return description

    def _long_description(self):
        description = self._description_helper()
        if len(description) < 1:
            return None
        return self._long_description_helper()

    def _long_description_helper(self):
        rows = self.tree_html.xpath("//*[@itemprop='description']//text()")
        long_description = "".join(rows)
        long_description = long_description.replace("View a video of this product.", "")
        long_description = long_description.replace("View a video of this product", "")
        rows = self.tree_html.xpath("//*[@itemprop='description']/*")
        row_txts = []
        for row in rows:
            if row.tag == 'style' or row.tag == 'h3':
                row_txt = "".join(row.xpath(".//text()"))
                long_description = long_description.replace(row_txt, "")
        # row_txts = [self._clean_text(r) for r in row_txts if len(self._clean_text(r)) > 0]
        # if row_txts[0] == "Description":
        #     row_txts = row_txts[1:]
        # long_description = "\n".join(row_txts)
        return long_description.strip()

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        if self.image_count == -1:
            self.image_urls = None
            self.image_count = 0
            script = "/n".join(self.tree_html.xpath("//div[@class='container']//script//text()"))
            m = re.findall(r"imageList = '(.+)?'", script)
            imglist = m[0]
            url = "http://scene7.samsclub.com/is/image/samsclub/%s?req=imageset,json&id=init" % imglist
            contents = urllib.urlopen(url).read()
            m2 = re.findall(r'\"IMAGE_SET\"\:\"(.*?)\"', contents)
            img_set = m2[0]
            img_urls = []
            if len(img_set) > 0:
                img_arr = img_set.split(",")
                for img in img_arr:
                    img2 = img.split(";")
                    img_url = "http://scene7.samsclub.com/is/image/%s" % img2[0]
                    if img_url[-1:] not in "0123456789":
                        img_urls.append(img_url)

            if len(img_urls) == 0:
                img_urls = self.tree_html.xpath("//div[contains(@class, 'imgCol')]//div[@id='plImageHolder']//img/@src")
                if len(img_urls) < 1:
                    return None
                try:
                    if self._no_image(img_urls[0]):
                        return None
                except Exception, e:
                    print "WARNING: ", e.message

            self.image_urls = img_urls
            self.image_count = len(img_urls)
            return img_urls
        else:
            return self.image_urls

    def _image_count(self):
        if self.image_count == -1:
            image_urls = self.image_urls()
        return self.image_count

    # return True if there is a no-image image and False otherwise
    # Certain products have an image that indicates "there is no image available"
    # a hash of these "no-images" is saved to a json file and new images are compared to see if they're the same
    # def _no_image(self):
    #     #get image urls
    #     head = 'http://scene7.samsclub.com/is/image/'
    #     image_url = self.tree_html.xpath("//section[@class='main-details']//script//text()")[1]
    #     image_url = re.findall("scene7PdpData\.s7ImageSet = '(.*)';", image_url)[0]
    #     image_url = image_url.split(',')
    #     image_url = [head+link for link in image_url]
    #     path = 'no_img_list.json'
    #     no_img_list = []
    #     if os.path.isfile(path):
    #         f = open(path, 'r')
    #         s = f.read()
    #         if len(s) > 1:
    #             no_img_list = json.loads(s)
    #         f.close()
    #     first_hash = str(MurmurHash.hash(self.fetch_bytes(image_url[0])))
    #     if first_hash in no_img_list:
    #         return True
    #     else:
    #         return False
    #
    # #read the bytes of an image
    # def fetch_bytes(self, url):
    #     file = cStringIO.StringIO(urllib.urlopen(url).read())
    #     img = Image.open(file)
    #     b = BytesIO()
    #     img.save(b, format='png')
    #     data = b.getvalue()
    #     return data

    def _video_urls(self):
        if self.video_count is not None:
            return self.video_urls
        self.video_count = 0
        rows = self.tree_html.xpath("//div[@id='tabItemDetails']//a/@href")
        rows = [r for r in rows if "video." in r or "/mediaroom/" in r or ("//media." in r and (".flv" in r or ".mov" in r))]

        url = "http://content.webcollage.net/sc/smart-button?ird=true&channel-product-id=%s" % self._product_id()
        html = urllib.urlopen(url).read()
        # \"src\":\"\/_cp\/products\/1374451886781\/tab-6174b48c-58f3-4d4b-8d2f-0d9bf0c90a63
        # \/552b9366-55ed-443c-b21e-02ede6dd89aa.mp4.mobile.mp4\"
        video_base_url = self._find_between(html, 'data-resources-base=\\"', '\\">').replace("\\", "") + "%s"
        m = re.findall(r'"src":"([^"]*?\.mp4)"', html.replace("\\",""), re.DOTALL)
        for item in m:
            if ".blkbry" in item or ".mobile" in item:
                pass
            else:
                if video_base_url % item not in rows and item.count(".mp4") < 2:
                    rows.append(video_base_url % item)
        m = re.findall(r'"src":"([^"]*?\.flv)"', html.replace("\\",""), re.DOTALL)
        for item in m:
            if ".blkbry" in item or ".mobile" in item:
                pass
            else:
                if video_base_url % item not in rows and item.count(".flv") < 2:
                    rows.append(video_base_url % item)
        if len(rows) < 1:
            return None
        new_rows = [r for r in rows if ("%s.flash.flv" % r) not in rows]
        self.video_urls = list(set(new_rows))
        self.video_count = len(self.video_urls)
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
        pdfs = self.tree_html.xpath("//a[contains(@href,'.pdf')]")
        for pdf in pdfs:
            try:
                pdf_hrefs.append(pdf.attrib['href'])
            except KeyError:
                pass
        pdfs = self.tree_html.xpath("//a[contains(@href,'pdfpdf')]")
        for pdf in pdfs:
            try:
                if pdf.attrib['href'] not in pdf_hrefs:
                    pdf_hrefs.append(pdf.attrib['href'])
            except KeyError:
                pass
        pdfs = self.tree_html.xpath("//a[contains(@href,'pdf')]")
        for pdf in pdfs:
            try:
                if pdf.attrib['href'].endswith("pdf") and pdf.attrib['href'] not in pdf_hrefs:
                    pdf_hrefs.append(pdf.attrib['href'])
            except KeyError:
                pass
        pdfs = self.tree_html.xpath("//a[contains(@onclick,'.pdf')]")
        for pdf in pdfs:
            # window.open('http://graphics.samsclub.com/images/pool-SNFRound.pdf','_blank')
            try:
                url = re.findall(r"open\('(.*?)',", pdf.attrib['onclick'])[0]
                if url not in pdf_hrefs:
                    pdf_hrefs.append(url)
            except IndexError:
                pass
        pdfs = self.tree_html.xpath("//a[contains(@onclick,'pdf')]")
        for pdf in pdfs:
            # window.open('http://graphics.samsclub.com/images/pool-SNFRound.pdf','_blank')
            try:
                url = re.findall(r"open\('(.*?)',", pdf.attrib['onclick'])[0]
                if url not in pdf_hrefs and url.endswith("pdf"):
                    pdf_hrefs.append(url)
            except IndexError:
                pass
        # http://content.webcollage.net/sc/smart-button?ird=true&channel-product-id=prod8570143
        url = "http://content.webcollage.net/sc/smart-button?ird=true&channel-product-id=%s" % self._product_id()
        html = urllib.urlopen(url).read()
        # \"src\":\"\/_cp\/products\/1374451886781\/tab-6174b48c-58f3-4d4b-8d2f-0d9bf0c90a63
        # \/552b9366-55ed-443c-b21e-02ede6dd89aa.mp4.mobile.mp4\"
        m = re.findall(r'wcobj="([^\"]*?\.pdf)"', html.replace("\\",""), re.DOTALL)
        pdf_hrefs += m
        pdf_hrefs = [r for r in pdf_hrefs if "JewelryDeliveryTimeline.pdf" not in r]
        if len(pdf_hrefs) < 1:
            return None
        self.pdf_urls = pdf_hrefs
        self.pdf_count = len(self.pdf_urls)
        return pdf_hrefs

    def _pdf_count(self):
        if self.pdf_count is None:
            self._pdf_urls()
        return self.pdf_count

    def _webcollage(self):
        # http://content.webcollage.net/sc/smart-button?ird=true&channel-product-id=prod10740044
        url = "http://content.webcollage.net/sc/smart-button?ird=true&channel-product-id=%s" % self._product_id()
        html = urllib.urlopen(url).read()
        m = re.findall(r'_wccontent = (\{.*?\});', html, re.DOTALL)
        try:
            if ".webcollage.net" in m[0]:
                return 1
        except IndexError:
            pass
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
    #populate the reviews_tree variable for use by other functions
    def _load_reviews(self):
        try:
            if not self.max_score or not self.min_score:
                # for ex: http://samsclub.ugc.bazaarvoice.com/1337/prod12250457/reviews.djs?format=embeddedhtml
                url = "http://samsclub.ugc.bazaarvoice.com/1337/%s/reviews.djs?format=embeddedhtml" % self._product_id()
                contents = urllib.urlopen(url).read()
                tmp_reviews = re.findall(r'<span class=\\"BVRRHistAbsLabel\\">(.*?)<\\/span>', contents)
                reviews = []
                for review in tmp_reviews:
                    review = review.replace(",", "")
                    m = re.findall(r'([0-9]+)', review)
                    reviews.append(m[0])

                reviews = reviews[:5]
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
                total_review = 0
                review_cnt = 0
                for review in reversed(reviews):
                    self.reviews.append([score, int(review)])
                    total_review += score * int(review)
                    review_cnt += int(review)
                    score += 1
                self.review_count = review_cnt
                self.average_review = total_review * 1.0 / review_cnt
                # self.reviews_tree = html.fromstring(contents)
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
        if self.price:
            return self.price
        try:
            price_amount = self.tree_html.xpath("//span[@class='price']//text()")[0].strip()
            currency = self.tree_html.xpath("//span[@class='superscript']//text()")[0].strip()
            superscript = self.tree_html.xpath("//span[@class='superscript']//text()")[1].strip()
            price = "%s%s.%s" % (currency, price_amount, superscript)
            self.price = price
            return price
        except:
            pass
        try:
            if self._site_online() == 0:
                return "not available online - no price given"
        except:
            pass
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
        '''in_stores - the item can be ordered online for pickup in a physical store
        or it can not be ordered online at all and can only be purchased in a local store,
        irrespective of availability - binary
        '''
        in_stores = None
        rows = self.tree_html.xpath("//div[contains(@class,'moneyBoxContainer')]//div[contains(@class,'moneyBoxBtn')]//text()")
        if "Visit your local Club for pricing & availability" in rows:
            in_stores = 1
        rows = self.tree_html.xpath("//div[@id='itemPageMoneyBox']//span//text()")
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        if "Select your Club" in rows and "for price and availability" in rows:
            in_stores = 1
        if in_stores is not None:
            return in_stores
        return 0

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
        rows = self.tree_html.xpath("//*[@id='addtocartsingleajaxonline']")
        if len(rows) > 0:
            return 1
        rows = self.tree_html.xpath("//div[contains(@class,'biggraybtn')]//text()")
        if "Out of stock online" in rows:
            return 1
        rows = self.tree_html.xpath("//div[contains(@class,'moneyBoxContainer')]//div[contains(@class,'moneyBoxBtn')]//text()")
        if "See online price in cart" in rows:
            return 1
        rows = self.tree_html.xpath("//button[@class='biggreenbtn']//text()")
        if len(rows) > 0:
            return 1
        return 0
        #
        # rows = self.tree_html.xpath("//div[contains(@class,'moneyBoxContainer')]//div[contains(@class,'moneyBoxBtn')]//text()")
        # site_online = None
        # if "Buy online" in rows:
        #     return 1
        # if "Unavailable online" in rows:
        #     site_online = 0
        # rows = self.tree_html.xpath("//div[@id='itemPageMoneyBox']//span//text()")
        # rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        # if "Select your Club" in rows and "for price and availability" in rows:
        #     site_online = 0
        # if site_online is not None:
        #     return site_online
        # return 1

    def _site_online_out_of_stock(self):
        #  site_online_out_of_stock - currently unavailable from the site - binary
        rows = self.tree_html.xpath("//div[contains(@class,'biggraybtn')]//text()")
        if "Out of stock online" in rows:
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
        all = self.tree_html.xpath("//div[contains(@id, 'breadcrumb')]//a/text()")
        out = [self._clean_text(r) for r in all][1:]

        if out:
            return out

        return None

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        return self.tree_html.xpath("//span[@itemprop='brand']//text()")[0].strip()

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
        "model" : _model, \
        "upc" : _upc,\
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "long_description" : _long_description, \

        # CONTAINER : PAGE_ATTRIBUTES
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        # "no_image" : _no_image, \
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
        # CONTAINER : PAGE_ATTRIBUTES
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \

         # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \
    }

