import re
import socket
import time
import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from product_ranking.checkout_base import BaseCheckoutSpider
from product_ranking.items import CheckoutProductItem
from selenium.common.exceptions import WebDriverException

import scrapy
import random
import os
import requests

is_empty = lambda x, y="": x[0] if x else y


def _get_random_proxy():
    proxy_file = '/tmp/http_proxies.txt'
    if os.path.exists(proxy_file):
        with open(proxy_file, 'r') as f:
            proxies = [l.strip()
                     for l in f.readlines() if l.strip()]
            for i in proxies:
                proxy = random.choice(proxies)
                try:
                    ans = requests.get(
                        'http://kohls.com/',
                        proxies={'http': proxy, 'https': proxy},
                        timeout=10
                    )
                    if ans.status_code == 200:
                        return proxy.replace('http://','')
                except:
                    pass


class KohlsSpider(BaseCheckoutSpider):
    name = 'kohls_checkout_products'
    allowed_domains = ['kohls.com']  # do not remove comment - used in find_spiders()

    SHOPPING_CART_URL = 'http://www.kohls.com/checkout/shopping_cart.jsp'
    CHECKOUT_PAGE_URL = "https://www.Kohls.com/dotcom/" \
                        "jsp/checkout/secure/checkout.jsp"

    def __init__(self, *args, **kwargs):
        super(KohlsSpider, self).__init__(*args, **kwargs)
        self.proxy = _get_random_proxy()
        self.proxy_type = 'http'

    def start_requests(self):
        yield scrapy.Request('http://www.kohls.com/')

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
                    self.current_color = color
                    self.current_quantity = qty
                    self.log('Color: %s' % (color or 'None'))
                    clickable_error = True
                    self.retries = 0
                    while clickable_error:
                        if self.retries >= self.MAX_RETRIES:
                            self.log('Max retries number reach,'
                                     ' skipping this product')
                            break

                        else:
                            self.proxy = _get_random_proxy()
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
                            self.log("Exception: %s" % str(e))
                            self.driver.close()
                            self._open_new_session(url)

                        except:
                            print traceback.print_exc()
                            self.log('Error while parsing color %s of %s'
                                     % (color, url))
                            self.driver.close()
                            self._open_new_session(url)

                self.driver.close()

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
            item['price'] = float(price.replace(',', '')) / quantity
            item['quantity'] = quantity
            item['requested_color'] = self.requested_color
            item['requested_quantity_not_available'] = quantity != self.current_quantity

        if color:
            item['color'] = color

        item['requested_color_not_available'] = (
            color and self.requested_color and
            (self.requested_color != color))
        return item

    def _get_colors_names(self):
        time.sleep(30)
        swatches = self._find_by_xpath(
            '//a[@data-skucolor and '
            'not(contains(@class,"color-unavailable"))]')
        return [x.get_attribute("alt") for x in swatches]

    def select_size(self, element=None):
        time.sleep(10)
        size_attribute_xpath = ('*//*[@id="size-dropdown"]/'
                                'option[@select]|*//'
                                'a[@class="pdp-size-swatch active"]')

        size_attributes_xpath = ('*//*[@id="size-dropdown"]/'
                                 'option[not(@disabled) and not(@data-skusize="false")] | '
                                 '*//a[contains(@class,"pdp-size-swatch")'
                                 ' and not(contains(@class, "unavailable"))]')
        self._click_attribute(size_attribute_xpath,
                              size_attributes_xpath,
                              element)
        time.sleep(10)
        self.log('Size selected')

    def select_color(self, element=None, color=None):
        time.sleep(30)
        color_attribute_xpath = ('*//*[@class="pdp-color-swatches-info"]'
                                 '/div[contains(@class,"active")]/a')
        color_attributes_xpath = ('*//*[@class="pdp-color-swatches-info"]'
                                  '/div/a[not(contains(@class, color-unavailable))]')

        if color and color in self._get_colors_names():
            color_attribute_xpath = (
                '*//*[@class="pdp-color-swatches-info"]'
                '/div/a[@alt="%s"]' % color)

        self._click_attribute(color_attribute_xpath,
                              color_attributes_xpath,
                              element)
        time.sleep(10)
        self.log('Color selected')
        # Remove focus to avoid hiddend the above element
        # self._find_by_xpath('//h1')[0].click()

    def _get_products(self):
        time.sleep(30)
        condition = EC.presence_of_all_elements_located(
            (By.XPATH, '//div[contains(@class, "pdp-main-container")]'))
        return self.wait.until(condition)

    def _add_to_cart(self):
        time.sleep(10)
        self._click_on_element_with_id('addtobagID')
        time.sleep(20)
        select_lower = self._find_by_xpath('//*[contains(., "select a lower amount")]')
        if select_lower:
            self._set_quantity(None, 1)
            self._add_to_cart()

    def _set_quantity(self, product, quantity):
        time.sleep(10)
        self.driver.execute_script(
            "document.getElementsByClassName('pdp-product-quantity')[0]"
            ".setAttribute('value', '%s')" % quantity)
        time.sleep(10)
        self.log('Quantity selected')

    def _get_product_list_cart(self):
        time.sleep(30)
        condition = EC.visibility_of_element_located(
            (By.ID, 'shoppingCartLineItem_container'))
        return self.wait.until(condition)

    def _get_products_in_cart(self, product_list):
        time.sleep(10)
        html_text = product_list.get_attribute('outerHTML')
        selector = scrapy.Selector(text=html_text)
        return selector.xpath(
            '//*[@class="shoppingBagItem shoppingCartLineItem"]')

    def _get_subtotal(self):
        order_subtotal_element = self.wait.until(
            EC.visibility_of_element_located((
                By.ID, 'subtotal')))
        order_subtotal = order_subtotal_element.text
        return is_empty(re.findall('\$([\d\.]+)', order_subtotal))

    def _get_total(self):
        order_total_element = self.wait.until(
            EC.element_to_be_clickable(
                (By.ID, 'totalcharges')))

        order_total = order_total_element.text
        return is_empty(re.findall('\$([\d\.]+)', order_total))

    def _get_item_name(self, item):
        return is_empty(item.xpath(
                        '*//a[@class="shoppingbag_title"]/text()').extract())

    def _get_item_id(self, item):
        return is_empty(item.xpath(
                        '*//*[contains(@id, "sku_")]/text()').re('SKU # (\d+)'))

    def _get_item_price(self, item):
        return is_empty(item.xpath(
                        '*//*[@class="shoppingbag_itemtotal"]/text()').re(
                        '\$(.*)'))

    def _get_item_price_on_page(self, item):
        return min(map((lambda x: float(x.replace(',', '').strip())),
                       item.xpath('*//*[contains(@id,"saleprice_")]/text()|'
                                  '*//*[contains(@id, "regularprice_")]'
                                  '/text()').re('\$(.*)')))

    def _get_item_color(self, item):
        return is_empty(item.xpath(
                        '*//span[contains(@id, "color_")]/text()').re(
                        'Color: (.*)'))

    def _get_item_quantity(self, item):
        return is_empty(item.xpath(
                        '*//input[@name="ship_bill_quantity"]'
                        '/@value').extract())
