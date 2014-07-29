from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re

from scrapy.log import ERROR
from scrapy.selector import Selector

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set


def cond_set_re(item, key, match, conv=lambda l: l[0]):
    if match:
        cond_set(item, key, match.groups(), conv=conv)


def brand_at_start(brand):
    words = len(brand.split())

    return (
        lambda t: t.lower().startswith(brand.lower()),
        lambda _: brand,
        lambda t: ' '.join(t.split(' ', words + 1)[words:]),
    )


class TescoProductsSpider(BaseProductsSpider):
    name = 'tesco_products'
    allowed_domains = ["tesco.com"]

    SEARCH_URL = "http://www.tesco.com/groceries/product/search/default.aspx" \
        "?searchBox={search_term}&icid=tescohp_sws-1_{search_term}&N=0&Nao=0"

    KNOWN_BRANDS = (
        brand_at_start('Dri Pak'),
        brand_at_start('Girlz Only'),
        brand_at_start('Alberto Balsam'),
        brand_at_start('Mum & Me'),
        brand_at_start('Head & Shoulder'),  # Also matcher Head & Shoulders.
        brand_at_start('Ayuuri Natural'),
        (lambda t: ' method ' in t.lower(),
         lambda _: 'Method',
         lambda t: t
         ),
        (lambda t: t.lower().startswith('dr ') or t.lower().startswith('dr. '),
         lambda t: ' '.join(t.split()[:2]),
         lambda t: ' '.join(t.split()[2:])
         ),
    )

    @staticmethod
    def brand_from_title(title):
        brand = None
        new_title = None
        for recognize, parse_brand, clean_title \
                in TescoProductsSpider.KNOWN_BRANDS:
            if recognize(title):
                brand = parse_brand(title)
                new_title = clean_title(title)
                break
        else:
            brand = title.split()[0]
            new_title = ' '.join(title.split()[1:])
        return brand, new_title

    def parse_product(self, response):
        sel = Selector(response)

        p = response.meta['product']

        self._populate_from_js(response.url, sel, p)

        self._populate_from_html(response.url, sel, p)

        cond_set(p, 'locale', ['en-GB'])  # Default locale.

        return p

    def _populate_from_html(self, url, sel, product):
        cond_set(product, 'title',
                 sel.css('div.productDetails > h1 ::text').extract())
        # XPath indexes are base 1, so the first div is selected.
        cond_set(product, 'description',
                 sel.xpath('//div[@class="content"][1]/node()').extract(),
                 conv=lambda vals: ''.join(vals))
        cond_set(product, 'locale', sel.xpath('/html/@lang').extract())

    def _populate_from_js(self, url, sel, product):
        js_data = sel.xpath("/html/head/script").re(
            r"new TESCO\.sites\.UI\.entities\.Product\((\{.+\})\);")
        if not js_data:
            msg = "No JS matched in %s" % url
            self.log(msg, ERROR)
            raise AssertionError(msg)
        if len(js_data) > 1:
            msg = "Matched multiple script blocks in %s" % url
            self.log(msg, ERROR)
            raise AssertionError(msg)
        js = js_data[0]

        cond_set_re(product, 'model',
                    re.search(r'[,{]productId:\s*"(.+?)",', js))
        cond_set_re(product, 'price',
                    re.search(r'[,{]price:\s*((\d*\.)?\d+),', js),
                    conv=lambda gs: float(gs[0]))
        cond_set_re(product, 'image_url',
                    re.search(r'[,{]imageURL:\s*"(.+?)",', js))

        m = re.search(r'[,{]name:\s*"(.+?)",', js)
        if m:
            brand, title = self.brand_from_title(m.group(1))
            cond_set(product, 'brand', [brand])
            cond_set(product, 'title', [title])

    def _scrape_total_matches(self, sel):
        return int(sel.css("span.pageTotalItemCount ::text").extract()[0])

    def _scrape_product_links(self, sel):
        # JS and locale of the products is available at this point.
        # If HTML parsing were not necessary, fetching product pages could be
        # skipped. Currently only the description needs the product page.

        links = sel.css('h3.inBasketInfoContainer > a ::attr(href)').extract()
        if not links:
            self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, sel):
        next_pages = sel.css('p.next > a ::attr(href)').extract()
        next_page = None
        if len(next_pages) == 2:
            next_page = next_pages[0]
        elif len(next_pages) > 2:
            self.log("Found more than two 'next page' link.", ERROR)
        return next_page
