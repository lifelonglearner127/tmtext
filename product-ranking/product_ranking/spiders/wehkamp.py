from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set
from scrapy.log import ERROR


class WehkampProductsSpider(BaseProductsSpider):
    name = 'wehkamp_products'
    allowed_domains = ["wehkamp.nl"]
    start_urls = []
    SEARCH_URL = \
        "http://www.wehkamp.nl/Winkelen/SearchOverview.aspx" \
        "?N=186&Nty=1&Ntk=ART&Ztb=False&VIEW=Grid&Ntt={search_term}"

    def parse_product(self, response):

        product = response.meta['product']

        cond_set(
            product,
            'title',
            response.xpath(
                "//div[@class='pdp-topmatter']"
                "/h1[@itemprop='name']/text()").extract(),
            conv=string.strip
        )

        cond_set(
            product,
            'brand',
            response.xpath(
                "//div[@class='merk']/a"
                "/img[@class='brandLogo']/@title").extract()
        )

        cond_set(
            product,
            'image_url',
            response.xpath(
                "//img[@id='mainImage']/@src").extract()
        )

        cond_set(
            product,
            'price',
            response.xpath(
                "//div[@class='priceblock']"
                "/span[@class='price']/text()").extract()
        )

        cond_set(
            product,
            'upc',
            response.xpath(
                "//input[@id='EanCode']/@value").extract(),
            conv=int
        )

        cond_set(
            product,
            'locale',
            response.xpath(
                "//html/@lang").extract()
        )

        j = response.xpath(
            "//div[@id='extraInformatie']/"
            "/descendant::*[text()]/text()")
        info = "\n".join(
            [x.strip() for x in j.extract() if len(x.strip()) > 0])

        j2 = response.xpath(
            "//div[@id='kenmerkenOverzicht']/"
            "/descendant::*[text()]/text()")
        info2 = " ".join(
            [x.strip() for x in j2.extract() if len(x.strip()) > 0])

        product['description'] = info + info2

        rel = response.xpath(
            "//div[@id='bijverkopen']/div[contains(@class,'product')]")
        prodlist = []
        for r in rel:
            try:
                href = r.xpath('a/@href').extract()[0]
                title = r.xpath('a/span/span/text()').extract()[0]
                prodlist.append(RelatedProduct(title, href))
            except (ValueError, KeyError, IndexError):
                pass
        if prodlist:
            product['related_products'] = {"recommended": prodlist}

        return product

    def _scrape_total_matches(self, response):
        total = response.xpath(
            "//div[@class='resultsHeader']/p"
            "/text()").re(r'" geeft (\d+) resultaten.')
        if total:
            total = total[0].replace(".", "")
            try:
                return int(total)
            except ValueError:
                return 0
        else:
            return 0

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//ul[@id='articleList']/li[contains(@class,'article-card')]"
            "/a/@href").extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath(
            "//ul[contains(@class,'js-pagination')]"
            "/li[contains(@class,'pagination-page-next')]/a/@href")
        if next:
            return next.extract()[0]
