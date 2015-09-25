# -*- coding: utf-8 -*-#

import re
import hjson
from ..items import SiteProductItem
from scrapy.http import FormRequest, Request
from scrapy.log import ERROR, INFO, WARNING
from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set_value
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi

is_empty = lambda x, y=None: x[0] if x else y


class HagelshopProductSpider(BaseProductsSpider):

    name = 'hagelshop_products'
    allowed_domains = ["www.hagel-shop.de"]
    pages = 0
    SEARCH_URL = "http://www.hagel-shop.de/catalogsearch/result/?q={search_term}"

    def __init__(self, *args, **kwargs):
        super(HagelshopProductSpider, self).__init__(
            site_name=self.allowed_domains[0],
            *args, **kwargs)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        # Parse image_url
        image = self.parse_image_url(response)
        cond_set_value(product, 'image_url', image)

        # Parse description
        description = self.parse_description(response)
        cond_set_value(product, 'description', description)

        # Parse price
        price = self.parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse category

        # Parse title
        title = self.parse_title(response)
        cond_set_value(product, 'title', title)

        # Parse related products

        # Parse buyer reviews

        # Parse upc
        sku = self.parse_upc(response)
        cond_set_value(product, 'sku', sku)

        # Parse out_of_stock
        in_stock = self.parse_stock(response)
        cond_set_value(product, 'is_out_of_stock', in_stock)

        # Parse brand
        brand = self.parse_brand(response)
        cond_set_value(product, 'brand', brand)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def parse_upc(self, response):
        sku = is_empty(response.xpath(
            '//span[@itemprop="sku"]/text()').extract())

        return sku

    def parse_stock(self, response):
        stock = is_empty(
            response.xpath(
                '//link[@itemprop="availability"]/@href').extract())

        if stock == 'http://schema.org/OutOfStock':
            in_stock = True
        else:
            in_stock = False

        return in_stock

    def parse_brand(self, response):
        brand = is_empty(response.xpath(''
                                        '//span[@class="prod-brand"]/'
                                        'img[@itemprop="logo"]/@alt').extract())

        return brand

    def parse_title(self, response):
        title = is_empty(response.xpath(
            '//div[@class="page-title product-name"]/'
            'h1[@itemprop="name"]/text()').extract())

        return title

    def parse_description(self, response):
        description = is_empty(
            response.xpath('//div[@class="shortDescription"]').extract())

        return description

    def parse_price(self, response):
        meta = response.meta.copy()
        product = meta['product']
        price_sel = response.xpath('//span[@itemprop="price"]/'
                                   'span[@class="price"]/text() | '
                                   '//p[@class="special-price"]/'
                                   'span[@itemprop="price"]/text()')
        if price_sel:
            price = is_empty(
                price_sel.extract()
            ).strip()
            price = is_empty(
                re.findall(r'\d+,\d+', price))
            price = price.replace(',', '.')
            product['price'] = Price(
                priceCurrency="EUR",
                price=price
            )
            return 'price'

        else:
            product['price'] = Price(
                priceCurrency="EUR",
                price=float(0)
            )

    def parse_image_url(self, response):
        image = is_empty(response.xpath(
            '//p[@class="product-image product-image-zoom"]/'
            'img[@itemprop="image"]/@src').extract())

        if image:
            image = image.replace('//', '')

        return image

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
        try:
            total_matches = is_empty(response.xpath(
                '//ul[@class="nav nav-list"]/li/'
                'a/span/text()').extract())

            total_matches = re.findall(r'(\d+)', total_matches)
            return int(total_matches[0])
        except:
            return 0

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """

        return self.per_page


    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """

        items = response.xpath(
            '//a[contains(@class, "product-image")]')
        self.per_page = len(items)
        if items:
            for item in items:
                link = is_empty(
                    item.xpath('@href').extract()
                )
                res_item = SiteProductItem()

                yield link, res_item
        else:
            self.log("Found no product links in {url}".format(url=response.url), INFO)

    def _scrape_next_results_page_link(self, response):
        url = is_empty(
            response.xpath('//div[@class="toolbar-bottom"]/div/div/ul/li/'
                           'a[contains(@class, "next i-next")]/@href').extract()
            )
        if url:
            self.pages += 1
            return url
        else:
            self.log(
                "No Next page", ERROR
            )
