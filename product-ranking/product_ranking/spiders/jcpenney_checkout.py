#
# turns pages into screenshots
#

import base64
import tempfile
import os
import sys
import time
import socket
import random
import re
import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import scrapy
from scrapy.conf import settings
from scrapy.http import Request, FormRequest
from scrapy.log import INFO, WARNING, ERROR, DEBUG
import lxml.html
try:
    from pyvirtualdisplay import Display
except ImportError:
    print('pyvirtualdisplay not installed')

try:
    import requesocks as requests
except ImportError:
    import requests

is_empty = lambda x, y="": x[0] if x else y

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD, '..', '..', '..', '..', '..'))

try:
    from search.captcha_solver import CaptchaBreakerWrapper
except ImportError as e:
    CaptchaBreakerWrapper = None
    print 'Error loading captcha breaker!', str(e)


def _get_random_proxy():
    proxy_file = '/tmp/http_proxies.txt'
    if os.path.exists(proxy_file):
        with open(proxy_file, 'r') as fh:
            lines = [l.strip().replace('http://', '')
                     for l in fh.readlines() if l.strip()]
            return random.choice(lines)


def _get_domain(url):
    return urlparse.urlparse(url).netloc.replace('www.', '')


class JCPennyCheckoutItem(scrapy.Item):
    name = scrapy.Field()
    id = scrapy.Field()
    price = scrapy.Field()


class JCpenneySpider(scrapy.Spider):
    name = 'jcpenney_checkout_products'
    allowed_domains = ['jcpenney.com']  # do not remove comment - used in find_spiders()
    available_drivers = ['chromium', 'firefox']

    handle_httpstatus_list = [403, 404, 502, 500]

    SHOPPING_CART_URL = 'http://www.jcpenney.com/jsp/cart/viewShoppingBag.jsp'
    CHECKOUT_PAGE_URL = "https://www.jcpenney.com/dotcom/" \
                        "jsp/checkout/secure/checkout.jsp"

    def __init__(self, product_urls, *args, **kwargs):
        self.user_agent = kwargs.get(
            'user_agent',
            ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0) Gecko/20100101 Firefox/32.0")
        )

        self.product_urls = product_urls
        self.close_popups = kwargs.get('close_popups', kwargs.get('close_popup', None))
        self.driver = kwargs.get('driver', None)  # if None, then a random UA will be used
        self.proxy = kwargs.get('proxy', '')  # e.g. 192.168.1.42:8080
        self.proxy_type = kwargs.get('proxy_type', '')  # http|socks5
        self.disable_site_settings = kwargs.get('disable_site_settings', None)

        self.driver = self.init_driver()
        self.wait = WebDriverWait(self.driver, 25)

        settings.overrides['ITEM_PIPELINES'] = {}
        super(JCpenneySpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        yield scrapy.Request('https://www.jcpenney.com')

    def parse(self, request):
        for product_url in self.product_urls.split('|'):
            # Open product URL
            self._parse_product(product_url)

        for item in self._parse_cart():
            yield item

        self._parse_checkout_page()
        

    def _click_attribute(self, selected_attribute_xpath, others_attributes_xpath):
        selected_attribute = self.driver.find_elements(
            By.XPATH, selected_attribute_xpath)
        available_attributes = self.driver.find_elements(
            By.XPATH, others_attributes_xpath)

        # If not size is set and there are available sizes
        if not selected_attribute and available_attributes:
            available_attributes[0].click()

    def _parse_product(self, product_url):
        socket.setdefaulttimeout(30)
        self.driver.get(product_url)

        # Mark search attribute
        size_attribute_xpath = '//*[@class="sku_alt_options ' \
            'sku_alt_designs"]//li[@class="sku_select"]'
        size_attributes_xpath = '//*[@class="sku_alt_options ' \
            'sku_alt_designs"]//li[not(@class="sku_not_available")]/a'
        self._click_attribute(size_attribute_xpath, size_attributes_xpath)

        # Mark search attribute
        size_attribute_xpath = '//div[@id="skuOptions_size"]//' \
            'li[@class="sku_select"]'
        size_attributes_xpath = '//*[@id="skuOptions_size"]//' \
            'li[not(@class="sku_not_available")]/a'
        self._click_attribute(size_attribute_xpath, size_attributes_xpath)

        # Mark color attribute
        color_attribute_xpath = '//li[@class="swatch_selected"]'
        color_attributes_xpath = '//*[@class="small_swatches"]//a'
        self._click_attribute(color_attribute_xpath, color_attributes_xpath)

        # Click add button
        time.sleep(4)
        self._click_on_element_with_id('addtobagbopus')
        time.sleep(4)

    def _parse_cart(self):
        socket.setdefaulttimeout(30)
        self.driver.get(self.SHOPPING_CART_URL)
        element = self.wait.until(
            EC.visibility_of_element_located((
                By.ID, 'shoppingBagContentID')))

        if element:
            selector = scrapy.Selector(text=element.get_attribute('outerHTML'))
            for product in selector.xpath('//fieldset'):
                name = is_empty(product.xpath(
                    '*//*[contains(@class,"brand_name")]/a/text()').extract())
                id = is_empty(product.xpath(
                    '*//*[contains(@class,"item_number")]/text()').re('#(.*)'))
                price = is_empty(product.xpath(
                    '*//*[contains(@class,"flt_wdt total")]//'
                    'span[@class="flt_rgt"]/text()').re('\$(.*)'))
                quantity = is_empty(product.xpath(
                    '*//select[@name="quantity"]//option'
                    '[@selected="true"]/text()').extract())

                if name and id and price and quantity:
                    quantity = int(quantity)
                    price = float(price) / quantity
                    item = JCPennyCheckoutItem()
                    item['name'] = name
                    item['id'] = id
                    item['price'] = price
                    yield item

                else:
                    self.log('Missing field in product from shopping cart')

    def _parse_checkout_page(self):
        socket.setdefaulttimeout(30)
        self._click_on_element_with_id('Checkout')
        time.sleep(5)
        element = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//input[@class="blue-Button'
                           ' btn_continue_as_guest"]')))
        element.click()
        element = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//input[@class="row order_total"]')))

        time.sleep(5)

    def _click_on_element_with_id(self, _id):
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.ID, _id)))
            element.click()
        except Exception as e:
            self.log('Error on clicking element with ID %s: %s' % (_id, str(e)))

    def _choose_another_driver(self):
        for d in self.available_drivers:
            if d != self._driver:
                return d

    def _init_chromium(self):
        from selenium import webdriver
        chrome_flags = webdriver.DesiredCapabilities.CHROME  # this is for Chrome?
        chrome_options = webdriver.ChromeOptions()  # this is for Chromium
        if self.proxy:
            chrome_options.add_argument(
                '--proxy-server=%s' % self.proxy_type+'://'+self.proxy)
        chrome_flags["chrome.switches"] = ['--user-agent=%s' % self.user_agent]
        chrome_options.add_argument('--user-agent=%s' % self.user_agent)
        executable_path = '/usr/sbin/chromedriver'
        if not os.path.exists(executable_path):
            executable_path = '/usr/local/bin/chromedriver'
        # initialize webdriver, open the page and make a screenshot
        driver = webdriver.Chrome(desired_capabilities=chrome_flags,
                                      chrome_options=chrome_options,
                                      executable_path=executable_path)
        return driver

    def _init_firefox(self):
        from selenium import webdriver
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", self.user_agent)
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
        return driver

    def init_driver(self, name=None):
        if name:
            self._driver = name
        else:
            if not self.driver:
                self._driver = 'chromium'
            elif self.driver == 'random':
                self._driver = random.choice(self.available_drivers)
            else:
                self._driver = self.driver
        print('Using driver: ' + self._driver)
        self.log('Using driver: ' + self._driver)
        init_driver = getattr(self, '_init_'+self._driver)
        return init_driver()

    @staticmethod
    def _get_proxy_ip(driver):
        driver.get('http://icanhazip.com')
        ip = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', driver.page_source)
        if ip:
            ip = ip.group(1)
            return ip

    def _has_captcha(self, response_or_text):
        if not isinstance(response_or_text, (str, unicode)):
            response_or_text = response_or_text.body_as_unicode()
        return '.images-amazon.com/captcha/' in response_or_text

    def _solve_captcha(self, response_or_text):
        if not isinstance(response_or_text, (str, unicode)):
            response_or_text = response_or_text.body_as_unicode()
        doc = lxml.html.fromstring(response_or_text)
        forms = doc.xpath('//form')
        assert len(forms) == 1, "More than one form found."

        captcha_img = forms[0].xpath(
            '//img[contains(@src, "/captcha/")]/@src')[0]

        self.log("Extracted capcha url: %s" % captcha_img, level=WARNING)

        return CaptchaBreakerWrapper().solve_captcha(captcha_img)

    def _handle_captcha(self, response, callback):
        # FIXME This is untested and wrong.
        captcha_solve_try = response.meta.get('captcha_solve_try', 0)
        url = response.url

        self.log("Captcha challenge for %s (try %d)."
                 % (url, captcha_solve_try),
                 level=INFO)

        captcha = self._solve_captcha(response)
        if captcha is None:
            self.log(
                "Failed to guess captcha for '%s' (try: %d)." % (
                    url, captcha_solve_try),
                level=ERROR
            )
            result = None
        else:
            self.log(
                "On try %d, submitting captcha '%s' for '%s'." % (
                    captcha_solve_try, captcha, url),
                level=INFO
            )

            meta = response.meta.copy()
            meta['captcha_solve_try'] = captcha_solve_try + 1

            result = FormRequest.from_response(
                response,
                formname='',
                formdata={'field-keywords': captcha},
                callback=callback,
                dont_filter=True,
                meta=meta)

        return result