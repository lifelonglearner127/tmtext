from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urllib
import urlparse

from scrapy import Request
from scrapy.log import ERROR

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider
from product_ranking.spiders import cond_set, cond_set_value


def is_num(s):
    try:
        int(s.strip())
        return True
    except ValueError:
        return False


_TRANSLATE_TABLE = string.maketrans('', '')


def _normalize(s):
    """Returns a representation of a string useful for comparing words and
    disregarding punctuation.

    :param s: The string to normalize.
    :type s: unicode
    :return: Normalized string.
    :rtype: unicode
    """
    try:
        return s.lower().encode('utf-8').translate(
            _TRANSLATE_TABLE, string.punctuation).decode('utf-8')
    except UnicodeEncodeError:
        # Less efficient version.
        for c in string.punctuation:
            s = s.replace(c, '')
        return s


class CvsProductsSpider(BaseProductsSpider):
    name = 'cvs_products'
    allowed_domains = ["cvs.com"]
    start_urls = []

    SEARCH_URL = "http://www.cvs.com/search/_/N-0?searchTerm={search_term}" \
        "&pt=global&pageNum=1&sortBy=&navNum=20"

    def _set_brand(self, product, phrase, brands):
        phrase = _normalize(phrase)
        for brand in sorted(brands, key=len, reverse=True):
            if _normalize(brand) in phrase:
                cond_set_value(product, 'brand', brand)
                break

    def parse_product(self, response):
        brands = response.meta.get('brands', frozenset())
        product = response.meta['product']

        cond_set(product, 'title',
                 response.xpath("//h1[@class='prodName']/text()").extract())

        self._set_brand(product, product['title'], brands)
        if 'brand' not in product:
            descs = response.css('.brandBanner > a ::attr(title)')
            if descs:
                desc, = descs.extract()
                self._set_brand(product, desc, brands)

        if 'brand' not in product and 'is_single_result' in product:
            cond_set(product, 'brand', ['NOT RECOGNIZED FOR REQUEST BY URL.'])
        image_url = response.xpath(
            "//div[@class='productImage']/img/@src").extract()[0]
        product['image_url'] = urlparse.urljoin(response.url, image_url)

        size = response.xpath(
            "//form[@id='addCart']/table/tr/td[@class='col1']/"
            "text()[.='Size:']/../../td[2]/text()"
        ).extract()
        cond_set(product, 'model', size, conv=string.strip)

        addbasketbutton = response.xpath('//a[@id="addBasketButton"]')
        if not addbasketbutton:
            addbasketbutton = response.xpath('//div[@class="addBasket"]/a')

        if addbasketbutton:
            product['upc'] = int(addbasketbutton.xpath(
                '@data-upcnumber').extract()[0])
            product['price'] = addbasketbutton.xpath(
                '@data-listprice').extract()[0]
            if product.get('price', None):
                if not '$' in product['price']:
                    self.log('Unknown currency at' % response.url)
                else:
                    product['price'] = Price(
                        price=product['price'].replace(',', '').replace(
                            '$', '').strip(),
                        priceCurrency='USD'
                    )

        desc = response.xpath("//div[@id='prodDesc']/p/text()")
        desc = (" ".join(desc.extract())).strip()
        product['description'] = desc

        product['locale'] = "en-US"

        return product

    def _scrape_total_matches(self, response):
        totals = response.xpath("//form[@id='topForm']/strong/text()").re(
            r'Results.*of (\d+)')
        if len(totals) > 1:
            self.log(
                "Found more than one 'total matches' for %s" % response.url,
                ERROR
            )
        elif totals:
            total = totals[0].strip()
            return int(total)
        else:
            self.log(
                "Failed to find 'total matches' for %s" % response.url,
                ERROR
            )
        return None

    def _scrape_product_links(self, response):

        def full_url(url):
            return urlparse.urljoin(response.url, url)

        links = response.xpath(
            "//div[contains(@class, 'product')]/"
            "div[contains(@class, 'innerBox')]/"
            "div[contains(@class, 'productSection1')]/a/@href"
        ).extract()

        brands = response.meta.get('brands', set())
        brands.update(response.xpath(
            "//ul[@id='Brand']/li/label/span/a/text()").re(r'\s+(.*)\s\(.*\)'))

        if not links:
            self.log("Found no product links.", ERROR)

        for link in links:
            prod_item = SiteProductItem()
            new_meta = response.meta.copy()
            new_meta['brands'] = brands
            new_meta['product'] = prod_item
            yield (
                Request(full_url(link), self.parse_product, meta=new_meta),
                prod_item,
            )

    def _scrape_next_results_page_link(self, response):
        url_parts = urlparse.urlsplit(response.url)
        query_string = urlparse.parse_qs(url_parts.query)

        current_page_num = int(query_string.get("pageNum", [1])[0])

        last_page_num = max(
            int(value.strip())
            for value in response.xpath(
                '//form[@id="topForm"]/*/text()').extract()
            if is_num(value)
        )

        if current_page_num == last_page_num:
            link = None  # No next page.
        else:
            query_string["pageNum"] = [current_page_num + 1]
            url_parts = url_parts._replace(
                query=urllib.urlencode(query_string, True))
            link = urlparse.urlunsplit(url_parts)
        return link

    def _parse_single_product(self, response):
        return self.parse_product(response)
