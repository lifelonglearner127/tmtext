# -*- coding: utf-8 -*-#

import json
import re
import string

from scrapy.http import FormRequest, Request
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set_value

is_empty = lambda x, y=None: x[0] if x else y


class WayfairProductSpider(BaseProductsSpider):

    name = 'wayfair_products'
    allowed_domains = ["wayfair.com"]

    SEARCH_URL = "http://www.wayfair.com/keyword.php?keyword={search_term}"

    def __init__(self, *args, **kwargs):
        super(WayfairProductSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        # Parse title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title, conv=string.strip)

        # Parse brand
        brand = self._parse_brand(response)
        cond_set_value(product, 'brand', brand, conv=string.strip)

        # Parse price
        price = self._parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse special pricing
        special_pricing = self._parse_special_pricing(response)
        cond_set_value(product, 'special_pricing', special_pricing, conv=bool)

        # Parse image link
        image_url = self._parse_image_url(response)
        cond_set_value(product, 'image_url', image_url)

        # Parse description
        description = self._parse_description(response)
        cond_set_value(product, 'description', description)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_title(self, response):
        """
        Parse product title
        """
        title = is_empty(
            response.xpath('//*[@class="title_name"]/text()').extract()
        )

        return title

    def _parse_brand(self, response):
        """
        Parse product brand
        """
        brand = is_empty(
            response.xpath('//*[@class="manu_name"]/a/text()').extract()
        )

        return brand

    def _parse_special_pricing(self, response):
        """
        Parse product special price
        """
        special_pricing = is_empty(
            response.xpath('//*[contains(@class, "listprice")]').extract()
        )

        return special_pricing

    def _parse_image_url(self, response):
        """
        Parse product image link
        """
        image_url = is_empty(
            response.xpath('//*[@id="zoomimg"]/.//*[contains(@class, "pdp_main_carousel_container")]/./'
                           '/a/img/@src').extract()
        )

        return image_url

    def _parse_description(self, response):
        """
        Parse product description
        """
        description = is_empty(
            response.xpath('//*[@id="information"]/div').extract()
        )

        return description

    def _parse_price(self, response):
        """
        Parse product price
        """
        price = is_empty(
            response.xpath('//span[contains(@class, "product_price")]')
        )

        if price:
            usd = is_empty(
                price.xpath('./text()').extract(), ''
            )
            coins = is_empty(
                price.xpath('.//sup/text()').extract(), ''
            )

            if usd:
                usd = usd.strip().replace('$', '')

                if coins:
                    coins = coins.strip()
                    price = usd + coins
                else:
                    price = usd + '00'
            else:
                price = '0.00'
        else:
            self.log('No price in {0}'. format(response.url), WARNING)
            price = '0.00'

        return Price(price=price, priceCurrency='USD')

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
            response.xpath("//span[@class='viewingItems']/text()").extract(),
        )

        if total_matches:
            total_matches = total_matches.replace(',', '')
            return int(total_matches)
        else:
            self.log(
                "Failed to get total matches", WARNING
            )
            return 0

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """
        num = is_empty(
            response.xpath("//span[@class='js-product-range-end']/text()").extract()
        )

        if not num:
            self.log(
                "Failed to get number of results", WARNING
            )
            return 0

        return int(num)

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """

        items = response.xpath(
            '//div[@id="sbprodgrid"]/.//a'
        )

        if items:
            for item in items:
                link = is_empty(
                    item.xpath('.//@href').extract()
                )
                res_item = SiteProductItem()
                yield link, res_item
        else:
            self.log("Found no product links in {url}".format(response.url), INFO)

    def _scrape_next_results_page_link(self, response):
        url = response.xpath(
            '//a[contains(@class, "pages_prev_next")]/@href'
        ).extract()

        if len(url) == 1:
            return url[0]
        elif len(url) == 0:
            self.log("Found no 'next page' links", WARNING)
            return None
        else:
            return url[1]
