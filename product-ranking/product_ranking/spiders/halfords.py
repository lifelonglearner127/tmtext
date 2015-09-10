# -*- coding: utf-8 -*-#

import hjson
import re
import string

from scrapy.http import Request
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set_value
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi

is_empty = lambda x, y=None: x[0] if x else y


class HalfordsProductSpider(BaseProductsSpider):

    name = 'halfords_products'
    allowed_domains = [
        "halfords.com",
        "halfords.ugc.bazaarvoice.com"
    ]

    SEARCH_URL = "http://www.halfords.com/webapp/wcs/stores/servlet/SearchCmd?storeId=10001" \
                 "&catalogId=10151&langId=-1&srch={search_term}&categoryId=-1&action=listrefine&" \
                 "tabNo=1&qcon=fh_location=%2F%2Fcatalog_10151%2Fen_GB%2F%24s%3Dblah%3Bt%3Ddefault" \
                 "%2Fattr_78cdb44b%3D1&channel=desktop&sort={sort}"
    BUYER_REVIEWS_URL = "http://halfords.ugc.bazaarvoice.com/4028-redes/{product_id}/" \
                        "reviews.djs?format=embeddedhtml"

    _SORT_MODES = {
        'price asc': 'price-low-to-high',
        'price desc': 'price-high-to-low',
        'best seller': 'best-seller',
        'star rating': 'star-rating',
        'recommended': 'we-recommend'
    }

    def __init__(self, search_sort='recommended', *args, **kwargs):
        self.br = BuyerReviewsBazaarApi(called_class=self)

        super(HalfordsProductSpider, self).__init__(
            site_name=self.allowed_domains[0],
            url_formatter=FormatterWithDefaults(
                sort=self._SORT_MODES[search_sort]
            ),
            *args, **kwargs)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        # Set locale
        product['locale'] = 'en_GB'

        # Set product id
        product_id = is_empty(
            response.xpath(
                '//input[@name="catCode"]/@value'
            ).extract(), '0'
        )
        response.meta['product_id'] = product_id

        # Set title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title, conv=string.strip)

        # Set price
        price = self._parse_price(response)
        cond_set_value(product, 'price', price)

        # Set special pricing
        special_pricing = self._parse_special_pricing(response)
        cond_set_value(product, 'special_pricing', special_pricing, conv=bool)

        # Set image url
        image_url = self._parse_image_url(response)
        cond_set_value(product, 'image_url', image_url)

        # Set categories
        category = self._parse_category(response)
        cond_set_value(product, 'category', category)
        if category:
            # Set department
            department = category[-1]
            cond_set_value(product, 'department', department)

        # Set variants
        variants = self._parse_variants(response)
        cond_set_value(product, 'variants', variants)

        #  Set stock status
        is_out_of_stock = self._parse_stock_status(response)
        cond_set_value(product, 'is_out_of_stock', is_out_of_stock, conv=bool)

        #  Set description
        description = self._parse_description(response)
        cond_set_value(product, 'description', description)

        #  Parse related products
        related_products = self._parse_related_products(response)
        cond_set_value(product, 'related_products', related_products)

        # Parse buyer reviews
        reqs.append(
            Request(
                url=self.BUYER_REVIEWS_URL.format(product_id=product_id),
                dont_filter=True,
                callback=self.br.parse_buyer_reviews
            )
        )

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_title(self, response):
        title = is_empty(
            response.xpath(
                '//h1[@class="productDisplayTitle"]/text()'
            ).extract()
        )

        return title

    def _parse_price(self, response):
        price = is_empty(
            response.xpath(
                '//div[@id="priceAndLogo"]/h2/text()'
            ).extract(), 0.00
        )
        if price:
            price = price.strip().replace(u'£', '')

        return Price(
            price=price,
            priceCurrency='GBP'
        )

    def _parse_special_pricing(self, response):
        special_pricing = is_empty(
            response.xpath(
                '//div[@class="saveWasPricing"]/./'
                '/span[@class="wasValue"]'
            ).extract(), False
        )

        return special_pricing

    def _parse_image_url(self, response):
        image_url = is_empty(
            response.xpath(
                '//*[@id="tempImage"]/@src'
            ).extract()
        )

        return image_url

    def _parse_category(self, response):
        category = response.xpath(
            '//*[@id="breadcrumb"]/.//li/a/text()'
        ).extract()

        if category:
            category = category[1:]

        return category

    def _parse_stock_status(self, response):
        is_out_of_stock = is_empty(
            response.xpath(
                '//*[@id="productBuyable"][@class="hidden"]'
            ).extract(), False
        )

        return is_out_of_stock

    def _parse_description(self, response):
        description = is_empty(
            response.xpath(
                '//*[@id="productFeatures"]/li'
            ).extract()
        )

        return description

    def _parse_related_products(self, response):
        related_products = []
        data = response.xpath(
            '//*[@id="PDPCrossSellContent"]/li'
        )

        if data:
            for item in data:
                title = is_empty(
                    item.xpath(
                        '././/span[@class="productTitle"]/./'
                        '/a[@class="productTitleLink"]/text()'
                    ).extract()
                )
                url = is_empty(
                    item.xpath(
                        '././/span[@class="productTitle"]/./'
                        '/a[@class="productTitleLink"]/@href'
                    ).extract()
                )

                if url and title:
                    related_products.append(
                        RelatedProduct(
                            url=url,
                            title=title.strip()
                        )
                    )

        return related_products

    def _parse_variants(self, response):
        meta = response.meta.copy()
        product = meta['product']

        number_of_variants = is_empty(
            re.findall(
                r'var ItemVariantSelectionWidget\s?=\s?\{(?:.|\n)+'
                r'numberOfVariants:\s+(\d+),',
                response.body_as_unicode()
            )
        )

        if number_of_variants:
            data = is_empty(
                re.findall(
                    r'(ItemVariantSelectionWidget\s?=\s?\{(?:.|\n)+?\};)',
                    response.body_as_unicode()
                )
            )

            name = is_empty(
                re.findall(
                    r'ItemVariantSelectionWidget\s?=\s?\{(?:.|\n)+variant1:\s+\{'
                    r'(?:.|\n)+name:\s+\'(.+)?\',',
                    data
                )
            )

            if name:
                name = name.replace('-', ' ').lower()

                variants_data = is_empty(
                    re.findall(
                        r'ItemVariantSelectionWidget\s?=\s?\{(?:.|\n)+multiVariantArray'
                        r':\s+(\[(?:.|\n)+?\]),',
                        data
                    )
                )
                try:
                    variants_data = hjson.loads(variants_data, object_pairs_hook=dict)
                except ValueError as exc:
                    self.log('Unable to parse variants on {url}: {exc}'.format(
                        url=response.url,
                        exc=exc
                    ), ERROR)
                    return []

                variants = []
                for item in variants_data:
                    stock = item['inStock']
                    properties = {
                        name: item['value1']
                    }
                    variants.append({
                        'in_stock': stock,
                        'price': product['price'].price.__float__(),
                        'properties': properties
                    })

                return variants

        return []

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
                '//*[@id="resultsTabs"]/.//a[@data-tabname="products"]'
                '/span/text()'
            ).extract(), '0'
        )

        return int(total_matches)

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """
        num = is_empty(
            response.xpath(
                '//*[@id="pgSize"]/option[@selected="selected"]'
                '/@value'
            ).extract(), '0'
        )

        return int(num)

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """

        items = response.xpath(
            '//ul[@id="product-listing"]/li'
        )

        if items:
            for item in items:
                link = is_empty(
                    item.xpath('././/span[@class="productTitle"]/a/@href').extract()
                )
                res_item = SiteProductItem()
                yield link, res_item
        else:
            self.log("Found no product links in {url}".format(url=response.url), INFO)

    def _scrape_next_results_page_link(self, response):
        url = is_empty(
            response.xpath(
                '//section[@class="pagination"]/./'
                '/a[contains(@class,"next")]/@href'
            ).extract()
        )

        if url:
            return url
        else:
            self.log("Found no 'next page' links", WARNING)
            return None
