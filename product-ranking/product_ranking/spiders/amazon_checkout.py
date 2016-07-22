import re
import socket
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from product_ranking.checkout_base import BaseCheckoutSpider
from product_ranking.items import CheckoutProductItem
import scrapy


is_empty = lambda x, y="": x[0] if x else y


class AmazonSpider(BaseCheckoutSpider):
    name = 'amazon_checkout_products'
    allowed_domains = ['amazon.com']  # do not remove comment - used in find_spiders()

    SHOPPING_CART_URL = 'https://www.amazon.com/gp/cart/view.html/ref=nav_cart'
    ZIP_CODE = '94117'

    def start_requests(self):
        yield scrapy.Request('http://www.amazon.com/')

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
            item['price'] = float(price) * quantity
            item['quantity'] = quantity
            item['requested_color'] = self.requested_color

        if color:
            item['color'] = color

        item['requested_color_not_available'] = (
            color and self.requested_color and
            (self.requested_color != color))
        return item

    def _get_colors_names(self):
        pattern = re.compile("\"color_name\":\[(.+?)\]")
        try:
            colors_names = self._find_by_xpath(
                '//script[contains(text(), "var dataToReturn")]')[0].get_attribute('innerText')
        except IndexError:
            colors_names = ""
        try:
            matched_colors = filter(lambda x: len(x) > 1, pattern.findall(colors_names)[0].split('"'))
        except IndexError:
            matched_colors = []
        return matched_colors

    def select_size(self, element=None):
        size_attribute_xpath = '//option[contains(@class, "dropdownSelect")]'
        size_attributes_xpath = '//option[contains(@class, "dropdownAvailable")]'
        self._click_attribute(size_attribute_xpath,
                              size_attributes_xpath,
                              element)

    def select_color(self, element=None, color=None):
        # TODO:
        color_attribute_xpath = '*//li[@class="swatchSelect"]'
        color_attributes_xpath = ('*//li[@class="swatchAvailable"]')

        if color and color in self._get_colors_names():
            color_attribute_xpath = '//button//img[contains(@alt, "{}")]'.format(color)

        self._click_attribute(color_attribute_xpath,
                              color_attributes_xpath,
                              element)

        # Remove focus to avoid hiddend the above element
        self._find_by_xpath('//h1')[0].click()
        time.sleep(4)

    def select_width(self, element=None):
        width_attribute_xpath = '*//div[@id="skuOptions_width"]//' \
            'li[@class="sku_select"]'
        width_attributes_xpath = '*//*[@id="skuOptions_width"]//' \
            'li[not(@class="sku_not_available" or @class="sku_illegal")]/a'
        self._click_attribute(width_attribute_xpath,
                              width_attributes_xpath,
                              element)
        time.sleep(4)


    def select_waist(self, element=None):
        default_attr_xpath = (
            '*//*[@id="skuOptions_waist"]//li[@class="sku_select"]')

        avail_attr_xpath = ('*//*[@id="skuOptions_waist"]//'
                            'li[not(@class="sku_not_available" '
                            'or @class="sku_illegal")]')

        self._click_attribute(default_attr_xpath,
                              avail_attr_xpath,
                              element)
        time.sleep(4)


    def select_inseam(self, element=None):
        default_attr_xpath = (
            '*//*[@id="skuOptions_inseam"]//li[@class="sku_select"]')

        avail_attr_xpath = ('*//*[@id="skuOptions_inseam"]//'
                            'li[not(@class="sku_not_available" '
                            'or @class="sku_illegal")]')

        self._click_attribute(default_attr_xpath,
                              avail_attr_xpath,
                              element)
        time.sleep(4)

    def select_neck(self, element=None):
        default_attr_xpath = (
            '*//*[@id="skuOptions_neck size"]//li[@class="sku_select"]')

        avail_attr_xpath = ('*//*[@id="skuOptions_neck size"]//'
                            'li[not(@class="sku_not_available" '
                            'or @class="sku_illegal")]')

        self._click_attribute(default_attr_xpath,
                              avail_attr_xpath,
                              element)
        time.sleep(4)

    def select_sleeve(self, element=None):
        default_attr_xpath = (
            '*//*[@id="skuOptions_sleeve"]//li[@class="sku_select"]')

        avail_attr_xpath = ('*//*[@id="skuOptions_sleeve"]//'
                            'li[not(@class="sku_not_available" '
                            'or @class="sku_illegal")]')

        self._click_attribute(default_attr_xpath,
                              avail_attr_xpath,
                              element)
        time.sleep(4)

    def _parse_attributes(self, product, color, quantity):
        self.select_color(product, color)
        self.select_size(product)
        # self.select_width(product)
        # self.select_waist(product)
        # self.select_inseam(product)
        # self.select_neck(product)
        # self.select_sleeve(product)
        self._set_quantity(product, quantity)

    def _get_products(self):
        return self._find_by_xpath(
            '//*[@id="ppd"]')

    def _add_to_cart(self):
        add_to_bag = self._find_by_xpath(
            '//input[contains(@id, "add-to-cart-button")]')

        if add_to_bag:
            add_to_bag[0].click()
            time.sleep(4)

    def _do_others_actions(self):
        skip_this_offer = self._find_by_xpath(
            '//a[contains(@href,"javascript:skipThisOffer")]')
        if skip_this_offer:
            skip_this_offer[0].click()
            time.sleep(4)

    def _set_quantity(self, product, quantity):
        time.sleep(4)
        quantity_option = self._find_by_xpath(
            '//select[@name="quantity"]/'
            'option[@value="{}"]'.format(quantity))

        if quantity_option:
            quantity_option[0].click()
            time.sleep(4)

    def _get_product_list_cart(self):
        condition = EC.visibility_of_element_located(
            (By.XPATH, '//div[@class="sc-list-body"]'))
        return self.wait.until(condition)

    def _get_products_in_cart(self, product_list):
        html_text = product_list.get_attribute('outerHTML')
        selector = scrapy.Selector(text=html_text)
        return selector.xpath('//div[contains(@class, "a-row sc-list-item")]')

    def _get_subtotal(self):
        order_subtotal_element = self.wait.until(
            EC.visibility_of_element_located((
                By.XPATH, '(//span[contains(@class, "sc-white-space-nowrap")])[1]')))
        if order_subtotal_element:
            order_subtotal = order_subtotal_element.text
            return is_empty(re.findall('\$([\d\.]+)', order_subtotal))

    def _get_total(self):
        try:
            time.sleep(1)
            element = self._find_by_xpath(
                '//span[@class="a-expander-prompt"]'
            )[0].click()
            self.wait.until(
                EC.visibility_of_element_located((
                    By.XPATH, '//input[@name="zipcode"]')))
            element = self._find_by_xpath(
                '//input[@name="zipcode"]')[0]
            element.send_keys(self.ZIP_CODE)
            element.send_keys(Keys.ENTER)
        except:
            pass
        try:
            order_total_element = self.wait.until(
                EC.visibility_of_element_located((
                    By.XPATH, '//span[@class="a-size-base sc-price-sign"]/'
                'span[@class="a-nowrap"]')))
            if order_total_element:
                order_total = order_total_element.text
                return is_empty(re.findall('\$([\d\.]+)', order_total))
        except:
            return '0'

    def _get_item_name(self, item):
        return is_empty(item.xpath(
                        '*//*[contains(@class,"sc-product-title a-text-bold")]/text()').extract())

    def _get_item_id(self, item):
        return is_empty(item.xpath(
                        '*//*[contains(@class,"item_number")]/text()').re('#(.*)'))

    def _get_item_price(self, item):
        return is_empty(item.xpath(
                        '*//*[contains(@class,"sc-price-sign a-text-bold")]/text()'
        ).re('\$(.*)'))

    def _get_item_price_on_page(self, item):
        return is_empty(item.xpath(
                        '*//*[contains(@class, "a-color-price sc-price")]/text()'
        ).re('\$(.*)'))

    def _get_item_color(self, item):
        return is_empty(item.xpath(
                        '*//span[@class="size" and contains(text(),"color:")]'
                        '/strong/text()').extract())

    def _get_item_quantity(self, item):
        return is_empty(item.xpath(
                        '*//span[@class="a-dropdown-prompt"]/text()').extract())
