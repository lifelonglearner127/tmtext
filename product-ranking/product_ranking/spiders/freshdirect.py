from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import urlparse
import json

from scrapy.log import ERROR, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value


class FreshDirectProductsSpider(BaseProductsSpider):
    name = "freshdirect_products"
    allowed_domains = ["freshdirect.com"]
    start_urls = []

    SEARCH_URL = "https://www.freshdirect.com/search.jsp?" \
        "searchParams={search_term}&view=grid&refinement=1"

    def parse_product(self, response):
        prod = response.meta['product']

        prod['url'] = response.url

        self._populate_from_js(response, prod)

        self._populate_from_html(response, prod)

        cond_set_value(prod, 'locale', 'en-US')

        return prod

    def _populate_from_html(self, response, prod):
        des = response.xpath(
            '//div[contains(@class,"pdp-accordion-description-description")]'
            '//text()'
        ).extract()
        des = ''.join(i.strip() for i in des)
        cond_set_value(prod, 'description', des)

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

            title = ' '.join(s.strip() for s in li.xpath(
                './/div[@class="portrait-item-header"]//text()').extract())

            if url and title:
                related_products.append(RelatedProduct(title, url))
        cond_set_value(
            prod.setdefault('related_products', {}),
            'recommended',
            related_products,
        )

    def _populate_from_js(self, response, product):
        data_jsons = response.xpath('//script/text()').re(
            "productData=(\{.+\})")
        if not data_jsons:
            self.log("Could not get JSON match in %s" % response.url, WARNING)
        else:
            data = json.loads(data_jsons[0])

            brand = data.get('brandName')
            if brand:
                product['brand'] = brand

            price = data.get('price')
            if price:
                product['price'] = price

            img_url = data.get('productZoomImage')
            if img_url:
                product['image_url'] = urlparse.urljoin(response.url, img_url)

            title = data.get('productName')
            if title:
                product['title'] = title

            model = data.get('skuCode')
            if model:
                product['model'] = model

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
