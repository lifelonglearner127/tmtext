#!/usr/bin/python
#  -*- coding: utf-8 -*-

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


class AutozoneScraper(Scraper):

    ##########################################
    # PREP
    #########################################

    INVALID_URL_MESSAGE = (
        "Expected URL format is (http|https)://www.autozone.com/us/.*")
    BASE_URL = "http://www.autozone.com/"
    BASE_URL_REVIEWSREQ = 'https://pluck.autozone.com/ver1.0/sys/jsonp?' \
                          'widget_path=pluck/reviews/rollup&' \
                          'plckReviewOnKey={product_id}&' \
                          'plckReviewOnKeyType=article&' \
                          'plckReviewShowAttributes=true&' \
                          'plckDiscoveryCategories=&' \
                          'plckArticleUrl={product_url}&' \
                          'clientUrl={product_url}&'

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        self.max_review = None
        self.min_review = None
        self.average_review = None
        self.review_count = None
        self.reviews = None
        # whether product has any webcollage media
        self.wc_360 = 0
        self.wc_emc = 0
        self.wc_video = 0
        self.wc_pdf = 0
        self.wc_prodtour = 0

        self.features = None
        self.ingredients = None
        self.images = None
        self.videos = None

    def check_url_format(self):
        m = re.match(r"^(https|http)://www\.autozone\.com\/.*",
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

    def _url(self):
        return self.product_page_url

    # product_info

    def _product_id(self):
        product_id = self.tree_html.xpath("//div[@id='product-data']//div[@id='SkuId']//text()")
        if len(product_id) > 0:
            product_id = product_id[0].strip()
        return product_id

    def _product_name(self):
        el = self.tree_html.xpath("//h3[@property='name']//text()")
        if len(el) > 0:
            el = el[0]
            return el.strip()
        return None

    def _product_title(self):
        el = self.tree_html.xpath("//title")
        return self._ret(el)

    def _title_seo(self):
        return self._ret(self.tree_html.xpath("//meta[@name='title']/@content"))

    def _model(self):
        return None

    def _description(self):
        el = self.tree_html.xpath("//div[@id='features']")
        if len(el) > 0:
            description = self._clean_text(html.tostring(el[0]))
            return description
        return None

    def _shipping(self):
        ret = 'Ships in' in self.page_raw_text
        return ret

    def _features(self):
        trs = self.tree_html.xpath("//table[@id='prodspecs']//tr")
        features = []
        for tr in trs:
            txt = tr.xpath(".//text()")
            txt = " ".join([r.strip() for r in txt if len(r.strip())>0])
            features.append(txt)
        return "\n".join(features)

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
        image_urls = self.tree_html.xpath(
            "//div[contains(@class,'productThumbsblock')]//li//a//img/@src")
        if len(image_urls) == 0:
            image_urls = self.tree_html.xpath("//img[@id='mainimage']/@src")
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
        return "Autozone"

    # reviews
    def _review_count(self):
        self._reviews()
        cnt = 0
        for i, review in self.review_list:
            cnt += review
        return cnt

    def _average_review(self):
        self._reviews()
        sum = 0
        cnt = 0
        for i, review in self.review_list:
            sum += review*i
            cnt += review
        return float(sum)/cnt

    def _max_review(self):
        self._reviews()
        if self._review_count() == 0:
            return None

        for i, review in self.review_list:
            if review > 0:
                return i

    def _min_review(self):
        self._reviews()
        if self._review_count() == 0:
            return None

        for i, review in reversed(self.review_list):
            if review > 0:
                return i

    def _reviews(self):
        if hasattr(self, 'reviews_called'):
            return self.review_list

        self.reviews_called = True
        contents = self.load_page_from_url_with_number_of_retries(
            self.BASE_URL_REVIEWSREQ.format(
                product_id=self._product_id(),
                product_url=self.product_page_url)
        )

        review_html = html.fromstring(
            re.search('(<div id="pluck_reviews_rollup.+?\'\))', contents).group(1)
        )

        arr = review_html.xpath(
            "//div[contains(@class,'pluck-dialog-middle')]"
            "//span[contains(@class,'pluck-review-full-attributes-name-post')]/text()"
        )
        review_list = []
        if len(arr) >= 5:
            review_list = [[5 - i, int(re.findall('\d+', mark)[0])]
                           for i, mark in enumerate(arr)]
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

    def _categories(self):
        arr = self.tree_html.xpath("//ul[contains(@class,'breadcrumb')]//li//a//text()")
        line_txts = [r.strip() for r in arr if len(r.strip())>0]
        if len(line_txts) < 1:
            return None
        return line_txts

    def _category_name(self):
        return self._categories()[-1]

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
        "brand": lambda x: "Autozone"
    }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = {
    }