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
    dump_url_to_file, FLOATING_POINT_RGEX
from product_ranking.guess_brand import guess_brand_from_first_words

is_empty = lambda x, y=None: x[0] if x else y

class SnapdealProductSpider(BaseProductsSpider):


    name = 'snapdeal_products'
    allowed_domains = ["www.snapdeal.com"]

    SEARCH_URL = ("http://www.snapdeal.com/acors/json/product/get/search"
        "/0/0/20?q=&sort={sort}&keyword={search_term}&clickSrc=go_header"
        "&viewType=List&lang=en&snr=false")

    START_URL = ("http://www.snapdeal.com/search?keyword={search_term}"
        "&santizedKeyword=&catId=&categoryId=&suggested=false&vertical="
        "&noOfResults=20&clickSrc=go_header&lastKeyword=&prodCatId="
        "&changeBackToAll=false&foundInAll=false&categoryIdSearched="
        "&cityPageUrl=&url=&utmContent=&catalogID=&dealDetail=")

    RELATED_URL = ("http://www.snapdeal.com/acors/json/"
        "getPersonalizationWidgetDataById?"
        "pogId={ppid}&categoryId={catId}&brandId={brandId}")

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

    tm = None

    def __init__(self, *args, **kwargs):
        super(SnapdealProductSpider, self).__init__(*args, **kwargs)
        self.sort_by = self.SORT_MODES.get(
            kwargs.get("sort_mode", "RELEVANCE"))
        self.SEARCH_URL = ("http://www.snapdeal.com/acors/json/product/get/"
        "search/0/0/20?q=&sort=%s&keyword={search_term}&clickSrc=go_header"
        "&viewType=List&lang=en&snr=false" % (self.sort_by,))

    def start_requests(self):
        if not self.product_url:
            yield Request(
                url=self.START_URL.format(search_term=self.searchterms[0]),
                callback=self.after_start,
            )
        else:
            for req in super(SnapdealProductSpider, self).start_requests():
                yield req

    def after_start(self, response):
        url = is_empty(response.xpath(
            "//div[contains(@class, 'viewallbox')]/a/@href").extract())
        if url:
            return Request(url=url, callback=self.after_start)
        self.tm = self._scrape_total_matches(response)
        return super(SnapdealProductSpider, self).start_requests()

    def parse_product(self, response):
        product = response.meta.get("product")
        reqs = []

        text = response.body_as_unicode()
        text = text.replace('_blank"', '').replace('target="', '')
        response = response.replace(body=text)

        product["locale"] = "en_US"

        title = is_empty(response.xpath(
            "//h1[@itemprop='name']/text()").extract())
        cond_set(product, "title", (title,))

        brand = guess_brand_from_first_words(title)
        if brand:
            product["brand"] = brand

        cond_set(product, "image_url", response.xpath(
            "//ul[@id='product-slider']/li[1]/img/@src |"
            "//img[@itemprop='image']/@src"
        ).extract())

        model = is_empty(response.xpath(
            "//div[contains(@class, 'buybutton')]/a/@supc |"
            "//div[@id='defaultSupc']/text()"
        ).extract())
        if model:
            product["model"] = model

        cond_set(product, "description", response.xpath(
            "//div[contains(@class, 'details-content')] |"
            "//div[itemprop='description' and class='detailssubbox']"
        ).extract())

        price = is_empty(response.xpath(
            "//span[@id='selling-price-id']/text() |"
            "//input[@id='productSellingPrice']/@value"
        ).extract())

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

        variantsJSON = is_empty(response.xpath(
            "//input[@id='productAttributesJson']/@value").extract())
        try:
            variants = json.loads(variantsJSON)
        except (ValueError, TypeError):
            variants = []

        product["variants"] = []
        default_cat_id = is_empty(response.xpath(
            "//div[@id='defaultCatalogId']/text()").extract())
        for variant in variants:
            dc = {
                variant.get("name", "color").lower(): variant.get("value"),
                "image_url": urljoin(
                    "http://n4.sdlcdn.com/", variant["images"][0]),
                "in_stock": not variant.get("soldOut", True),
                "selected": False,
            }
            if str(variant.get("id", -1)) == str(default_cat_id):
                dc["selected"] = True
            product["variants"].append(dc)
        if not product["variants"]:
            product["variants"] = None

        pid = is_empty(response.xpath(
            "//div[@id='pppid']/text() |"
            "//input[@id='pppid']/@value"
        ).extract())
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
            "/.//div[contains(@class, 'product-title')]/a |"
            "//div[contains(@class, 'product-txtWrapper')]/div/a"
        )

        for item in a:
            title = is_empty(item.xpath("text() | "
                ".//p[contains(@class, 'product-title')]/text()"
            ).extract(), "").strip()
            link = is_empty(item.xpath("@href").extract(), "")
            related_products[0]["similar products"].append(
                RelatedProduct(title=title, url=link)
            )

        if related_products[0]["similar products"]:
            product["related_products"] = related_products

        brandId = is_empty(response.xpath(
            "//div[@id='brndId']/text()").extract())
        catId = is_empty(response.xpath(
            "//div[@id='categoryId']/text()").extract())

        if brandId and catId and pid:
            url = self.RELATED_URL.format(
                ppid=pid, catId=catId, brandId=brandId)
            reqs.append(
                Request(
                    url=url,
                    callback=self.parse_related
                )
            )

        marketplace_link = is_empty(response.xpath(
            "//a[@id='buyMoreSellerLink']/@href").extract())
        if marketplace_link:
            marketplace_link = urljoin(
                "http://www.snapdeal.com/", marketplace_link)
            marketplace_req = Request(
                url=marketplace_link,
                callback=self.parse_marketplace,
            )
            reqs.append(marketplace_req)

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
            return self.send_next_request(reqs, response)

        return product

    def parse_marketplace(self, response):
        product = response.meta.get("product")
        reqs = response.meta.get("reqs")

        marketplace = []

        for div in response.xpath("//div[@id='mvfrstVisible']"
                "/div[contains(@class, 'cont')]"):
            name = is_empty(div.xpath(
                ".//a[contains(@class, 'mvLink')]/text()").extract(), "")
            price = is_empty(div.xpath(
                ".//strong/text()").re(FLOATING_POINT_RGEX), "")
            if price:
                price = Price(priceCurrency="INR", price=price)
            if name and price:
                marketplace.append({"price": price, "name": name.strip()})

        product["marketplace"] = marketplace

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def parse_related(self, response):
        product = response.meta.get("product")
        reqs = response.meta.get("reqs")
        related_products = []

        try:
            data = json.loads(response.body)
            for rp in data[0]["personalizationWidgetDTO"]["widgetData"]:
                related_products.append(RelatedProduct
                    (
                        title=rp.get("name"),
                        url=urljoin(
                            "http://snapdeal.com", rp.get("pageUrl", "")),
                    )
                )
        except (ValueError, TypeError, IndexError):
            data = []

        if related_products:
            product["related_products"] = related_products

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _scrape_total_matches(self, response):
        fl=open('file.html', 'w')
        fl.write(response.body)
        fl.close()
        if self.tm is None:
            total_matches = is_empty(re.findall(
                "totItmsFound\s+\=\s+(\d+)", response.body))
            if not total_matches:
                total_matches = is_empty(response.xpath(
                    "//span[@id='no-of-results-filter']/text() |"
                    "//b[@id='no-of-results-filter']/text()").extract(), "0")
            if not total_matches:
                total_matches = is_empty(response.xpath(
                    "//input[@id='resultsOnPage']/@value").extract())
            return int(total_matches.replace("+", ""))
        else:
            return self.tm

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
       
