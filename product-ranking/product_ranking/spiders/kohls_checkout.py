import json
import re
import itertools
import time
from HTMLParser import HTMLParser
from collections import OrderedDict
import scrapy
from scrapy.conf import settings
from product_ranking.items import CheckoutProductItem


class KohlsSpider(scrapy.Spider):
    name = 'kohls_checkout_products'
    allowed_domains = ['kohls.com']  # do not remove comment - used in find_spiders()

    SHOPPING_CART_URL = 'http://www.kohls.com/checkout/shopping_cart.jsp'
    PROMO_CODE_URL = "https://www.kohls.com/checkout/v2/includes/kohlsCash.jsp?shouldIncludeForms=true"
    TAX_URL = "http://www.kohls.com/checkout/v2/json/shipping_surcharges_gift_tax_json.jsp"

    def __init__(self, *args, **kwargs):
        settings.overrides['ITEM_PIPELINES'] = {}
        super(KohlsSpider, self).__init__(*args, **kwargs)
        self.user_agent = kwargs.get(
            'user_agent',
            ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
             'Chrome/51.0.2704.79 Safari/537.36')
        )

        self.product_data = kwargs.get('product_data', "[]")
        self.product_data = json.loads(self.product_data)

        self.quantity = kwargs.get('quantity')
        if self.quantity:
            self.quantity = [x for x in self.quantity.split(',')]
            self.quantity = sorted(self.quantity)
        else:
            self.quantity = ["1"]

        self.promo_code = kwargs.get('promo_code', '')  # ticket 10585
        self.promo_code = [promo_code.strip() for promo_code in self.promo_code.split(',')]
        self.promo_price = int(kwargs.get('promo_price', 0))
        self.promo_mode = self.promo_code and self.promo_price
        self.promo_code = self.promo_code if self.promo_code else [None]

    def start_requests(self):
        for product in self.product_data:
            url = product.get('url')
            yield scrapy.Request(url,
                                 meta={'product': product,
                                       'cookiejar': url})

    def parse(self, response):
        quantity = self.quantity
        product = response.meta.get('product')
        colors = product.get('color', [])
        if colors:
            is_colors_input = True
            if isinstance(colors, basestring):
                colors = [colors]
        else:
            is_colors_input = False
        json_data = self._parse_product_json_data(response)
        variants = json_data.get('productItem').get('skuDetails')
        product_id = str(json_data.get('productItem').get('productDetails').get('productId'))
        variants = self._variants_dict(variants)
        formdata = {'_D:add_cart_quantity': '+',
                    'isRedirectToJsonUrl': 'true',
                    '_D:/atg/commerce/order/purchase/'
                    'CartModifierFormHandler.productId': '+',
                    '/atg/commerce/order/purchase/'
                    'CartModifierFormHandler.useForwards': 'true',
                    '/atg/commerce/order/purchase/'
                    'CartModifierFormHandler.'
                    'addItemToOrderSuccessURL': 'shopping_cart_add_to_cart_success_url',
                    '_D:/atg/commerce/order/purchase/'
                    'CartModifierFormHandler.useForwards': '+',
                    '_D:/atg/commerce/order/purchase/'
                    'CartModifierFormHandler.addItemToOrderSuccessURL': '+',
                    '_DARGS': '/catalog/v2/fragments/pdp_addToBag_Form.jsp',
                    '_D:/atg/commerce/order/purchase/'
                    'CartModifierFormHandler.addItemToOrder': '+',
                    '_D:/atg/commerce/order/purchase/'
                    'CartModifierFormHandler.addItemToOrderErrorURL': '+',
                    '/atg/commerce/order/purchase/'
                    'CartModifierFormHandler.catalogRefIds': '34000344',
                    '_dyncharset': 'UTF-8',
                    'addItemToOrderSuccessURL': 'shopping_cart_add_to_cart_json_success_url',
                    '/atg/commerce/order/purchase/CartModifierFormHandler.addItemToOrder': '+',
                    'addItemToOrderErrorURL': 'shopping_cart_add_to_cart_json_error_url',
                    'add_cart_quantity': '1',
                    '_D:/atg/commerce/order/purchase/CartModifierFormHandler.catalogRefIds': '+',
                    '/atg/commerce/order/purchase/'
                    'CartModifierFormHandler.'
                    'addItemToOrderErrorURL': 'shopping_cart_add_to_cart_error_url',
                    '/atg/commerce/order/purchase/CartModifierFormHandler.productId': product_id}
        meta = {}

        if response.meta.get('retry'):
            quantity = ["1"]
            colors = [response.meta.get(
                'item').get('color')]
        elif product.get('FetchAllColors'):
            colors = variants.keys()
        elif not is_colors_input:
            colors.append(variants.keys()[0])

        for i, (quantity, color) in enumerate(itertools.product(quantity, colors)):

            item = CheckoutProductItem()
            item['color'] = color
            item['url'] = response.url

            meta['item'] = item
            meta['product'] = product

            if is_colors_input:
                item['requested_color'] = color

            formdata['/atg/commerce/order/purchase/' \
                     'CartModifierFormHandler.catalogRefIds'] = variants.get(color)
            formdata['add_cart_quantity'] = quantity

            if response.meta.get('retry'):
                item['requested_quantity_not_available'] = True
                meta['cookiejar'] = response.meta.get('cookiejar')
            else:
                item['requested_quantity_not_available'] = False
                meta['cookiejar'] = str(i)


            if color not in variants.keys():
                item['requested_color_not_available'] = True
                yield item
            else:
                for b, promo_code in enumerate(self.promo_code):
                    meta['promo_code'] = promo_code
                    if response.meta.get('retry'):
                        item['requested_quantity_not_available'] = True
                        meta['cookiejar'] = response.meta.get('cookiejar')
                    else:
                        item['requested_quantity_not_available'] = False
                        meta['cookiejar'] = str(i) if not self.promo_mode else str(i) + promo_code + str(b)

                    item['requested_color_not_available'] = False
                    yield scrapy.FormRequest.from_response(response,
                                                           formname='pdpAddToBag',
                                                           formdata=formdata,
                                                           callback=self.parse_availability,
                                                           method='POST',
                                                           dont_filter=True,
                                                           meta=meta
                                                           )

    def parse_availability(self, response):
        meta = response.meta
        if 'You can only purchase' in response.body_as_unicode():
            meta['retry'] = True
            yield scrapy.Request(response.meta.get('item').get('url'),
                                 meta=meta,
                                 dont_filter=True)
        else:
            yield scrapy.Request(self.SHOPPING_CART_URL,
                                 callback=self.parse_cart,
                                 dont_filter=True,
                                 meta=meta
                                )

    def parse_cart(self, response):
        item = response.meta.get('item')
        json_data = self._parse_cart_json_data(response)
        product = json_data.get('shoppingBag').get('items')[0]
        html_parser = HTMLParser()
        item['name'] = html_parser.unescape(product.get('displayName'))
        item['id'] = product.get('skuNumber')
        sale_price = product.get('salePrice').replace('$', '')
        regular_price = product.get('regularPrice').replace('$', '')
        price = sale_price if sale_price else regular_price
        item['price_on_page'] = price
        quantity = product.get('quantity')
        item['quantity'] = quantity
        order_subtotal = product.get('subtotal').replace('$', '')
        item['order_subtotal'] = order_subtotal
        item['price'] = round(
            float(order_subtotal) / item['quantity'], 2)
        item['order_total'] = float(json_data.get('orderSummary').get('total').replace('$', ''))
        if self.promo_mode:
            yield self.promo_logic(response, response.meta.get('promo_code'))
        else:
            yield item

    @staticmethod
    def _parse_product_json_data(response):
        json_data = response.xpath(
            '//script[contains(text(), "productJsonData")]/text()').extract()[0]
        json_regex = re.compile('productJsonData = ({.*?});', re.DOTALL)
        json_data = json.loads(
            json_regex.findall(json_data)[0])
        return json_data

    @staticmethod
    def _parse_cart_json_data(response):
        json_data = response.xpath("//script[contains(text(), \"var trJsonData = {\")"
                                   " and @type=\"text/javascript\"]/text()").extract()[0]
        json_regex = re.compile('trJsonData = ({.*?});', re.DOTALL)
        json_data = json_regex.findall(json_data)[0]
        json_data = json.loads(json_data)
        return json_data

    @staticmethod
    def _variants_dict(color_list):
        variants_dict = OrderedDict()
        for variant in color_list:
            color = variant.get('color')
            if color not in variants_dict.keys():
                variant_id = variant.get('skuId')
                variants_dict[color] = variant_id
        return variants_dict

    def promo_logic(self, response, promo_code=None):
        meta = response.meta
        item = meta.get('item')
        item['promo_code'] = meta.get('promo_code')
        if response.meta.get('promo'):
            promo_order_total = response.meta.get('promo_order_total')
            promo_order_subtotal = self._calculate_promo_subtotal(response, promo_order_total)
            promo_price = promo_order_subtotal / meta.get('item').get('quantity')
            is_promo_code_valid = not (promo_order_total == item['order_total'])
            item['is_promo_code_valid'] = is_promo_code_valid
            if self.promo_price == 1:
                item['order_total'] = promo_order_total
                item['order_subtotal'] = promo_order_subtotal
                item['price'] = promo_price
            if self.promo_price == 2:
                item['promo_order_total'] = promo_order_total
                item['promo_order_subtotal'] = promo_order_subtotal
                item['promo_price'] = promo_price
            return item
        return self._enter_promo_code(response, promo_code, item)

    @staticmethod
    def _calculate_promo_subtotal(response, promo_order_total):
        tax_rate = int(json.loads(response.body_as_unicode()).get('taxDetails').get('rate'))
        delivery = response.meta.get('delivery')
        promo_order_subtotal = round(
            (promo_order_total - delivery *
             (tax_rate / 100.0) - delivery) / (1 + (tax_rate / 100.0)), 2)
        return promo_order_subtotal

    def _parse_cart_tax(self, response):
        meta = response.meta
        y = lambda x: x.split(';')[0].split('=')
        cookies = response.headers.getlist('Set-Cookie')
        prices_raw = [y(b)[1].replace('$', '') for b in cookies if y(b)[0] == 'VisitorBagTotals']
        prices = [float(price.split('|')[0]) for price in prices_raw]
        promo_order_total = min(prices)
        delivery = float([delivery.split('|')[-1] for delivery in prices_raw if
                          float(delivery.split('|')[0]) == promo_order_total][0].replace('$', ''))
        meta['promo'] = True
        meta['delivery'] = delivery
        meta['promo_order_total'] = promo_order_total
        return scrapy.Request(self.TAX_URL,
                              meta=meta,
                              callback=self.promo_logic,
                              dont_filter=True
                              )

    def _enter_promo_code(self, response, promo_code, item):
        formdata = {"_dyncharset": "UTF-8",
                    "/atg/commerce/order/purchase/KLSPaymentInfoFormHandler.promoCode": promo_code,
                    "_D:/atg/commerce/order/purchase/KLSPaymentInfoFormHandler.promoCode": "+",
                    "/atg/commerce/order/purchase/KLSPaymentInfoFormHandler.paymentInfoSuccessURL": "applied_discounts_tr_success_url",
                    "_D:/atg/commerce/order/purchase/KLSPaymentInfoFormHandler.paymentInfoSuccessURL": "+",
                    "/atg/commerce/order/purchase/KLSPaymentInfoFormHandler.paymentInfoErrorURL": "applied_discounts_tr_success_url",
                    "_D:/atg/commerce/order/purchase/KLSPaymentInfoFormHandler.paymentInfoErrorURL": "+",
                    "/atg/commerce/order/purchase/KLSPaymentInfoFormHandler.useForwards": "true",
                    "_D:/atg/commerce/order/purchase/KLSPaymentInfoFormHandler.useForwards": "+",
                    "apply_promo_code": "submit",
                    "_D:apply_promo_code": "+",
                    "_DARGS": "/checkout/v2/includes/discounts_update_forms.jsp.2"}
        return scrapy.FormRequest.from_response(response,
                                                formxpath='//form[@id="apply_promo_code_form"]',
                                                formdata=formdata,
                                                callback=self._parse_cart_tax,
                                                method='POST',
                                                dont_filter=True,
                                                meta=response.meta
                                               )