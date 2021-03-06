# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals

import json
import pprint
import re
import urlparse
import hashlib
import random
import re
from datetime import datetime
import lxml.html
import urllib
import time
import socket

import os
import logging
logger = logging.getLogger(__name__)
import boto
from boto.s3.key import Key
from scrapy.conf import settings
from scrapy import Selector
from scrapy.http import Request, FormRequest
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.guess_brand import guess_brand_from_first_words
from product_ranking.items import (SiteProductItem, RelatedProduct,
                                   BuyerReviews, Price)
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set, cond_set_value, FLOATING_POINT_RGEX
from product_ranking.validation import BaseValidator
from product_ranking.validators.walmart_validator import WalmartValidatorSettings
from spiders_shared_code.walmart_variants import WalmartVariants
from spiders_shared_code.walmart_categories import WalmartCategoryParser
#from spiders_shared_code.walmart_extra_data import WalmartExtraData

from selenium.webdriver.common.by import By
from selenium import webdriver
from pyvirtualdisplay import Display


is_empty = lambda x, y="": x[0] if x else y


def get_string_from_html(xp, link):
    loc = is_empty(link.xpath(xp).extract())
    return Selector(text=loc).xpath('string()').extract()


def get_walmart_id_from_url(url):
    """ Returns item ID from the given URL """
    # possible variants:
    # http://walmart.com/ip/37002591?blabla=1
    # http://www.walmart.com/ip/Pampers-Swaddlers-Disposable-Diapers-Economy-Pack-Plus-Choose-your-Size/27280840
    if '?' in url:
        url = url.rsplit('?', 1)[0]
    if '/ip/' in url:
        url = url.split('/ip/')[1]
    if re.match(r'^[0-9]{3,20}$', url):
        return url
    g = re.search(r'\/([0-9]{3,20})', url)
    if not g:
        return
    return g.group(1)


def _get_walmart_original_redirect_item_id(response):
    """ Detects if the item was redirected, see BZ #2126
    :return: None if no redirect; item ID otherwise
    """
    redirects = response.request.meta.get('redirect_urls')
    if not redirects:
        return
    original_url = redirects[0]
    return get_walmart_id_from_url(original_url)


def _get_walmart_api_key():
    # TODO: implement loading from a config file!
    keys = ['yahac2smt4p4fjhgpz394kbp', 'upg664pajfcj7scau9ajq5zq',
            '63y2yz3qnes9vwn97tjpshtb']
    key = random.choice(keys)
    return key


class WalmartProductsSpider(BaseValidator, BaseProductsSpider):
    """Implements a spider for Walmart.com.

    This spider has 2 very peculiar things.
    First, it receives 2 types of pages so it need 2 rules for every action.
    Second, the site sometimes redirects a request to the same URL so, by
    default, Scrapy would discard it. Thus we override everything to handle
    redirects.

    FIXME: Currently we redirect infinitely, which could be a problem.
    """
    name = 'walmart_products'
    allowed_domains = ["walmart.com", "msn.com", 'api.walmartlabs.com']

    default_hhl = [404, 500, 502, 520]

    SEARCH_URL = "https://www.walmart.com/search/?query={search_term}"

    LOCATION_URL = "https://www.walmart.com/location"
    LOCATION_PROD_URL = "https://www.walmart.com/product/dynamic/{product_id}?" \
                        "location={zip_code}&selected=true"

    QA_URL = "https://www.walmart.com/reviews/api/questions" \
             "/{product_id}?sort=mostRecentQuestions&pageNumber={page}"
    ALL_QA_URL = 'http://www.walmart.com/reviews/api/questions/%s?pageNumber=%i'

    REVIEW_URL = 'https://walmart.ugc.bazaarvoice.com/1336/{product_id}/' \
                 'reviews.djs?format=embeddedhtml&sort=submissionTime'

    REVIEW_DATE_URL = 'https://www.walmart.com/reviews/api/product/{product_id}?' \
                      'limit=3&sort=submission-desc&filters=&showProduct=false'

    QA_LIMIT = 0xffffffff

    _SEARCH_SORT = {
        'best_match': 0,
        'high_price': 'price_high',
        'low_price': 'price_low',
        'best_sellers': 'best_seller',
        'newest': 'new',
        'rating': 'rating_high',
    }

    settings = WalmartValidatorSettings

    sponsored_links = []

    _JS_DATA_RE = re.compile(
        r'define\(\s*"product/data\"\s*,\s*(\{.+?\})\s*\)\s*;', re.DOTALL)

    user_agent = 'default'

    def __init__(self, search_sort='best_match', zip_code='94117',
                 *args, **kwargs):

        global SiteProductItem
        if zip_code:
            self.zip_code = zip_code
        if search_sort != 'best_match':
            self.SEARCH_URL += "&sort={search_sort}"
        if search_sort == 'best_sellers':
            self.SEARCH_URL += '&soft_sort=false&cat_id=0'
        # avoid tons of 'items' in logs
        self.search_sort = search_sort
        SiteProductItem.__repr__ = lambda _: '[product item]'
        self.use_data_from_redirect_url = kwargs.get('use_data_from_redirect_url', False)
        self.username = kwargs.get('username', None)
        super(WalmartProductsSpider, self).__init__(
            site_name=self.allowed_domains[0],
            url_formatter=FormatterWithDefaults(
                search_sort=self._SEARCH_SORT[search_sort]
            ),
            *args, **kwargs)

        settings.overrides['RETRY_HTTP_CODES'] = [500, 502, 503, 504, 400, 403, 404, 408, 429]
        settings.overrides['DOWNLOAD_DELAY'] = self._get_download_delay()
        settings.overrides['CONCURRENT_REQUESTS'] = 1

        local_filename = "/tmp/_proxy_providers_settings.cfg"

        if os.path.isfile(local_filename) or random.randint(0, 5) == 0:
            proxy_config = self._parse_proxy_config_file(local_filename)
        else:
            proxy_config = self._download_and_parse_proxy_config_file(local_filename)
        if not proxy_config:
            proxy_config = {
                            "crawlera": 100,
                            "luminati": 0,
                            "proxyrain": 0,
                            "shaderio": 0,
                            }

        self.force_proxy_provider = kwargs.get('force_proxy_provider', None)
        if self.force_proxy_provider:
            logger.warning("*** Proxy provider forced via command line: {} ***".format(
                self.force_proxy_provider))
            chosen_proxy_provider = self.force_proxy_provider
        else:
            chosen_proxy_provider = self._weighted_choice(proxy_config)
            logger.warning("*** Proxy provider will be chosen randomly from: {} ***".format(proxy_config))
            logger.warning("*** Chosen : {} ***".format(chosen_proxy_provider))

        middlewares = settings.get('DOWNLOADER_MIDDLEWARES')

        # Disabled, in this moment we use EU Crawlera key, so there is no random redirections
        # middlewares['product_ranking.custom_middlewares.WalmartRetryMiddleware'] = 800
        # middlewares['scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware'] = None

        middlewares['product_ranking.randomproxy.RandomProxy'] = None

        if chosen_proxy_provider == "crawlera":
            logger.warning('*** Using Crawlera ***')
            settings.overrides['CRAWLERA_URL'] = 'http://content.crawlera.com:8010'
            settings.overrides['CRAWLERA_APIKEY'] = "4810848337264489a1d2f2230da5c981"
            settings.overrides['CRAWLERA_ENABLED'] = True
            settings.overrides['CRAWLERA_PRESERVE_DELAY'] = True
        elif chosen_proxy_provider == "luminati":
            logger.warning('*** Using Luminati ***')
            middlewares['product_ranking.custom_middlewares.LuminatiProxy'] = 750
            middlewares['product_ranking.scrapy_fake_useragent.middleware.RandomUserAgent'] = 400
            middlewares['scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware'] = None
        elif chosen_proxy_provider == "proxyrain":
            logger.warning('*** Using Proxyrain ***')
            middlewares['product_ranking.custom_middlewares.ProxyrainProxy'] = 750
            middlewares['product_ranking.scrapy_fake_useragent.middleware.RandomUserAgent'] = 400
            middlewares['scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware'] = None
        elif chosen_proxy_provider == "shaderio":
            logger.warning('*** Using Shader.io ***')
            middlewares['product_ranking.custom_middlewares.ShaderioProxy'] = 750
            middlewares['product_ranking.scrapy_fake_useragent.middleware.RandomUserAgent'] = 400
            middlewares['scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware'] = None

        settings.overrides['DOWNLOADER_MIDDLEWARES'] = middlewares

        self.scrape_questions = kwargs.get('scrape_questions', None)
        if self.scrape_questions not in ('1', 1, True, 'true', 'True'):
            self.scrape_questions = False
        self.cookies = {}
        self.cookies[
            'prefper'] = 'PREFSTORE~12648~2PREFCITY~1San%20Leandro~2PREFFULLSTREET~11919%20Davis%20St~2PREFSTATE~1CA~2PREFZIP~194117'
        self.cookies['PSID'] = '2648'
        self.cookies['NSID'] = '2648'

        self.visited_links = {}

    def _weighted_choice(self, choices_dict):
        try:
            choices = [(key, value) for (key, value) in choices_dict.iteritems()]
            # Accept dict, converts to list
            # of iterables in following format
            # [("choice1", 0.6), ("choice2", 0.2), ("choice3", 0.3)]
            # Returns chosen variant
            total = sum(w for c, w in choices)
            r = random.uniform(0, total)
            upto = 0
            for c, w in choices:
                if upto + w >= r:
                    return c
                upto += w
        except Exception as e:
            return "crawlera"

    def _get_download_delay(self):
        amazon_bucket_name = "sc-settings"
        config_filename = "walmart_download_delay.cfg"
        default_download_delay = 1.0
        try:
            S3_CONN = boto.connect_s3(is_secure=False)
            S3_BUCKET = S3_CONN.get_bucket(amazon_bucket_name, validate=False)
            k = Key(S3_BUCKET)
            k.key = config_filename
            value = k.get_contents_as_string()
            logging.info('Retrieved download_delay={}'.format(value))
            return float(value)
        except Exception as e:
            logging.error(e)
            return default_download_delay

    @staticmethod
    def _download_and_parse_proxy_config_file(local_filename):
        amazon_bucket_name = "sc-settings"
        bucket_config_filename = "walmart_proxy_config.cfg"
        # local_filename = "/tmp/_proxy_providers_settings.cfg"
        proxy_config = None
        try:
            S3_CONN = boto.connect_s3(is_secure=False)
            S3_BUCKET = S3_CONN.get_bucket(amazon_bucket_name, validate=False)
            k = Key(S3_BUCKET)
            k.key = bucket_config_filename
            value = k.get_contents_as_string()
            proxy_config = json.loads(value)
            # Save config to file
            with open(local_filename, "w") as conf_file:
                conf_file.write(value)
        except Exception as e:
            logger.error(e)
        else:
            logger.info('Retrieved proxy config from bucket: {}'.format(value))
            logger.info('Saved to file: {}'.format(local_filename))
        return proxy_config

    @staticmethod
    def _parse_proxy_config_file(local_filename):
        proxy_config = None
        try:
            with open(local_filename) as conf_file:
                proxy_config = json.load(conf_file)
        except Exception as e:
            logger.error(e)
        else:
            logger.info('Retrieved proxy config from file: {}'.format(proxy_config))
        return proxy_config

    @staticmethod
    def _replace_http_with_https(url):
        return re.sub('^http:\/\/', 'https://', url)

    def start_requests(self):
        # uncomment below to enable sponsored links (but this may cause walmart.com errors!)
        """
        for st in self.searchterms:
            url = "http://www.walmart.com/midas/srv/ypn?" \
                "query=%s&context=Home" \
                "&clientId=walmart_us_desktop_backfill_search" \
                "&channel=ch_8,backfill" % (st,)
            yield Request(
                url=url,
                callback=self.get_sponsored_links,
                dont_filter=True,
                meta={"handle_httpstatus_list": [404, 502]},
            )
        """

        if self.product_url:
            # remove odd spaces for single product urls
            if type(self.product_url) is str or type(self.product_url) is unicode:
                self.product_url = self.product_url.strip()
                self.product_url = self._replace_http_with_https(self.product_url)
            prod = SiteProductItem()
            prod['is_single_result'] = True
            yield Request(self.product_url,
                          self._parse_single_product,
                          meta={'product': prod, 'handle_httpstatus_list': [404, 502, 520]},
                          dont_filter=True,
                          cookies=self.cookies)

        else:
            # reduce quantity to 100 because we're having issues with Walmart now
            #  (it bans us so we're using Crawlera)
            # TODO COMMENT THOSE, IF MORE THAN 100 products per job needed
            if not self.quantity or not isinstance(self.quantity, int):
                self.quantity = 100
            if self.quantity and isinstance(self.quantity, int):
                if self.quantity > 100:
                    self.quantity = 100

            for st in self.searchterms:
                self.visited_links[st] = []
                yield Request(self.SEARCH_URL.format(search_term=urllib.quote_plus(st.encode('utf-8')),
                                                     search_sort=self._SEARCH_SORT[self.search_sort]),
                              #self._parse_single_product,
                              meta={'handle_httpstatus_list': [404, 502, 520],
                                    'remaining': self.quantity, 'search_term': st},
                              dont_filter=True,
                              cookies=self.cookies)

    def get_sponsored_links(self, response):
        self.reql = []
        self.sponsored_links = []
        for link in response.xpath(
            '//div[contains(@class, "yahoo_sponsored_link")]'
                '/div[contains(@class, "yahoo_sponsored_link")]'):
            ad_title = is_empty(
                get_string_from_html('div/span[@class="title"]/a', link))
            ad_text = is_empty(
                get_string_from_html('div/span[@class="desc"]/a', link))
            visible_url = is_empty(
                get_string_from_html('div/span/span[@class="host"]/a', link))
            actual_url = is_empty(
                link.xpath('div/span[@class="title"]/a/@href').extract())
            sld = {"ad_title": ad_title,
                   "ad_text": ad_text,
                   "visible_url": visible_url,
                   "actual_url": actual_url,
                   }
            new_meta = response.meta.copy()
            new_meta["sld"] = sld
            new_meta['handle_httpstatus_list'] = [400, 403, 404, 405]
            self.reql.append(Request(
                actual_url,
                callback=self.parse_sponsored_links,
                errback=self.parse_sponsored_links,
                meta=new_meta,
                dont_filter=True))
        if self.reql:
            req1 = self.reql.pop(0)
            new_meta = req1.meta
            new_meta['reql'] = self.reql
            self.sld = new_meta["sld"]
            return req1.replace(meta=new_meta)
        return self.update_native_start_requests()

    def parse_sponsored_links(self, response):
        self.temp_spons_link = None
        if hasattr(response, "meta"):
            if response.status == 200:
                self.sld['actual_url'] = response.url
                self.sponsored_links.append(self.sld)

            if self.reql:
                req1 = self.reql.pop(0)
                new_meta = req1.meta
                new_meta['reql'] = self.reql
                self.temp_spons_link = req1.url
                self.sld = new_meta["sld"]
                return req1.replace(meta=new_meta)
        else:
            self.sld['actual_url'] = self.temp_spons_link
            self.sponsored_links.append(self.sld)
            if not self.reql:
                del self.temp_spons_link, self.sld, self.reql
                return super(WalmartProductsSpider, self).start_requests()
            req1 = self.reql.pop(0)
            new_meta = req1.meta
            new_meta['reql'] = self.reql
            self.temp_spons_link = req1.url
            self.sld = new_meta["sld"]
            return req1.replace(meta=new_meta)
        del self.temp_spons_link, self.sld, self.reql
        return self.update_native_start_requests()

    def update_native_start_requests(self):
        reqs = []
        for req in super(WalmartProductsSpider, self).start_requests():
            new_meta = req.meta.copy()
            new_meta["handle_httpstatus_list"] = self.default_hhl
            reqs.append(req.replace(meta=new_meta))
        return reqs

    def parse_product(self, response):
        product = response.meta.get("product")

        if self._parse_temporary_unavailable(response):
            product['temporary_unavailable'] = True
            return product
        else:
            product['temporary_unavailable'] = False

        product['_subitem'] = True

        if "we can't find the product you are looking for" \
                in response.body_as_unicode().lower():
            product['not_found'] = True
            return product

        if response.status in self.default_hhl:
            if response.status == 502:  # no longer available?
                product.update({"no_longer_available": True})
            product.update({"locale":'en-US'})
            return product
        if self._search_page_error(response):
            self.log(
                "Got 404 when coming from %r." % response.request.url, ERROR)
            return

        wv = WalmartVariants()
        wv.setupSC(response)
        product['variants'] = wv._variants()

        not_available = self.parse_available(response)
        cond_set_value(product, 'no_longer_available', not_available)

        if self.sponsored_links:
            product["sponsored_links"] = self.sponsored_links

        self._populate_from_js_alternative(response, product)
        self._populate_from_js(response, product)
        self._populate_from_html(response, product)

        # TODO implement for dropdowns as well
        if self.product_url and response.xpath('.//*[@class="variant-swatch"]'):
            self.log('Using selenium to get INLA status for swatch product', INFO)
            INLA, err = self.parse_available_selenium(self.product_url, product.get("variants",[]))
            if not err:
                product['no_longer_available'] = INLA
            else:
                self.log('Second try', INFO)
                INLA, err = self.parse_available_selenium(self.product_url, product.get("variants", []))
                if not err:
                    product['no_longer_available'] = INLA
                else:
                    self.log('Failed second try, giving up', INFO)

        buyer_reviews = self._build_buyer_reviews(response)
        if buyer_reviews:
            cond_set_value(product, 'buyer_reviews', buyer_reviews)
        else:
            cond_set_value(product, 'buyer_reviews', 0)
        cond_set_value(product, 'locale', 'en-US')  # Default locale.
        if 'brand' not in product:
            cond_set_value(product, 'brand', None)

        # parse category and department
        wcp = WalmartCategoryParser()
        wcp.setupSC(response)
        try:
            categories = wcp._categories_hierarchy()
            cond_set_value(product, 'categories', categories)
        except Exception as e:
            self.log('Category not parsed: '+str(e), WARNING)
        try:
            department = wcp._category()
            cond_set_value(product, 'department', department)
        except Exception as e:
            self.log('No department to parse: '+str(e), WARNING)
        categories_full_info = wcp.full_categories_with_links()
        cond_set_value(product, 'categories_full_info', categories_full_info)

        model = is_empty(
            response.xpath('//tr[@class="js-product-specs-row"]/'
                           'td[contains(text(), "Model No")]/'
                           'following::td[1]/text() |'
                           '//table[@class="SpecTable"]/tr/'
                           'td[contains(text(), "Walmart No")]'
                           '/following::td[1]/text()').extract())
        if model:
            product['model'] = model.strip()
        else:
            cond_set(product,
                     'model',
                     response.xpath(
                         '//meta[@itemprop="model"]/@content'
                     ).extract())
        if response.xpath('//*[contains(@class, "submap-flyout")]'
                          '//*[contains(@class, "submap-price")]'
                          '[contains(text(), "See details in cart")]').extract():
            product['price_details_in_cart'] = True

        flag = 'not available'
        if response.xpath('//meta[@name="Keywords"]').extract():
            if not flag in response.body_as_unicode():
                cond_set_value(product,
                               'shipping',
                               False)
        else:
            shipping = response.xpath(
                '//div[@class="product-no-fulfillment Grid-col '
                'u-size-6-12-l active"][1]/span/text()'
                '[contains(.,"not available")] |'
                '//span[@class="js-shipping-delivery-date-msg '
                'delivery-date-msg"]/text()[contains(., "Not available")]'
            ).extract()

            if not 'shipping' in product:
                if len(shipping) > 0:
                    cond_set_value(product,
                                   'shipping',
                                   False)
                else:
                    cond_set_value(product,
                                   'shipping',
                                   True)

        sku = response.xpath('//*[@itemprop="sku"]/text()').extract()
        if sku:
            product['sku'] = sku[0]

        id = re.findall('\/(\d+)', response.url)
        response.meta['product_id'] = id[-1] if id else None
        # if id:
        #    url = 'http://www.walmart.com/reviews/api/questions/{0}?' \
        #          'sort=mostRecentQuestions&pageNumber=1'.format(id[0])
        #    meta = {
        #        "product": product,
        #        "relreql": response.meta["relreql"],
        #        "response": response
        #    }

        #    return Request(url=url, meta=meta, callback=self.get_questions)

        seller_ranking = self._scrape_seller_ranking(response)
        # if seller_ranking:
            # product['seller_ranking'] = seller_ranking
        # seller_ranking = seller_ranking[0].get('ranking') if seller_ranking else None
        cond_set_value(product, 'bestseller_rank', seller_ranking)

        if 'is_in_store_only' not in product:
            if re.search(
                    "only available .{0,20} Walmart store",
                    response.body_as_unicode()):
                product['is_in_store_only'] = True

        special_pricing = response.xpath(
            '//div[contains(@class, "price-flags")]//text()').extract()
        special_pricing = [
            r.strip() for r in special_pricing if len(r.strip())>0]
        if 'Rollback' in special_pricing:
            product['special_pricing'] = True
        else:
            product['special_pricing'] = False

        if not product.get('price', None):
            prod_data = re.search('"product/data",(.+?);', response.body)
            if prod_data:
                prod_data = prod_data.group(1)
                if prod_data.endswith(')'):
                    prod_data = prod_data[0:-1]
                prod_data = json.loads(prod_data.strip())
                display_price = prod_data.get('buyingOptions',{}).get('price', {}).get('displayPrice', '')

                if not display_price:
                    display_price = prod_data.get('buyingOptions',{}).get('minPrice', {}).get('displayPrice', '')

                display_price = re.search('[\d\.]+', display_price)
                if display_price:
                    display_price = display_price.group()
                    price_amount = float(display_price)
                    product['price'] = Price(price=price_amount, priceCurrency="USD")

        # randomly walmart respond with a different JS data, so we should make this extra request
        if not product.get('price'):
            cond_set_value(product, 'url', response.url)
            return self._gen_location_request(response)

        _na_text = response.xpath(
            '//*[contains(@class, "NotAvailable")]'
            '[contains(@style, "block")]/text()'
        ).extract()
        if not _na_text:
            _na_text = response.css('#WMNotAvailableLine ::text').extract()
        if _na_text:
            if 'not available' in _na_text[0].lower():
                product['is_out_of_stock'] = True

        _meta = response.meta
        _meta['handle_httpstatus_list'] = [404, 502, 520]

        m = re.search(
            self._JS_DATA_RE, response.body_as_unicode().encode('utf-8'))
        if m:
            text = m.group(1)
            try:
                data = json.loads(text)
                self._on_dynamic_api_response(response, data)
            except ValueError:
                pass

        if self.scrape_questions:
            return Request(  # make another call - to scrape questions/answers
                self.ALL_QA_URL % (
                    get_walmart_id_from_url(product['url']), 1),
                meta={'product': response.meta['product']},
                callback=self._parse_all_questions_and_answers
            )
        else:
            return product

    def _scrape_seller_ranking(self, response):
        # Old, more detailed bestseller ranking format
        # ranking = response.xpath('//div[@class="Grid-col item-ranks"]/ol')
        # ranking_data = []
        # for i in ranking:
        #     x = i.xpath('li//text()').extract()
        #     x = [i for i in x if i != ' ']
        #     ranking_data.append(x)
        #
        # seller_ranking = []
        # for i in ranking_data:
        #     data = {}
        #     rank = i[0].replace('#', '').replace(',', '')
        #     print rank
        #     data['ranking'] = int(rank) if rank else None
        #
        #     cat = i[2:]
        #     data['categories'] = cat
        #     seller_ranking.append(data)
        bestseller_rank = response.xpath('(//*[@class="item-rank"])[1]/span[1]/text()').extract()
        try:
            bestseller_rank = bestseller_rank[0].strip().strip('#').replace(',','') if bestseller_rank else None
            seller_ranking = int(bestseller_rank) if bestseller_rank else None
        except BaseException:
            seller_ranking = None
        if seller_ranking:
            return seller_ranking

    def parse_available(self, response):
        available = is_empty(response.xpath(
            '//div[@class="prod-no-buying-option"]/'
            'div[@class="heading-d"]/text()').extract())
        if available == 'This Item is no longer available':
            not_available = True
        else:
            not_available = False
        if response.xpath('//*[contains(@class, "invalid")'
                          ' and contains(text(), "tem not available")]'):
            not_available = True
        if response.xpath('//*[contains(@class, "invalid")'
                          ' and contains(text(), "no longer available")]'):
            not_available = True
        if response.xpath('//*[contains(@class, "NotAvailable")'
                          ' and contains(text(), "ot Available")]'):
            not_available = True
        if response.xpath('//*[contains(@class, "heading")'
                          ' and contains(text(), "nformation unavailable")]'):
            not_available = True
        if response.xpath('.//div[contains(text(), "This Item is no longer available")]'):
            not_available = True
        # commented into 13176 ticket
        # if response.xpath('.//div[contains(@class, "price-display-oos-color")]'):
        #     not_available = True
        if response.xpath('//*[contains(., "This item is no longer available")]'):
            not_available = True
        return not_available

    def _on_api_response(self, response):
        if self.use_data_from_redirect_url:
            yield self.parse_product(response.meta['original_response_'])
            return

        if hasattr(response, 'getErrorMessage'):
            if response.getErrorMessage():
                # API request failed
                with open('/tmp/walmart_api_requests_failed.log', 'a') as fh:
                    fh.write(str(datetime.utcnow())+'\n')
                _response_from_parse_single_product = getattr(
                    self, '_response_from_parse_single_product', None)
                if _response_from_parse_single_product:
                    if not 'product' in _response_from_parse_single_product.meta:
                        _response_from_parse_single_product.meta['product'] = {}
                    _response_from_parse_single_product.meta['product'][
                        '_walmart_original_oos'] = True
                    yield self.parse_product(_response_from_parse_single_product)
                    return

        # if API request succeed
        original_id = response.meta['original_id']
        current_id = response.meta['current_id']
        original_response = response.meta['original_response_']
        if not 'product' in response.meta:
            response.meta['product'] = {}
        product = response.meta['product']
        j = json.loads(response.body)
        if str(j['itemId']) != str(original_id):
            self.log('API: itemId mismatch at URL %s' % response.url,
                     level=ERROR)
        else:
            product['_walmart_original_oos'] \
                = j.get('stock', '').lower() == 'not available'
            product['_walmart_original_price'] \
                = j.get('price', j.get('salePrice'))
            product['upc'] = j.get('upc', product.get('upc', ''))  # set original item UPC
        original_response.meta['product'] = product
        yield self.parse_product(original_response)

    def _get_walmart_api_data_for_item_id(self, original_response, original_id, current_id, meta):
        api_url = 'https://api.walmartlabs.com/v1/items/%s?apiKey=%s&format=json'
        api_key = _get_walmart_api_key()
        meta['original_id'] = original_id
        meta['current_id'] = current_id
        meta['original_response_'] = original_response
        self._response_from_parse_single_product = original_response  # needed for FailedRequest
        return Request(
            url=api_url % (original_id, api_key),
            callback=self._on_api_response, meta=meta,
            errback=self._on_api_response
        )

    def _parse_single_product(self, response):
        if response.status == 404:
            if 'product' not in response.meta:
                product = SiteProductItem()
            else:
                product = response.meta['product']
            product['response_code'] = response.status
            product['not_found'] = True
            if not 'url' in product:
                product['url'] = getattr(self, 'product_url', '')
            yield product
            return

        original_parent_id = _get_walmart_original_redirect_item_id(response)
        current_id = get_walmart_id_from_url(response.url)
        if str(original_parent_id) == str(current_id):
            # there was redirect but the IDs are the same, so it's the same product
            original_parent_id = None
        # store current ID to identify it later to match the products
        if 'product' not in response.meta:
            response.meta['product'] = {}
        response.meta['product']['_walmart_original_id'] = original_parent_id
        response.meta['product']['_walmart_current_id'] = current_id
        response.meta['product']['reseller_id'] = current_id
        if original_parent_id:
            # ok we've been redirected and we get the original item ID. Now:
            # * perform API call (in method _get_walmart_api_data_from_item_id
            # * get the original ("parent") item Price and Out_of_stock (in _on_api_response)
            # * replace the existing data with the original Price and OOS in WalmartRedirectedItemFieldReplace
            yield self._get_walmart_api_data_for_item_id(
                original_response=response,
                original_id=original_parent_id, current_id=current_id,
                meta=response.meta)
        else:
            yield self.parse_product(response)

    def _search_page_error(self, response):
        path = urlparse.urlsplit(response.url)[2]
        return path == '/FileNotFound.aspx'

    def _build_buyer_reviews_old(self, response):
        product = response.meta['product']
        buyer_reviews = {}
        h = re.findall('"BVRRSecondaryRatingSummarySourceID":"(.*)",',
                           response.body)
        if len(h) > 0:
            tree = lxml.html.fromstring(h[0])
            if not tree.xpath(
                    '//span[contains(@class,"BVRRCount")]/span/text()'):
                product['buyer_reviews'] = ZERO_REVIEWS_VALUE
                return product
            num = int(is_empty(re.findall('\d+', tree.xpath(
                '//span[contains(@class,"BVRRCount")]/span/text()')[0])))

            if num == 0:
                product['buyer_reviews'] = ZERO_REVIEWS_VALUE
                return product
            buyer_reviews['num_of_reviews'] = num
            avg = float(is_empty(
                re.findall(
                    '\d+.\d+',
                    is_empty(tree.xpath('//div[contains(@class,'
                               '"BVRRRatingNormalImage")]/img/@alt'), ""))
            , 0))
            buyer_reviews['average_rating'] = avg
            stars = tree.xpath(
                '//span[contains(@class,"BVRRHistAbsLabel")]/text()')
            by_star = {1: stars[4], 2: stars[3],
                       3: stars[2], 4: stars[1],
                       5: stars[0]}
            buyer_reviews['rating_by_star'] = by_star
            product['buyer_reviews'] = BuyerReviews(**buyer_reviews)
        else:
            product['buyer_reviews'] = 0

        self._parse_last_buyer_review_date_old(self, response, product)
        return product

    def _parse_last_buyer_review_date_old(self, response, product):
        data = re.findall('var materials={(.*)}', response.body_as_unicode())
        h = json.loads(data[0])
        sel = Selector(text=h['BVRRSourceID'])
        cond_set(
            product,
            'last_buyer_review_date',
            sel.xpath(
                '//span[contains(@class, "BVRRReviewDate")]/text()'
            ).extract()
        )

    def _build_buyer_reviews(self, response):
        overall_block = response.xpath(
            '//*[contains(@class, "review-summary")]'
            '//p[contains(@class, "heading")][contains(text(), "|")]//text()'
        ).extract()
        overall_text = ' '.join(overall_block)
        if not overall_text.strip():
            return ZERO_REVIEWS_VALUE
        buyer_reviews = {}
        num_of_reviews = overall_text.split('review')[0].strip()
        if not num_of_reviews.strip():
            return ZERO_REVIEWS_VALUE
        num_of_reviews = int(num_of_reviews)
        buyer_reviews['num_of_reviews'] = num_of_reviews
        buyer_reviews['average_rating'] = float(
            overall_text.split('|')[1].split('out')[0].strip())
        buyer_reviews['rating_by_star'] = {}
        for _revs in response.css('.review-histogram .rating-filter'):
            _star = _revs.css('.meter-inline ::text').extract()[0].strip()

            try:
                _reviews = _revs.css('.rating-val ::text').extract()[0].strip()
            except:
                _reviews = 0
            _star = (_star.lower().replace('stars', '').replace('star', '')
                     .strip())
            buyer_reviews['rating_by_star'][int(_star)] = int(_reviews)
        return BuyerReviews(**buyer_reviews)

    def _populate_from_html(self, response, product):
        cond_set_value(product, 'url', response.url)
        cond_set(
            product,
            'description',
            response.css('.about-product-section, #SITCC_1column').extract(),
            conv=''.join
        )

        if product.get('description', ''):
            upc = re.findall('UPC: (\d+)', product['description'])
            cond_set(product, 'upc', upc)

        title = is_empty(response.xpath(
                "//h1[contains(@class,'product-name')]/text() |"
                "//h1[@class='productTitle']/text()"
        ).extract(), "")
        if not title.strip():
            title = is_empty(response.xpath(
                "//h1[contains(@class,'product-name')]/span/text()"
            ).extract())
        if title:
            title = Selector(text=title).xpath('string()').extract()
            title = is_empty(title, "").strip()
            cond_set_value(product, 'title', title)
        if ((isinstance(title, (str, unicode)) and not title.strip())
                or (isinstance(title, (list, tuple)) and not ''.join(title).strip())):
            title = response.css('h1[itemprop="name"] ::text').extract()
            title = ''.join(title).strip()
            if title:
                cond_set_value(product, 'title', title)
        brand = is_empty(response.xpath(
                "//div[@class='product-subhead-section']"
                "/a[@id='WMItemBrandLnk']/text()").extract())
        if not brand:
            brand = is_empty(response.xpath(
                ".//*[@id='WMItemBrandLnk']//*[@itemprop='brand']/text()").extract())
        if not brand:
            brand = guess_brand_from_first_words(product.get('title', '').replace(u'®', ''))
        elif '&amp;' in brand:
            brand = brand.replace('&amp;', "&")
        brand = brand.replace('\ufffd','')
        cond_set_value(product, 'brand', brand)

        try:
            cond_set(
                product, 'image_url',
                response.xpath('//img[contains(@class, "product-image")]/@src'),
                ""
            )
        except TypeError:
            pass
        if not product.get('image_url', None):
            product['image_url'] = is_empty(response.xpath(
                    '//meta[@property="og:image"]/@content').extract(), "")

        if not product.get("brand"):
            brand = is_empty(response.xpath(
                "//h1[contains(@class, 'product-name product-heading')]/text()"
                " | //h1[@class='productTitle']/text()"
            ).extract())
            brand = brand.replace('\ufffd', '')
            cond_set(
                product,
                'brand',
                (guess_brand_from_first_words(brand.strip()),)
            )

        if not product.get('price'):
            currency = response.css('[itemprop=priceCurrency]::attr(content)')
            price = response.css('[itemprop=price]::attr(content)')
            if price and currency:
                currency = currency.extract()[0]
                price = re.search('[,. 0-9]+', price.extract()[0])
                if price:
                    price = price.group()
                    price = price.replace(',', '').replace(' ', '')
                    cond_set_value(product, 'price',
                                   Price(priceCurrency=currency, price=price))

        if not product.get('upc'):
            cond_set(
                product,
                'upc',
                response.xpath('//strong[@id="UPC_CODE"]/text()').extract()
            )

    def _gen_location_request(self, response):
        data = {"postalCode": ""}
        new_meta = response.meta.copy()
        new_meta['handle_httpstatus_list'] = [404, 405]
        # Need Conetnt-Type= app/json
        req = FormRequest.from_response(
            response=response,
            url=self.LOCATION_URL,
            method='POST',
            formdata=data,
            callback=self._after_location,
            meta=new_meta,
            headers={'x-requested-with': 'XMLHttpRequest',
                     'Content-Type': 'application/json'},
            dont_filter=True)
        req = req.replace(body='{"postalCode":"' + self.zip_code + '"}')
        return req

    def _start_related(self, response):
        product = response.meta['product']
        reql = response.meta.get('relreql')
        if not reql:
            return self._request_questions_info(response)
            #return product
        (url, proc) = reql.pop(0)
        response.meta['relreql'] = reql
        return Request(
            url,
            meta=response.meta.copy(),
            callback=proc,
            dont_filter=True)

    @staticmethod
    def _extract_product_info_json_alternative(response):
        js_data = response.xpath('//script[@id="content" and @type="application/json"]/text()')
        if js_data:
            text = js_data.extract()[0]
            try:
                data = json.loads(text).get('content')
                return data if data else None
            except ValueError:
                pass

        _JS_DATA_RE = re.compile(
            r'window\.__WML_REDUX_INITIAL_STATE__\s*=\s*(\{.+?\})\s*;\s*<\/script>', re.DOTALL)
        js_data = re.search(_JS_DATA_RE, response.body_as_unicode().encode('utf-8'))
        if js_data:
            text = js_data.group(1)
            try:
                data = json.loads(text)
                return data
            except ValueError:
                pass

    def _populate_from_js_alternative(self, response, product):
        data = self._extract_product_info_json_alternative(response)
        if data:
            # Parse selected product id
            selected_product_id = self._parse_selected_product_id(data)

            # Parse selected product data
            selected_product = self._parse_selected_product_alternative(data, selected_product_id)

            # Parse selected product offers
            selected_product_offers = self._parse_selected_product_offers(selected_product)

            # Parse marketplaces
            marketplaces_data = self._parse_marketplaces_data_alternative(data)

            # Parse brand
            brand = self._parse_brand_alternative(selected_product)
            cond_set_value(product, 'brand', brand)

            # Parse title
            title = self._parse_title_alternative(selected_product)
            cond_set_value(product, 'title', title)

            # Parse out of stock
            is_out_of_stock = self._parse_out_of_stock_alternative(marketplaces_data, selected_product_offers)
            cond_set_value(product, 'is_out_of_stock', is_out_of_stock)

            # Parse price
            price = self._parse_price_alternative(marketplaces_data, selected_product_offers)
            cond_set_value(product, 'price', Price(priceCurrency='USD', price=price))

            # Parse description
            description = self._parse_description_alternative(selected_product)
            cond_set_value(product, 'description', description)

            # Parse image url
            image_url = self._parse_image_url_alternative(data)
            cond_set_value(product, 'image_url', image_url)

            # Parse marketplaces names
            marketplaces_names = self._parse_marketplaces_names(data)

            # Parse selected product available marketplaces
            selected_product_marketplaces = self._parse_selected_product_marketplaces(selected_product)

            # Parse marketplace
            marketplace = self._parse_marketplaces_alternative(
                marketplaces_data, marketplaces_names, selected_product_marketplaces)
            cond_set_value(product, 'marketplace', marketplace)

            # Parse buyer reviews
            buyer_reviews = self._parse_buyer_reviews_alternative(data)
            cond_set_value(product, 'buyer_reviews', buyer_reviews)

            # Parse bestseller rank
            bestseller_rank = self._parse_bestseller_rank_alternative(selected_product)
            cond_set_value(product, 'bestseller_rank', bestseller_rank)

            # Parse upc
            upc = self._parse_upc_alternative(selected_product)
            cond_set_value(product, 'upc', upc)

            # Parse categories data
            categories_data = self._parse_categories_data_alternative(selected_product)

            # Parse categories
            categories = self._parse_categories_alternative(categories_data)
            cond_set_value(product, 'categories', categories)

            # Parse categories_full_info
            categories_full_info = self._parse_categories_full_info_alternative(response, categories_data)
            cond_set_value(product, 'categories_full_info', categories_full_info)

            # Parse department
            department = self._parse_department_alternative(categories)
            cond_set_value(product, 'department', department)

            # Parse products
            products = self._parse_products_alternative(data)

            # Parse variants
            variants = self._parse_variants_alternative(response, marketplaces_data, data, products, selected_product)
            cond_set_value(product, 'variants', variants)

    @staticmethod
    def _parse_department_alternative(categories):
        return categories[-1] if categories else None

    @staticmethod
    def _parse_categories_full_info_alternative(response, categories_data):
        for category in categories_data:
            category['url'] = urlparse.urljoin(response.url, category.get('url'))
        return categories_data

    @staticmethod
    def _parse_categories_alternative(categories_data):
        return [category.get('name') for category in categories_data]

    @staticmethod
    def _parse_categories_data_alternative(selected_product):
        return selected_product.get('productAttributes', {}).get(
            'productCategory', {}).get('path')

    @staticmethod
    def _parse_selected_product_marketplaces(selected_product):
        return selected_product.get('offers')

    @staticmethod
    def _parse_selected_product_id(data):
        return data.get('product', {}).get('selected', {}).get('product')

    @staticmethod
    def _parse_selected_product_alternative(data, selected_product_id):
        selected = data.get('product', {}).get('products', {}).get(selected_product_id)
        if selected:
            return selected
        else:
            return data.get('product', {}).get('primaryProduct', {})

    @staticmethod
    def _parse_products_alternative(data):
        return data.get('product', {}).get('products', {})

    def _parse_variants_alternative(self, response, marketplaces, data, products, selected_product):
        variants = []
        primary_product_id = data.get('product', {}).get('primaryProduct')
        try:
            variants_map = data.get('product', {}).get('variantCategoriesMap', {}).get(primary_product_id, {})
        except:
            variants_map = {}
        for product in products.values():
            selected_product_offers = self._parse_selected_product_offers(product)
            price = self._parse_price_alternative(marketplaces, selected_product_offers)
            variant = {}
            properties = product.get('variants', {})
            variant_id = product.get('usItemId')
            url = urlparse.urljoin(response.url, '/ip/{}'.format(variant_id))
            selected_id = selected_product.get('usItemId')
            selected = selected_id == variant_id
            variant['selected'] = selected
            variant['url'] = url
            variant['price'] = price
            properties = self._parse_variant_properties_alternative(variant, variants_map, properties)
            variant['properties'] = properties
            variants.append(variant)
        return variants if len(variants) > 1 else None

    @staticmethod
    def _parse_variant_properties_alternative(variant, variants_map, properties):
        property_data = {}
        for property_name, property_value in properties.items():
            variant_data = variants_map.get(
                property_name).get('variants', {}).get(property_value)
            name = variant_data.get('name')
            in_stock = variant_data.get('availabilityStatus') == 'AVAILABLE'
            variant['in_stock'] = in_stock
            if 'color' in property_name:
                property_data['color'] = name
            elif 'size' in property_name:
                property_data['size'] = name
            elif 'number_of_pieces' in property_name:
                property_data['count'] = name
            else:
                property_data[property_name] = name
        return property_data

    @staticmethod
    def _parse_selected_product_offers(selected_product):
        # TODO: remove try-exception
        try:
            return selected_product.get('offers', [])
        except:
            return []

    @staticmethod
    def _parse_marketplaces_data_alternative(data):
        # if there is one seller, structure of json is different
        needed_data = data.get('product', {}).get('offers')
        if needed_data.get("availabilityStatus"):
            # pprint.pprint([needed_data])
            return [needed_data]
        else:
            # pprint.pprint(needed_data.values())
            return needed_data.values()

    @staticmethod
    def _parse_brand_alternative(selected_product):
        brand = selected_product.get('productAttributes', {}).get('brand')
        brand = brand.replace('\ufffd', '')
        return brand

    @staticmethod
    def _parse_title_alternative(selected_product):
        return selected_product.get('productAttributes', {}).get('productName')

    @staticmethod
    def _parse_upc_alternative(selected_product):
        return selected_product.get('upc')

    @staticmethod
    def _parse_out_of_stock_alternative(marketplaces, selected_product_offers):
        for offer in marketplaces:
            offer_id = offer.get('id')
            if offer_id in selected_product_offers \
                    and offer.get('productAvailability', {}).get('availabilityStatus') == "IN_STOCK":
                return False
        if len(marketplaces) == 1:
            for offer in marketplaces:
                offer_id = offer.get('offerInfo', {}).get('offerId')
                if offer_id in selected_product_offers and offer.get('availabilityStatus') == "IN_STOCK":
                    return False
        return True

    @staticmethod
    def _parse_price_alternative(marketplaces, offers):
        prices = [marketplace.get('pricesInfo', {}).get('priceMap', {}).get('CURRENT', {}).get('price')
                  for marketplace in marketplaces if marketplace.get('id') in offers]
        try:
            price = float(min(prices))
        except:
            price = 0
        return price

    @staticmethod
    def _parse_description_alternative(selected_product):
        return selected_product.get('productAttributes', {}).get('detailedDescription')

    @staticmethod
    def _parse_image_url_alternative(data):
        images = data.get('product', {}).get('images', {}).values()
        for image in images:
            if image.get('type') == 'PRIMARY':
                return image.get('assetSizeUrls', {}).get('main')

    @staticmethod
    def _parse_marketplaces_names(data):
        names = {}
        sellers = data.get('product', {}).get('sellers', {})
        sellers = sellers.values() if not sellers.get('sellerId') else [sellers]
        for seller in sellers:
            seller_id = seller.get('sellerId')
            seller_name = seller.get('sellerDisplayName')
            names[seller_id] = seller_name
        return names

    @staticmethod
    def _parse_marketplaces_alternative(marketplaces_data, marketplaces_names, selected_product_marketplaces):
        marketplaces = []
        for marketplace in marketplaces_data:
            offer_id = marketplace.get('id')
            seller_id = marketplace.get('sellerId')
            price = marketplace.get(
                'pricesInfo', {}).get('priceMap', {}).get('CURRENT', {}).get('price', 0)
            currency = marketplace.get(
                'pricesInfo', {}).get('priceMap', {}).get('CURRENT', {}).get('currencyUnit')
            name = marketplaces_names.get(seller_id)
            if offer_id in selected_product_marketplaces:
                marketplaces.append({'name': name,
                                     'price': price,
                                     'currency': currency})
        return marketplaces

    @staticmethod
    def _parse_buyer_reviews_alternative(data):
        selected = data.get('product', {}).get('selected', {}).get('product')
        review_data = data.get('product', {}).get('reviews', {}).get(selected, {})
        num_of_reviews = review_data.get('totalReviewCount', 0)
        average_rating = review_data.get('averageOverallRating', 0)
        rating_by_star = {
            1: review_data.get('ratingValueOneCount', 0),
            2: review_data.get('ratingValueTwoCount', 0),
            3: review_data.get('ratingValueThreeCount', 0),
            4: review_data.get('ratingValueFourCount', 0),
            5: review_data.get('ratingValueFiveCount', 0)
        }
        buyer_reviews = {'rating_by_star': rating_by_star,
                         'average_rating': average_rating,
                         'num_of_reviews': num_of_reviews}
        return BuyerReviews(**buyer_reviews)

    @staticmethod
    def _parse_bestseller_rank_alternative(selected_product):
        ranks = selected_product.get('itemSalesRanks')
        return ranks[0].get('rank') if ranks else None

    def _after_location(self, response):
        if response.status == 200:
            url = response.meta['product']['url']
            return Request(
                url,
                meta=response.meta.copy(),
                callback=self._reload_page,
                dont_filter=True)
        return self._start_related(response)

    def _reload_page(self, response):
        product = response.meta['product']
        self._populate_from_js_alternative(response, product)
        self._populate_from_js(response, product)
        self._populate_from_html(response, product)
        _meta = response.meta
        _meta['handle_httpstatus_list'] = [404, 502, 520]

        m = re.search(
            self._JS_DATA_RE, response.body_as_unicode().encode('utf-8'))
        if m:
            text = m.group(1)
            try:
                data = json.loads(text)
                self._on_dynamic_api_response(response, data)
            except ValueError:
                pass

        if self.scrape_questions:
            return Request(  # make another call - to scrape questions/answers
                self.ALL_QA_URL % (
                    get_walmart_id_from_url(product['url']), 1),
                meta={'product': response.meta['product']},
                callback=self._parse_all_questions_and_answers
            )
        else:
            return product

    @staticmethod
    def _parse_is_out_of_stock(data):
        return not data.get('analyticsData', {}).get('inStock')

    def _on_dynamic_api_response(self, response, data):
        if data:
            prod = response.meta['product']
            opts = data.get('buyingOptions', {})
            if opts is None:
                # product "no longer available"?
                self.log('buyingOptions are None: %s' % response.url, WARNING)
                prod.update({"no_longer_available": True})
            else:
                prod['is_out_of_stock'] = not opts.get('available', False)

                prod['is_out_of_stock'] = self._parse_is_out_of_stock(data)

                if 'not available' in opts.get('shippingDeliveryDateMessage', '').lower():
                    prod['shipping'] = False
                prod['is_in_store_only'] = opts.get('storeOnlyItem', None)
                if 'price' in opts and 'displayPrice' in opts['price']:
                    if opts['price']['displayPrice']:
                        prod['price'] = Price(
                            priceCurrency='USD',
                            price=opts['price']['displayPrice'].replace('$', '')
                        )
                self.log(
                    'Scraped and parsed unofficial APIs from %s' % response.url,
                    INFO
                )

    def _populate_from_js(self, response, product):
        data = {}
        m = re.search(
            self._JS_DATA_RE, response.body_as_unicode().encode('utf-8'))
        if m:
            text = m.group(1)
            try:
                data = json.loads(text)
            except ValueError:
                pass
        if not data:
            self.log("No JS matched in %r." % response.url, WARNING)
            return
        try:
            # Parse marketplace
            marketplace = self._parse_marketplace_from_js(data)
            cond_set_value(product, 'marketplace', marketplace)

            response.meta['productid'] = str(data['buyingOptions']['usItemId'])
            title = is_empty(Selector(text=data['productName']).xpath(
                'string()').extract())
            cond_set_value(product, 'title', title)
            available = data['buyingOptions']['available']
            cond_set_value(
                product,
                'is_out_of_stock',
                not available,
            )
            # the next 2 lines of code should not be uncommented, see BZ #1459
            #if response.xpath('//button[@id="WMItemAddToCartBtn"]').extract():
            #    product['is_out_of_stock'] = False
            if 'is_in_store_only' not in product:
                cond_set_value(
                    product,
                    'is_in_store_only',
                    data['buyingOptions']['storeOnlyItem'],
                )
            if available:
                price_block = None
                try:
                    price_block = data['buyingOptions']['price']
                except KeyError:
                    # Packs of products have different buyingOptions.
                    try:
                        price_block =\
                            data['buyingOptions']['minPrice']
                        #     data['buyingOptions']['maxPrice']
                    except KeyError:
                        self.log((
                            "Product with unknown buyingOptions "
                            "structure: %s\n%s") % (
                                response.url, pprint.pformat(data)),
                            WARNING
                        )
                if price_block:
                    try:
                        _price = Price(
                            priceCurrency=price_block['currencyUnit'],
                            price=price_block['currencyAmount']
                        )
                        cond_set_value(product, 'price', _price)
                    except KeyError:
                        try:
                            if price_block["currencyUnitSymbol"] == "$":
                                _price = Price(
                                    priceCurrency="USD",
                                    price=price_block['currencyAmount']
                                )
                            cond_set_value(product, 'price', _price)
                        except KeyError:
                            self.log(
                                ("Product with unknown buyingOptions "
                                    "structure: %s\n%s") % (
                                        response.url, pprint.pformat(data)),
                                ERROR
                            )
        except KeyError:
            pass
        if not product.get('upc', None):
            try:
                cond_set_value(
                    product, 'upc', data['analyticsData']['upc'], conv=unicode)
            except (ValueError, KeyError):
                pass  # Not really a UPC.
        try:
            cond_set_value(
                product,
                'image_url',
                data['primaryImageUrl'],
                conv=unicode)
        except KeyError:
            pass

        try:
            brand = data['analyticsData']['brand']
            brand = brand.replace('\ufffd', '')
            cond_set_value(
                product,
                'brand',
                brand,
                conv=unicode)
        except KeyError:
            pass

    def _scrape_total_matches(self, response):
        if response.css('.no-results'):
            return 0

        matches = response.css('.result-summary-container ::text').re(
            'Showing \d+ of (.+) results')
        if matches:
            num_results = matches[0].replace(',', '')
            num_results = int(num_results)
        else:
            num_results = None
            self.log(
                "Failed to extract total matches from %r." % response.url,
                ERROR
            )
        return num_results

    def _scrape_results_per_page(self, response):
        num = response.css('.result-summary-container ::text').re(
            'Showing (\d+) of')
        if num:
            return int(num[0])
        return None

    def _scrape_product_links(self, response):
        items = response.xpath(
            '//div[@class="js-tile tile-landscape"] | '
            '//div[contains(@class, "js-tile js-tile-landscape")] | '
            '//div[contains(@class,"js-tile tile-grid-unit")]'
        )
        if not items:
            items = response.xpath('//div[contains(@class, "js-tile")]')

        if not items:
            self.log("Found no product links in %r." % response.url, INFO)

        for item in items:
            link = item.css('a.js-product-title ::attr(href)')[0].extract()
            if link in self.visited_links.get(response.meta.get('search_term'), []):
                continue
            else:
                self.visited_links.get(response.meta.get('search_term'), []).append(link)

            title = ''.join(item.xpath(
                'div/div/h4[contains(@class, "tile-heading")]/a/node()'
            ).extract()).strip()
            title = is_empty(Selector(text=title).xpath('string()').extract())

            image_url = is_empty(item.xpath(
                "a/img[contains(@class, 'product-image')]/@data-default-image"
            ).extract())

            if item.css('div.pick-up-only').xpath('text()').extract():
                is_pickup_only = True
            else:
                is_pickup_only = False

            if item.xpath(
                './/div[@class="tile-row"]'
                '/span[@class="in-store-only"]/text()'
            ).extract():
                is_in_store_only = True
            else:
                is_in_store_only = False

            if item.xpath(
                './/div[@class="tile-row"]'
                '/span[@class="flag-rollback"]/text()'
            ).extract():
                special_pricing = True
            else:
                special_pricing = False

            if item.css('div.out-of-stock').xpath('text()').extract():
                shelf_page_out_of_stock = True
            else:
                shelf_page_out_of_stock = False

            res_item = SiteProductItem()
            if title:
                res_item["title"] = title.strip()
            if image_url:
                res_item["image_url"] = image_url
            res_item['is_pickup_only'] = is_pickup_only
            res_item['is_in_store_only'] = is_in_store_only
            res_item['special_pricing'] = special_pricing
            res_item['shelf_page_out_of_stock'] = shelf_page_out_of_stock
            yield link, res_item

    def _scrape_next_results_page_link(self, response):
        next_page = None

        next_page_links = response.css(".paginator-btn-next ::attr(href)")
        if len(next_page_links) == 1:
            next_page = next_page_links.extract()[0]
        elif len(next_page_links) > 1:
            self.log(
                "Found more than one 'next page' link in %r." % response.url,
                ERROR
            )
        else:
            self.log(
                "Found no 'next page' link in %r (which could be OK)."
                % response.url,
                INFO
            )

        return next_page

    def _request_questions_info(self, response):
        product_id = response.meta['product_id']
        if product_id is None:
            return response.meta['product']
        new_meta = response.meta.copy()
        new_meta['product']['recent_questions'] = []
        url = self.QA_URL.format(product_id=product_id, page=1)
        if self.scrape_questions:
            return Request(url, self._parse_questions,
                           meta=new_meta, dont_filter=True)
        else:
            return response.meta['product']

    def _parse_questions(self, response):
        data = json.loads(response.body_as_unicode())
        product = response.meta['product']
        if not data:
            if not product.get('buyer_reviews') or\
                            product.get('buyer_reviews') == 0:
                pass
            else:
                return product
        last_date = product.get('date_of_last_question')
        questions = product['recent_questions']
        dateconv = lambda date: datetime.strptime(date, '%m/%d/%Y').date()
        for question_data in data.get('questionDetails', []):
            date = dateconv(question_data['submissionDate'])
            if last_date is None:
                product['date_of_last_question'] = last_date = date
            if date == last_date:
                questions.append(question_data)
            else:
                break
        else:
            total_pages = min(self.QA_LIMIT,
                              data['pagination']['pages'][-1]['num'])
            current_page = response.meta.get('current_qa_page', 1)
            if current_page < total_pages:
                url = self.QA_URL.format(
                    product_id=response.meta['product_id'],
                    page=current_page + 1)
                response.meta['current_qa_page'] = current_page + 1
                return Request(url, self._parse_questions, meta=response.meta,
                               dont_filter=True)
        if not questions:
            del product['recent_questions']
        else:
            product['date_of_last_question'] = str(last_date)
        if not product.get('buyer_reviews') or \
                        product.get('buyer_reviews') == 0:
            pass
        else:
            if 'buyer_reviews' in product.keys():
                new_meta = response.meta.copy()
                return Request(url=self.REVIEW_DATE_URL.format(
                    product_id=response.meta['product_id']),
                               callback=self._parse_last_buyer_review_date,
                               meta=new_meta,
                               dont_filter=True)
            else:
                return product

    def _parse_all_questions_and_answers(self, response):
        original_prod_url = response.meta['product']['url']
        product = response.meta['product']
        product['_subitem'] = True
        recent_questions = product.get('recent_questions', [])
        current_qa_page = int(
            re.search('pageNumber\=(\d+)', response.url).group(1))

        content = json.loads(response.body)
        if not content['questionDetails']:
            # pagination reached its end?
            yield product
            return
        recent_questions.extend(content['questionDetails'])
        if self.username:
            for idx, q in enumerate(recent_questions):
                if not 'answeredByUsername' in q:
                    recent_questions[idx]['answeredByUsername'] = False
                    if 'answers' in q:
                        for answer in q['answers']:
                            if 'userNickname' in answer:
                                if self.username.strip().lower() == answer['userNickname'].strip().lower():
                                    recent_questions[idx]['answeredByUsername'] = True

        product['recent_questions'] = recent_questions
        # this is for [future] debugging - do not remove!
        #for qa in content['questionDetails']:
        #    print; print;
        #    print '__', qa['questionSummary'][0:200].encode('utf8')
        #    for answer in qa['answers']:
        #        print '____', answer['answerText'][0:200].encode('utf8')

        _meta = response.meta
        _meta['product'] = product
        yield product
        yield Request(
            self.ALL_QA_URL % (get_walmart_id_from_url(original_prod_url), current_qa_page+1),
            callback=self._parse_all_questions_and_answers,
            meta=_meta
        )

    def _parse_last_buyer_review_date(self, response):
        product = response.meta['product']
        data = json.loads(response.body_as_unicode())
        sel = Selector(text=data['reviewsHtml'])
        lbrd = sel.xpath('//span[contains(@class, "customer-review-date")]'
                         '/text()').extract()
        if lbrd:
            lbrd = datetime.strptime(lbrd[0].strip(), '%m/%d/%Y')
            product['last_buyer_review_date'] = lbrd.strftime('%d-%m-%Y')

        return product

    def _parse_temporary_unavailable(self, response):
        condition = response.xpath(
            '//p[contains(@class, "error-page-message-details text-center") '
            'and contains(text(), "We\'re having technical difficulties and are looking into the problem now.")]')
        return bool(condition)

    def parse(self, response):
        # call the appropriate method for the code. It'll only work if you set
        #  `handle_httpstatus_list = [502, 503, 504]` in the spider
        if hasattr(self, 'handle_httpstatus_list'):
            for _code in self.handle_httpstatus_list:
                if response.status == _code:
                    _callable = getattr(self, 'parse_' + str(_code), None)
                    if callable(_callable):
                        yield _callable()

        if self._search_page_error(response):
            remaining = response.meta['remaining']
            search_term = response.meta['search_term']

            self.log("For search term '%s' with %d items remaining,"
                     " failed to retrieve search page: %s"
                     % (search_term, remaining, response.request.url),
                     WARNING)
        elif self._parse_temporary_unavailable(response):
            item = SiteProductItem()
            item['temporary_unavailable'] = True
            yield item
        else:
            prods_count = -1  # Also used after the loop.
            for prods_count, request_or_prod in enumerate(
                    self._get_products(response)):
                yield request_or_prod
            prods_count += 1  # Fix counter.

            request = self._get_next_products_page(response, prods_count)
            if request is not None:
                yield request

    @staticmethod
    def _parse_marketplace_from_js(data):
        marketplaces = []
        marketplaces_data = data.get('buyingOptions', {}).get('marketplaceOptions', [])
        if not marketplaces_data:
            marketplaces_data = [data.get('buyingOptions', {})]
        for marketplace in marketplaces_data:
            price = marketplace.get('price', {}).get('currencyAmount')
            currency = marketplace.get('price', {}).get('currencyUnit')
            name = marketplace.get('seller', {}).get('displayName')
            marketplaces.append({'price': price,
                                 'currency': currency,
                                 'name': name})
        return marketplaces

    def parse_available_selenium(self, url, variants):
        try:
            #TODO debug mode - visible switch
            display = Display(visible=False, size=(1280, 768))
            display.start()
            driver = self._init_chromium()
            driver.set_page_load_timeout(120)
            driver.set_script_timeout(120)
            socket.setdefaulttimeout(120)
            driver.set_window_size(1280, 768)
            driver.get(url)
            time.sleep(5)
            def_var = [v.get("properties",{}).values() for v in variants if v.get('selected')]
            # print def_var
            def_var = def_var[0] if def_var else None
            # print def_var
            default_property = def_var[0] if def_var else None
            # print default_property
            attribute_xpath = ('.//span[contains(text(), "{}")]/..'.format(default_property))
            # print attribute_xpath
            self._click_attribute(driver=driver, selected_attribute_xpath=attribute_xpath)
            time.sleep(15)
            INLA = driver.find_elements(By.XPATH, './/h2[contains(text(), "Item not available")]')
            driver.quit()
        except Exception as e:
            self.log('Exception while getting INLA with selenium: ' + str(e), WARNING)
            return None, e
        else:
            return bool(INLA), None

    def _init_chromium(self, proxy=None, proxy_type=None):
        # TODO use random useragent script here
        # UA = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0) Gecko/20100101 Firefox/32.0"

        chrome_flags = webdriver.DesiredCapabilities.CHROME  # this is for Chrome?
        chrome_options = webdriver.ChromeOptions()  # this is for Chromium
        if proxy:
            chrome_options.add_argument(
                '--proxy-server=%s' % proxy_type+'://'+proxy)
        # chrome_flags["chrome.switches"] = ['--user-agent=%s' % UA]
        # chrome_options.add_argument('--user-agent=%s' % UA)
        executable_path = '/usr/sbin/chromedriver'
        if not os.path.exists(executable_path):
            executable_path = '/usr/local/bin/chromedriver'
        # initialize webdriver, open the page and make a screenshot
        driver = webdriver.Chrome(desired_capabilities=chrome_flags,
                                  chrome_options=chrome_options,
                                  executable_path=executable_path)
        return driver

    @staticmethod
    def _click_attribute(driver, selected_attribute_xpath, others_attributes_xpath=None, element=None):
        """
        Check if the attribute given by selected_attribute_xpath is checkout
        if checkeck don't do it anything,
        else find the first available attribute and click on it
        """
        if element:
            target = element
        else:
            target = driver

        available_attributes = None

        selected_attribute = target.find_elements(
            By.XPATH, selected_attribute_xpath)

        if others_attributes_xpath:
            available_attributes = target.find_elements(
                By.XPATH, others_attributes_xpath)

        # If not attribute is set and there are available attributes
        if not selected_attribute and available_attributes:
            available_attributes[0].click()
        elif selected_attribute:
            selected_attribute[0].click()
