# -*- coding: utf-8 -*-#

import json
import re
import string
import itertools
import urllib

from scrapy.http import FormRequest, Request
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set_value
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi

is_empty = lambda x, y=None: x[0] if x else y


class DebenhamsProductSpider(BaseProductsSpider):

    name = 'debenhams_products'
    allowed_domains = ["debenhams.com"]

    #SEARCH_URL = "http://www.debenhams.com/webapp/wcs/stores/servlet/" \
    #             "Navigate?langId=-1&storeId=10701&catalogId=10001&txt={search_term}"

    # SEARCH_URL = "http://int.debenhams.com/us/search/{search_term}/"

    SEARCH_URL = 'http://www.debenhams.com/search/{search_term}'

    items_per_page = 60

    BUYER_REVIEWS_URL = 'http://debenhams.ugc.bazaarvoice.com/9364redes-en_gb/{upc}/' \
                        'reviews.djs?format=embeddedhtml'

    def __init__(self, *args, **kwargs):
        self.br = BuyerReviewsBazaarApi(called_class=self)

        super(DebenhamsProductSpider, self).__init__(*args, **kwargs)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        # Set locale
        product['locale'] = 'en_GB'

        # Parse title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title, conv=string.strip)

        # Parse brand
        brand = self._parse_brand(response)
        cond_set_value(product, 'brand', brand)

        # Parse department
        department = self._parse_department(response)
        cond_set_value(product, 'department', department)

        # Parse categories
        categories = self._parse_categories(response)
        cond_set_value(product, 'categories', categories)

        # Parse price
        price, currency = self._parse_price(response)
        price = Price(price=float(price), priceCurrency=currency)
        cond_set_value(product, 'price', price)

        # Parse special pricing
        special_pricing = self._parse_special_pricing(response)
        cond_set_value(product, 'special_pricing', special_pricing, conv=bool)

        # Parse image url
        image_url = self._parse_image_url(response)
        cond_set_value(product, 'image_url', image_url, conv=string.strip)

        # Parse description
        description = self._parse_description(response)
        cond_set_value(product, 'description', description, conv=string.strip)

        # Parse stock status
        is_out_of_stock = self._parse_stock_status(response)
        cond_set_value(product, 'is_out_of_stock', is_out_of_stock)

        # Parse upc
        upc = self._parse_upc(response)
        cond_set_value(product, 'upc', upc)

        # Parse variants
        variants = self._parse_variants(response)
        cond_set_value(product, 'variants', variants)

        # Parse buyer reviews
        reqs.append(
            Request(
                url=self.BUYER_REVIEWS_URL.format(upc=upc),
                dont_filter=True,
                callback=self.br.parse_buyer_reviews
            )
        )

        # Parse related products
        related_products = self._parse_related_products(response)
        cond_set_value(product, 'related_products', related_products)

        if reqs:
            yield self.send_next_request(reqs, response)

        yield product

    def _parse_title(self, response):
        title = is_empty(
            response.xpath('//meta[@property="og:title"]/@content').extract()
        )

        return title

    def _parse_brand(self, response):
        brand = is_empty(
            response.xpath('//img[@class="brand"]/@alt').extract()
        )

        return brand

    def _parse_department(self, response):
        # field is not present in the new design
        department = is_empty(
            response.xpath('//meta[@property="department"]/@content').extract()
        )

        return department

    def _parse_categories(self, response):
        categories = []
        categories_sel = response.xpath(
                '//div[@class="breadcrumb"]/ol/li//text()').extract()
        for cat in categories_sel:
            categories.append(cat.strip())
        return categories

    def _parse_price(self, response):
        currency = is_empty(
            response.xpath('//span[@itemprop="priceCurrency"]'
                           '/@content').extract(),
            'GBP'
        )
        price = is_empty(
            response.xpath('//span[@itemprop="price"]'
                           '/text() |'
                           '//span[@itemprop="lowPrice"]'
                           '/text()').extract()
        )
        if not price:
            # discount (sales) price
            price = response.xpath(
                '//*[contains(@class, "attributes")]//*[contains(@class, "price")]'
                '//*[contains(@class, "attr-price-now")]'
                '//*[contains(@class, "amount")]/text()').extract()
            if price:
                price = price[0]
                if not price.strip():
                    price = None
                if price:
                    currency = response.xpath(
                        '//*[contains(@class, "attributes")]//*[contains(@class, "price")]'
                        '//*[contains(@class, "attr-price-now")]'
                        '//*[contains(@class, "amount")]/span/@title').extract()[0]
        if not price:
            # normal price
            price = response.xpath(
                '//*[contains(@class, "attributes")]//*[contains(@class, "price")]'
                '//*[contains(@class, "amount")]/text()').extract()
            if price:
                price = price[0]
                currency = response.xpath(
                    '//*[contains(@class, "attributes")]//*[contains(@class, "price")]'
                    '//*[contains(@class, "amount")]/span/@title').extract()[0]
        if price:
            price = is_empty(
                re.findall(
                    r'(\d+\.\d+)',
                    price
                ), 0.00
            )
        return price, currency

    def _parse_special_pricing(self, response):
        special_pricing = is_empty(
            response.xpath('//li[@class="first-child attr-price-was"]/span[2]').extract(),
            False
        )

        return special_pricing

    def _parse_image_url(self, response):
        image_url = is_empty(
            response.xpath('//meta[@property="og:image"]/@content').extract()
        )

        return image_url

    def _parse_description(self, response):
        description = is_empty(
            response.xpath('//h3[@class="description"]/text()').extract()
        )

        return description

    def _parse_stock_status(self, response):
        stock_status = is_empty(
            response.xpath('//meta[@name="twitter:data2"]/@content').extract()
        )

        if stock_status and 'In stock' in stock_status[0]:
            stock_status = False
        else:
            stock_status = True

        return stock_status

    def _parse_upc(self, response):
        upc = is_empty(
            response.xpath('//span[@class="product-code"]/text()').extract()
        )

        if upc:
            return upc

        return None

    def _parse_variants(self, response):
        meta = response.meta.copy()
        product = meta['product']

        variants = []
        variant_drop_down = response.xpath('//div[@class="product-size '
                                           'drop-down"]').extract()
        if variant_drop_down:
            stock_status = response.xpath('//div[@class="attributes"]'
                                          '//div[@class="product-size '
                                          'drop-down"]/select/'
                                          'option[position() > 1]/'
                                          '@data-item-stock').extract()
            sizes = response.xpath('//div[@class="attributes"]'
                                   '//div[@class="product-size drop-down"]'
                                   '/select/option[position() > 1]'
                                   '/@data-item-size').extract()
            price = None

        else:
            sizes = response.xpath('//ul[@class="size"]/li/label/span'
                                  '/text()').extract()
            stock_status = response.xpath('//ul[@class="size"]/li/label'
                                          '/@title').extract()
            price, currency = self._parse_price(response)
            price = float(price)

        for index, size in enumerate(sizes):
            properties = {}
            variant = {}

            properties['size'] = size
            variant['is_out_of_stock'] = True if 'Out of stock' in \
                                                  stock_status[index] else False

            variant['price'] = price if price else None
            variant['properties'] = properties

            variants.append(variant)

        return variants

    def _parse_related_products(self, response):
        related_products = []
        title = response.xpath('//div[@class="product-cross-sells '
                               'tab-container"]//ul[@class="jcarousel-skin-1"]'
                               '/li/div[1]/h2/a/text()').extract()
        url = response.xpath('//div[@class="product-cross-sells '
                             'tab-container"]//ul[@class="jcarousel-skin-1"]'
                             '/li/div[1]/h2/a/@href').extract()

        if title and url:
            for index, title in enumerate(title):
                related_products.append(
                    RelatedProduct(
                        url=url[index],
                        title=title
                    )
                )
            return related_products

        if related_products:
            return related_products
        else:
            return None

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """

        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _scrape_total_matches(self, response):
        """
        Scraping number of resulted product links
        """
        total_matches = is_empty(
            response.xpath('//span[@class="products_count"]'
                           '/text()').re('\d.\d+'), 0)

        if total_matches:
            total_matches = total_matches.replace(',', '')
            return int(total_matches)
        else:
            return 0

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """
        return self.items_per_page

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """
        links = response.xpath('//div[contains(@class, "item_container")]//'
                               'input/@value').extract()
        if links:
            for link in links:
                yield link, SiteProductItem()
        else:
            self.log("Found no product links in {url}".format(
                url=response.url), INFO)

    def _scrape_next_results_page_link(self, response):
        url = response.xpath('//div[@class="product_nav"]//'
                             'a[contains(text(), "Next")]/@href').extract()
        if url:
            return url[0]
        else:
            self.log("Found no 'next page' links", WARNING)
            return None
