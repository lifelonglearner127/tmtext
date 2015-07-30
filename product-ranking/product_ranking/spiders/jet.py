# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

import re
import json
import urllib
import urlparse

from scrapy.http import Request

from product_ranking.items import Price
from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, FLOATING_POINT_RGEX
from product_ranking.spiders import cond_set, cond_set_value


is_empty = lambda x, y=None: x[0] if x else y


class JetProductsSpider(BaseProductsSpider):
    name = 'jet_products'
    allowed_domains = ["jet.com"]
    #SEARCH_URL = "https://jet.com/search/results?term={search_term}%20"

    SEARCH_URL = "https://jet.com/search/results"

    START_URL = "http://jet.com"

    PRICE_URL = "https://jet.com/api/product/price"

    SYM_USD = '$'
    SYM_GBP = '£'
    SYM_CRC = '₡'
    SYM_EUR = '€'
    SYM_JPY = '¥'

    CURRENCY_SIGNS = {
        SYM_USD: 'USD',
        SYM_GBP: 'GBP',
        SYM_CRC: 'CRC',
        SYM_EUR: 'EUR',
        SYM_JPY: 'JPY'
    }

    SORT_MODES = {
        "relevance": "relevance|1",
        "best_selling": "product.best_selling|1",
        "new_arrivals": "product.is_new|1",
        "pricelh": "product.price_from|0",
        "pricehl": "product.price_to|1",
        "rating":  "product.rating|1"
    }

    product_links = []

    DEFAULT_MARKETPLACE = "Jet"

    def start_requests(self):
        if not self.product_url:
            for st in self.searchterms:
                yield Request(
                    url=self.START_URL,
                    meta={'search_term': st, 'remaining': self.quantity},
                    dont_filter=True,
                    callback=self.start_requests_with_csrf,
                )
        else:
            for req in super(JetProductsSpider, self).start_requests():
                yield req


    def start_requests_with_csrf(self, response):
        csrf = is_empty(re.findall("__csrf\"\:\"([^\"]*)", response.body))
        if not self.product_url:
            for st in self.searchterms:
                yield Request(
                    url=self.SEARCH_URL,
                    callback=self.after_start,
                    method="POST",
                    body=json.dumps({"term": self.searchterms[0]}),
                    meta={'search_term': st, 'remaining': self.quantity},
                    dont_filter=True,
                    headers={
                        "content-type": "application/json",
                        "x-csrf-token": csrf,
                    },
                )

    def after_start(self, response):
        if "24 of 10,000+ results" in response.body_as_unicode():
            a = response.xpath("//div[contains(@class, 'pagination')]"
                "/a[contains(@class, 'history') and "
                "not(contains(@class, 'next'))][last()]"
            )
            link = is_empty(a.xpath("@href").extract())
            max_num = int(is_empty(a.xpath("span/text()").extract(), 0))
            url = urlparse.urljoin("http://"+self.allowed_domains[0], link)

            print('+'*50)
            print(link)
            print('+'*50)

            yield Request(
                url=url,
                meta={"max_num": max_num-1},
                callback=self.calculate_total,
            )

    def calculate_total(self, response):
        max_num = response.meta.get("max_num", 0)

        fl=open('file.html', 'w')
        fl.write(response.body)
        fl.close()

        links = is_empty(response.xpath("//div[contains(@class, 'pagination')]"
            "/a[contains(@class, 'next')]/@href").extract())

        last_page_num = len(links)
        self.tm = 24*max_num+links
        return super(JetProductsSpider, self).start_requests()

    def parse_product(self, response):
        product = response.meta['product']
        reqs = []

        cond_set(product, "title", response.xpath(
                "//div[contains(@class, 'content')]"
                "/div[contains(@class, 'title')]"
            ).extract()
        )
        brand = is_empty(response.xpath("//div[contains(@class, 'content')]"
            "/div[contains(@class, 'brand')]/text()").extract())
        if brand:
            brand = brand.replace("by ", "")
            product["brand"] = brand
        
        image_url = is_empty(response.xpath(
            "//div[contains(@class, 'images')]/div/@style"
        ).extract())
        if image_url:
            image_url = is_empty(re.findall(
                "background\:url\(([^\)]*)", image_url))
            product["image_url"] = image_url

        cond_set(product, "description", response.xpath(
                "//div[contains(@class, 'container')]"
                "/div[contains(@class, 'half')]"
            ).extract()
        )

        cond_set(product, "model", response.xpath(
            "//div[contains(@class, 'products')]/div/@rel").extract()
        )

        product["locale"] = "en_US"

        csrf = is_empty(re.findall("__csrf\"\:\"([^\"]*)", response.body))
        if product.get("model") and csrf:
            reqs.append(
                Request(
                    url=self.PRICE_URL,
                    method="POST",
                    callback=self.parse_price_and_marketplace,
                    meta={"product": product},
                    body=json.dumps({"sku": product.get("model")}),
                    headers={
                        "content-type": "application/json",
                        "x-csrf-token": csrf,
                    }
                )
            )

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def parse_price_and_marketplace(self, response):
        product = response.meta.get("product")
        reqs = response.meta.get("reqs")

        data = json.loads(response.body)
        if not product.get("price"):
            for price in data.get("quantities", []):
                if price.get("quantity") == 1:
                    product["price"] = Price(
                        priceCurrency="USD",
                        price=price.get("price")
                    )

        marketplace = []
        if data.get("comparisons"):
            for markp in data.get("comparisons", []):
                marketplace.append({
                    "name": markp.get("source"),
                    "price": markp.get("price")
                })
            if marketplace:
                marketplace.append({
                    "name": self.DEFAULT_MARKETPLACE,
                    "price": product["price"].price.__float__()
                })
                product["marketplace"] = marketplace

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def send_next_request(self, reqs, response):
        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)

    def _scrape_total_matches(self, response):
        total_matches = response.xpath(
            "//div[contains(@class, 'text open-sans-regular')]/text()"
        ).re(FLOATING_POINT_RGEX)
        if total_matches:
            total_matches = int(total_matches[len(total_matches)-1].replace(
                ",", ""))
        else:
            total_matches = 0

        if "24 of 10,000+ results" in response.body_as_unicode():
            total_matches = self.tm
        
        return int(total_matches)

    def _scrape_product_links(self, response):
        for item in response.xpath("//div[contains(@class, 'product')]"):
            link = is_empty(item.xpath("a/@href").extract())
            price = is_empty(item.xpath(
                ".//div[contains(@class, 'price')]/div/text()").extract(), "")
            priceCurrency = ''.join(
                re.findall("[^\d]*", price)).strip().replace(
                    ".", "").replace(",", "")
            price = is_empty(re.findall(FLOATING_POINT_RGEX, price))
            if price:
                price = Price(
                    priceCurrency=self.CURRENCY_SIGNS.get(priceCurrency, "GBP"),
                    price=price,
                )
            if link and not link in self.product_links:
                self.product_links.append(link)
                yield link, SiteProductItem(price=price)
            continue

    def _scrape_next_results_page_link(self, response):
        link = is_empty(response.xpath("//div[contains(@class, 'pagination')]"
            "/a[contains(@class, 'next')]/@href").extract())
        return link

    def _parse_single_product(self, response):
        return self.parse_product(response)
