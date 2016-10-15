# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

import re
import json
import urllib
import urlparse
import unicodedata
from scrapy.conf import settings

from scrapy.http import Request

from itertools import islice
from scrapy.log import ERROR, WARNING, INFO
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

    PROD_URL = "https://jet.com/api/product/v2"

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
        self.current_page = 1
        # settings.overrides['CRAWLERA_ENABLED'] = True

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
            yield Request(
                url=self.START_URL,
                meta={'search_term': "", 'remaining': self.quantity},
                dont_filter=True,
                callback=self.start_requests_with_csrf,
            )

    def start_requests_with_csrf(self, response):
        csrf = self.get_csrf(response)
        st = response.meta.get('search_term')
        if not self.product_url:
            yield Request(
                url=self.SEARCH_URL,
                # callback=self._get_products,
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
        elif self.product_url:
            prod_id = self.product_url.split('/')[-1]
            yield Request(
                url=self.PROD_URL,
                callback=self.parse_product,
                method="POST",
                body=json.dumps({"sku": prod_id, "origination": "none"}),
                meta={
                    "product": SiteProductItem(),
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
        elif self.products_url:
            urls = self.products_url.split('||||')
            for url in urls:
                prod_id = url.split('/')[-1]
                yield Request(
                    url=self.PROD_URL,
                    callback=self.parse_product,
                    method="POST",
                    body=json.dumps({"sku": prod_id, "origination": "none"}),
                    meta={
                        "product": SiteProductItem(),
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

    def parse_product(self, response):
        csrf = response.meta.get('csrf')
        remaining = response.meta['remaining']
        search_term = response.meta['search_term']
        meta = response.meta.copy()
        product = meta['product']
        reqs = []
        if "jet.com/api/product/v2" in response.url:
            # New layout
            try:
                data = json.loads(response.body)
                prod_data = data.get('result')
            except Exception as e:
                self.log(
                    "Failed parsing json at {} - {}".format(response.url, e)
                    , WARNING)
                cond_set_value(product, "not_found", True)
                if not product.get('url'):
                    cond_set_value(product, "url", self.product_url)
                return product

            cond_set_value(product, "title", prod_data.get('title'))

            # Uncomment when reseller_id ticket will be deployed, see bz #12076
            # cond_set(product, "reseller_id", prod_data.get('retailSkuId'))

            cond_set_value(product, "model", prod_data.get('part_no'))

            cond_set_value(product, "upc", prod_data.get('upc'))

            cond_set_value(product, "description", prod_data.get('description'))

            cond_set_value(product, "brand", prod_data.get('manufacturer'))

            cond_set_value(product, "sku", prod_data.get('sku'))

            image_url = prod_data.get('images')
            image_url = image_url[0].get('raw') if image_url else None
            cond_set_value(product, "image_url", image_url)

            cond_set_value(product, "title", prod_data.get('title'))

            cond_set_value(product, "locale", "en_US")

            if prod_data.get("productPrice", {}).get('shippingPromise') == "TwoDay":
                product["deliver_in"] = "2 Days"

            if prod_data.get("productPrice", {}).get('status'):
                cond_set_value(product, "is_out_of_stock", True)
            else:
                cond_set_value(product, "is_out_of_stock", False)

            if not product.get("price"):
                price = prod_data.get('productPrice', {})
                price = price.get("referencePrice")
                cond_set_value(product, "price", Price(priceCurrency="USD", price=price))

            JV = JetVariants()
            JV.setupSC(response)
            product["variants"] = JV._variants_v2()

            # Filling other variants prices
            # with additional requests
            # See bz #11124
            if self.scrape_variants_with_extra_requests:
                for variant in product.get("variants"):
                    # Default variant already have price filled
                    if not variant.get("selected"):
                        # Construct additional requests to get prices for variants
                        prod_id = variant.get("sku")
                        req = Request(
                            url=self.PROD_URL,
                            callback=self.parse_variant_price,
                            method="POST",
                            body=json.dumps({"sku": prod_id, "origination": "none"}),
                            meta={
                                  'csrf': csrf,
                                  "reqs": reqs,
                                  "product": product
                                 },
                            dont_filter=True,
                            headers={
                                "content-type": "application/json",
                                "x-csrf-token": csrf,
                                "X-Requested-With": "XMLHttpRequest",
                                "jet-referer": "/search?term={}".format(search_term),
                            },
                        )
                        reqs.append(req)
            if reqs:
                return self.send_next_request(reqs, response)
            return product

        else:
            # Old layout
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

    def parse_variant_price(self, response):
        product = response.meta.get('product')
        reqs = response.meta.get('reqs')

        try:
            data = json.loads(response.body)
            prod_data = data.get('result')
            variant_price = prod_data.get('productPrice', {}).get("referencePrice")
            variant_prod_id = prod_data.get('retailSkuId')
        except Exception as e:
            self.log("Failed parsing json at {} - {}".format(response.url, e), WARNING)
            variant_price = None
            variant_prod_id = None

        for variant in product['variants']:
            if not variant.get("selected"):
                if variant.get("sku") == variant_prod_id:
                    variant["price"] = variant_price
                    break

        # Continue with other requests
        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def send_next_request(self, reqs, response):
        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)

    def _scrape_results_per_page(self, response):
        try:
            data = json.loads(response.body)
            prods = data['result'].get('products')
            results_per_page = len(prods)
        except Exception as e:
            print e
            results_per_page = 0

        return int(results_per_page)

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

        if not total_matches:
            try:
                data = json.loads(response.body)
                total_matches = data['result'].get('total')
                total_matches = int(total_matches) if total_matches else 0
            except Exception as e:
                print e
                total_matches = 0

        return int(total_matches)

    def _scrape_product_links(self, response):
        try:
            data = json.loads(response.body)
            prods = data['result'].get('products', [])
        except Exception as e:
            self.log(
                "Failed parsing json at {} - {}".format(response.url, e)
                , WARNING)
            prods = []

        for prod in prods:
            prod_id = prod.get('id')
            # Construct product url
            prod_name = prod.get('title')
            prod_slug = self.slugify(prod_name)
            prod_url = "https://jet.com/product/{}/{}".format(prod_slug, prod_id)
            yield prod_url, SiteProductItem()

    @staticmethod
    def slugify(value):
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        # Removed .lower() for this website
        value = re.sub('[^\w\s-]', '', value).strip()
        return re.sub('[-\s]+', '-', value)

    def _get_products(self, response):
        csrf = response.meta.get('csrf')
        remaining = response.meta['remaining']
        search_term = response.meta['search_term']
        prods_per_page = response.meta.get('products_per_page')
        total_matches = response.meta.get('total_matches')
        scraped_results_per_page = response.meta.get('scraped_results_per_page')

        prods = self._scrape_product_links(response)

        if prods_per_page is None:
            # Materialize prods to get its size.
            prods = list(prods)
            prods_per_page = len(prods)
            response.meta['products_per_page'] = prods_per_page

        if scraped_results_per_page is None:
            scraped_results_per_page = self._scrape_results_per_page(response)
            if scraped_results_per_page:
                self.log(
                    "Found %s products at the first page" %scraped_results_per_page
                    , INFO)
            else:
                scraped_results_per_page = prods_per_page
                if hasattr(self, 'is_nothing_found'):
                    if not self.is_nothing_found(response):
                        self.log(
                            "Failed to scrape number of products per page", WARNING)
            response.meta['scraped_results_per_page'] = scraped_results_per_page

        if total_matches is None:
            total_matches = self._scrape_total_matches(response)
            if total_matches is not None:
                response.meta['total_matches'] = total_matches
                self.log("Found %d total matches." % total_matches, INFO)
            else:
                if hasattr(self, 'is_nothing_found'):
                    if not self.is_nothing_found(response):
                        self.log(
                            "Failed to parse total matches for %s" % response.url,ERROR)

        if total_matches and not prods_per_page:
            # Parsing the page failed. Give up.
            self.log("Failed to get products for %s" % response.url, ERROR)
            return

        for i, (prod_url, prod_item) in enumerate(islice(prods, 0, remaining)):
            # Initialize the product as much as possible.
            prod_item['site'] = self.site_name
            prod_item['search_term'] = search_term
            prod_item['total_matches'] = total_matches
            prod_item['results_per_page'] = prods_per_page
            prod_item['scraped_results_per_page'] = scraped_results_per_page
            # The ranking is the position in this page plus the number of
            # products from other pages.
            prod_item['ranking'] = (i + 1) + (self.quantity - remaining)
            if self.user_agent_key not in ["desktop", "default"]:
                prod_item['is_mobile_agent'] = True

            if prod_url is None:
                # The product is complete, no need for another request.
                yield prod_item
            elif isinstance(prod_url, Request):
                cond_set_value(prod_item, 'url', prod_url.url)  # Tentative.
                yield prod_url
            else:
                # Another request is necessary to complete the product.
                url = urlparse.urljoin(response.url, prod_url)
                cond_set_value(prod_item, 'url', url)  # Tentative.
                # Getting product data from api POST request instead of regular url
                prod_id = prod_url.split('/')[-1]
                yield Request(
                    url=self.PROD_URL,
                    callback=self.parse_product,
                    method="POST",
                    body=json.dumps({"sku": prod_id, "origination": "none"}),
                    meta={
                        "product": prod_item,
                        'search_term': search_term,
                        'remaining': self.quantity,
                        'csrf': csrf
                    },
                    dont_filter=True,
                    headers={
                        "content-type": "application/json",
                        "x-csrf-token": csrf,
                        "X-Requested-With": "XMLHttpRequest",
                        "jet-referer": "/search?term={}".format(search_term),

                    },
                )

    def _scrape_next_results_page_link(self, response):
        csrf = self.get_csrf(response) or response.meta.get("csrf")
        st = response.meta.get("search_term")
        if int(self.current_page)*24 > self.quantity+24:
            return None
        else:
            self.current_page += 1
            return Request(
                url=self.SEARCH_URL,
                method="POST",
                body=json.dumps({"term": st, "origination": "none", "page": self.current_page}),
                meta={
                    'search_term': st,
                    'csrf': csrf
                },
                dont_filter=True,
                headers={
                    "content-type": "application/json",
                    "x-csrf-token": csrf,
                    "X-Requested-With": "XMLHttpRequest",
                },
            )

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def get_csrf(self, response):
        return is_empty(response.xpath('//*[@data-id="csrf"]/@data-val').re('[^\"\']+'))
