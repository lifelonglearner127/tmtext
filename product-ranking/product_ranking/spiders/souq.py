from __future__ import division, absolute_import, unicode_literals

import re
import json

from scrapy.http import Request
from scrapy.log import INFO
from scrapy.selector import Selector

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, FLOATING_POINT_RGEX
from product_ranking.spiders import FormatterWithDefaults


is_empty = lambda x,y=None: x[0] if x else y


class SouqProductsSpider(BaseProductsSpider):
    name = 'souq_products'
    allowed_domains = ["souq.com"]
    start_urls = []
    SEARCH_URL = "http://uae.souq.com/ae-en/{search_term}/s/?sortby={sort_by}"
    _RECOM_URL = "http://uae.souq.com/ae-en/item_one.php?action=get_views_box&"

    counter = 2

    SORT_MODES = {
        "default": "",
        "bestmatch": "",
        "popularity": "sr",
        "pricelh": "cp_asc",
        "pricehl": "cp_desc",
    }

    def __init__(self, sort_mode="default", *args, **kwargs):
        if sort_mode not in self.SORT_MODES:
            self.log('"%s" not in SORT_MODES')
            sort_mode = 'default'
        formatter = FormatterWithDefaults(sort_by=self.SORT_MODES[sort_mode])
        super(SouqProductsSpider, self).__init__(
            formatter,
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        product = response.meta['product']

        product["title"] = is_empty(response.xpath(
            '//div/h1[@itemprop="name"]/text()').extract())

        product["image_url"] = is_empty(response.xpath(
            "//div[contains(@class, 'img-bucket')]/img/@src").extract())

        price = is_empty(response.xpath(
            "//div/h3[contains(@class, 'price')]/text()"
        ).re(FLOATING_POINT_RGEX))
        priceCurrency = is_empty(response.xpath(
            "//div/h3[contains(@class, 'price')]/" \
            "small[contains(@class, 'currency')]/text()"
        ).extract())
        if price:
            product["price"] = Price(price=price, priceCurrency=priceCurrency)
        
        product["description"] = is_empty(response.xpath(
            '//ul/li[@id="description"]').extract())

        product["brand"] = is_empty(response.xpath(
            "//dl[contains(@class, 'stats')]/" \
            "dt[contains(text(), 'Brand')]/following::dd/text()"
        ).extract())

        seller_all = response.xpath(
            "//dl[contains(@class, 'stats')]" \
            "/dt[contains(text(), 'Sold by:')]/following::dd/span/a")
        seller = is_empty(seller_all.xpath("text()").extract())
        if seller:
            product["marketplace"] = [{
                "price": product["price"], 
                "name": seller
            }]

        product["model"] = is_empty(response.xpath(
            "//dl[contains(@class, 'stats')]/" \
            "dt[contains(text(), 'Item EAN')]/following::dd/text()"
        ).extract())

        is_out_of_stock = is_empty(response.xpath(
            '//span[contains(@class, "label")]/strong/text()').extract(), "")
        if "In Stock" in is_out_of_stock:
            product["is_out_of_stock"] = False
        else:
            product["is_out_of_stock"] = True

        average = is_empty(response.xpath(
            "//div[contains(@class, 'mainRating')]/strong/text()").extract())
        num_of_reviews = is_empty(response.xpath(
            "//div[contains(@class, 'mainRating')]/following::h6/text()"
        ).re(FLOATING_POINT_RGEX))
        if average and num_of_reviews:
            rating_by_star = {}
            for item in response.xpath("//div[contains(@class, 'row')]" \
                "/div/div[contains(@class, 'review-rate ')]"):
                star = int(is_empty(item.xpath(
                    "div[1]/span/text()").re(FLOATING_POINT_RGEX)))
                rating_by_star[star] =  int(is_empty(item.xpath(
                    "div[last()]/span/text()").re(FLOATING_POINT_RGEX)))

            product["buyer_reviews"] = BuyerReviews(
                average_rating=average,
                num_of_reviews=num_of_reviews,
                rating_by_star=rating_by_star
            ) if num_of_reviews else ZERO_REVIEWS_VALUE
        elif response.css('[data-dropdown=REVIEWS_POPUP_BOX]'):
            product["buyer_reviews"] = ZERO_REVIEWS_VALUE

        product["locale"] = "en-US"

        id_item = is_empty(re.findall(
            "ItemIDs=\"(\d+)\"", response.body_as_unicode()))
        id_unit = is_empty(re.findall(
            "products=\"\;{0,1}(\d+)\"", response.body_as_unicode()))

        if id_item:
            url = self._RECOM_URL + "&id_item=" + id_item
            if id_unit:
                url += "&id_unit=" + id_unit

            count = is_empty(response.xpath(
                "//a[@id='MORE_OFFERS_LINK']/strong/text()"
            ).re(FLOATING_POINT_RGEX))
            meta = {
                "product": product,
            }
            if count:
                mtp_link = "http://uae.souq.com/ae-en/Action.php" \
                    "?action=ajaxRemote&type=getUnitsCondition" \
                    "&limit=%s&id_item=%s" % (count, id_item)
                meta["mtp_link"] = mtp_link
            
            return Request(url=url, callback=self._parse_recomendar, meta=meta)

        return product

    def _parse_recomendar(self, response):
        product = response.meta['product']
        jdata = {}
        try:
            jdata = json.loads(response.body)
        except ValueError:
            return product

        if "interest" in jdata:
            sel = Selector(text=jdata["interest"])
            titles = sel.xpath("//h6/a/text()").extract()
            links = sel.xpath("//h6/a/@href").extract()
            tl = is_empty(sel.xpath(
                '//div[contains(@class, "row")]/div/' \
                'h3[contains(@class, "slider-header")]/text()'
            ).extract(), "Customers Also Viewed").strip()
            if not titles:
                return product
            related_prod = dict(zip(iter(titles), iter(links)))
            related_prod = [RelatedProduct(title=k, url=v) for k, v in related_prod.items()]
            product["related_products"] = {tl: related_prod}

        if "mtp_link" in response.meta:
            meta = {"product": product}
            return Request(url=response.meta["mtp_link"], callback=self.parse_marketplace, meta=meta)

        return product

    def parse_marketplace(self, response):
        product = response.meta['product']

        try: 
            data = json.loads(response.body)
        except ValueError:
            return product

        sel = Selector(text=data.get("html", ""))

        marketplaces = []
        for seller in sel.xpath("//div[contains(@class, 'unit')]"):
            price = is_empty(seller.xpath(
                "div/div/div[contains(@class, 'larg-price')]/text()"
            ).re(FLOATING_POINT_RGEX))
            name = is_empty(seller.xpath(
                "div/div/span/a/text()"
            ).extract())

            marketplaces.append({
                "price": Price(price=price, priceCurrency="AED"),
                "name": name
            })

        if marketplaces:
            product["marketplace"] = marketplaces

        return product

    def _scrape_total_matches(self, response):
        total = is_empty(response.xpath(
            '//span[contains(@class, "listing-page-text")]/text()'
        ).re(FLOATING_POINT_RGEX))
        self.total = int(total) or 0
        if total:
            return int(total)
        self.log("No products found.", INFO)
        return 0

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//h6[contains(@class, 'result-item-title')]/a/@href").extract()
        if not links:
            self.log("No products links found.", INFO)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        url = response.url
        if "page=" in url:
            self.counter = self.counter + 1
            url = re.sub("page=(\d+)", "", url) + "page=" + str(self.counter)
        else:
            url += "&page=2"
        if self.total / 15 + 1 > self.counter:
            return url
        return None

    def _parse_single_product(self, response):
        return self.parse_product(response)
