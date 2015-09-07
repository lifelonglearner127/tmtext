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

    SEARCH_URL = "http://www.debenhams.com/webapp/wcs/stores/servlet/" \
                 "Navigate?langId=-1&storeId=10701&catalogId=10001&txt={search_term}"

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

        # Parse category
        category = self._parse_category(response)
        cond_set_value(product, 'category', category)

        # Parse price
        price = self._parse_price(response)
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
            return self.send_next_request(reqs, response)

        return product

    def _parse_title(self, response):
        title = is_empty(
            response.xpath('//meta[@property="og:title"]/@content').extract()
        )

        return title

    def _parse_brand(self, response):
        brand = is_empty(
            response.xpath('//meta[@property="brand"]/@content').extract()
        )

        return brand

    def _parse_department(self, response):
        department = is_empty(
            response.xpath('//meta[@property="department"]/@content').extract()
        )

        return department

    def _parse_category(self, response):
        category = is_empty(
            response.xpath('//meta[@property="category"]/@content').extract(),
            ''
        )
        subcategory = is_empty(
            response.xpath('//meta[@property="subcategory"]/@content').extract(),
            ''
        )

        if subcategory and category:
            return [category, subcategory]

        return category

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
        if price:
            price = is_empty(
                re.findall(
                    r'(\d+\.\d+)',
                    price
                ), 0.00
            )

        return Price(
            price=float(price),
            priceCurrency=currency
        )

    def _parse_special_pricing(self, response):
        special_pricing = is_empty(
            response.xpath('//span[@class="price-was"]').extract(),
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
            response.xpath('//div[@id="item-description-block"]').extract()
        )

        return description

    def _parse_stock_status(self, response):
        stock_status = is_empty(
            response.xpath('//meta[@name="twitter:data2"]'
                           '/@content').extract()
        )

        if stock_status.lower() is 'in stock':
            stock_status = True
        else:
            stock_status = False

        return stock_status

    def _parse_upc(self, response):
        upc = is_empty(
            response.xpath('//meta[@property="product_number"]'
                           '/@content').extract()
        )

        if upc:
            upc = is_empty(
                re.findall(
                    r'(\d{12})+',
                    upc
                )
            )

        return upc

    def _parse_variants(self, response):
        meta = response.meta.copy()
        product = meta['product']

        variants = []
        data = is_empty(re.findall(
            r'<div id="entitledItem_\w+" class="hidediv">(\[(.|\n)*?\])',
            response.body_as_unicode()
        ))

        if data:
            data = list(data)[0]

            try:
                variants_data = json.loads(data.replace('\'', '"'))
            except ValueError as exc:
                self.log(
                    'Unable to parse variants from {url}: {exc}'.format(
                        exc=exc,
                        url=response.url
                    ), ERROR
                )
                return []

            for var_data in variants_data:
                properties = {}

                for attr, value in var_data['Attributes'].iteritems():
                    attr = attr.lower().split('_')
                    properties[attr[0]] = attr[1]

                price = is_empty(
                    re.findall(
                        r'(\d+\.\d+)',
                        var_data.get('offer_price', 0.00)
                    ), product['price'].price.__float__()
                )

                status = var_data.get('inventory_status', 'unavailable')
                stock = status.lower() == 'unavailable'

                image_url = 'http://debenhams.scene7.com/is/image/Debenhams/' \
                            '{upc}_{id}'.format(
                                upc=product['upc'],
                                id=var_data['part_number']
                            )

                variant = {
                    'properties': properties,
                    'price': float(price),
                    'is_out_of_stock': stock,
                    'image_url': image_url
                }

                variants.append(variant)
        else:
            return []

        return variants

    def _parse_related_products(self, response):
        related_products = []
        data = is_empty(re.findall(
            r'<div name="upSell_entitledItems_\w+" id="upSell_entitledItems_\w+"'
            r' class="hidediv">(\[(.|\n)*?\])</div>',
            response.body_as_unicode()
        ))

        if data:
            data = list(data)[0]

            try:
                data = json.loads(data)
            except ValueError as exc:
                self.log(
                    'Unable to parse related products from {url}: {exc}'.format(
                        exc=exc,
                        url=response.url
                    ), ERROR
                )
                return

            for rel_prod in data:
                url = rel_prod.get('pdpUrl')
                if url:
                    url = 'www.{domain}{url}'.format(
                        domain=self.allowed_domains[0],
                        url=url
                    )

                title = rel_prod.get('description')

                if title and url:
                    related_products.append(
                        RelatedProduct(
                            url=url,
                            title=title
                        )
                    )
        else:
            return
        return related_products

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
            response.xpath(
                '//*[@id="products_found"]/span/text()'
            ).extract(), 0
        )
        total_matches = is_empty(
            re.findall(
                r'(\d+) products found',
                total_matches
            )
        )

        if total_matches:
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

        items = response.xpath(
            '//div[@id="productDisplay"]/./'
            '/tr[@class="item_container"]'
            '/td[contains(@class, "item")]'
        )

        if items:
            for item in items:
                link = is_empty(
                    item.xpath('././/input[@id="productTileImageUrl"]'
                               '/@value').extract()
                )
                res_item = SiteProductItem()
                yield link, res_item
        else:
            self.log("Found no product links in {url}".format(url=response.url), INFO)

    def _scrape_next_results_page_link(self, response):
        url = is_empty(
            response.xpath(
                '//a[text()="Next"]/@href'
            ).extract()
        )

        if url:
            return url
        else:
            self.log("Found no 'next page' links", WARNING)
            return None
