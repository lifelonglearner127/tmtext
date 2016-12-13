# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

import re
import time
import json

from scrapy.http import Request

from product_ranking.items import Price, BuyerReviews
from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, FLOATING_POINT_RGEX
from product_ranking.spiders import cond_set, cond_set_value


is_empty = lambda x, y=None: x[0] if x else y


class MarksandspencerProductsSpider(BaseProductsSpider):
    name = 'marksandspencer_products'
    allowed_domains = ["marksandspencer.com", "recs.richrelevance.com",]

    SEARCH_URL = ("http://www.marksandspencer.com/MSSearchResultsDisplayCmd"
        "?&searchTerm={searchterm}&langId={langId}&storeId={storeId}"
        "&catalogId={catalogId}&categoryId={categoryId}"
        "&typeAhead={typeAhead}&sortBy={sortBy}")

    REVIEW_URL = ("http://reviews.marksandspencer.com/2050-en_gb/"
        "{id}/reviews.djs?format=embeddedhtml")

    RELATED_URL = ("http://recs.richrelevance.com/rrserver/p13n_generated.js?"
        "a={RRApiKey}"
        "&ts={time}"
        "&p={prodId}"
        "&re=true"
        "&pt=%7C{RRPlacementTypes}"
        "&u=6234ad35-b082-414e-b02d-bd5387fab6b7"
        "&s=6234ad35-b082-414e-b02d-bd5387fab6b7"
        "&cts=http%3A%2F%2Fwww.marksandspencer.com"
        "&chi=%7C{RRCategoryHintId}"
        "&flv=15.0.0"
        "&rcs=eF4FwbENgDAMBMAmFaMgvZS3jWNvwBoIp6CgA-"
        "bnri3391y1qg_QdLjRKdIDht7ec59hSmaClQJTcXhFhx-bctoMhv4ylxAI"
        "&l=1"
    )

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

    def __init__(self, sort_mode=None, *args, **kwargs):
        self.sort_mode = sort_mode or "relevance"
        super(MarksandspencerProductsSpider, self).__init__(
                site_name=self.allowed_domains[0],
                *args,
                **kwargs)

    def start_requests(self):
        yield Request(
            url="http://www.marksandspencer.com",
            callback=self.after_start,
        )

    def after_start(self, response):
        storeId = is_empty(response.xpath(
            "//form/.//input[@name='storeId']/@value").extract(), "")
        catalogId = is_empty(response.xpath(
            "//form/.//input[@name='catalogId']/@value").extract(), "")
        categoryId = is_empty(response.xpath(
            "//form/.//input[@name='categoryId']/@value").extract(), "")
        langId = is_empty(response.xpath(
            "//form/.//input[@name='langId']/@value").extract(), "")
        typeAhead = is_empty(response.xpath(
            "//form/.//input[@name='typeAhead']/@value").extract(), "")
        for st in self.searchterms:
            url = self.SEARCH_URL.format(
                searchterm=self.searchterms[0], storeId=storeId,
                catalogId=catalogId, categoryId=categoryId,
                langId=langId, typeAhead=typeAhead,
                sortBy=self.SORT_MODES.get(self.sort_mode)
            )
            yield Request(
                url=url,
                meta={'search_term': st, 'remaining': self.quantity},
            )

        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            prod['url'] = self.product_url
            yield Request(self.product_url,
                          self._parse_single_product,
                          meta={'product': prod})

    def parse_product(self, response):
        product = response.meta['product']

        price = is_empty(response.xpath(
            "//dd[contains(@class, 'price')]/span/text()"
        ).extract())

        priceCurrency = ''.join(
            re.findall("[^\d]*", price)).strip().replace(
                ".", "").replace(",", "")
        price = is_empty(re.findall(FLOATING_POINT_RGEX, price))
        if price:
            product["price"] = Price(
                priceCurrency=self.CURRENCY_SIGNS.get(priceCurrency, "GBP"),
                price=price,
            )

        image_url = is_empty(response.xpath(
            "//ul[contains(@class, 'custom-wrap')]/li/img/@srcset |"
            "//img[@id='mainProdDefaultImg']/@src"
        ).extract())
        image_url = is_empty(re.findall("[^\$]*", image_url))
        if image_url:
            if not "http" in image_url:
                image_url = "http:" + image_url
            product["image_url"] = image_url

        #cond_set_value(product, "brand", "Marks and Spencer")
        cond_set(
            product,
            "brand",
            response.xpath(
                "//ul[contains(@class, 'sub-brand-des')]/li/text()").extract(),
            lambda x: x.strip(),
            )

        cond_set_value(product, "title", is_empty(response.xpath(
            "//h1[@itemprop='name']/text()").extract()))

        cond_set(
            product,
            "model",
            response.xpath("//p[contains(@class, 'code')]/text()").extract(),
            lambda x: x.strip(),
        )

        cond_set(
            product,
            "description",
            response.xpath(
                "//div[@class='content']/"
                "div[contains(@class, 'information-panel')] |"
                "//div[contains(@class, 'product-information-flyout')]"
            ).extract(),
            lambda x: x.strip()
        )

        product["locale"] = "en_GB"

        regex = "\/p\/([a-z0-9$]+)"
        reseller_id = re.findall(regex, response.url)
        reseller_id = reseller_id[0] if reseller_id else None
        cond_set_value(product, "reseller_id", reseller_id)

        variants_stock = is_empty(re.findall(
            "itemStockDetailsMap_\d+\s+\=\s+([^\;]*)", response.body), "{}")
        variants_price = is_empty(re.findall(
            "priceLookMap_\d+\s+\=\s+(.*)};", response.body), "{}")

        try:
            vs = json.loads(variants_stock)
        except (ValueError, TypeError):
            vs = {}
        try:
            vp = json.loads(variants_price+"}")
        except (ValueError, TypeError):
            vp = {}


        variants = []
        for k, v in vs.items():
            for k_in, v_in in vs[k].items():
                obj = {"id": k+"_"+k_in}
                color = is_empty(re.findall("\d+_([^_]*)", k))
                if color:
                    obj["color"] = color
                size = k_in.replace("DUMMY", "")
                if size:
                    obj["size"] = size
                if vs[k][k_in].get("count") == 0:
                    obj["in_stock"] = False
                else:
                    obj["in_stock"] = True
                variants.append(obj)

        for variant in variants:
            price = vp.get(variant["id"], {}).get("price", "")
            price = is_empty(re.findall(FLOATING_POINT_RGEX, price))
            if price:
                variant["price"] = price
            del variant["id"]

        if variants:
            product["variants"] = variants

        reqs = []

        prodId = is_empty(re.findall("productId\s+\=\'(\w+)", response.body))

        if prodId:
            reqs.append(
                Request(
                    url=self.REVIEW_URL.format(id=prodId),
                    callback=self.parse_buyer_reviews,
                )
            )

        ts = time.time()
        RRApiKey = is_empty(re.findall(
            "RRApiKey\s+\=\s+\'(\w+)", response.body))
        if not RRApiKey:
            RRApiKey = is_empty(re.findall(
                "setApiKey\(\'([^\']*)", response.body))
        RRPlacementTypes = is_empty(re.findall(
            "RRPlacementTypes\s+\=\s+\'([^\']*)", response.body))
        if not RRPlacementTypes:
            RRPlacementTypes = '|'.join(re.findall(
                "addPlacementType\(\'([^\']*)", response.body))
        RRCategoryHintId = is_empty(re.findall(
            "RRCategoryHintId\s+\=\s+\'([^\']*)", response.body))
        if not RRCategoryHintId:
            RRCategoryHintId = is_empty(re.findall(
                "addCategoryHintId\(\'([^\']*)", response.body))

        if prodId:
            reqs.append(
                Request(
                    url=self.RELATED_URL.format(
                        RRApiKey=RRApiKey, time=ts, prodId=prodId,
                        RRPlacementTypes=RRPlacementTypes,
                        RRCategoryHintId=RRCategoryHintId
                    ),
                    callback=self.parse_related_product,
                )
            )

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def parse_buyer_reviews(self, response):
        product = response.meta.get("product")
        reqs = response.meta.get("reqs")

        total = int(is_empty(response.xpath(
            "//span[contains(@class, 'BVRRRatingSummaryHeaderCounterValue')]"
            "/text()"
        ).re(FLOATING_POINT_RGEX), 0))

        average = float(is_empty(re.findall(
            "avgRating\"\:(\d+\.\d+)", response.body), 0))

        rbs = response.xpath(
            "//span[contains(@class, 'BVRRHistAbsLabel')]/text()"
        ).extract()[:5]
        rbs.reverse()
        rating_by_star = {}
        if rbs:
            for i in range(5, 0, -1):
                rating_by_star[i] = int(rbs[i-1].replace(
                    "\n", "").replace("\t", "").replace("\\n", ""))
        if total and average:
            product["buyer_reviews"] = BuyerReviews(
                num_of_reviews=total,
                average_rating=average,
                rating_by_star=rating_by_star
            )
        else:
            product["buyer_reviews"] = ZERO_REVIEWS_VALUE

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def parse_related_product(self, response):
        product = response.meta.get("product")
        reqs = response.meta.get("reqs")

        data = re.findall(
            "currentItemObjArray\[\d\].items.push\(([^}]*)}\);", response.body)

        rp = []
        for item in data:
            title = is_empty(re.findall("name\:\"([^\"]*)", item))
            url = is_empty(re.findall("url\:\"([^\"]*)", item))

            if title and url:
                rp.append(
                    RelatedProduct(
                        title=title,
                        url=url,
                    )
                )

        if rp:
            product["related_products"] = rp

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
        total_matches = is_empty(response.xpath(
            "//span[contains(@class, 'count')]/text()"
        ).re(FLOATING_POINT_RGEX), 0)

        return int(total_matches)

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//h3/a[contains(@class, 'prodAnchor')]/@href").extract()
        if not links:
            links = response.xpath(
                '//li/div[contains(@class, "detail")]/a/@href').extract()
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next_page = "&pageChoice={now}"
        url = response.url
        _max_page = response.xpath(
            "//legend[contains(@class, 'web-only')]/span[last()]/text()"
        ).re(FLOATING_POINT_RGEX)
        if _max_page and isinstance(_max_page, (list, tuple)):
            _max_page = _max_page[0]
        if not _max_page:
            _max_page  = response.xpath(
                '//*[contains(@class, "pagination")]/legend[contains(text(), "/")]/text()'
            ).extract()
            if _max_page:
                _max_page = _max_page[0].strip()
                if _max_page.count('/') == 1:
                    _max_page = _max_page.split('/')[1].strip()
        if _max_page.isdigit():
            maximum = int(_max_page)
        else:
            maximum = 0
        now = int(is_empty(re.findall("pageChoice=(\d+)", url), 1))
        if now >= maximum:
            return None
        if not "pageChoice=" in url:
            return url + next_page.format(now=now+1)
        return re.sub("pageChoice=(\d+)", next_page.format(now=now+1), url)

    def _parse_single_product(self, response):
        return self.parse_product(response)
