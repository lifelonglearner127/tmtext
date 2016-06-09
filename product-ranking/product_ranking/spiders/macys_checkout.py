import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from product_ranking.checkout_base import BaseCheckoutSpider

import scrapy

is_empty = lambda x, y="": x[0] if x else y


class MacysSpider(BaseCheckoutSpider):
    name = 'macys_checkout_products'
    allowed_domains = ['macys.com']  # do not remove comment - used in find_spiders()

    SHOPPING_CART_URL = 'http://www1.macys.com/bag/index.ognc'

    def start_requests(self):
        yield scrapy.Request('http://www1.macys.com/')

    def _get_colors_names(self):
        xpath = '//div[@class="colorsSection"]//li[@data-title]'
        swatches = self._find_by_xpath(xpath)
        return [x.get_attribute("data-title") for x in swatches]

    def select_size(self, element=None):
        size_attribute_xpath = (
            '*//*[@class="sizesSection"]//li[@class="swatch selected"]')

        size_attributes_xpath = (
            '*//*[@class="sizesSection"]//'
            'li[contains(@class, "swatch") '
            'and not(contains(@class, "disabled"))]')

        self._click_attribute(size_attribute_xpath,
                              size_attributes_xpath,
                              element)

    def select_color(self, element=None, color=None):
        # If color was requested and is available
        if color and color in self._get_colors_names():
            color_attribute_xpath = (
                '*//div[@class="colorsSection"]//li[@data-title="%s"]' % color)

        # If color is set by default on the page
        else:
            color_attribute_xpath = (
                '*//div[@class="colorsSection"]//li[@class="swatch selected"]')

        # All Availables Collors
        color_attributes_xpath = (
            '*//*[@class="colorsSection"]//'
            'li[contains(@class, "swatch") '
            'and not(contains(@class, "disabled"))]')

        self._click_attribute(color_attribute_xpath,
                              color_attributes_xpath,
                              element)


    def select_width(self, element=None):
        return

    def select_others(self, element=None):
        return

    def _get_products(self):
        return self._find_by_xpath('//*[@id="productSidebar"]')

    def _add_to_cart(self):
        add_to_bag = self._find_by_xpath(
            '//*[contains(@class,"addToBagButton")]')

        if add_to_bag:
            add_to_bag[0].click()
            time.sleep(4)

    def _do_others_actions(self):
        return

    def _set_quantity(self, product, quantity):
        quantity_option = self._find_by_xpath(
            '*//*[@class="productQuantity"]'
            '/option[@value="%d"]' % quantity, product)

        if quantity_option:
            quantity_option[0].click()

        time.sleep(4)

    def _get_product_list_cart(self):
        condition = EC.visibility_of_element_located(
            (By.ID, 'itemsContainer'))
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
