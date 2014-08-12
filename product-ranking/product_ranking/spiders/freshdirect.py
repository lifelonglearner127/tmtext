from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import urlparse

from scrapy.log import ERROR

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value


def strip_cond_set(item, key, values, conv=lambda l: l[0].strip()):
    """
    Helper function to ease conditionally setting a value in a dict.
    Added strip()
    """
    values = list(values)  # Copy and materialize values.
    if not item.get(key) and values:
        item[key] = conv(values)


class FreshDirectProductsSpider(BaseProductsSpider):
    name = "freshdirect_products"
    allowed_domains = ["freshdirect.com"]
    start_urls = []

    SEARCH_URL = "https://www.freshdirect.com/search.jsp?" \
        "searchParams={search_term}&view=grid&refinement=1"

    def parse_product(self, response):
        prod = response.meta['product']

        title = response.xpath('//h1[@class="pdpTitle"]/text()').extract()
        strip_cond_set(prod, 'title', title)

        price = response.xpath('//div[@class="pdp-price"]/text()').extract()
        if price:
            price = price[0].strip()
            if price:
                prod['price'] = price
            else:
                price = response.xpath(
                    '//span[@class="save-price"]/text()').extract()
                strip_cond_set(prod, 'price', price)

        des = response.xpath(
            '//div[contains(@class,"pdp-accordion-description-description")]'
            '//text()'
        ).extract()
        des = ''.join(i.strip() for i in des)
        cond_set_value(prod, 'description', des)

        img_url = response.xpath(
            '//div[@class="main-image"]/img/@src').extract()
        if img_url:
            prod['image_url'] = urlparse.urljoin(response.url, img_url[0])

        model = response.xpath(
            '//div[@class="pdp-productconfig"]//input[@name="skuCode"]/@value'
        ).extract()
        strip_cond_set(prod, 'model', model)

        cond_set(prod, 'locale', ['en-US'])
        prod['url'] = response.url

        related_products = []
        for li in response.xpath(
                '//div[@class="pdp-likethat"]'
                '//li[contains(@class,"portrait-item")]'
        ):
            url = None
            urls = li.xpath(
                './/div[@class="portrait-item-header"]/a/@href').extract()
            if urls:
                url = urlparse.urljoin(response.url, urls[0])

            title = None
            titles = li.xpath(
                './/div[@class="portrait-item-header"]/a//text()').extract()
            if titles:
                title = titles[0].strip()

            if url and title:
                related_products.append(RelatedProduct(title, url))

        if related_products:
            prod['related_products'] = {'recommended': related_products}

        return prod

    def _search_page_error(self, response):
        if not self._scrape_total_matches(response):
            self.log("Freshdirect: unable to find a match", ERROR)
            return True
        return False

    def _scrape_total_matches(self, response):
        try:
            count = response.xpath(
                '//span[@class="itemcount"]/text()').extract()[0]
            return int(count)
        except IndexError:
            return 0

    def _scrape_product_links(self, response):
        for link in response.xpath(
                '//div[@class="items"]//div[@class="grid-item-name"]/a/@href'
        ).extract():
            link = urlparse.urljoin(response.url, link)
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        links = response.xpath('//span[@class="pager-next"]/a/@href').extract()

        if links:
            link = urlparse.urljoin(response.url, links[0])
        else:
            link = None

        return link
