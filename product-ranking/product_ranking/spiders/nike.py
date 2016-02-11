from __future__ import division, absolute_import, unicode_literals

# TODO:
# 1) buyer reveiws
# 2) tweak line 167 ("this will be an infinte loop")
# 3) individual url parsing
# 4) remove unused methods and code

import os
import json
import re
import time
import urlparse
import socket
import random

from scrapy import Request
from scrapy.log import ERROR, WARNING
from pyvirtualdisplay import Display

from product_ranking.items import RelatedProduct, BuyerReviews
from product_ranking.items import SiteProductItem, Price
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi
from product_ranking.spiders import FLOATING_POINT_RGEX
from product_ranking.spiders import cond_set_value, populate_from_open_graph
from spiders_shared_code.nike_variants import NikeVariants


socket.setdefaulttimeout(60)


class NikeProductSpider(BaseProductsSpider):
    name = 'nike_products'
    allowed_domains = ["nike.com"]

    SEARCH_URL = "http://nike.com/#{search_term}"

    REVIEW_URL = "http://reviews.dell.com/2341_mg/{product_id}/reviews.htm?format=embedded"

    handle_httpstatus_list = [404, 403, 429]

    use_proxies = True

    def __init__(self, sort_mode=None, *args, **kwargs):
        from scrapy.conf import settings
        settings.overrides['DEPTH_PRIORITY'] = 1
        settings.overrides['SCHEDULER_DISK_QUEUE'] = 'scrapy.squeue.PickleFifoDiskQueue'
        settings.overrides['SCHEDULER_MEMORY_QUEUE'] = 'scrapy.squeue.FifoMemoryQueue'

        self.quantity = kwargs.get('quantity', 1000)  # default is 1000

        self.proxy = kwargs.get('proxy', '')  # e.g. 192.168.1.42:8080
        self.proxy_type = kwargs.get('proxy_type', '')  # http|socks5
        self.user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0) Gecko/20100101 Firefox/32.0'

        self.br = BuyerReviewsBazaarApi(called_class=self)

        super(NikeProductSpider, self).__init__(
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    @staticmethod
    def _get_antiban_headers():
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0) Gecko/20100101 Firefox/32.0',
            'Connection': 'keep-alive',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate'
        }

    def _get_store_cookies(self):
        raise NotImplementedError

    def start_requests(self):
        yield Request('http://store.nike.com',
                      callback=self._get_store_cookies,
                      headers=self._get_antiban_headers(),
                      priority=99999)

        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=st.encode('utf-8'),
                ),
                meta={'search_term': st, 'remaining': self.quantity},
                headers=self._get_antiban_headers()
            )
        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            yield Request(self.product_url,
                          self._parse_single_product,
                          meta={'product': prod},
                          headers=self._get_antiban_headers())

    def _init_firefox(self):
        from selenium import webdriver
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", self.user_agent)
        profile.set_preference('intl.accept_languages', 'en-US')
        profile.set_preference("network.proxy.type", 1)  # manual proxy configuration
        if self.proxy:
            if 'socks' in self.proxy_type:
                profile.set_preference("network.proxy.socks", self.proxy.split(':')[0])
                profile.set_preference("network.proxy.socks_port", int(self.proxy.split(':')[1]))
            else:
                profile.set_preference("network.proxy.http", self.proxy.split(':')[0])
                profile.set_preference("network.proxy.http_port", int(self.proxy.split(':')[1]))
        profile.update_preferences()
        driver = webdriver.Firefox(profile)
        driver.set_window_size(1280, 1024)
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(60)
        return driver

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _get_product_links_from_serp(self, driver):
        results = []
        links = driver.find_elements_by_xpath(
            '//*[contains(@class, "grid-item-image")]//a[contains(@href, "/pd/")]')
        for l in links:
            href = l.get_attribute('href')
            if href:
                if not href.startswith('http'):
                    href = urlparse.urljoin('http://' + self.allowed_domains[0], href)
                results.append(href)
        return results

    def _is_product_page(self, response):
        return 'is_product_page' in response.meta

    @staticmethod
    def _get_proxy_ip(driver):
        driver.get('http://icanhazip.com')
        ip = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', driver.page_source)
        if ip:
            ip = ip.group(1)
            return ip

    def parse(self, response):

        if not self._is_product_page(response):
            display = Display(visible=1, size=(1280, 1024))
            display.start()

            product_links = []
            # scrape "quantity" products
            driver = self._init_firefox()
            if self.proxy:
                ip_via_proxy = NikeProductSpider._get_proxy_ip(driver)
                print 'IP via proxy:', ip_via_proxy
                self.log('IP via proxy: %s' % ip_via_proxy)
            try:
                driver.get('http://store.nike.com/us/en_us')
            except Exception as e:
                print(str(e))
                self.log(str(e), WARNING)
            driver.find_element_by_name('searchList').send_keys(self.searchterms[0] + '\n')
            time.sleep(6)  # let AJAX finish
            new_meta = response.meta.copy()
            # get all products we need (scroll down)
            for _ in xrange(7):  # TODO: this will be an infinte loop!
                try:
                    driver.execute_script("scrollTo(0,50000)")
                    time.sleep(6)
                    product_links = self._get_product_links_from_serp(driver)
                    if len(product_links) > self.quantity:
                        break
                    print 'Collected %i product links' % len(product_links)
                except Exception as e:
                    print str(e)
                    break
            selenium_cookies = driver.get_cookies()
            try:
                driver.quit()
                display.stop()
            except Exception as e:
                self.log('Error on clearing resources: %s' % str(e))
            #driver.save_screenshot('/tmp/1.png')
            new_meta['is_product_page'] = True
            new_meta['proxy'] = 'http://127.0.0.1:8118'
            for i, product_link in enumerate(product_links):
                new_meta['_ranking'] = i+1
                yield Request(product_link, meta=new_meta, callback=self.parse_product,
                              headers=self._get_antiban_headers(),
                              cookies=selenium_cookies)

    def parse_product(self, response):
        meta = response.meta.copy()
        product = meta.get('product', SiteProductItem())

        product['_subitem'] = True

        _ranking = response.meta.get('_ranking', None)
        product['ranking'] = _ranking
        product['url'] = response.url

        # product data in json
        js_data = self.parse_data(response)

        # product id
        self.product_id = self.parse_product_id(response, js_data)

        print('--------------- product_id  %s' % self.product_id)
        self.product_color = self.parse_product_color(response, js_data)
        self.product_price = 0

        # Parse product_id
        title = self.parse_title(response, js_data)
        cond_set_value(product, 'title', title)

        # Parse locate
        locale = 'en_US'
        cond_set_value(product, 'locale', locale)

        # Parse model
        self.product_model = self.parse_product_model(response)
        cond_set_value(product, 'model', self.product_model)

        # Parse title
        title = self.parse_title(response, js_data)
        cond_set_value(product, 'title', title)

        # Parse image
        image = self.parse_image(response, js_data)
        cond_set_value(product, 'image_url', image)

        # Parse brand
        # brand = self.parse_brand(response)
        # cond_set_value(product, 'brand', brand)

        # Parse upc
        # upc = self.parse_upc(response)
        # cond_set_value(product, 'upc', upc)

        

        # Parse sku
        sku = self.parse_sku(response)
        cond_set_value(product, 'sku', sku)

        # Parse description
        description = self.parse_description(response)
        cond_set(product, 'description', description)

        # Parse price
        price = self.parse_price(response, js_data)
        cond_set_value(product, 'price', price)

        # Parse variants
        nv = NikeVariants()
        nv.setupSC(response)
        product['variants'] = nv._variants()

        response.meta['marks'] = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}

        yield product

    def parse_data(self, response):
        script_data = response.xpath(
            '//script[contains(@id, "product-data")]/text()').extract()
        try:
            js_data = json.loads(script_data[0])
            return js_data
        except:
            return

    def parse_image(self, response, js_data):
        if js_data:
            try:
                image = js_data['imagesHeroLarge'][0]
                return image
            except:
                return

    def parse_description(self, response):
        # js_data['content']
        desc = response.xpath(
            '//div[contains(@class, "pi-pdpmainbody")]').extract()

        return desc

    def parse_sku(self, response):
        skuid = response.xpath(
            '//span[contains(@class, "exp-style-color")]/text()').extract()
        if skuid:
            return skuid[0].replace('Style: ', '')

    def parse_price(self, response, js_data):
        if js_data:
            try:
                currency = js_data['crossSellConfiguration']['currency']
            except KeyError:
                currency = "USD"

            try:
                price = js_data['rawPrice']
                self.product_price = price
            except KeyError:
                price = 0.00

            if price and currency:
                price = Price(price=price, priceCurrency=currency)
        else:
            price = Price(price=0.00, priceCurrency="USD")

        return price

    def _scrape_total_matches(self, response):
        totals = response.css('.productCount ::text').extract()
        if totals:
            totals = totals[0].replace(',', '').replace('.', '').strip()
            if totals.isdigit():
                if not self.TOTAL_MATCHES:
                    self.TOTAL_MATCHES = int(totals)
                return int(totals)

    def _scrape_product_links(self, response):
        for link in response.xpath(
                '//li[contains(@class, "product-tile")]'
                '//a[contains(@rel, "product")]/@href'
        ).extract():
            yield link, SiteProductItem()

    def _get_nao(self, url):
        nao = re.search(r'nao=(\d+)', url)
        if not nao:
            return
        return int(nao.group(1))

    def _replace_nao(self, url, new_nao):
        current_nao = self._get_nao(url)
        if current_nao:
            return re.sub(r'nao=\d+', 'nao='+str(new_nao), url)
        else:
            return url+'&nao='+str(new_nao)

    def parse_product_id(self, response, js_data):
        if js_data:
            try:
                product_id = js_data['productId']
                return product_id
            except:
                return

    def parse_product_model(self, response):
        model = response.xpath(
            '//div[contains(@class, "hero-product-style-color-info")]/@data-stylenumber'
        ).extract()
        return model[0] if model else None

    def parse_product_color(self, response, js_data):
        if js_data:
            try:
                product_color = js_data['colorDescription']
                return product_color
            except:
                return

    def parse_title(self, response, js_data):
        if js_data:
            try:
                title = js_data['productTitle']
                return title
            except:
                return