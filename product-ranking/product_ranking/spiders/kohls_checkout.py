import re
import socket
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from product_ranking.checkout_base import BaseCheckoutSpider

import scrapy


is_empty = lambda x, y="": x[0] if x else y


class KohlsSpider(BaseCheckoutSpider):
    name = 'kohls_checkout_products'
    allowed_domains = ['kohls.com']  # do not remove comment - used in find_spiders()

    SHOPPING_CART_URL = 'http://www.kohls.com/checkout/shopping_cart.jsp'
    CHECKOUT_PAGE_URL = "https://www.Kohls.com/dotcom/" \
                        "jsp/checkout/secure/checkout.jsp"

    def start_requests(self):
        yield scrapy.Request('http://www.kohls.com/')

    def _get_colors_names(self):
        time.sleep(4)
        swatches = self._find_by_xpath(
            '//a[@data-skucolor and '
            'not(contains(@class,"color-unavailable"))]')
        return [x.get_attribute("alt") for x in swatches]

    def select_size(self, element=None):
        size_attribute_xpath = ('*//*[@id="size-dropdown"]/'
                                'option[@select]|*//'
                                'a[@class="pdp-size-swatch active"]')

        size_attributes_xpath = ('*//*[@id="size-dropdown"]/'
                                 'option[not(@disabled="disabled")] | '
                                 '*//a[contains(@class,"pdp-size-swatch")'
                                 ' and not(contains(@class, "unavailable"))]')
        self._click_attribute(size_attribute_xpath,
                              size_attributes_xpath,
                              element)
        time.sleep(1)

    def select_color(self, element=None, color=None):
        time.sleep(4)
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

        # Remove focus to avoid hiddend the above element
        self._find_by_xpath('//h1')[0].click()

    def select_width(self, element=None):
        width_attribute_xpath = '*//div[@id="skuOptions_width"]//' \
            'li[@class="sku_select"]'
        width_attributes_xpath = '*//*[@id="skuOptions_width"]//' \
            'li[not(@class="sku_not_available" or @class="sku_illegal")]/a'
        self._click_attribute(width_attribute_xpath,
                              width_attributes_xpath,
                              element)

    def _get_products(self):
        time.sleep(4)
        return self._find_by_xpath(
            '//div[contains(@class, "pdp-main-container")]')

    def _add_to_cart(self):
        self._click_on_element_with_id('addtobagID')
        time.sleep(4)

    def _set_quantity(self, product, quantity):
        self.driver.execute_script(
            "document.getElementsByClassName('pdp-product-quantity')[0]"
            ".setAttribute('value', '%s')" % quantity)

    def _get_product_list_cart(self):
        time.sleep(4)
        condition = EC.visibility_of_element_located(
            (By.ID, 'shoppingCartLineItem_container'))
        return self.wait.until(condition)

    def _get_products_in_cart(self, product_list):
        time.sleep(4)
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
