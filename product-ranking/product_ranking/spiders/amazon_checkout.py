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
delete_commas = lambda x: x.replace(',', '')

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
        color = self.current_color
        quantity = self._get_item_quantity(product)

        if quantity and price:
            quantity = int(quantity)
            item['price'] = float(price) * quantity
            item['quantity'] = quantity
            item['requested_color'] = self.requested_color
            item['requested_quantity_not_available'] = quantity != int(self.current_quantity)

        if color:
            item['color'] = color

        item['requested_color_not_available'] = (
            color and self.requested_color and
            (self.requested_color.lower() != color.lower()))
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
            matched_colors = [None]
        return matched_colors

    def select_size(self, element=None):
        size_attribute_xpath = '//option[contains(@class, "dropdownSelect")]'
        size_attributes_xpath = '//option[contains(@class, "dropdownAvailable")]'
        self._click_attribute(size_attribute_xpath,
                              size_attributes_xpath,
                              element)
        self.log('Size selected')

    def select_color(self, element=None, color=None):
        time.sleep(4)
        color_attributes_xpath = ('*//li[@class="swatchAvailable"]')

        if color and color.lower() in map(lambda x: x.lower(), self._get_colors_names()):
            color_attribute_xpath = '//*[contains(@id, "color_name_")]//' \
                                    'img[contains(translate(' \
                                    '@alt, "ABCDEFGHIJKLMNOPQRSTUVWXYZ",' \
                                    ' "abcdefghijklmnopqrstuvwxyz"), "{}")]'.format(color.lower())

        self._click_attribute(color_attribute_xpath,
                              color_attributes_xpath,
                              element)
        self.log('Color {} selected'.format(color))

    def _get_products(self):
        return self._find_by_xpath(
            '//*[@role="main"]')

    def _add_to_cart(self):
        add_to_bag = self._click_on_element_with_id('add-to-cart-button')
        if add_to_bag:
            pop_up_xpath = '//button[@class="a-button-close a-declarative"' \
                            'and @aria-label="Close"]'
            if self._find_by_xpath(pop_up_xpath):
                self._click_on_element_with_xpath(pop_up_xpath)
            added_to_cart_xpath = '//*[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "added to cart")]'
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, added_to_cart_xpath)
                )
            )
            self.log('Added to bag')

    def _set_quantity(self, product, quantity):
        quantity_attribute_xpath = '//select[@name="quantity"]/' \
                         'option[@value="{}"]'.format(quantity)
        quantity_attributes_xpath = '//select[@name="quantity"]/option'
        self._click_attribute(quantity_attribute_xpath,
                              quantity_attributes_xpath)
        self.log('Quantity selected')

    def _get_product_list_cart(self):
        time.sleep(4)
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
                By.XPATH, '(//span[contains(@class, "a-size-medium a-color-price'
                          ' sc-price sc-white-space-nowrap  sc-price-sign")])[1]')))
        if order_subtotal_element:
            order_subtotal = order_subtotal_element.text
            return delete_commas(is_empty(re.findall('\$(.*)', order_subtotal)))

    def _get_total(self):
        try:
            xpath = '(//span[@class="a-expander-prompt"])[1]'
            self._click_on_element_with_xpath(xpath)
            self.wait.until(
                EC.visibility_of_element_located((
                    By.XPATH, '//input[@name="zipcode"]')))
            element = self._find_by_xpath(
                '//input[@name="zipcode"]')[0]
            element.send_keys(self.ZIP_CODE)
            element.send_keys(Keys.ENTER)
            time.sleep(4)
        except Exception as e:
            self.log('Error {}'.format(str(e)))
        try:
            order_total_element = self.wait.until(
                EC.visibility_of_element_located((
                    By.XPATH, '//span[@class="a-size-base sc-price-sign"]/'
                'span[@class="a-nowrap"]')))
            if order_total_element:
                order_total = order_total_element.text
                return delete_commas(is_empty(re.findall('\$(.*)', order_total)))
        except Exception as e:
            self.log('Error {}'.format(str(e)))
            return '0'

    def _get_item_name(self, item):
        return is_empty(item.xpath(
                        '*//*[contains(@class,"a-size-medium sc-product-title a-text-bold")]/text()').extract())

    def _get_item_id(self, item):
        return is_empty(item.xpath('@data-asin').extract())

    def _get_item_price(self, item):
        return delete_commas(is_empty(item.xpath(
                        '*//*[contains(@class,"sc-price-sign a-text-bold")]/text()'
        ).re('\$(.*)')))

    def _get_item_price_on_page(self, item):
        return delete_commas(is_empty(item.xpath(
                        '*//*[contains(@class, "a-color-price sc-price")]/text()'
        ).re('\$(.*)')))

    def _get_item_color(self, item):
        return is_empty(item.xpath(
                        '*//span[@class="size" and contains(text(),"color:")]'
                        '/strong/text()').extract())

    def _get_item_quantity(self, item):
        return is_empty(item.xpath(
                        '*//span[@class="a-dropdown-prompt"]/text()').extract())

    def _click_on_element_with_id(self, _id):
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.ID, _id)))
            element.click()
            time.sleep(4)
            return True
        except Exception as e:
            self.log('Error on clicking element with ID %s: %s' % (_id, str(e)))
            return False

    def _click_on_element_with_xpath(self, _xpath):
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, _xpath)))
            element.click()
            time.sleep(4)
            return True
        except Exception as e:
            self.log('Error on clicking element with XPATH %s: %s' % (_xpath, str(e)))
