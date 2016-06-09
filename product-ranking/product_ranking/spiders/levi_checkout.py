import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from product_ranking.checkout_base import BaseCheckoutSpider

import scrapy

is_empty = lambda x, y="": x[0] if x else y


class LeviSpider(BaseCheckoutSpider):
    name = 'levi_checkout_products'
    allowed_domains = ['levi.com']  # do not remove comment - used in find_spiders()

    SHOPPING_CART_URL = 'http://www.levi.com/US/en_US/cart'

    def start_requests(self):
        yield scrapy.Request('http://www.levi.com/US/en_US/')

    def _get_colors_names(self):
        xpath = ('//*[@class="color-swatches"]//'
                 'li[not(contains(@class,"not-available"))]'
                 '/img[@class="color-swatch-img"]')

        swatches = self._find_by_xpath(xpath)
        return [x.get_attribute("title") for x in swatches]

    def select_size(self, element=None):
        size_attribute_xpath = (
            '*//*[@id="pdp-buystack-size-values"]'
            '/li[contains(@class,"selected")]')
        print size_attribute_xpath
        size_attributes_xpath = (
            '*//*[@id="pdp-buystack-size-values"]'
            '/li[not(contains(@class, "not-available"))]')
        print size_attributes_xpath
        print "select size"
        self._click_attribute(size_attribute_xpath,
                              size_attributes_xpath,
                              element)

    def select_color(self, element=None, color=None):
        # If color was requested and is available
        if color and color in self._get_colors_names():
            color_attribute_xpath = (
                '*//*[@class="color-swatches"]//'
                'li[contains(@class,"color-swatch") '
                'and img[@title="%s"]]' % color)

        # If color is set by default on the page
        else:
            color_attribute_xpath = (
                '*//*[@class="color-swatches"]//'
                'li[contains(@class,"color-swatch") '
                'and contains(@class, "selected")]')

        # All Availables Collors
        color_attributes_xpath = (
            '*//*[@class="color-swatches"]//'
            'li[contains(@class,"color-swatch") '
            'and not(contains(@class,"not-available"))]')

        self._click_attribute(color_attribute_xpath,
                              color_attributes_xpath,
                              element)

    def _pre_parse_products(self):
        """Close Modal Windows requesting Email"""
        promp_window = self._find_by_xpath(
            '//*[@class="email-lightbox"]//span[@class="close"]')

        if promp_window:
            promp_window[0].click()
            time.sleep(4)

    def select_width(self, element=None):
        return

    def select_others(self, element=None):
        return

    def _get_products(self):
        return self._find_by_xpath(
            '//*[@itemtype="http://schema.org/Product"]')

    def _add_to_cart(self):
        add_to_bag = self._find_by_xpath(
            '//*[contains(@class,"add-to-bag")]')

        if add_to_bag:
            add_to_bag[0].click()
            time.sleep(4)

    def _do_others_actions(self):
        return

    def _set_quantity(self, product, quantity):
        quantity_option = self._find_by_xpath(
            '*//*[@class="quantity"]'
            '/li[@data-qty-dropdown-value="%d"]' % quantity, product)

        if quantity_option:
            quantity_option[0].click()

        time.sleep(4)

    def _get_product_list_cart(self):
        condition = EC.visibility_of_element_located(
            (By.ID, 'time.sleep(4)'))
        return self.wait.until(condition)

    def _get_products_in_cart(self, product_list):
        html_text = product_list.get_attribute('outerHTML')
        selector = scrapy.Selector(text=html_text)

        return selector.xpath('//*[contains(@id, "lineitem_")]')

    def _get_subtotal(self):
        order_subtotal_element = self.wait.until(
            EC.visibility_of_element_located((
                By.ID, 'bagMerchandiseTotal')))
        if order_subtotal_element:
            order_subtotal = order_subtotal_element.text
            return is_empty(re.findall('\$([\d\.]+)', order_subtotal))

    def _get_total(self):
        order_total_element = self.wait.until(
            EC.element_to_be_clickable(
                (By.ID, 'bagTotal')))

        if order_total_element:
            order_total = order_total_element.text
            return is_empty(re.findall('\$([\d\.]+)', order_total))

    def _get_item_name(self, item):
        return is_empty(item.xpath(
            '*//*[@class="itemName"]/a/text()').extract())

    def _get_item_id(self, item):
        return is_empty(item.xpath(
                        '*//*[@class="valWebId"]/text()').extract())

    def _get_item_price(self, item):
        return is_empty(item.xpath(
                        '*//*[@class="itemTotal"]/text()').re('\$(.*)'))

    def _get_item_price_on_page(self, item):
        return min(item.xpath('//*[@class="colPrice"]//text()').re('\$(.*)'))

    def _get_item_color(self, item):
        return is_empty(item.xpath(
                        '*//*[@class="valColor"]/text()').extract())

    def _get_item_quantity(self, item):
        return is_empty(item.xpath(
                        '//*[@class="colQty"]//'
                        'option[@selected]/text()').extract())
