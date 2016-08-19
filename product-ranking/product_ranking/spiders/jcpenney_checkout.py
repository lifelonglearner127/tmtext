import re
import socket
import time

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from product_ranking.checkout_base import BaseCheckoutSpider

import scrapy


is_empty = lambda x, y="": x[0] if x else y


class JCpenneySpider(BaseCheckoutSpider):
    name = 'jcpenney_checkout_products'
    allowed_domains = ['jcpenney.com']  # do not remove comment - used in find_spiders()

    SHOPPING_CART_URL = 'http://www.jcpenney.com/jsp/cart/viewShoppingBag.jsp'
    CHECKOUT_PAGE_URL = "https://www.jcpenney.com/dotcom/" \
                        "jsp/checkout/secure/checkout.jsp"

    def start_requests(self):
        yield scrapy.Request('http://www.jcpenney.com/')

    def _get_colors_names(self):
        swatches = self._find_by_xpath(
            '//ul[@class="small_swatches"]'
            '/li[not(@class="sku_not_available_select")]'
            '//a[not(span[@class="no_color"]) and '
            'not(span[@class="color_illegal"])]/img')
        return [x.get_attribute("name") for x in swatches]

    def select_size(self, element=None):
        size_attribute_xpath = '*//div[@id="skuOptions_size"]//' \
            'li[@class="sku_select"]'
        size_attributes_xpath = '*//*[@id="skuOptions_size"]//' \
            'li[not(@class="sku_not_available" or @class="sku_illegal")]/a'
        self._click_attribute(size_attribute_xpath,
                              size_attributes_xpath,
                              element)

    def select_color(self, element=None, color=None):
        color_attribute_xpath = '*//li[@class="swatch_selected"]'
        color_attributes_xpath = ('*//*[@class="small_swatches"]'
                                  '//a[not(span[@class="no_color"]) and '
                                  'not(span[@class="color_illegal"])]')

        if color and color in self._get_colors_names():
            color_attribute_xpath = '*//*[@class="small_swatches"]//a' \
                                    '[img[@name="%s"]]' % color

        self._click_attribute(color_attribute_xpath,
                              color_attributes_xpath,
                              element)
        time.sleep(10)
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
        self.select_width(product)
        self.select_waist(product)
        self.select_inseam(product)
        self.select_neck(product)
        self.select_sleeve(product)
        self._set_quantity(product, quantity)

    def _get_products(self):
        return self._find_by_xpath(
            '//*[@id="regularPP"]|//*[contains(@class,"product_row")]')

    def _add_to_cart(self):
        addtobagbopus = self._find_by_xpath('//*[@id="addtobagbopus"]')
        addtobag = self._find_by_xpath('//*[@id="addtobag"]')

        if addtobagbopus:
            self._click_on_element_with_id('addtobagbopus')

        elif addtobag:
            self._click_on_element_with_id('addtobag')
        time.sleep(4)

    def _do_others_actions(self):
        skip_this_offer = self._find_by_xpath(
            '//a[contains(@href,"javascript:skipThisOffer")]')
        if skip_this_offer:
            skip_this_offer[0].click()
            time.sleep(4)

    def _set_quantity(self, product, quantity):
        quantity_option = self._find_by_xpath(
            '*//*[@name="prod_quantity"]'
            '/option[@value="%d"]' % quantity, product)

        if quantity_option:
            quantity_option[0].click()

        time.sleep(4)

    def _get_product_list_cart(self):
        condition = EC.visibility_of_element_located(
            (By.ID, 'shoppingBagContentID'))
        return self.wait.until(condition)

    def _get_products_in_cart(self, product_list):
        html_text = product_list.get_attribute('outerHTML')
        selector = scrapy.Selector(text=html_text)
        return selector.xpath('//fieldset')

    def _get_subtotal(self):
        order_subtotal_element = self.wait.until(
            EC.visibility_of_element_located((
                By.XPATH, '//*[@class="flt_wdt merch_subtotal"]/span/'
                          'span[@class="flt_rgt"]')))
        if order_subtotal_element:
            order_subtotal = order_subtotal_element.text
            return is_empty(re.findall('\$([\d\.]+)', order_subtotal))

    def _get_total(self):
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
            return is_empty(re.findall('\$([\d\.]+)', order_total))

    def _get_item_name(self, item):
        return is_empty(item.xpath(
                        '*//*[contains(@class,"brand_name")]/a/text()').extract())

    def _get_item_id(self, item):
        return is_empty(item.xpath(
                        '*//*[contains(@class,"item_number")]/text()').re('#(.*)'))

    def _get_item_price(self, item):
        return is_empty(item.xpath(
                        '*//*[contains(@class,"flt_wdt total")]//'
                        'span[@class="flt_rgt"]/text()').re('\$(.*)'))

    def _get_item_price_on_page(self, item):
        return is_empty(item.css(
                        '.gallery_page_price  .priceValueSpacer::text').re('\$(.*)'))

    def _get_item_color(self, item):
        return is_empty(item.xpath(
                        '*//span[@class="size" and contains(text(),"color:")]'
                        '/strong/text()').extract())

    def _get_item_quantity(self, item):
        return is_empty(item.xpath(
                        '*//select[@name="quantity"]//option'
                        '[@selected="true"]/text()').extract())

    def _enter_promo_code(self, promo_code):
        self.log('Enter promo code: {}'.format(promo_code))
        promo_field= self._find_by_xpath('//div[@class="cr-coupon"]/*[@id="cr-code"]')[0]
        promo_field.send_keys(promo_code)
        time.sleep(2)
        promo_field.send_keys(Keys.ENTER)
        time.sleep(8)

    def _get_promo_total(self):
        order_total_element = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[@class="row order_total"]'
                           '/span[@class="flt_rgt"]')))

        if order_total_element:
            order_total = order_total_element.text
            return is_empty(re.findall('\$([\d\.]+)', order_total))

    def _get_promo_subtotal(self):
        order_subtotal_element = self.wait.until(
            EC.visibility_of_element_located((
                By.XPATH, '//*[@class="flt_wdt total"]/'
                          'span[@class="flt_rgt marginlft"]')))
        if order_subtotal_element:
            order_subtotal = order_subtotal_element.text
            return is_empty(re.findall('\$([\d\.]+)', order_subtotal))
