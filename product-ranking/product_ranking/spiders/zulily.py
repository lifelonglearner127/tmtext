# -*- coding: utf-8 -*-
import string
import urllib
import re
import json
import time
from scrapy.utils.response import open_in_browser
from scrapy.log import DEBUG
from scrapy import FormRequest, Request, Spider
from product_ranking.items import SiteProductItem, BuyerReviews, Price
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FLOATING_POINT_RGEX, cond_set_value


class KrogerProductsSpider(BaseProductsSpider):
    name = "zulily_products"
    allowed_domains = ["zulily.com"]

    LOG_IN_URL = "https://www.zulily.com/auth"
    SEARCH_URL = 'http://www.petsmart.com/search?SearchTerm={search_term}'
    IMAGE_URL = 'http://s7d2.scene7.com/is/image/PetSmart/{sku}_Imageset'
    use_proxies = True

    def __init__(self, login="", password="", *args, **kwargs):
        super(KrogerProductsSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

    def start_requests(self):
        body = '{"login": {"username": "arnoldmessi777@gmail.com", "password": "apple123"}, ' \
               '"redirectUrl": "https://www.zulily.com/"}'

        yield Request(self.LOG_IN_URL,
                      method='POST',
                      body=body,
                      callback=self._log_in,
                      headers={'Content-Type': 'application/json;charset=UTF-8'})

    def _log_in(self, response):
        prod = SiteProductItem()
        prod['is_single_result'] = True
        prod['url'] = self.product_url
        prod['search_term'] = ''

        yield Request(self.product_url, callback=self._start_requests, meta={'product': prod})

    def _scrape_next_results_page_link(self, response):
        # <a role="button" class="right_arrow " id = "WC_SearchBasedNavigationResults_pagination_link_right_categoryResults" href = 'javascript:dojo.publish("showResultsForPageNumber",[{pageNumber:"2",pageSize:"60", linkId:"WC_SearchBasedNavigationResults_pagination_link_right_categoryResults"}])' title="Show next page"></a>
        # pageNumber:"2",pageSize:"60",
        next_page = response.xpath('//a[@class="right_arrow "]/@href').re('pageNumber:"(\d+)"')
        if next_page:
            next_page = int(next_page[0])
        else:
            return
        url = re.sub('pageNumber=\d+', 'pageNumber={}'.format(next_page), response.url)

    def _start_requests(self, response):
        """Generate Requests from the SEARCH_URL and the search terms."""
        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=urllib.quote_plus(st.encode('utf-8'),),
                    page=1,
                    store_id=self.store_id
                ),
                meta={'search_term': st, 'remaining': self.quantity},
            )

        if self.product_url:
            yield self.parse_product(response)

    def extract_product_json(self, response):
        product_json = {"id_json": {}, "event_data": {}, "style_data": {}}

        try:
            id_json = response.xpath("//script[@type='application/ld+json']/text()").extract()[0].strip()
            product_json["id_json"] = json.loads(id_json)
        except Exception as e:
            self.log("Parsing issue in id_json.", DEBUG)

        try:
            event_data = re.findall(r'window.eventData =(.+);\n\twindow.styleData =', response.body_as_unicode())[0]
            product_json["event_data"] = json.loads(event_data)
        except Exception as e:
            self.log("Parsing issue in even_data.", DEBUG)

        try:
            style_data = re.findall(r'window.styleData =(.+);\n', response.body_as_unicode())[0]
            product_json["style_data"] = json.loads(style_data)
        except Exception as e:
            self.log("Parsing issue in style_data.", DEBUG)

        return product_json

    def parse_product(self, response):
        product = response.meta['product']

        # locale
        product['locale'] = 'en_US'

        product_json = self.extract_product_json(response)

        # title
        title = product_json["id_json"]["name"]
        cond_set_value(product, 'title', title)

        # categories
        categories = [category_info["value"] for category_info in product_json["style_data"]["categories"]]

        if categories:
            cond_set_value(product, 'categories', categories)

        if product.get('categories'):
            product['category'] = product['categories'][-1]

        # description
        description = product_json["style_data"]["descriptionHtml"]
        cond_set_value(product, 'description', description)

        # price
        price = product_json["style_data"]["price"]
        cond_set_value(product, 'price', price)

        # variants

        return product

        # variants
        variants = set(response.xpath(self.XPATH['product']['variants']).extract())

        if len(variants) > 1:
            product['variants'] = []
            response.meta['product'] = product
            variant_sku = variants.pop()
            response.meta['variants'] = variants
            return Request(
                response.url.split('?')[0].split(';')[0] + '?var_id=' + variant_sku,
                meta=response.meta,
                callback=self._parse_variants,
                # dont_filter=True
            )
        else:
            product['variants'] = [self._parse_variant_data(response)]
            return product

    def _parse_variants(self, response):
        response.meta['product']['variants'].append(
            self._parse_variant_data(response)
        )
        if response.meta.get('variants'):
            variant_sku = response.meta['variants'].pop()
            return Request(
                response.url.split('?')[0] + '?var_id=' + variant_sku,
                meta=response.meta,
                callback=self._parse_variants,
                # dont_filter=True
            )
        else:
            return response.meta['product']

    def _parse_variant_data(self, response):
        data = {}
        # id
        id = response.xpath(self.XPATH['product']['id']).extract()
        _populate(data, 'id', id, first=True)

        # sku
        sku = response.xpath(self.XPATH['product']['sku']).extract()
        _populate(data, 'sku', sku, first=True)

        # image url
        if data.get('sku'):
            image_url = [self.IMAGE_URL.format(sku=data['sku'])]
        else:
            image_url = [""]
        _populate(data, 'image_url', image_url, first=True)

        # in stock?
        stock = response.xpath(self.XPATH['product']['out_of_stock_button']).extract()
        data['is_out_of_stock'] = True
        if stock:
            if re.search('in stock', stock[0], re.IGNORECASE):
                data['is_out_of_stock'] = False
            else:
                data['is_out_of_stock'] = True

        if data['is_out_of_stock']:
            data['available_online'] = False
            data['available_store'] = False
        else:
            available_online = re.search('this item is not available for in-store pickup', response.body_as_unicode(), re.IGNORECASE)
            available_store = re.search('your items will be available', response.body_as_unicode(), re.IGNORECASE)
            data['available_online'] = False
            data['available_store'] = False
            data['is_in_store_only'] = False
            if available_store:
                data['is_in_store_only'] = True
                data['available_online'] = False
                data['available_store'] = True
            elif available_online:
                data['available_online'] = True
                data['available_store'] = False
                data['is_in_store_only'] = False

        # currency
        currency = response.xpath(self.XPATH['product']['currency']).extract()
        _populate(data, 'currency', currency, first=True)

        # price
        price = response.xpath(self.XPATH['product']['price']).extract()
        if price:
            price = price[0].strip(currency[0])
            data['price'] = float(price)

        # size
        size = response.xpath(self.XPATH['product']['size']).extract()
        _populate(data, 'size', size)

        # color
        color = response.xpath(self.XPATH['product']['color']).extract()
        _populate(data, 'color', color)

        return data

    def _total_matches_from_html(self, response):
        total_matches = response.xpath(self.XPATH['search']['total_matches']).re(r'\d+')
        if total_matches:
            return int(total_matches[0])

    def _scrape_next_results_page_link(self, response):
        next_page = response.xpath(self.XPATH['search']['next_page']).extract()
        if next_page:
            return next_page[0]

    def _scrape_product_links(self, response):
        for link in response.xpath(self.XPATH['search']['prod_links']).extract():
            yield link.split('?')[0].split(';')[0], SiteProductItem()
