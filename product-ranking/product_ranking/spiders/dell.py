from __future__ import division, absolute_import, unicode_literals

import json
import re
import time
import urlparse

from scrapy import Request
from scrapy.log import ERROR, WARNING

from product_ranking.items import RelatedProduct, BuyerReviews
from product_ranking.items import SiteProductItem, Price
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set
from product_ranking.spiders import FLOATING_POINT_RGEX
from product_ranking.spiders import cond_set_value, populate_from_open_graph


def _init_webdriver():
    from selenium import webdriver
    driver = webdriver.PhantomJS()
    driver.set_window_size(1280, 1024)
    return driver


class DellProductSpider(BaseProductsSpider):
    name = 'dell_products'
    allowed_domains = ["dell.com"]

    SEARCH_URL = "http://pilot.search.dell.com/{search_term}"

    def __init__(self, sort_mode=None, *args, **kwargs):
        from scrapy.conf import settings
        settings.overrides['DEPTH_PRIORITY'] = 1
        settings.overrides['SCHEDULER_DISK_QUEUE'] = 'scrapy.squeue.PickleFifoDiskQueue'
        settings.overrides['SCHEDULER_MEMORY_QUEUE'] = 'scrapy.squeue.FifoMemoryQueue'

        self.quantity = kwargs.get('quantity', 1000)  # default is 1000

        super(DellProductSpider, self).__init__(
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _get_product_links_from_serp(self, driver):
        results = []
        links = driver.find_elements_by_xpath('//h4/../../a[contains(@href, "/")]')
        for l in links:
            href = l.get_attribute('href')
            if href:
                if not href.startswith('http'):
                    href = urlparse.urljoin('http://' + self.allowed_domains[0], href)
                results.append(href)
        return results

    def _is_product_page(self, response):
        return 'is_product_page' in response.meta

    def parse(self, response):

        if not self._is_product_page(response):
            product_links = []
            # scrape "quantity" products
            driver = _init_webdriver()
            driver.get(response.url)
            new_meta = response.meta.copy()
            # get all products we need (or till the "show more products" button exists)
            paging_button = '//button[contains(@id, "paging-button")]'
            while driver.find_elements_by_xpath(paging_button):
                try:
                    button = driver.find_elements_by_xpath(paging_button)
                    button[0].click()
                    time.sleep(4)
                    product_links = self._get_product_links_from_serp(driver)
                    if len(product_links) > self.quantity:
                        break
                    print 'Collected %i product links' % len(product_links)
                except Exception as e:
                    print str(e)
                    break
            driver.save_screenshot('/tmp/1.png')
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
        img_src = response.xpath('//*[contains(@id, "product_main_image")]'
                                 '//img[contains(@src, ".jp")]/@src').extract()
        if not img_src:
            img_src = response.xpath('//*[contains(@class, "oneImageUp")]'
                                     '//img[contains(@src, ".jp")]/@src').extract()
        if not img_src:
            img_src = response.xpath('//*[contains(@class, "leftRightMainImg")]'
                                     '//img[contains(@src, ".jp")]/@src').extract()
        if img_src:
            return img_src[0]

    def parse_product(self, response):
        prod = response.meta.get('product', SiteProductItem())

        _ranking = response.meta.get('_ranking', None)
        prod['ranking'] = _ranking
        prod['url'] = response.url

        cond_set(prod, 'title', response.css('h1 ::text').extract())
        prod['price'] = DellProductSpider._parse_price(response)
        prod['image_url'] = DellProductSpider._parse_image(response)
        yield prod