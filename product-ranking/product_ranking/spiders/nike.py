from __future__ import division, absolute_import, unicode_literals

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


socket.setdefaulttimeout(60)


"""
def _init_webdriver():
    from selenium import webdriver
    driver = webdriver.PhantomJS()
    driver.set_window_size(1280, 1024)
    driver.set_page_load_timeout(60)
    driver.set_script_timeout(60)

    return driver
"""


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

        #self.br = BuyerReviewsBazaarApi(called_class=self)

        super(NikeProductSpider, self).__init__(
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

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
            '//*[contains(@class, "grid-item-image")]//a[contains(@href, "id=")]')
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
            for _ in xrange(5):  # TODO: this will be an infinte loop!
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
            #driver.save_screenshot('/tmp/1.png')
            new_meta['is_product_page'] = True
            for i, product_link in enumerate(product_links):
                new_meta['_ranking'] = i+1
                yield Request(product_link, meta=new_meta, callback=self.parse_product)

            driver.quit()

    @staticmethod
    def _parse_price(response):
        dell_price = response.xpath('//*[contains(text(), "Dell Price")]')
        dell_price = re.search('\$(\d+\.\d+)', ''.join(dell_price.xpath('./..//text()').extract()))
        if dell_price:
            dell_price = dell_price.group(1)
            price = Price(price=dell_price, priceCurrency='USD')
            return price
        price = response.xpath('//*[contains(@name, "pricing_sale_price")]'
                               '[contains(text(), "$")]//text()').extract()
        if not price:
            price = response.xpath('//*[contains(@name, "pricing_retail_price")]'
                                   '[contains(text(), "$")]//text()').extract()
        if price:
            price = Price(price=price[0].strip().replace('$', ''), priceCurrency='USD')
            return price

    @staticmethod
    def _parse_image(response):
        img_src = response.xpath('//*[contains(@class, "zoom-image-holder")]'
                                 '/img[contains(@class, "active")]/@src').extract()
        if img_src:
            return img_src[0]

    @staticmethod
    def _parse_brand(response):
        # <meta itemprop="brand" content = "DELL"/>
        brand = response.xpath('//meta[contains(@itermprop, "brand")]/@content').extract()
        if not brand:
            brand = response.xpath('//a[contains(@href, "/brand.aspx")]/img/@alt').extract()
        if brand:
            return brand[0].title()

    def _related_products(self, response):
        results = []
        rps = response.xpath('//*[contains(@class, "psItemDescription")]//'
                            'div[contains(@class, "psTeaser")]//a[contains(@href, "productdetail.aspx")]')
        for rp in rps:
            results.append(RelatedProduct(rp.xpath('text()').extract()[0].strip(),
                                          rp.xpath('@href').extract()[0].strip()))  # TODO: check if it's a valid format
        # TODO: scrape dynamic related products
        return results

    def parse_buyer_reviews(self, response):
        buyer_reviews_per_page = self.br.parse_buyer_reviews_per_page(response)
        #import pdb; pdb.set_trace()
        pass
        # TODO!

    def _parse_stock_status(self, response):
        element = response.xpath(
            '//a[contains(@class, "smallBlueBodyText")]'
            '[contains(@href, "makeWin")]//text()').extract()
        if element:
            return element[0]

    def parse_product(self, response):
        prod = response.meta.get('product', SiteProductItem())

        prod['_subitem'] = True

        _ranking = response.meta.get('_ranking', None)
        prod['ranking'] = _ranking
        prod['url'] = response.url

        cond_set(prod, 'title', response.css('h1 ::text').extract())
        #prod['price'] = DellProductSpider._parse_price(response)
        prod['image_url'] = NikeProductSpider._parse_image(response)
        #prod['sku'] = 'TODO'
        #prod['model'] = 'TODO'
        #prod['description'] = 'TODO'
        #prod['brand'] = DellProductSpider._parse_brand(response)
        #prod['related_products'] = self._related_products(response)
        #prod['description'] = self._parse_stock_status(response)  # this should be OOS field

        meta = {}
        meta['product'] = prod
        yield Request(
            url=self.REVIEW_URL.format(product_id='inspiron-15-5558-laptop'),
            dont_filter=True,
            callback=self.parse_buyer_reviews,
            meta=meta
        )

        yield prod