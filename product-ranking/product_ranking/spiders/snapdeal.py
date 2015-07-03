# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

from urlparse import urljoin
import json
import re

from scrapy.http import FormRequest, Request

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    dump_url_to_file
from product_ranking.guess_brand import guess_brand_from_first_words

is_empty = lambda x, y=None: x[0] if x else y

class SnapdealProductSpider(BaseProductsSpider):


    name = 'snapdeal_products'
    allowed_domains = ["www.snapdeal.com"]

    SEARCH_URL = ("http://www.snapdeal.com/acors/json/product/get/search"
        "/0/0/20?q=&sort={sort}&keyword={search_term}&clickSrc=go_header"
        "&viewType=List&lang=en&snr=false")

    # SEARCH_URL = ("http://www.snapdeal.com/search?keyword={search_term}"
    #     "&santizedKeyword=&catId=&categoryId=&suggested=false&vertical="
    #     "&noOfResults=20&clickSrc=go_header&lastKeyword=&prodCatId="
    #     "&changeBackToAll=false&foundInAll=false&categoryIdSearched="
    #     "&cityPageUrl=&url=&utmContent=&catalogID=&dealDetail=")

    REVIEWS_URL = "http://www.snapdeal.com/getReviewsInfoGram?pageId={id}"

    NEXT_PAGI_PAGE = "http://www.snapdeal.com/acors/json/product/get/search" \
        "/0/{pos}/50?q=&sort={sort}rlvncy&keyword={term}&clickSrc=go_header" \
        "&viewType=List&lang=en&snr=false"

    position = 20

    STOP = False

    SORT_MODES = {
        "RELEVANCE": "",
        "POPULARITY": "plrty",
        "BESTSELLERS": "bstslr",
        "PRICE": "plth",
        "DISCOUNT": "dhtl",
        "FRESH_ARRIVALS": "rec",
    }

    def __init__(self, *args, **kwargs):
        super(SnapdealProductSpider, self).__init__(*args, **kwargs)
        self.sort_by = self.SORT_MODES.get(
            kwargs.get("sort_mode", "RELEVANCE"))
        self.SEARCH_URL = ("http://www.snapdeal.com/acors/json/product/get/"
        "search/0/0/20?q=&sort=%s&keyword={search_term}&clickSrc=go_header"
        "&viewType=List&lang=en&snr=false" % (self.sort_by,))

    def parse_product(self, response):
        product = response.meta.get("product")
        reqs = []

        product["locale"] = "en_US"

        title = is_empty(response.xpath(
            "//h1[@itemprop='name']/text()").extract())
        cond_set(product, "title", (title,))

        brand = guess_brand_from_first_words(title)
        if brand:
            product["brand"] = brand

        cond_set(product, "image_url", response.xpath(
            "//ul[@id='product-slider']/li[1]/img/@src").extract())

        model = is_empty(response.xpath(
            "//div[contains(@class, 'buybutton')]/a/@supc").extract())
        if model:
            product["model"] = model

        cond_set(product, "description", response.xpath(
            "//div[contains(@class, 'details-content')]").extract())

        price = is_empty(response.xpath(
            "//span[@id='selling-price-id']/text()").extract())

        if price:
            priceCurrency = is_empty(response.xpath(
                "//meta[@itemprop='priceCurrency']/@content").extract())
            product["price"] = Price(
                priceCurrency=priceCurrency or "INR", price=price)

            market_name = is_empty(response.xpath(
                "//span[@id='vendorName']/text()").extract())
            if market_name:
                product["marketplace"] = [{
                    "name": market_name, 
                    "price": price,
                    "priceCurrency": priceCurrency,
                }]

        if "is currently unavailable" in response.body_as_unicode():
            product["is_out_of_stock"] = True
        else:
            product["is_out_of_stock"] = False

        pid = is_empty(response.xpath("//div[@id='pppid']/text()").extract())
        if not pid:
            pid = is_empty(re.findall("/(\d+)", response.url))

        if pid:
            buyer_reviews_url = Request(
                url=self.REVIEWS_URL.format(id=pid),
                callback=self.parse_buyer_reviews,
                dont_filter=True,
            )
            reqs.append(buyer_reviews_url)

        related_products = [{"similar products": []}]
        a = response.xpath("//div[contains(@class, 'product_grid_box')]"
            "/.//div[contains(@class, 'product-title')]/a")

        for item in a:
            title = is_empty(item.xpath("text()").extract(), "").strip()
            link = is_empty(item.xpath("@href").extract(), "")
            related_products[0]["similar products"].append(
                RelatedProduct(title=title, url=link)
            )

        if related_products[0]["similar products"]:
            product["related_products"] = related_products

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def send_next_request(self, reqs, response):
        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)


    def parse_buyer_reviews(self, response):
        product = response.meta.get("product")
        reqs = response.meta.get("reqs")
        total = 0

        rev = is_empty(re.findall("temp\s+=\s+\(([^\)]*)", response.body))
        if rev:
            try:
                rev = json.loads(rev)
            except ValueError:
                rev = {}
            for v in rev.values():
                total += int(v)

        avg = is_empty(response.xpath(
            "//p[contains(@class, 'ig-heading')]/span/text()").extract(), 0)
        if avg:
            avg = float(is_empty(re.findall("([^\/]*)", str(avg)),0))

        if avg and total:
            product["buyer_reviews"] = BuyerReviews(
                num_of_reviews=total, average_rating=avg, rating_by_star=rev)
        else:
            product["buyer_reviews"] = 0

        if reqs:
            return self.send_next_request(reqs)

        return product

    def _scrape_total_matches(self, response):
        total_matches = is_empty(response.xpath(
            "//b[@id='no-of-results-filter']/text()").extract(), "0")
        return int(total_matches.replace("+", ""))

    def _scrape_product_links(self, response):
        links = []
        try:
            data = json.loads(response.body_as_unicode())
            if data.get("status", "") == "Fail":
                self.STOP = True
            for item in data.get("productOfferGroupDtos") or []:
                url = urljoin(
                    "http://www.snapdeal.com", item.get("pageUrl", ""))
                links.append(url)
        except ValueError:
            links = response.xpath(
                "//a[@id='prodDetails']/@href").extract()
            if not links:
                links = response.xpath(
                    "//a[contains(@class, 'prodLink')]/@href").extract()

        for link in links:
            yield (link, SiteProductItem())

    def _scrape_next_results_page_link(self, response):
        if self.STOP:
            return None
        url = self.NEXT_PAGI_PAGE.format(
            term=self.searchterms[0], pos=self.position, sort=self.sort_by)
        self.position += 50
        return url

    def _parse_single_product(self, response):
        return self.parse_product(response)
       
