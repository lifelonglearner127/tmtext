from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json
import urlparse
import string

from scrapy import Request
from scrapy.log import ERROR

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value


class CanadiantireProductsSpider(BaseProductsSpider):
    name = 'canadiantire_products'
    allowed_domains = ["canadiantire.ca"]
    start_urls = []

    SEARCH_URL = "http://www.canadiantire.ca/en/search-results.html" \
        "?searchByTerm=true&q={search_term}"

    _PROD_DATA_RELATIVE_URL = "{load_url}?productCodes={product_code}" \
        "&locale={locale}&storeId=&showAdSkus={show_ad}"

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(product, 'title', response.xpath(
            "//div[contains(@class,'product-title')]/div/h1/text()").extract())

        cond_set(product, 'brand', response.xpath(
            "//div[contains(@class,'product-title')]/img/@title").extract())

        cond_set(product, 'image_url', response.xpath(
            "//link[@rel='image_src']/@href").extract())

        productid = response.xpath("//span[@class='displaySkuCode']/text()")
        if productid:
            productid = productid.extract()[0].strip().replace(
                '#', '', 1
            ).replace('-', '')
            product['upc'] = int(productid)

        info = response.xpath(
            "//div[@class='features_wrap']/descendant::*[text()]/text()")
        if info:
            info = "\n".join(map(string.strip, info.extract()))
            product['description'] = info

        related = response.xpath(
            "//div[@class='sr-cross-sell__wrapper']/*/*/*/a")
        lrelated = []
        for sel in related:
            link = sel.xpath('@href')
            link = link.extract()[0]
            link = urlparse.urljoin(response.url, link)

            ltitle = sel.xpath('img/@title')
            ltitle = ltitle.extract()[0]

            lrelated.append(RelatedProduct(ltitle, link))
        product['related_products'] = {"recommended": lrelated}

        price = response.xpath(
            "//div[contains(@class,'product-price')]/@data-load-params")
        if price:
            load_params = json.loads(price.extract()[0])

            cond_set_value(product, 'locale', load_params.get('lang'))

            prod_data_rel_url = self._PROD_DATA_RELATIVE_URL.format(
                load_url=load_params.get('loadUrl'),
                product_code=load_params.get('productCode'),
                locale=load_params.get('lang'),
                show_ad="false",  # Fetch only what's necessary.
            )
            prod_data_url = urlparse.urljoin(response.url, prod_data_rel_url)
            return Request(
                prod_data_url, self._parse_json, meta=response.meta.copy())
        else:
            cond_set_value(product, 'locale', "en-US")

            return product

    def _parse_json(self, response):
        product = response.meta['product']

        data = json.loads(response.body_as_unicode())
        prod_data = data[0]

        cond_set_value(product, 'price', prod_data.get('regularPrice'))
        cond_set_value(product, 'title', prod_data.get('name'))

        return product

    def _scrape_total_matches(self, response):
        total = response.xpath(
            "//span[@class='search_results_filter__hilite-count']/text()")
        if total:
            return int(total.extract()[0])
        else:
            return 0

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//div[@id='search_results']/*/*/*"
            "/div[contains(@class,'product_result')]/a/@href"
        ).extract()
        if not links:
            self.log("Found no product links.", ERROR)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next_page_links = response.xpath(
            "//li[@class='pagination']/ul/li/a[contains(text(),'Next')]/@href")
        if next_page_links:
            next_page_link = urlparse.urljoin(
                response.url, next_page_links.extract()[0])
        else:
            next_page_link = None
        return next_page_link
