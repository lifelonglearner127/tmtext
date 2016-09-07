import json
import re
from HTMLParser import HTMLParser
from collections import OrderedDict
import scrapy
from scrapy import FormRequest
from scrapy.conf import settings
from product_ranking.items import CheckoutProductItem


class KohlsSpider(scrapy.Spider):
    name = 'kohls_checkout_products'
    allowed_domains = ['kohls.com']  # do not remove comment - used in find_spiders()

    SHOPPING_CART_URL = 'http://www.kohls.com/checkout/shopping_cart.jsp'
    ADD_TO_BAG_URL = 'http://www.kohls.com/catalog/navigation.jsp?_DARGS=/catalog/v2/fragments/pdp_addToBag_Form.jsp'

    def __init__(self, *args, **kwargs):
        settings.overrides['ITEM_PIPELINES'] = {}
        settings.overrides['COOKIES_ENABLED'] = True

        super(KohlsSpider, self).__init__(*args, **kwargs)
        self.user_agent = kwargs.get(
            'user_agent',
            ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0)'
             ' Gecko/20100101 Firefox/32.0')
        )

        product_data = kwargs.get('product_data', "[]")
        self.product_data = json.loads(self.product_data)
        self.quantity = kwargs.get('quantity')
        if self.quantity:
            self.quantity = [int(x) for x in self.quantity.split(',')]
            self.quantity = sorted(self.quantity)
        else:
            self.quantity = [1]

        self.promo_code = kwargs.get('promo_code')  # ticket 10585
        self.promo_price = int(kwargs.get('promo_price', 0))

        # settings.overrides['CRAWLERA_ENABLED'] = True

    def start_requests(self):
        for i, product in enumerate(self.product_data):
            url = product.get('url')
            yield scrapy.Request(url,
                                 meta={'product': product,
                                       'cookiejar': i})

    def parse(self, response):
        product = response.meta.get('product')
        parse_all = True if product.get('FetchAllColors') else None
        colors = product.get('color')
        if colors:
            is_requested_color = True
            if isinstance(colors, basestring):
                colors = [colors]
        json_data = response.xpath('//script[contains(text(), "productJsonData")]/text()').extract()[0]
        JSON = re.compile('productJsonData = ({.*?});', re.DOTALL)
        json_data = JSON.findall(json_data)[0]
        json_data = json.loads(json_data)
        variants = json_data.get('productItem').get('skuDetails')
        product_id = str(json_data.get('productItem').get('productDetails').get('productId'))
        variants = self._variants_dict(variants)
        formdata = {'_D:add_cart_quantity': '+',
                    'isRedirectToJsonUrl': 'true',
                    '_D:/atg/commerce/order/purchase/CartModifierFormHandler.productId': '+',
                    '/atg/commerce/order/purchase/CartModifierFormHandler.useForwards': 'true',
                    '/atg/commerce/order/purchase/CartModifierFormHandler.addItemToOrderSuccessURL': 'shopping_cart_add_to_cart_success_url',
                    '_D:/atg/commerce/order/purchase/CartModifierFormHandler.useForwards': '+',
                    '_D:/atg/commerce/order/purchase/CartModifierFormHandler.addItemToOrderSuccessURL': '+',
                    '_DARGS': '/catalog/v2/fragments/pdp_addToBag_Form.jsp',
                    '_D:/atg/commerce/order/purchase/CartModifierFormHandler.addItemToOrder': '+',
                    '_D:/atg/commerce/order/purchase/CartModifierFormHandler.addItemToOrderErrorURL': '+',
                    '/atg/commerce/order/purchase/CartModifierFormHandler.catalogRefIds': '34000344',
                    '_dyncharset': 'UTF-8',
                    'addItemToOrderSuccessURL': 'shopping_cart_add_to_cart_json_success_url',
                    '/atg/commerce/order/purchase/CartModifierFormHandler.addItemToOrder': '+',
                    'addItemToOrderErrorURL': 'shopping_cart_add_to_cart_json_error_url',
                    'add_cart_quantity': '1',
                    '_D:/atg/commerce/order/purchase/CartModifierFormHandler.catalogRefIds': '+',
                    '/atg/commerce/order/purchase/CartModifierFormHandler.addItemToOrderErrorURL': 'shopping_cart_add_to_cart_error_url',
                    '/atg/commerce/order/purchase/CartModifierFormHandler.productId': product_id}

        if response.meta.get('retry'):
            self.log('RETRY WITH QUANTITY 1')
            key = response.meta.get('color')
            i = response.meta.get('cookiejar')
            formdata['/atg/commerce/order/purchase/CartModifierFormHandler.catalogRefIds'] = variants.get(key)
            formdata['add_cart_quantity'] = '1'
            yield self._request(response, formdata, key, i, response.url, requested_color_not_available=True)

        elif parse_all:
            for y, quantity in enumerate(self.quantity):
                for i, key in enumerate(variants.keys()):
                    formdata['/atg/commerce/order/purchase/CartModifierFormHandler.catalogRefIds'] = variants.get(key)
                    formdata['add_cart_quantity'] = str(quantity)
                    yield self._request(response, formdata, key, str(y) + str(i), response.url, product=product)

        elif colors:
            for y, quantity in enumerate(self.quantity):
                for i, key in enumerate(colors):
                    formdata['/atg/commerce/order/purchase/CartModifierFormHandler.catalogRefIds'] = variants.get(key)
                    formdata['add_cart_quantity'] = str(quantity)
                    yield self._request(response, formdata, key, str(y) + str(i), response.url, key, product=product)

        else:
            color = variants.keys()[0]
            formdata['/atg/commerce/order/purchase/CartModifierFormHandler.catalogRefIds'] = variants.get(color)
            formdata['add_cart_quantity'] = '1'
            yield self._request(response, formdata, color, 1, response.url)

    def _request(self, response, formdata, color, cookie_jar, url, requested_color=None,
                 requested_color_not_available=False, product=None):
        return FormRequest.from_response(response,
                                         formname='pdpAddToBag',
                                         formdata=formdata,
                                         callback=self.parse_page,
                                         method='POST',
                                         dont_filter=True,
                                         meta={'cookiejar': cookie_jar,
                                               'color': color,
                                               'url': url,
                                               'requested_color': requested_color,
                                               'requested_color_not_available': requested_color_not_available,
                                               'product': product}
                                         )

    def parse_page(self, response):
        meta = response.meta
        if 'You can only purchase' in response.body_as_unicode():
            meta['retry'] = True
            meta['quantity'] = 1
            yield scrapy.Request(response.meta.get('url'),
                                 callback=self.parse,
                                 meta=meta,
                                 dont_filter=True)
        else:
            yield scrapy.Request(self.SHOPPING_CART_URL,
                                 callback=self.parse_cart,
                                 dont_filter=True,
                                 meta=meta
                                 )

    def parse_cart(self, response):

        item = CheckoutProductItem()
        json_data = \
        response.xpath(
            '//script[contains(text(), "var trJsonData = {") and @type="text/javascript"]/text()').extract()[0]
        JSON = re.compile('trJsonData = ({.*?});', re.DOTALL)
        json_data = JSON.findall(json_data)[0]
        json_data = json.loads(json_data)
        product = json_data.get('shoppingBag').get('items')[0]
        h = HTMLParser()
        item['name'] = h.unescape(product.get('displayName'))
        item['id'] = product.get('skuNumber')
        sale_price = product.get('salePrice').replace('$', '')
        regular_price = product.get('regularPrice').replace('$', '')
        price = sale_price if sale_price else regular_price
        item['price_on_page'] = price
        quantity = product.get('quantity')
        item['quantity'] = quantity
        item['color'] = product.get('color')
        order_subtotal = product.get('subtotal').replace('$', '')
        item['order_subtotal'] = order_subtotal
        item['price'] = round(
            float(order_subtotal) / item['quantity'], 2)
        item['order_total'] = json_data.get('orderSummary').get('total').replace('$', '')
        item['url'] = response.meta.get('url')
        item['requested_color'] = response.meta.get('requested_color')
        item['requested_color_not_available'] = (
            item['color'] and item['requested_color'] and
            (item['requested_color'] != item['color']))
        item['requested_quantity_not_available'] = response.meta.get('requested_color_not_available')
        yield self.promo_logic(response, item)

    @staticmethod
    def _variants_dict(color_list):
        variants_dict = OrderedDict()
        for variant in color_list:
            color = variant.get('color')
            if color not in variants_dict.keys():
                variant_id = variant.get('skuId')
                variants_dict[color] = variant_id
        return variants_dict

    def promo_logic(self, response, item):
        if response.meta.get('promo'):
            if self.promo_price == 1:
                return item
            if self.promo_price == 2:
                promo_item = response.meta.get('item')
                promo_item['promo_order_total'] = item['order_total']
                promo_item['promo_order_subtotal'] = item['order_subtotal']
                promo_item['promo_price'] = item['price']
                return promo_item
        elif self.promo_code and self.promo_price:
            return self._request_promo_code(response, self.promo_code, item)
        else:
            return item

    def _request_promo_code(self, response, promo_code, item):
        dynSessConf =  response.xpath('//input[@name="_dynSessConf"]/@value').extract()[0]
        formdata = {"_dyncharset": "UTF-8",
                    "_dynSessConf": dynSessConf,
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
        meta = response.meta
        meta['item'] = item
        meta['promo'] = True
        return FormRequest.from_response(response,
                                         formxpath='//form[@id="apply_promo_code_form"]',
                                         formdata=formdata,
                                         callback=self.parse_page,
                                         method='POST',
                                         dont_filter=True,
                                         meta=meta
                                         )
    