#!/usr/bin/python
#  -*- coding: utf-8 -*-

<<<<<<< HEAD
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
=======
import cStringIO
import json
import os.path
import re
import sys
import time
import urllib
from functools import partial
from io import BytesIO
from urlparse import urljoin

import mmh3 as MurmurHash
import requests
from extract_data import Scraper
from lxml import etree, html
from lxml.etree import _ElementStringResult
from PIL import Image


def pphtml(el):
    if isinstance(el, list):
        return map(pphtml, el)
    elif isinstance(el, _ElementStringResult):
        return str(el)
    return etree.tostring(el, encoding='unicode', pretty_print=True)
>>>>>>> e3921632d0d8ef473cbcbe019725692ed1c2293c


class SamsungScraper(Scraper):

    ##########################################
<<<<<<< HEAD
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.samsung.com/.*"

    reviews_tree = None
    max_score = None
    min_score = None
    review_count = None
    average_review = None
    reviews = None
    feature_count = None
    features = None

    def check_url_format(self):
        # http://www.samsung.com/us/home-appliances/refrigerators/4-door-flex/36-wide-34-cu-ft-capacity-4-door-flex-chef-collection-refrigerator-with-sparkling-water-dispenser-rf34h9960s4-aa/
        self.image_urls = None
        self.video_urls = None
        m = re.match("^http://www\.samsung\.com/.*$", self.product_page_url)
        return (not not m)

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        rows = self.tree_html.xpath("//div[contains(@class,'product-details__photo')]")
        if len(rows) > 0:
            return False
        return True

    ##########################################
    ############### CONTAINER : NONE
    ##########################################
=======
    # PREP
    #########################################

    INVALID_URL_MESSAGE = (
        "Expected URL format is (http|https)://www.samsung.com/us/.*")
    BASE_URL = "http://www.samsung.com/"
    BASE_URL_REVIEWSREQ = 'http://samsung.ugc.bazaarvoice.com/7463-en_us/{}/reviews.djs?format=embeddedhtml&dir=desc&sort=rating'
    PRICESPIDER_WC = '64196902-DEA5-435E-A54E-4CEA19C33575'
    PRICESPIDER_IMPRESSION_ID = '066b523a-dd7b-4ce2-a7b2-3438e92b9829'

    # xpaths
    bullet_xpath = "//section[contains(@class,'product-summary')]//div[contains(@class,'product-summary__card')]"

    def check_url_format(self):
        m = re.match(r"^(https|http)://www\.samsung\.com\/us\/.*",
                     self.product_page_url)
        return bool(m)

    def _ret(self, el):
        f_el = el[0] if el else None
        if isinstance(f_el, unicode):
            return f_el if f_el else None
        elif isinstance(f_el, _ElementStringResult):
            return f_el if f_el else None
        ret = f_el.text if f_el is not None else None
        return ret if ret else None
>>>>>>> e3921632d0d8ef473cbcbe019725692ed1c2293c

    def _url(self):
        return self.product_page_url

<<<<<<< HEAD
    def _product_id(self):
        product_id = self.tree_html.xpath("//h2[contains(@class,'type-p3 product-details__info-sku')]/text()")[0].strip()
        return product_id

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath("//h1[@itemprop='name']/text()")[0].strip()

    def _product_title(self):
        return self.tree_html.xpath("//h1[@itemprop='name']/text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()
    
    def _model(self):
        return None

    def _upc(self):
        return None

    def _features(self):
        if self.feature_count is not None:
            return self.features
        self.feature_count = 0
        spec_cards = self.tree_html.xpath("//div[@class='spec-card']//text()")
        line_txts = []
        for spec_card in spec_cards:
            line = spec_card.xpath(".//text()")
            line = [r.strip() for r in line if len(r.strip()) > 0]
            line = " ".join(line)
            if len(line) > 0:
                line_txts.append(line)
        if len(line_txts) < 1:
            return None
        self.feature_count = len(line_txts)
        return line_txts

    def _feature_count(self):
        if self.feature_count is None:
            self._features()
        return self.feature_count

    def _model_meta(self):
        return None

    def _description(self):
        description = self._description_helper()
        if description is None or len(description) < 1:
            return self._long_description_helper()
        return description

    def _description_helper(self):
        rows = self.tree_html.xpath("//div[contains(@class,'product-details__info-description')]//text()")
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        line_txts = rows

        if len(line_txts) < 1:
            return None
        description = "".join(line_txts)
        return description

    def _long_description(self):
        description = self._description_helper()
        if description is None or len(description) < 1:
            return None
        return self._long_description_helper()

    def _long_description_helper(self):
        line_txts = []

        feature_items = self.tree_html.xpath("//div[contains(@class,'feature-benefit--inline')]")
        for r in feature_items:
            line = r.xpath(".//text")
            line = [r.strip() for r in line if len(r.strip()) > 0]
            line = " ".join(line)
            if len(line) > 0:
                line_txts.append(line)

        if len(line_txts) < 1:
            return None
        description = "".join(line_txts)
        return description

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_url = self.tree_html.xpath(
            "//div[contains(@class,'product-details__thumbnail')]"
            "//img[contains(@class,'product-details__img')]/@src")
        if len(image_url) < 1:
            return None
        try:
            if self._no_image(image_url[0]):
                return None
        except Exception, e:
            print "WARNING: ", e.message
        return image_url

    def _image_count(self):
        image_urls = self._image_urls()
        if image_urls:
            return len(image_urls)
        return 0

    def _video_urls(self):
        return None
    def _video_count(self):
        urls = self._video_urls()
        if urls:
            return len(urls)
        return 0

    def _pdf_urls(self):
        pdfs = self.tree_html.xpath("//a[contains(@href,'.pdf')]")
        pdf_hrefs = []
        for pdf in pdfs:
            pdf_url_txts = [self._clean_text(r) for r in pdf.xpath(".//text()") if len(self._clean_text(r)) > 0]
            if len(pdf_url_txts) > 0:
                pdf_hrefs.append(pdf.attrib['href'])
        if len(pdf_hrefs) < 1:
            return None
        pdf_hrefs = list(set(pdf_hrefs))
        return pdf_hrefs

    def _pdf_count(self):
        urls = self._pdf_urls()
        if urls is not None:
            return len(urls)
        return 0

    def _webcollage(self):
        atags = self.tree_html.xpath("//a[contains(@href, 'webcollage.net/')]")
        if len(atags) > 0:
            return 1
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
    def _average_review(self):
        if self.review_count is not None:
            return self.average_review
        self._reviews()
        return self.average_review

    def _review_count(self):
        if self.review_count is not None:
            return self.review_count
        self._reviews()
        return self.review_count

    def _max_review(self):
        if self.review_count is not None:
            return self.max_score
        self._reviews()
        return self.max_score

    def _min_review(self):
        if self.review_count is not None:
            return self.min_score
        self._reviews()
        return self.min_score

    def _reviews(self):
        if self.review_count is not None:
            return self.reviews

        lines = self.tree_html.xpath("//div[contains(@class,'star-details')]//div[contains(@class,'star-text')]//text()")
        lines = [r.strip() for r in lines if len(r.strip()) > 0]
        try:
            self.average_review = float(lines[0])
        except:
            pass

        lines = self.tree_html.xpath("//div[contains(@class,'reviews__total')]//text()")
        lines = [r.strip() for r in lines if len(r.strip()) > 0]
        try:
            num = re.findall(r"(\d+)", lines[0], re.DOTALL)[0]
            self.review_count = int(num)
        except:
            pass


        # link = self.tree_html.xpath("//span[contains(@class,'star-text__total')]//a/@href")
        # if len(link) > 0:
        #     link = "http://www.samsung.com%s" % link[0]
        #
        #     agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20140319 Firefox/24.0 Iceweasel/24.4.0'
        #     headers ={'User-agent': agent}
        #     with requests.Session() as s:
        #         s.get(self.product_page_url, headers=headers, timeout=30)
        #         response = s.get(link, headers=headers, timeout=30)
        #         if response != 'Error' and response.ok:
        #             contents = response.content
        #             # document.location.replace('
        #             tree = html.fromstring(contents)
        #             rows = tree.xpath("//text()")
        #             line_txts = []

        return None

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        try:
            price = self.tree_html.xpath(
                "//div[contains(@class,'product-details__info-price')]"
                "/span[contains(@class,'epp-price')]/text()"
            )[0].strip()
            arr = self.tree_html.xpath(
                "//div[contains(@class,'product-details__info-price')]"
                "/span[contains(@class,'after')]/text()")
            if '$' in arr:
                price = '$' + price
            return price
        except IndexError:
            pass
        return price

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
        return 1

    def _site_online_out_of_stock(self):
        #  site_online_out_of_stock - currently unavailable from the site - binary
        rows = self.tree_html.xpath("//span[contains(@class,'outOfStock')]//text()")
        if "out of stock" in rows:
            return 1
        rows = self.tree_html.xpath("//div[@class='buy_button']")
        if len(rows) < 1:
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
        arr = self.tree_html.xpath("//ol[@typeof='BreadcrumbList']//li//a")
        line_txts = []
        for r in arr:
            line = r.xpath(".//text()")
            line = [r.strip() for r in line if len(r.strip()) > 0]
            line = "".join(line)
            if len(line) > 0:
                line_txts.append(line)
        if len(line_txts) < 1:
            return None
        return line_txts
=======
    # product_info

    def _product_id(self):
        product_id = re.findall("product_id.*\"(.*)\"", self.page_raw_text)
        return self._ret(product_id)

    def _product_name(self):
        el = self.tree_html.xpath("//h1[@itemprop='name']")
        return self._ret(el)

    def _product_title(self):
        el = self.tree_html.xpath("//title")
        return self._ret(el)

    def _title_seo(self):
        return self._ret(self.tree_html.xpath("//meta[@name='title']/@content"))

    def _model(self):
        model = pphtml(self.tree_html.xpath(
            "//section[@class='breadcrumb section']//span[@property='name']/text()"))
        return model[-1] if len(model) > 2 else None

    def _description(self):
        el = self.tree_html.xpath(
            "//p[contains(@class,'p1-description')]/text()")
        description = " ".join(filter(lambda x: "".join(x.split()), el))
        return description

    def _shipping(self):
        ret = 'Ships in' in self.page_raw_text
        return ret

    def _get_thumbnails(self, el):
        t = el.xpath("//div[@class='product-details__thumbnail']//img/@src")
        return t if t else None

    def _get_hero_image(self, el):
        h = el.xpath(
            "//div[@class='product-details__photo']//div[@class='photo-img active']/img/@src")
        return self._ret(h)

    def _set_swatch(self, c, ret, xs):
        d = {}
        color = c.xpath(".//span[@class='name']/text()")
        d['color'] = self._ret(color)
        d['swatch_name'] = 'color'
        d['hero_image'] = self._get_hero_image(xs)
        d['thumb_img'] = self._get_thumbnails(xs)
        d['thumb'] = 1 if d['thumb_img'] else 0
        ret.append(d)

    def _swatches(self):
        ret = []
        colors = self.tree_html.xpath(
            "//div[@class='selector-wrapper']//div[contains(@class,'color')]//div[@class='selector-option']/div")

        for c in colors:
            a = c.xpath(".//a/@href")
            html = pphtml(c)
            if a == ['#'] or 'selected' in html:
                if 'disable' not in html:
                    self._set_swatch(c, ret, self.tree_html)
            else:
                content = self.load_page_from_url_with_number_of_retries(
                    urljoin(self.BASE_URL, a[0])
                )
                color_id = c.xpath(".//*/@data-link_position")
                color_id = color_id[0] if color_id else None

                xs = etree.HTML(content)
                c = xs.xpath("//div[@data-current-selected]")[0]
                self._set_swatch(c, ret, xs)
        return ret

    def _thumbnail(self):
        return self._get_thumbnails()

    def _features(self):
        pass

    def _variants(self):
        ret = []
        colors = self.tree_html.xpath(
            "//div[@class='selector-wrapper']//div[contains(@class,'color')]//div[@class='selector-option']/div")
        for c in colors:
            d = {}
            a = c.xpath(".//a/@href")
            html = pphtml(c)
            if 'option-value selected ' in html:
                d['in_stock'] = True
                d['']

        return ret

    # page_attributes
    def _image_urls(self):
        urls = self.tree_html.xpath(
            "//img[@class='product-details__img']/@src")
        max_size = '$product-details-zoomed-png$'
        image_urls = map(
            lambda x:
                re.sub('\$.*\$', max_size, 'http:' +
                       x) if 'http' not in x else '',
                urls)
        return image_urls

    def _image_count(self):
        return len(self._image_urls())

    def _no_image_available(self):
        if len(self._image_urls()) == 0:
            return 1
        return 0

    def _pdf_count(self):
        return len(self._pdf_urls())

    def _pdf_urls(self):
        pdfs = list(
            set(filter(lambda x: '.pdf' in x, self.tree_html.xpath("//a/@href"))))
        return pdfs if pdfs else None

    def _wc_pdf(self):
        return 1 if self._pdf_count() != 0 else 0

    def _htags(self):
        h1 = self.tree_html.xpath("//h1/text()")
        h2 = self.tree_html.xpath("//h2/text()")
        return {'h1': h1, 'h2': h2}

    def _meta_description(self):
        return 1 if self._meta_description_count() else 0

    def _meta_description_count(self):
        description = self.tree_html.xpath(
            "//meta[@name='description']/@content")
        return len(description[0]) if description else None

    def _canonical_link(self):
        return self._ret(self.tree_html.xpath("//link[@rel='canonical']/@href"))

    def _manufacturer(self):
        return "Samsung"

    # reviews
    def _review_count(self):
        self._reviews()
        return self.review_json['jsonData']['attributes']['numReviews']

    def _average_review(self):
        self._reviews()
        average_review = round(float(self.review_json["jsonData"][
                               "attributes"]["avgRating"]), 1)

        if str(average_review).split('.')[1] == '0':
            return int(average_review)
        else:
            return float(average_review)

    def _max_review(self):
        self._reviews()
        if self._review_count() == 0:
            return None

        for i, review in enumerate(self.review_list):
            if review[i] > 0:
                return 5 - i

    def _min_review(self):
        self._reviews()
        if self._review_count() == 0:
            return None

        for i, review in enumerate(reversed(self.review_list)):
            if review[i] > 0:
                return i + 1

    def _reviews(self):
        if hasattr(self, 'reviews_called'):
            return self.review_list

        self.reviews_called = True
        contents = self.load_page_from_url_with_number_of_retries(
            self.BASE_URL_REVIEWSREQ.format(self._product_id().replace("/", "_")))

        try:
            start_index = contents.find(
                "webAnalyticsConfig:") + len("webAnalyticsConfig:")
            end_index = contents.find(
                "widgetInitializers:initializers,", start_index)

            self.review_json = contents[start_index:end_index - 2]
            self.review_json = json.loads(self.review_json)
        except:
            self.review_json = None

        review_html = html.fromstring(re.search(
            '"BVRRSecondaryRatingSummarySourceID":" (.+?)"},\ninitializers={', contents).group(1))
        reviews_by_mark = review_html.xpath(
            "//*[contains(@class, 'BVRRHistAbsLabel')]/text()")
        reviews_by_mark = reviews_by_mark[:5]
        review_list = [[5 - i, int(re.findall('\d+', mark)[0])]
                       for i, mark in enumerate(reviews_by_mark)]
        if review_list:
            self.review_list = review_list
            return review_list
        else:
            return None
    # sellers

    def _price(self):
        price = re.findall("product_price.*?\"(.*)\"", self.page_raw_text)
        return "$" + price[0] if price else None

    def _price_amount(self):
        price = self._price()
        return float(price.replace("$", '')) if price else None

    def _price_currency(self):
        return "USD"

    def site_online_in_stock(self):
        stock_status = re.findall(
            "stock_status.*?[\"\'](.*)[\"\']", self.page_raw_text)
        ss = stock_status[0] if stock_status else None
        if ss == 'B' or ss == 'Y':
            return 1
        return 0

    def _in_stores(self):
        if hasattr(self, 'in_stores_flag'):
            return self.in_stores_flag
        self.in_stores_flag = 1
        stock_status = re.findall(
            "stock_status.*?[\"\'](.*)[\"\']", self.page_raw_text)
        if stock_status:
            ss = stock_status[0]
            if ss == 'in stock':
                self._in_stores_flag = 1
                return 1
            elif ss == 'N':
                self.set_option_n()
            elif ss == 'B' or ss == 'Y':
                return 1
            else:
                self.in_stores_flag = 0
                return 0
        else:
            self.in_stores_flag = 0
            return 0

    def set_option_n(self):
        url_id = 'http://embedded.pricespider.com/WidgetScript.psjs?d=true&wc={}'\
            .format(self.PRICESPIDER_WC)
        content_impression_id = self.load_page_from_url_with_number_of_retries(
            url_id)

        impression_id = re.findall(
            "document._ps_ImpressionId=\'(.*)\'", content_impression_id)
        impression_id = impression_id[0] if impression_id else None

        url = 'http://embedded.pricespider.com/EmbeddedScriptRequestHandler.psss?wc='\
            '%s&cmd=configuration&impressionId=%s&skus=US_%s&redirectRefSeed=true' % (
                self.PRICESPIDER_WC,
                impression_id,
                urllib.quote_plus(self._product_id()))
        content = self.load_page_from_url_with_number_of_retries(url)
        try:
            self.sellers_json = json.loads(re.findall(
                "\nSellers:(.*)\}\;", content, re.S)[0])
            self.marketplace = True
        except:
            self.marketplace = False
            self.in_stores_flag = 0
            self.sellers_json = None

    def _marketplace(self):
        self._in_stores()
        return 1 if self.marketplace else 0

    def _marketplace_sellers(self):
        self._in_stores()
        if not self.marketplace:
            return None
        ret = []
        for seller in self.sellers_json:
            ret.append(seller['sellerName'])
        return ret if ret else None

    def _bullet_feature_X(i, self):
        bullets = self.tree_html.xpath(self.bullet_xpath)
        if len(bullets) > i - 1:
            b = bullets[i - 1]
            return self.clean_bullet_html(b)
        return None

    def _categories(self):
        p_c = re.findall("product_category.*?\"(.*)\"", self.page_raw_text)
        p_sc = re.findall("product_subcategory.*?\"(.*)\"", self.page_raw_text)
        p_c.extend(p_sc)
        return p_c
>>>>>>> e3921632d0d8ef473cbcbe019725692ed1c2293c

    def _category_name(self):
        return self._categories()[-1]

<<<<<<< HEAD
    def _brand(self):
        brand = "samsung"
        return brand

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
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "keywords" : _keywords, \
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


         # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \

        "loaded_in_seconds": None \
        }


    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
    }

=======
    def _specs(self):
        ret = {}
        specs = self.tree_html.xpath(
            "//div[@class='container-wrapper spec-details']")
        specs = specs[0] if specs else None
        k = specs.xpath(".//span[@class='specs-item-name']/text()")
        v = specs.xpath(
            ".//p[contains(@class,'sub-specs__item__value')]/text()")
        if len(k) == len(v):
            for i, j in zip(k, v):
                ret[i] = j
        return ret if ret else None

    def _full_specs(self):
        ret = {}
        specs_category = self.tree_html.xpath("//figcaption[@data-link_cat='tooltip']")
        for s in specs_category:
            text = s.xpath("./span/text()")
            text = text[0] if text else None
            ret[text] = s.xpath(".//parent::div/following-sibling::div//span[@class='specs-item-name']/text()")
        return ret if ret else None
    # HELPER function
    def clean_bullet_html(self, el):
        l = el.xpath(".//text()")
        l = " ".join(l)
        l = " ".join(l.split())
        return l

    ##########################################
    # RETURN TYPES
    ##########################################
    DATA_TYPES = { \
        # CONTAINER: NONE
        "url": _url,
        "product_id": _product_id,

        # CONTAINER: PRODUCT_INFO
        "product_name": _product_name,
        "product_title": _product_title,
        "model": _model,
        "description": _description,
        "shipping": _shipping,
        "title_seo": _title_seo,
        "features": _features,
        "bullet_feature_1": partial(_bullet_feature_X, 1),
        "bullet_feature_2": partial(_bullet_feature_X, 2),
        "bullet_feature_3": partial(_bullet_feature_X, 3),
        "bullet_feature_4": partial(_bullet_feature_X, 4),
        "swatches": _swatches,
        "specs": _specs,
        "full_specs": _full_specs,

        # CONTAINER: PAGE Attributes
        "image_urls": _image_urls,
        "image_count": _image_count,
        "no_image_available": _no_image_available,
        "pdf_count": _pdf_count,
        "pdf_urls": _pdf_urls,
        "wc_pdf": _wc_pdf,
        "htags": _htags,
        "meta_description_count": _meta_description_count,
        "canonical_link": _canonical_link,
        "manufacturer": _manufacturer,
        "meta_description": _meta_description,

        # CONTAINER: reviews
        "reviews": _reviews,
        "review_count": _review_count,
        "average_review": _average_review,
        "max_review": _max_review,
        "min_review": _min_review,

        # CONTAINER:sellers
        "price": _price,
        "price_amount": _price_amount,
        "price_currency": _price_currency,
        "in_stores": _in_stores,
        "marketplace": _marketplace,
        "marketplace_sellers": _marketplace_sellers,

        # CONTAINER: classification
        "categories": _categories,
        "category_name": _category_name,
        "brand": lambda x: "Samsung"
    }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = {
    }
>>>>>>> e3921632d0d8ef473cbcbe019725692ed1c2293c
