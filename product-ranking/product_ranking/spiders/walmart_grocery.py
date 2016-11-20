# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

import json
import re
import time


from scrapy.http import Request
from scrapy.log import ERROR, WARNING

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider, cond_set_value
from product_ranking.guess_brand import guess_brand_from_first_words

is_empty = lambda x, y=None: x[0] if x else y

class WalmartGroceryProductSpider(BaseProductsSpider):


    name = 'walmart_grocery_products'
    allowed_domains = ["delivery.walmart.com", "grocery-api.walmart.com"]
    start_urls = []

    ZIP_URL = ("https://grocery-api.walmart.com/v0.1/"
        "api/postalCodeAvailability/{zip}")

    START_URL = "http://delivery.walmart.com/"

    DETAIL_URL = "https://grocery-api.walmart.com/v0.1/api/product/{skuId}"

    DEFAULT_URL = ("http://delivery.walmart.com/usd-estore/m/"
        "product-detail.jsp?skuId={skuId}")

    NEXT_PAGI_PAGE = ("https://grocery-api.walmart.com/v0.1/api/search?query={search_term}&rows=60&start={position}&storeId={storeId}")

    position = 0


    def __init__(self, zip_code="95030", *args, **kwargs):
        site_name = self.allowed_domains[0]
        super(WalmartGroceryProductSpider, self).__init__(
            site_name=site_name, *args, **kwargs)
        self.zip_code = zip_code

    def start_requests(self):
        if not self.product_url:
            yield Request(
                url=self.START_URL,
                callback=self.after_start,
            )
        else:
            skuId = is_empty(re.findall("skuId=(\d+)", self.product_url))
            if not skuId:
                self.log("Can't get product skuId", ERROR)
                return
            prod = SiteProductItem()
            prod['is_single_result'] = True
            prod['url'] = self.product_url
            prod['search_term'] = ''
            yield Request(
                url=self.DETAIL_URL.format(skuId=skuId),
                callback=self._parse_single_product,
                meta={'product': prod}
            )

    def after_start(self, response):
        try:
            data = json.loads(response.body)
        except (ValueError, TypeError):
            data = {}

        if data.get("availability") == "true":
            self.storeId = data.get("storeId")
            self.SEARCH_URL = ("https://grocery-api.walmart.com/v0.1/api/search?query={search_term}&rows=60&start=0&storeId=%s" % (
                    self.storeId))
            return super(WalmartGroceryProductSpider, self).start_requests()

        params = {
            "aVer":"1.0",
            "aid":"wm_us",
            "pid":"desktop",
            "tpid":"desktop",
            "mts":str(time.time()).replace(".", ""),
            "ua":"Mozilla/5.0 (X11; Linux i686 (x86_64)) AppleWebKit/537.36" \
                " (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36",
            "env":"prod",
            "events":[
                {
                    "event":"pageLoad",
                    "page":"home",
                    "startEvent":
                    "ContentByStoreIdRequest",
                    "deltatime":413
                },
                {
                    "event":"pageLoad",
                    "page":"home",
                    "startEvent":
                    "start",
                    "deltatime":12809
                }
            ]
        }

        return Request(
            url=self.ZIP_URL.format(zip=self.zip_code),
            callback=self.after_start,
            body=json.dumps(params),
        )

    def parse_product(self, response):
        product = response.meta.get("product")
        reqs = []

        try:
            data = json.loads(response.body)
        except (ValueError, TypeError):
            data = {}

        product.update(self.populate_from_json(data))

        if product.get("title"):
            product["brand"] = guess_brand_from_first_words(product["title"])

        data = data.get("data", {})

        cond_set_value (product, "description", data.get("description"))
        if len(data.get("upc")) == 1:
            cond_set_value(product, "upc", is_empty(data.get("upc")))
        elif len(data.get("upc")) > 1:
            upc = [str(x) for x in data.get("upc")]
            upc = ','.join(set(upc))
            cond_set_value(product, "upc", upc)

        is_out_of_stock = data.get("isOutOfStock")
        if is_out_of_stock == "true":
            is_out_of_stock = True
        else:
            is_out_of_stock = False
        cond_set_value(product, "is_out_of_stock", is_out_of_stock)

        cond_set_value(product, "model", data.get("modelNum"))

        self.set_product_url(product)

        cond_set_value(product, "locale", "en_US")

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def send_next_request(self, reqs, response, meta):
        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if meta:
            new_meta.update(meta)
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)

    def populate_from_json(self, item):
        images = item.get("data", {}).get("images", {})
        special_pricing = item.get("price", {}).get("isRollback")
        if special_pricing == "true":
            special_pricing = True
        elif special_pricing == "false":
            special_pricing = False

        price = Price(
            priceCurrency="USD",
            price=item.get("price", {}).get("list")
        )

        product = SiteProductItem(
            title=item.get("data", {}).get("name"),
            image_url=images.get("large", images.get("small")),
            price=price,
            special_pricing=special_pricing,
        )

        return product

    def set_product_url(self, product):
        url = product.get("url", "")
        if not url:
            return
        if re.search("api/product/", url):
            skuId = is_empty(re.findall("api/product/(\d+)", url))
            if not skuId:
                return
            product["url"] = self.DEFAULT_URL.format(skuId=skuId)


    def _scrape_total_matches(self, response):
        try:
            data = json.loads(response.body)
        except (ValueError, TypeError):
            data = {}

        self.tm = data.get("productCount", 0)
        return int(data.get("productCount", 0))

    def _scrape_product_links(self, response):
        try:
            data = json.loads(response.body)
        except (ValueError, TypeError):
            data = []

        products = []
        for item in data.get("products", []):
            products.append({
                "product": self.populate_from_json(item),
                "skuId": item.get("data", {}).get("id")
            })
        for product in products:
            sku = product.get("skuId")
            if sku:
                yield self.DETAIL_URL.format(skuId=sku), product["product"]
            else:
                self.log('Can\'t get product !!!', WARNING)

    def _scrape_next_results_page_link(self, response):
        if self.position < self.tm:
            self.position += 60
            return self.NEXT_PAGI_PAGE.format(
                search_term=self.searchterms[0],
                position=self.position,
                storeId=self.storeId,
            )
        return None

    def _parse_single_product(self, response):
        return self.parse_product(response)
