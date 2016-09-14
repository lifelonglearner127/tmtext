"""This is a base shoprite scraper module"""
# -*- coding: utf-8 -*-
import re
import json
from scrapy import Request
from product_ranking.items import SiteProductItem, BuyerReviews, Price
from product_ranking.spiders import BaseProductsSpider, cond_set_value, FLOATING_POINT_RGEX


class ShopriteProductsSpider(BaseProductsSpider):
    name = "shoprite_products"
    allowed_domains = ["shoprite.com"]

    PRODUCT_URL = "https://shop.shoprite.com/api/product/v5/product/store/{store}/sku/{sku}"
    SCREEN_URL = "https://shop.shoprite.com/store/{store}/browser/screen?width=1920&height=1080"
    def __init__(self, *args, **kwargs):
        """Initiate input variables and etc."""
        super(ShopriteProductsSpider, self).__init__(*args, **kwargs)

    @staticmethod
    def _scrape_total_matches(response):
        pass

    @staticmethod
    def _scrape_product_links(response):
        pass

    @staticmethod
    def _scrape_next_results_page_link(response):
        pass

    @staticmethod
    def _scrape_results_per_page(response):
        pass

    @staticmethod
    def _parse_title(product_info):
        return product_info.get('Name')

    @staticmethod
    def _parse_price(product_info):
        price_raw = product_info.get('CurrentPrice')
        price = re.findall(FLOATING_POINT_RGEX, price_raw)
        currency = 'USD'
        if price:
            return Price(price=price[0], priceCurrency=currency)
        else:
            None

    @staticmethod
    def _parse_description(product_info):
        return product_info.get('Description')

    @staticmethod
    def _parse_image_url(response):
        pass

    @staticmethod
    def _parse_categories(response):
        pass

    @staticmethod
    def _parse_category(product_info):
        return product_info.get('Category')

    @staticmethod
    def _parse_categories_full_info(categories_names, categories_links):
        pass

    @staticmethod
    def _parse_categories_links(response):
        pass

    @staticmethod
    def _parse_brand(product_info):
        return product_info.get('Brand')

    @staticmethod
    def _parse_store(url):
        store = re.findall(r'\/store\/(\d+)\#', url)
        return store[0] if store else None

    @staticmethod
    def _parse_sku_url(url):
        sku = re.findall(r'\#\/product\/sku\/(\d+)', url)
        return sku[0] if sku else None

    @staticmethod
    def _parse_info(response):
        token = response.xpath(
            '//script[contains(text(), "var configuration =")]/text()'
        ).re(r'var configuration = (\{.+?\});')
        return json.loads(token[0]) if token else {}

    @staticmethod
    def _parse_token(configuration):
        return configuration.get('Token')

    @staticmethod
    def _parse_entry_url(configuration):
        return configuration.get('EntryUrl')

    @staticmethod
    def _parse_sku(product_info):
        return product_info.get('Sku')

    @staticmethod
    def _parse_is_out_of_stock(product_info):
        return not product_info.get('InStock')

    @staticmethod
    def _parse_no_longer_available(product_info):
        return not product_info.get('IsAvailable')

    def _parse_single_product(self, response):
        """Same to parse_product."""
        meta = response.meta
        url = meta.get('product').get('url')
        meta['store'] = self._parse_store(url)
        meta['sku'] = self._parse_sku_url(url)
        configuration = self._parse_info(response)
        meta['token'] = self._parse_token(configuration)
        meta['entry_url'] = self._parse_entry_url(configuration)
        headers = {}
        headers['Authorization'] = meta['token']
        headers['Referer'] = response.url
        headers['Accept'] = 'application/vnd.mywebgrocer.shop-entry+json'
        return Request(self.PRODUCT_URL.format(store=meta['store'], sku=meta['sku']),
                       headers=headers,
                       callback=self.parse_product,
                       meta=meta)

    def parse_product(self, response):
        """Handles parsing of a product page."""
        product = response.meta['product']
        # Set locale
        product['locale'] = 'en_US'

        # Parse json
        product_info = json.loads(response.body)

        # Parse title
        title = self._parse_title(product_info)
        cond_set_value(product, 'title', title)

        # Parse brand
        brand = self._parse_brand(product_info)
        cond_set_value(product, 'brand', brand)

        # Parse sku
        sku = self._parse_sku(product_info)
        cond_set_value(product, 'sku', sku)

        # Parse description
        description = self._parse_description(product_info)
        cond_set_value(product, 'description', description)

        # Parse is_out_of_stock
        is_out_of_stock = self._parse_is_out_of_stock(product_info)
        cond_set_value(product, 'is_out_of_stock', is_out_of_stock)

        # Parse no_longer_available
        no_longer_available = self._parse_no_longer_available(product_info)
        cond_set_value(product, 'no_longer_available', no_longer_available)

        # Parse category
        category = self._parse_category(product_info)
        cond_set_value(product, 'category', category)

        # Parse price
        price = self._parse_price(product_info)
        cond_set_value(product, 'price', price)


        return product

