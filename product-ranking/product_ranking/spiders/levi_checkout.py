import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from product_ranking.checkout_base import BaseCheckoutSpider, retry_func
from product_ranking.items import CheckoutProductItem
import selenium.webdriver.support.ui as ui
from scrapy.log import WARNING

import scrapy

is_empty = lambda x, y="": x[0] if x else y


class LeviSpider(BaseCheckoutSpider):
    name = 'levi_checkout_products'
    allowed_domains = ['levi.com']  # do not remove comment - used in find_spiders()

    SHOPPING_CART_URL = 'http://www.levi.com/US/en_US/cart'
    # needed later in to get 'requested_quantity_not_available' field
    current_requested_quantity = 1

    def __init__(self, *args, **kwargs):
        super(LeviSpider, self).__init__(*args, **kwargs)
        # Levis have max 6 items added to cart
        fixed_quantity = []
        for q in self.quantity:
            fixed_q = 6 if q > 6 else q
            fixed_quantity.append(fixed_q)
        self.quantity = fixed_quantity

    def start_requests(self):
        yield scrapy.Request('http://www.levi.com/US/en_US/')

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
            if quantity < self.current_requested_quantity:
                item['requested_quantity_not_available'] = True
            else:
                item['requested_quantity_not_available'] = False
            item['price'] = round(float(price) / quantity, 2)
            item['quantity'] = quantity
            item['requested_color'] = self.requested_color

        if color:
            item['color'] = color

        item['requested_color_not_available'] = (
            color and self.requested_color and
            (self.requested_color.lower() != color.lower()))
        return item

    def _get_colors_names(self):
        time.sleep(15)
        xpath = ('//*[contains(@class,"color-swatches")]//'
                 'li[not(contains(@class,"not-available"))]'
                 '/img[@class="color-swatch-img"]')

        swatches = self._find_by_xpath(xpath)
        return [x.get_attribute("title") for x in swatches]

    def select_size(self, element=None):
        size_attribute_xpath = (
            '*//*[@id="pdp-buystack-size-values"]'
            '/li[contains(@class,"selected")]')
        size_attributes_xpath = (
            '*//*[@id="pdp-buystack-size-values"]'
            '/li[not(contains(@class, "not-available"))]')
        self._click_attribute(size_attribute_xpath,
                              size_attributes_xpath,
                              element)

    def select_color(self, element=None, color=None):
        # If color was requested and is available
        if color and color.lower() in map(
                (lambda x: x.lower()), self._get_colors_names()):
            color_attribute_xpath = (
                '*//*[contains(@class,"color-swatches")]//'
                'li[contains(@class,"color-swatch") '
                'and img[translate(@title, "ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
                ' "abcdefghijklmnopqrstuvwxyz")="%s"]]' % color.lower())

        # If color is set by default on the page
        else:
            color_attribute_xpath = (
                '*//*[contains(@class,"color-swatches")]//'
                'li[contains(@class,"color-swatch") '
                'and contains(@class, "selected")]')

        # All Availables Colors
        color_attributes_xpath = (
            '*//*[@class="color-swatches"]//'
            'li[contains(@class,"color-swatch") '
            'and not(contains(@class,"not-available"))]')

        self._click_attribute(color_attribute_xpath,
                              color_attributes_xpath,
                              element)

        time.sleep(1)

    def select_waist(self, element=None):
        size_attribute_xpath = (
            '*//*[@id="pdp-buystack-waist-values"]'
            '/li[contains(@class,"selected")]')
        size_attributes_xpath = (
            '*//*[@id="pdp-buystack-waist-values"]'
            '/li[not(contains(@class, "not-available"))]')
        self._click_attribute(size_attribute_xpath,
                              size_attributes_xpath,
                              element)

    def select_length(self, element=None):
        size_attribute_xpath = (
            '*//*[@id="pdp-buystack-length-values"]'
            '/li[contains(@class,"selected")]')
        size_attributes_xpath = (
            '*//*[@id="pdp-buystack-length-values"]'
            '/li[not(contains(@class, "not-available"))]')
        self._click_attribute(size_attribute_xpath,
                              size_attributes_xpath,
                              element)

    def _parse_attributes(self, product, color, quantity):
        time.sleep(4)
        self.select_color(product, color)
        self.select_size(product)
        self.select_waist(product)
        self.select_length(product)
        self._set_quantity(product, quantity)

    @retry_func(Exception)
    def _pre_parse_products(self):
        """Close Modal Windows requesting Email"""
        promp_window = self._find_by_xpath(
            '//*[@class="email-lightbox" or @class="email-lightbox"'
            ']//span[@class="close"]')

        if promp_window and promp_window[0].is_displayed():
            promp_window[0].click()
            time.sleep(2)

        more_colors_button = self._find_by_xpath(
            '//*[@class="color-swatch more-button"]')

        if more_colors_button and more_colors_button[0].is_displayed():
            more_colors_button[0].click()
            time.sleep(2)

    def _get_products(self):
        return self._find_by_xpath(
            '//*[@itemtype="http://schema.org/Product"]')

    def _add_to_cart(self):
        amount_in_cart = self._find_by_xpath('.//*[@id="minicart_bag_icon"]/*[@class="qty"]')
        amount_in_cart = amount_in_cart[0].text if amount_in_cart else None
        self.log("Amount of items in cart: %s" % amount_in_cart, level=WARNING)
        time.sleep(10)
        add_to_bag = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(@class,"add-to-bag")]')))
        add_to_bag.click()
        # add_to_bag = self._find_by_xpath(
        #     '//*[contains(@class,"add-to-bag")]')
        # if add_to_bag:
        # add_to_bag[0].click()
            # time.sleep(10)
        time.sleep(10)
        amount_in_cart = self._find_by_xpath('.//*[@id="minicart_bag_icon"]/*[@class="qty"]')
        amount_in_cart = amount_in_cart[0].text if amount_in_cart else None
        self.log("Amount of items in cart: %s" % amount_in_cart, level=WARNING)
        if not amount_in_cart or int(amount_in_cart) == 0:
            time.sleep(10)
            # add_to_bag[0].click()
            add_to_bag.click()
            time.sleep(10)
            amount_in_cart = self._find_by_xpath('.//*[@id="minicart_bag_icon"]/*[@class="qty"]')
            amount_in_cart = amount_in_cart[0].text if amount_in_cart else None
            self.log("Amount of items in cart: %s" % amount_in_cart, level=WARNING)
        if not amount_in_cart or int(amount_in_cart) == 0:
            raise Exception

    # @retry_func(Exception)
    def _set_quantity(self, product, quantity):
        self.current_requested_quantity = int(quantity)
        self._find_by_xpath(
            '//div[@class="quantity-display"]')[0].click()
        time.sleep(4)
        quantity_option = self._find_by_xpath(
            '*//*[@class="quantity"]'
            '//li[@data-qty-dropdown-value="%d"]' % quantity, product)

        if quantity_option:
            quantity_option[0].click()

        time.sleep(4)
        # to remove mouseover from size, blocking add to cart button
        self._find_by_xpath(
            './/*[@id="main-pdp-desc"]//*[@class="pdp-description"]')[0].click()
        time.sleep(4)

    def _get_product_list_cart(self):
        element = self._find_by_xpath(".//*[@id='useritems-container']")
        element = element[0] if element else None
        if not element:
            self.log("No element, waiting with timeout: %s" % element, level=WARNING)
            time.sleep(45)
            element = self._find_by_xpath(".//*[@id='useritems-container']")
            element = element[0] if element else None
        if not element:
            self.log("No element, using visibility_of_element_located: %s" % element, level=WARNING)
            # ui.WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, 'useritems-container')))
            condition = EC.visibility_of_element_located((By.ID, 'useritems-container'))
            element = self.wait.until(condition)
        return element

    def _get_products_in_cart(self, product_list):
        html_text = product_list.get_attribute('outerHTML')
        selector = scrapy.Selector(text=html_text)
        return selector.xpath('//*[@class="product-tile"]')

    def _get_subtotal(self):
        order_subtotal_element = self.wait.until(
            EC.visibility_of_element_located((
                By.XPATH, '//*[@class="bottom-subtotal-right"]')))
        if order_subtotal_element:
            order_subtotal = order_subtotal_element.text
            return is_empty(re.findall('\$([\d\.]+)', order_subtotal))

    def _get_total(self):
        order_total_element = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@class="bottom-estimated-total-right"]')))

        if order_total_element:
            order_total = order_total_element.text
            return is_empty(re.findall('\$([\d\.]+)', order_total))

    def _get_item_name(self, item):
        return is_empty(item.xpath(
            '*//p[@class="name"]/text()').extract())

    def _get_item_id(self, item):
        item_id = is_empty(item.xpath(
            '*//*[@class="material_sku"]/span/text()').extract())
        if not item_id:
            self.log("No item id timeout: %s" % item_id, level=WARNING)
            time.sleep(30)
            item_id = is_empty(item.xpath(
                '*//*[@class="material_sku"]/span/text()').extract())
        return item_id

    def _get_item_price(self, item):
        return is_empty(item.xpath(
                        '*//*[@class="totalprice"]/text()').re('\$(.*)'))

    def _get_item_price_on_page(self, item):
        return min(item.xpath(
            '*//*[@class="prod-price-info"]//text()').re('\$(.*)'))

    def _get_item_color(self, item):
        time.sleep(4)
        return is_empty(map((lambda x: x.strip()), filter((
            lambda x: x and 'color:' not in x.lower()),
            item.xpath('*//*[contains(@class,"material_color")]/text()').re(
                '\n\s*(.*)'))))

    def _get_item_quantity(self, item):
        return is_empty(item.xpath(
                        '*//*[@class="quantity"]//'
                        '*[@class="display"]/text()').extract())

    def _parse_cart_page(self):
        # socket.setdefaulttimeout(self.SOCKET_WAIT_TIME)
        # get cookies with our cart stuff and filter them
        dom_name = self._get_current_domain_name()
        cart_cookies = [c for c in self.driver.get_cookies() if dom_name in c.get('domain')]
        self.log("Got cookies from page: %s" % len(cart_cookies), level=WARNING)
        if not cart_cookies:
            time.sleep(30)
            cart_cookies = [c for c in self.driver.get_cookies() if dom_name in c.get('domain')]
            self.log("Got cookies from page after timeout: %s" % len(cart_cookies), level=WARNING)
        product_list = self._load_cart_page(cart_cookies=cart_cookies)
        if product_list:
            for product in self._get_products_in_cart(product_list):
                item = self._parse_item(product)
                if item:
                    item['order_subtotal'] = self._get_subtotal()
                    item['order_total'] = self._get_total()
                    yield item
                else:
                    self.log('Missing field in product from shopping cart')
