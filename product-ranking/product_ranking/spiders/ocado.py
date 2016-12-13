# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from future_builtins import map

import string
import urlparse

from scrapy.log import ERROR, DEBUG

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
     cond_set, cond_set_value
import re


class OcadoProductsSpider(BaseProductsSpider):
    name = 'ocado_products'
    allowed_domains = ["ocado.com"]
    start_urls = []

    SEARCH_URL = "https://www.ocado.com/webshop/getSearchProducts.do?" \
        "clearTabs=yes&isFreshSearch=true&entry={search_term}&sortBy={search_sort}"

    SEARCH_SORT = {
        "default" :"default",
        "price_asc": "price_asc",
        "price_desc": "price_desc",
        "name_asc": "name_asc",
        "name_desc":"name_desc",
        "shelf_life":"shelf_life",
        "customer_rating": "customer_rating",
    }

    def __init__(self, search_sort="default", *args, **kwargs):
        super(OcadoProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self.SEARCH_SORT[search_sort]
            ),
            *args, **kwargs)

    def clear_desc(self, l):
        return " ".join(
            [it for it in map(string.strip, l) if it])

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        product = response.meta['product']

        title_list = response.xpath(
            "//h1[@class='productTitle'][1]//text()").extract()
        if len(title_list) >= 2:
            cond_set_value(product, 'title', self.clear_desc(
               title_list[-2:]))

        cond_set(product, 'price', response.xpath(
            "//div[@id='bopRight']//meta[@itemprop='price']/@content"
        ).extract())

        if product.get('price', None):
            if isinstance(product['price'], str):
                product['price'] = product['price'].decode('utf8')
            if not u'£' in product['price']:
                self.log('Unknown currency at %s' % response.url, level=ERROR)
            else:
                product['price'] = Price(
                    priceCurrency='GBP',
                    price=product['price'].replace(u'£', '').replace(
                        ' ', '').replace(',', '').strip()
                )

        img_url = response.xpath(
            "//ul[@id='galleryImages']/li[1]/a/@href"
        ).extract()
        if img_url:
            cond_set_value(product, 'image_url',
                           urlparse.urljoin(response.url, img_url[0]))

        cond_set_value(
            product,
            'description',
            self.clear_desc(
                response.xpath(
                    "//div[@id='bopBottom']"
                    "//h2[@class='bopSectionHeader' and text()[1]='Product Description'][1]"
                    "/following-sibling::*[@class='bopSection']"
                    "//text()"
                ).extract()
            ))

        cond_set_value(product, 'locale', "en_GB")

        regex = "\/(\d+)"
        reseller_id = re.findall(regex, response.url)
        reseller_id = reseller_id[0] if reseller_id else None
        cond_set_value(product, "reseller_id", reseller_id)

        cond_set(
            product,
            'brand',
            response.xpath(
                "string(//div[@id='bopBottom']//*[@itemprop='brand'])"
            ).extract(),
            string.strip,
        )

        return product

    def _scrape_total_matches(self, response):
        totals = response.xpath("string(//h3[@id='productCount'])").re(
            r'(\d+) products')
        total = None
        if len(totals) > 1:
            self.log(
                "Found more than one 'total matches' for %s" % response.url,
                ERROR
            )
        elif totals:
            total = int(totals[0].strip())
        else:
            self.log(
                "Failed to find 'total matches' for %s" % response.url,
                ERROR
            )

        return total

    def _scrape_product_links(self, response):
        links = response.xpath('//h4[@class="productTitle"]/a/@href').extract()
        if not links:
            self.log("Found no product links.", ERROR)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        link = response.css('ul.pages a.next::attr(href)').extract()

        if not link:
            self.log("Next page link not found.", DEBUG)
            return None

        return link[0]
