import json
import os
import random
import re
import socket
import sys
import time
import traceback
import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from product_ranking.items import CheckoutProductItem

import scrapy
from scrapy.conf import settings
from scrapy.http import FormRequest
from scrapy.log import INFO, WARNING, ERROR
import lxml.html

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


class JCpenneySpider(scrapy.Spider):
    name = 'jcpenney_checkout_products'
    allowed_domains = ['jcpenney.com']  # do not remove comment - used in find_spiders()
    available_drivers = ['chromium', 'firefox']

    handle_httpstatus_list = [403, 404, 502, 500]

    SHOPPING_CART_URL = 'http://www.jcpenney.com/jsp/cart/viewShoppingBag.jsp'
    CHECKOUT_PAGE_URL = "https://www.jcpenney.com/dotcom/" \
                        "jsp/checkout/secure/checkout.jsp"

    def __init__(self, *args, **kwargs):
        socket.setdefaulttimeout(60)
        settings.overrides['ITEM_PIPELINES'] = {}
        super(JCpenneySpider, self).__init__(*args, **kwargs)
        self.user_agent = kwargs.get(
            'user_agent',
            ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0) Gecko/20100101 Firefox/32.0")
        )

        self.product_urls = kwargs.get('product_urls', None)
        self.product_data = kwargs.get('product_data', "[]")
        self.product_data = json.loads(self.product_data)
        self.close_popups = kwargs.get('close_popups', kwargs.get('close_popup', None))
        self.driver_name = kwargs.get('driver', None)  # if None, then a random UA will be used
        self.proxy = kwargs.get('proxy', '')  # e.g. 192.168.1.42:8080
        self.proxy_type = kwargs.get('proxy_type', '')  # http|socks5
        self.disable_site_settings = kwargs.get('disable_site_settings', None)
        self.quantity = kwargs.get('quantity', None)

        from pyvirtualdisplay import Display
        display = Display(visible=False)
        display.start()

        if self.quantity:
            self.quantity = [int(x) for x in self.quantity.split(',')]
            self.quantity = sorted(self.quantity)
        else:
            self.quantity = [1]

    def start_requests(self):
        yield scrapy.Request('http://www.jcpenney.com/')

    def parse(self, request):
        is_iterable = isinstance(self.product_data, (list, tuple))
        self.product_data = self.product_data if is_iterable else list(self.product_data)
        for product in self.product_data:
            self.log("Product: %r" % product)
            # Open product URL
            for qty in self.quantity:
                url = product.get('url')
                # Fastest way to empty the cart
                self.driver = self.init_driver()
                self.wait = WebDriverWait(self.driver, 25)
                socket.setdefaulttimeout(60)
                self.driver.get(url)

                if product.get('FetchAllColors'):
                    # Parse all the products colors
                    colors = self._get_colors_names()

                else:
                    # Only parse the selected color
                    # if None, the first fetched will be selected
                    colors = product.get('color', None)
                    if isinstance(colors, basestring) or not colors:
                        colors = [colors]

                self.log('Colors %r' % (colors))
                for color in colors:
                    self.log('Color: %s' % (color or 'None'))
                    clickable_error = True
                    while clickable_error:
                        clickable_error = False
                        try:
                            self._parse_product(url, qty, color)

                            for item in self._parse_cart():
                                item['url'] = url
                                yield item
                            # Fastest way to empty the cart
                            # and clear resources
                            self.driver.close()
                            self.driver = self.init_driver()
                            self.wait = WebDriverWait(self.driver, 25)
                            socket.setdefaulttimeout(60)
                            self.driver.get(url)

                        except WebDriverException as e:
                            if 'Element is not clickable at point' in str(e):
                                clickable_error = True

                            print "Exception: %s" % str(e)

                        except:
                            print traceback.print_exc()
                            self.log('Error while parsing color %s of %s' % (color, url))

                self.driver.close()

    def _get_colors_names(self):
        """
            Return the name of all the colors availables
        """
        swatches = self._find_by_xpath(
            '//ul[@class="small_swatches"]'
            '/li[not(@class="sku_not_available_select")]'
            '//a[not(span[@class="no_color"])]/img')
        return [x.get_attribute("name") for x in swatches]

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
            time.sleep(4)

    def select_size(self, element=None):
        """
        Select the size for the product if is not already selected
        """
        size_attribute_xpath = '*//div[@id="skuOptions_size"]//' \
            'li[@class="sku_select"]'
        size_attributes_xpath = '*//*[@id="skuOptions_size"]//' \
            'li[not(@class="sku_not_available" or @class="sku_illegal")]/a'
        self._click_attribute(size_attribute_xpath,
                              size_attributes_xpath,
                              element)

    def select_color(self, element=None, color=None):
        """
        Select the color for the product if is not already selected
        """
        color_attribute_xpath = '*//li[@class="swatch_selected"]'
        color_attributes_xpath = '*//*[@class="small_swatches"]//a'

        if color:
            color_attributes_xpath = '*//*[@class="small_swatches"]//a' \
                                     '[img[@name="%s"]]' % color

        self._click_attribute(color_attribute_xpath,
                              color_attributes_xpath,
                              element)

    def select_width(self, element=None):
        """
        Select the width for the product if is not already selected
        """
        width_attribute_xpath = '*//div[@id="skuOptions_width"]//' \
            'li[@class="sku_select"]'
        width_attributes_xpath = '*//*[@id="skuOptions_width"]//' \
            'li[not(@class="sku_not_available" or @class="sku_illegal")]/a'
        self._click_attribute(width_attribute_xpath,
                              width_attributes_xpath,
                              element)

    def select_others(self, element=None):
        """
        Select others attributes for the product
        if there aren't already selected
        """
        group_attributes = self._find_by_xpath(
            '*//ul[contains(@class,"sku_alt_options")]', element) or []

        for attribute in group_attributes:
            default_attr_xpath = 'li[@class="sku_select"]'
            avail_attr_xpath = 'li[not(@class="sku_not_available" '\
                'or @class="sku_illegal")]/a'
            self._click_attribute(default_attr_xpath,
                                  avail_attr_xpath,
                                  attribute)

    def _parse_product(self, product_url, quantity, color=None):
        products = self._find_by_xpath(
            '//*[@id="regularPP"]|//*[contains(@class,"product_row")]')

        # Make it iterable for convenience
        is_iterable = isinstance(products, (list, tuple))
        products = products if is_iterable else list(products)

        for product in products:
            self.select_color(product, color)
            self._find_by_xpath('//h1')[0].click()
            self.select_size(product)
            self.select_width(product)
            self.select_others(product)
            self._set_quantity(product, quantity)

            addtobagbopus = self._find_by_xpath('//*[@id="addtobagbopus"]')
            addtobag = self._find_by_xpath('//*[@id="addtobag"]')

            if addtobagbopus:
                self._click_on_element_with_id('addtobagbopus')

            elif addtobag:
                self._click_on_element_with_id('addtobag')
            time.sleep(4)

    def _set_quantity(self, product, quantity):
        quantity_option = self._find_by_xpath(
            '*//*[@name="prod_quantity"]'
            '/option[@value="%d"]' % quantity, product)

        if quantity_option:
            quantity_option[0].click()

        time.sleep(4)

    def _parse_cart(self):
        socket.setdefaulttimeout(60)
        self.driver.get(self.SHOPPING_CART_URL)
        product_list = self.wait.until(
            EC.visibility_of_element_located((
                By.ID, 'shoppingBagContentID')))

        if product_list:
            selector = scrapy.Selector(text=product_list.get_attribute(
                'outerHTML'))
            for product in selector.xpath('//fieldset'):
                name = is_empty(product.xpath(
                    '*//*[contains(@class,"brand_name")]/a/text()').extract())
                id = is_empty(product.xpath(
                    '*//*[contains(@class,"item_number")]/text()').re('#(.*)'))
                price = is_empty(product.xpath(
                    '*//*[contains(@class,"flt_wdt total")]//'
                    'span[@class="flt_rgt"]/text()').re('\$(.*)'))

                price_on_page = is_empty(product.css(
                    '.gallery_page_price  .priceValueSpacer::text').re('\$(.*)'))

                color = is_empty(product.xpath(
                    '*//span[@class="size" and contains(text(),"color:")]'
                    '/strong/text()').extract())

                quantity = is_empty(product.xpath(
                    '*//select[@name="quantity"]//option'
                    '[@selected="true"]/text()').extract())

                if name and id and price and quantity:
                    quantity = int(quantity)
                    price = float(price) / quantity
                    item = CheckoutProductItem()
                    item['name'] = name
                    item['id'] = id
                    item['price'] = price
                    item['price_on_page'] = price_on_page
                    item['quantity'] = quantity
                    if color:
                        item['color'] = color

                    order_subtotal_element = self.wait.until(
                        EC.visibility_of_element_located((
                            By.XPATH, '//*[@class="flt_wdt'
                                      ' merch_subtotal"]/span/'
                                      'span[@class="flt_rgt"]')))
                    if order_subtotal_element:
                        order_subtotal = order_subtotal_element.text
                        item['order_subtotal'] = is_empty(re.findall(
                            '\$([\d\.]+)', order_subtotal))
                        self._parse_checkout_page(item)

                    yield item
                else:
                    self.log('Missing field in product from shopping cart')

    def _parse_checkout_page(self, item):
        socket.setdefaulttimeout(60)
        self._click_on_element_with_id('Checkout')
        continue_as_guest_button = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//input[@class="blue-Button'
                           ' btn_continue_as_guest"]')))
        continue_as_guest_button.click()

        order_total_element = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[@class="row order_total"]'
                           '/span[@class="flt_rgt"]')))

        if order_total_element:
            order_total = order_total_element.text
            item['order_total'] = is_empty(re.findall('\$([\d\.]+)',
                                                      order_total))

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