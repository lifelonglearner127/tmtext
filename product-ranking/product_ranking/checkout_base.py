import json
import os
import random
import re
import socket
import sys
import time
import traceback
import urlparse

from abc import abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from product_ranking.items import CheckoutProductItem

import scrapy
from scrapy.conf import settings
from scrapy.http import FormRequest
from scrapy.log import INFO, WARNING, ERROR
import lxml.html

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


class BaseCheckoutSpider(scrapy.Spider):
    allowed_domains = []  # do not remove comment - used in find_spiders()
    available_drivers = ['chromium', 'firefox']

    handle_httpstatus_list = [403, 404, 502, 500]

    SHOPPING_CART_URL = ''
    CHECKOUT_PAGE_URL = ""

    retries = 0
    MAX_RETRIES = 3
    SOCKET_WAIT_TIME = 120
    WEBDRIVER_WAIT_TIME = 100

    def __init__(self, *args, **kwargs):
        socket.setdefaulttimeout(self.SOCKET_WAIT_TIME)
        settings.overrides['ITEM_PIPELINES'] = {}
        super(BaseCheckoutSpider, self).__init__(*args, **kwargs)
        self.user_agent = kwargs.get(
            'user_agent',
            ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0)'
             ' Gecko/20100101 Firefox/32.0')
        )

        self.product_urls = kwargs.get('product_urls', None)
        self.product_data = kwargs.get('product_data', "[]")
        self.product_data = json.loads(self.product_data)
        self.driver_name = kwargs.get('driver', None)
        self.proxy = kwargs.get('proxy', '')  # e.g. 192.168.1.42:8080
        self.proxy_type = kwargs.get('proxy_type', '')  # http|socks5
        self.disable_site_settings = kwargs.get('disable_site_settings', None)
        self.quantity = kwargs.get('quantity', None)

        self.requested_color = None
        self.is_requested_color = False

        from pyvirtualdisplay import Display
        display = Display(visible=False)
        display.start()

        if self.quantity:
            self.quantity = [int(x) for x in self.quantity.split(',')]
            self.quantity = sorted(self.quantity)
        else:
            self.quantity = [1]

    def parse(self, request):
        is_iterable = isinstance(self.product_data, (list, tuple))
        self.product_data = (self.product_data
                             if is_iterable
                             else list(self.product_data))

        for product in self.product_data:
            self.log("Product: %r" % product)
            # Open product URL
            for qty in self.quantity:
                self.requested_color = None
                self.is_requested_color = False
                url = product.get('url')
                # Fastest way to empty the cart
                self._open_new_session(url)
                if product.get('FetchAllColors'):
                    # Parse all the products colors
                    colors = self._get_colors_names()

                else:
                    # Only parse the selected color
                    # if None, the first fetched will be selected
                    colors = product.get('color', None)

                    if colors:
                        self.is_requested_color = True

                    if isinstance(colors, basestring) or not colors:
                        colors = [colors]

                self.log('Colors %r' % (colors))
                for color in colors:
                    if self.is_requested_color:
                        self.requested_color = color

                    self.log('Color: %s' % (color or 'None'))
                    clickable_error = True
                    self.retries = 0
                    while clickable_error:
                        if self.retries >= self.MAX_RETRIES:
                            self.log('Max retries number reach,'
                                     ' skipping this product')
                            break

                        else:
                            self.retries += 1

                        clickable_error = False
                        try:
                            self._parse_product_page(url, qty, color)

                            for item in self._parse_cart_page():
                                item['url'] = url
                                yield item

                            # Fastest way to empty the cart
                            # and clear resources
                            self.driver.close()
                            self._open_new_session(url)

                        except WebDriverException as e:
                            clickable_error = True
                            print traceback.print_exc()
                            print "Exception: %s" % str(e)
                            self._open_new_session(url)

                        except:
                            print traceback.print_exc()
                            self.log('Error while parsing color %s of %s'
                                     % (color, url))

                            self._open_new_session(url)

                self.driver.close()

    def _open_new_session(self, url):
        self.driver = self.init_driver()
        self.wait = WebDriverWait(self.driver, self.WEBDRIVER_WAIT_TIME)
        socket.setdefaulttimeout(self.SOCKET_WAIT_TIME)
        self.driver.get(url)

    def _parse_item(self, product):
        item = CheckoutProductItem()
        name = self._get_item_name(product)
        item['name'] = name.strip() if name else name
        item['id'] = self._get_item_id(product)
        price = self._get_item_price(product)
        item['price_on_page'] = self._get_item_price_on_page(product)
        color = self._get_item_color(product)
        quantity = self._get_item_quantity(product)

        if quantity and price:
            quantity = int(quantity)
            item['price'] = float(price) / quantity
            item['quantity'] = quantity
            item['requested_color'] = self.requested_color

        if color:
            item['color'] = color

        item['requested_color_not_available'] = (
            color and self.requested_color and
            (self.requested_color != color))
        return item

    def _parse_attributes(self, product, color, quantity):
        self.select_color(product, color)
        self.select_size(product)
        self._set_quantity(product, quantity)

    def _parse_product_page(self, product_url, quantity, color=None):
        """ Process product and add it to the cart"""
        products = self._get_products()

        # Make it iterable for convenience
        is_iterable = isinstance(products, (list, tuple))
        products = products if is_iterable else list(products)

        for product in products:
            self._parse_attributes(product, color, quantity)
            self._add_to_cart()
            self._do_others_actions()

    def _parse_cart_page(self):
        socket.setdefaulttimeout(self.SOCKET_WAIT_TIME)
        self.driver.get(self.SHOPPING_CART_URL)
        product_list = self._get_product_list_cart()
        if product_list:
            for product in self._get_products_in_cart(product_list):
                item = self._parse_item(product)
                if item:
                        item['order_subtotal'] = self._get_subtotal()
                        item['order_total'] = self._get_total()
                        yield item
                else:
                    self.log('Missing field in product from shopping cart')

    def _find_by_xpath(self, xpath, element=None):
        """
        Find elements by xpath,
        if element is defined, search from that element node
        """
        if element:
            target = element
        else:
            target = self.driver
        return target.find_elements(By.XPATH, xpath)

    def _click_attribute(self, selected_attribute_xpath, others_attributes_xpath, element=None):
        """
        Check if the attribute given by selected_attribute_xpath is checkout
        if checkeck don't do it anything,
        else find the first available attribute and click on it
        """
        if element:
            target = element
        else:
            target = self.driver

        selected_attribute = target.find_elements(
            By.XPATH, selected_attribute_xpath)

        available_attributes = target.find_elements(
            By.XPATH, others_attributes_xpath)

        # If not attribute is set and there are available attributes
        if not selected_attribute and available_attributes:
            available_attributes[0].click()
        elif selected_attribute:
            selected_attribute[0].click()
        time.sleep(8)

    @abstractmethod
    def start_requests(self):
        return

    @abstractmethod
    def _get_colors_names(self):
        """Return the name of all the colors availables"""
        return

    @abstractmethod
    def select_size(self, element=None):
        """Select the size for the product"""
        return

    @abstractmethod
    def select_color(self, element=None, color=None):
        """Select the color for the product"""
        return

    @abstractmethod
    def select_width(self, element=None):
        """Select the width for the product"""
        return

    @abstractmethod
    def select_others(self, element=None):
        """Select others attributes for the product"""
        return

    @abstractmethod
    def _set_quantity(self, product, quantity):
        """Select the quantity for the product"""
        return

    @abstractmethod
    def _get_products(self):
        """Return the products on the page"""
        return

    @abstractmethod
    def _add_to_cart(self):
        """Add the product to the cart"""
        return

    @abstractmethod
    def _do_others_actions(self):
        """Do actions after adding product to cart"""
        return

    @abstractmethod
    def _get_item_name(self, item):
        return

    @abstractmethod
    def _get_item_id(self, item):
        return

    @abstractmethod
    def _get_item_price(self, item):
        return

    @abstractmethod
    def _get_item_price_on_page(self, item):
        return

    @abstractmethod
    def _get_item_color(self, item):
        return

    @abstractmethod
    def _get_item_quantity(self, item):
        return

    @abstractmethod
    def _get_subtotal(self):
        return

    @abstractmethod
    def _get_total(self):
        return

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
            if not self.driver_name:
                self._driver = 'chromium'
            elif self.driver_name == 'random':
                self._driver = random.choice(self.available_drivers)
            else:
                self._driver = self.driver_name
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