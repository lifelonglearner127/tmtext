# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

import re
import json
import urllib
import urlparse

from scrapy.http import Request

from scrapy.log import ERROR
from product_ranking.items import Price
from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, FLOATING_POINT_RGEX
from product_ranking.spiders import cond_set, cond_set_value
from spiders_shared_code.jet_variants import JetVariants
from product_ranking.validators.jet_validator import JetValidatorSettings
from product_ranking.validation import BaseValidator

is_empty = lambda x, y=None: x[0] if x else y


class JetProductsSpider(BaseValidator, BaseProductsSpider):
    name = 'jet_products'
    allowed_domains = ["jet.com"]

    SEARCH_URL = "https://jet.com/api/search/"

    START_URL = "https://jet.com"

    PRICE_URL = "https://jet.com/api/productAndPrice"

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
        "relevance": "relevance",
        "pricelh": "price_low_to_high",
        "pricehl": "price_high_to_low",
        "member_savings":  "smart_cart_bonus"
    }

    product_links = []

    DEFAULT_MARKETPLACE = "Jet"

    settings = JetValidatorSettings

    def __init__(self, sort_mode=None, *args, **kwargs):
        super(JetProductsSpider, self).__init__(*args, **kwargs)
        self.sort = self.SORT_MODES.get(
            sort_mode) or self.SORT_MODES.get("relevance")

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
        csrf = self.get_csrf(response)
        st = response.met.get('search_term')
        if not self.product_url:
            yield Request(
                url=self.SEARCH_URL,
                callback=self.selftest,
                method="POST",
                body=json.dumps({"term": st,"origination":"none"}),
                meta={
                    'search_term': st,
                    'remaining': self.quantity,
                    'csrf': csrf
                },
                dont_filter=True,
                headers={
                    "content-type": "application/json",
                    "x-csrf-token": csrf,
                    "X-Requested-With":"XMLHttpRequest",
                    "jet-referer":"/search?term={}".format(st),

                },
            )

    def after_start(self, response):
        csrf = response.meta.get("csrf")
        st = response.meta.get("search_term")
        if "24 of 10,000+ results" in response.body_as_unicode():
            a = response.xpath("//div[contains(@class, 'pagination')]"
                "/a[contains(@class, 'history') and "
                "not(contains(@class, 'next'))][last()]"
            )
            link = is_empty(a.xpath("@href").extract())
            max_num = int(is_empty(a.xpath("span/text()").extract(), 0))
            url = urlparse.urljoin("http://"+self.allowed_domains[0], link)

            yield Request(
                url=self.SEARCH_URL,
                method="POST",
                meta={"max_num": max_num-1, "csrf": csrf},
                callback=self.calculate_total,
                body=json.dumps({
                    "page": str(max_num),
                    "sort": self.sort,
                    "term": self.searchterms[0],
                }),
                headers={
                    "content-type": "application/json",
                    "x-csrf-token": csrf,
                },
                dont_filter=True
            )
        else:
            yield Request(callback=self.selftest,
                    url=self.SEARCH_URL,
                    method="POST",
                    body=json.dumps({
                        "term": st,
                        "sort": self.sort,
                    }),
                    meta={
                        'search_term': st,
                        'remaining': self.quantity, 
                        'csrf': csrf
                    },
                    dont_filter=True,
                    headers={
                        "content-type": "application/json",
                        "x-csrf-token": csrf,
                        "X-Requested-With": "XMLHttpRequest",
                        "jet-referer": "/search?term={}".format(st),
                    },
                )

    def calculate_total(self, response):
        max_num = response.meta.get("max_num", 0)

        links = response.xpath("//div[contains(@class, 'product')]"
                               "/a/@href").extract()

        last_page_num = len(set(links))
        self.tm = 24*int(max_num)+last_page_num

        csrf = response.meta.get("csrf")
        if not self.product_url:
            for st in self.searchterms:
                yield Request(
                    url=self.SEARCH_URL,
                    method="POST",
                    body=json.dumps({
                        "term": self.searchterms[0], 
                        "sort": self.sort,
                    }),
                    meta={
                        'search_term': st, 
                        'remaining': self.quantity, 
                        'csrf': csrf
                    },
                    dont_filter=True,
                    headers={
                        "content-type": "application/json",
                        "x-csrf-token": csrf,
                    },
                )
        else:
            for req in super(JetProductsSpider, self).start_requests():
                yield req

    def redirected_from_product_to_main_page(self, response):
        """ Returns True if the spider was redirected from a product page
             to the main website page (//jet.com).
            Means "not_found" product. """
        history = response.meta.get('redirect_urls', None)
        if history:
            current_url = response.url.replace('/', '').replace('https:', '')\
                .replace('http:', '').replace('www.', '')
            if current_url == 'jet.com':
                return True

    def parse_product(self, response):
        meta = response.meta.copy()
        product = meta['product']
        reqs = []

        if self.redirected_from_product_to_main_page(response):
            product['not_found'] = True
            return product

        cond_set(
            product, "title", response.xpath(
                "//div[contains(@class, 'content')]"
                "//div[contains(@class, 'title')]/text()"
            ).extract()
        )
        if not product.get('title', '').strip():
            cond_set(
                product, "title", response.css("h1.title ::text").extract()
            )

        models = response.xpath("//div[contains(@class, 'products')]/div/@rel").extract()
        response.meta['model'] = response.url.split('/')[-1] if len(models) > 1 else is_empty(models)

        brand = is_empty(response.xpath("//div[contains(@class, 'content')]"
                                        "/div[contains(@class, 'brand')]/text()").extract())
        if not brand:
            brand = is_empty(response.css('.manufacturer ::text').extract())
        if brand:
            brand = brand.replace("by ", "")
            product["brand"] = brand

        image_url = is_empty(response.xpath(
            "//div[contains(@class,'images')]/div/@style"
        ).extract())

        if not image_url:
            image_url_list = response.xpath(
                "//div[contains(@class, 'images')]/.//a[@href='#']/@rel "
            ).extract()
            for img in image_url_list:
                if ("-0.500" in img) or (".500" in img):
                    image_url = img
                    break
        if image_url:
            if "background:url" in image_url:
                image_url = is_empty(re.findall(
                    "background\:url\(([^\)]*)", image_url))
            product["image_url"] = image_url

        if not product.get('image_url'):
            cond_set(product, 'image_url',
                response.xpath(
                    '//*[contains(@class, "container-image")]/img/@src').extract()
            )

        cond_set(
            product, "description", response.xpath(
                "//div[contains(@class, 'container')]"
                "/div[contains(@class, 'half')]"
            ).extract()
        )

        upc = re.search('"upc":"(\d+)"', response.body)
        if upc:
            product['upc'] = upc.group(1)

        product["locale"] = "en_US"

        JV = JetVariants()
        JV.setupSC(response)
        product["variants"] = JV._variants()

        csrf = self.get_csrf(response)

        # For each variant with SkuId we need to do a POST to get its price
        for skuids in map((lambda x: x['skuId']),filter((lambda x: 'skuId' in x), product["variants"] or [])):
            reqs.append(
                Request(
                    url=self.PRICE_URL+"?sku=%s" % skuids,
                    method="POST",
                    callback=self.parse_variant_prices,
                    meta={"product": product},
                    body=json.dumps({"sku": skuids}),
                    headers={
                        "content-type": "application/json",
                        "x-csrf-token": csrf,
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    dont_filter=True,
                )
            )

        if response.meta.get("model") and csrf:
            reqs.append(
                Request(
                    url=self.PRICE_URL,
                    method="POST",
                    callback=self.parse_price_and_marketplace,
                    meta={"product": product},
                    body=json.dumps({"sku": response.meta.get("model")}),
                    headers={
                        "content-type": "application/json",
                        "x-csrf-token": csrf,
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    dont_filter=True,
                )
            )

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def parse_variant_prices(self, response):
        sku = response.url.split('?sku=')[-1]
        product = response.meta.get('product')
        reqs = response.meta.get('reqs')
        data = json.loads(response.body)

        # Search for the variant with the given skuId on the list
        for variant in filter((lambda x: 'skuId' in x), product['variants']):
            if variant['skuId'] == sku:
                break

        # Got it's index
        index = product['variants'].index(variant)

        #Update price
        variant['price'] = data.get("referencePrice")

        # Replace it on the list 
        product['variants'].pop(index)
        product['variants'].insert(index, variant)
        
        # Continue with others requests
        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def parse_price_and_marketplace(self, response):
        product = response.meta.get("product")
        reqs = response.meta.get("reqs")
        try:
            data = json.loads(response.body)

            if str(data.get("twoDay")) == "True":
                product["deliver_in"] = "2 Days"

            if data.get("unavailable", None):
                cond_set_value(product, "is_out_of_stock", True)
            else:
                cond_set_value(product, "is_out_of_stock", False)

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
                        "price": Price(
                            priceCurrency="USD",
                            price=markp.get("price")
                        )
                    })
                if marketplace:
                    marketplace.append({
                        "name": self.DEFAULT_MARKETPLACE,
                        "price": product["price"]
                    })
                    product["marketplace"] = marketplace

            if data.get('unavailable', None):
                product['not_found'] = True
        except Exception as e:
            self.log(str(e), ERROR)
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
        data = json.loads(response.body)
        prods = data['result'].get('products')
        product_ids = [p.get('id') for p in prods]
        total_match = data['result'].get('total')
        total_match = int(total_match)

        # for item in response.xpath("//div[contains(@class, 'product')]"):
        #     link = is_empty(item.xpath("a/@href").extract())
        #     price = is_empty(item.xpath(
        #         ".//div[contains(@class, 'price')]/div/text()").extract(), "")
        #     priceCurrency = ''.join(
        #         re.findall("[^\d]*", price)).strip().replace(
        #             ".", "").replace(",", "")
        #     price = is_empty(re.findall(FLOATING_POINT_RGEX, price))
        #     if price:
        #         price = Price(
        #             priceCurrency=self.CURRENCY_SIGNS.get(priceCurrency, "GBP"),
        #             price=price,
        #         )
        #     if link and not link in self.product_links:
        #         self.product_links.append(link)
        #         yield link, SiteProductItem(price=price)
        #     continue

    def _scrape_next_results_page_link(self, response):
        csrf = self.get_csrf(response) or response.meta.get("csrf")
        link = is_empty(response.xpath("//div[contains(@class, 'pagination')]"
                                       "/a[contains(@class, 'next')]/@href").extract(), "")
        page = is_empty(re.findall("page=(\d+)", link))

        if not page or int(page)*24 > self.quantity+24:
            return None
        return Request(
                    url=self.SEARCH_URL,
                    method="POST",
                    dont_filter=True,
                    body=json.dumps({
                        "page": str(page),
                        "sort": self.sort,
                        "term": self.searchterms[0],
                    }),
                    meta={
                        'search_term': self.searchterms[0],
                        'remaining': self.quantity, 
                        'csrf': csrf
                    },
                    headers={
                        "content-type": "application/json",
                        "x-csrf-token": csrf,
                    },
                )

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def get_csrf(self, response):
        return is_empty(response.xpath('//*[@data-id="csrf"]/@data-val').re('[^\"\']+'))
        # return is_empty(re.findall("__csrf\"\:\"([^\"]*)", response.body))
