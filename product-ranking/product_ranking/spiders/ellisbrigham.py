# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re
import urllib
import urlparse

from scrapy.log import ERROR
from scrapy.selector import Selector




from scrapy.http.cookies import CookieJar




from scrapy.http import Request
from product_ranking.guess_brand import guess_brand_from_first_words
from product_ranking.items import SiteProductItem, Price, BuyerReviews, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FormatterWithDefaults, FLOATING_POINT_RGEX

# scrapy crawl amazoncouk_products -a searchterms_str="iPhone"

currencys = {"£": "GBP","€": "EUR","$": "USD"}

is_empty = lambda x: x[0] if x else ""

user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64)) AppleWebKit/537.36" \
    " (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"

class EllisbrighamProductsSpider(BaseProductsSpider):
    name = "ellisbrigham_products"
    allowed_domains = ["www.ellis-brigham.com"]
    start_urls = []

    add_url = "http://www.ellis-brigham.com"
    sort_url = "01"
    
    SEARCH_URL = "http://www.ellis-brigham.com/search?s={search_term}"

    SORT_MODES = {
        "Most relevant": "01",
        "Most recent": "02",
        "Price (High - Low)": "03",
        "Price (Low - High)": "04",
        "Alphabetically": "05",
    }

    def __init__(self, *args, **kwargs):
        if "sort_modes" in kwargs:
            self.sort_url = self.SORT_MODES[kwargs["sort_modes"]]
        super(EllisbrighamProductsSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=urllib.quote_plus(st.encode('utf-8')),
                ),
                meta={'search_term': st, 'remaining': self.quantity},
                callback=self.set_sort,
                dont_filter=True,
            )

    def set_sort(self, response):
        EVT = "ctl00$ctl00$ContentPlaceHolder1$SearchResults_1$rptSort$ctl%s$lbtnSortBy" % (self.sort_url,)
        CTL = "ctl00$ctl00$ContentPlaceHolder1$SearchResults_1$upSearch|"
        data = urllib.urlencode(self.collect_data_for_request(response, EVT, CTL))
        return self.compose_request(response, self.scrape_requests, data)

    def scrape_requests(self, response):
        cookieJar = response.meta.setdefault('cookiejar', CookieJar())
        self.coockies = cookieJar.extract_cookies(response, response.request)
        self.cookie = {}
        for c in cookieJar:
            self.cookie[c.name] = c.value

        for req in super(EllisbrighamProductsSpider, self).start_requests():
            req.cookies = self.cookie
            yield req

    def parse_product(self, response):
        prod = response.meta['product']

        title = response.xpath('//div[contains(@class, "product-detail")]/h1/text()').extract()
        if title:
            cond_set(prod, 'title', (title[0].strip(),))
        brand = response.xpath('//title/text()').extract()
        if brand:
            cond_set(prod, 'brand', (guess_brand_from_first_words(brand[0].strip()),))

        price = response.xpath('//div[@class="product-detail"]/h2/span[@class="price"]/text()').extract()
        if price:
            price = price[0].strip().replace(',', '').strip()
            currency = is_empty(re.findall("£|€|$", price[0]))
            price = re.findall("\d+.{0,1}\d+", price)
            if currency not in currencys:
                 self.log('Currency symbol not recognized: %s' % response.url,
                          level=ERROR)
            else:
                prod['price'] = Price(
                    priceCurrency=currencys[currency],
                    price=price[0]
                )

        image_url = response.xpath('//div[@class="product-detail-zoom"]/a/@href').extract()
        if image_url:
            image_url = "http:" + image_url[0]
        else:
            image_url = response.xpath('//div[@class="product-detail-zoom"]/img/@src').extract()
            image_url = "http:" + image_url[0]
        cond_set(prod, "image_url", (image_url,))

        desc = response.xpath('//div[@class="product-detail"]/p/text()').extract()
        if desc:
            cond_set(prod, 'description', (desc[0].strip(),))

        reviews = response.xpath('//span[@class="rating"]')
        average_rating = reviews.xpath('img/@src').extract()
        if average_rating:
            average_rating = re.findall("star-(\d+)", average_rating[0])
        num_of_reviews = reviews.xpath('text()').re(FLOATING_POINT_RGEX)
        if num_of_reviews or average_rating:
            prod["buyer_reviews"] = BuyerReviews(
                num_of_reviews=int(is_empty(num_of_reviews)),
                average_rating=float(is_empty(average_rating)),
                rating_by_star=None
            )

        rp = []
        for el in response.xpath('//ul[@class="product-recommend"]/li'):
            title = is_empty(el.xpath('div//a/text()').extract())
            url = is_empty(el.xpath('div//a/@href').extract())
            if url:
                url = str(self.add_url + url)
            if title or url:
                item = RelatedProduct(title=title, url=url)
                if item not in rp:
                    rp.append(item)
        prod["related_products"] = rp

        prod["locale"] = "en_GB"
        prod['url'] = response.url
        return prod

    def _scrape_total_matches(self, response):
        total_matches = response.xpath('//li[@class="search-results"]/text()').re(FLOATING_POINT_RGEX)
        if total_matches:
            return int(total_matches[0])    
        return 0

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[@class="product-description"]/h3/a/@href').extract()
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        if response.xpath('//div[@class="pagination-right"]/a[last()]/@href').extract():
            EVT = "ctl00$ctl00$ContentPlaceHolder1$SearchResults_1$PagingCtrl1$lbtnNext"
            CTL = "ctl00$ctl00$ContentPlaceHolder1$SearchResults_1$upnlFilter|"
            data = urllib.urlencode(self.collect_data_for_request(response, EVT, CTL))
            return self.compose_request(response, self.parse, data)
        return None

    def collect_data_for_request(self, response, EVT, CTL):
        VS = is_empty(response.xpath('//input[@id="__VIEWSTATE"]/@value').extract())
        VSG = is_empty(response.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value').extract())

        if not VS:
            VS = is_empty(re.findall("__VIEWSTATE\|([^\|]*)", response.body))
            VSG = is_empty(re.findall("__VIEWSTATEGENERATOR\|([^\|]*)", response.body))

        data = {
            "__EVENTTARGET": EVT,
            "ctl00$ctl00$sm": CTL+EVT,
            "__VIEWSTATE": VS,
            "__VIEWSTATEGENERATOR": VSG,
            "ctl00$ctl00$HeaderNavigation1$txtSearchText": "",
            "__ASYNCPOST": "true",
        }

        return data

    def compose_request(self, response, callback1, data):
        return Request(
                response.url,
                meta=response.meta,
                method="POST",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "User-Agent": user_agent,
                },
                body=data,
                callback=callback1,
                dont_filter=True,
            )