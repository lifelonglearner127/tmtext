from __future__ import division, absolute_import, unicode_literals

import urllib
import json

from scrapy.http import Request
from scrapy.log import ERROR, INFO

from product_ranking.items import SiteProductItem, RelatedProduct, Price
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults


class PGShopProductSpider(BaseProductsSpider):
    name = 'pgestore_products'
    allowed_domains = ["pgshop.com", "pgestore.recs.igodigital.com"]

    SEARCH_URL = "http://www.pgshop.com/pgshop/" \
                 "?prefn1=showOnShop" \
                 "&q={search_term}&start={start}&sz=40" \
                 "&action=sort&srule={search_sort}" \
                 "&prefv1=1|2&appendto=0&pindex=3&ptype=ajax"

    SEARCH_SORT = {
        'product_name_ascending': 'A-Z',
        'product_name_descending': 'Z-A',
        'high_price': 'price-high-to-low',
        'low_price': 'price-low-to-high',
        'best_sellers': 'top-sellers',
        'rating': 'top rated',
        'default': 'default sorting rule',
    }

    RECOMMENDED_URL = "http://pgestore.recs.igodigital.com/a/v2/" \
                      "pgestore/product/recommend.json" \
                      "?item={upc}&amp;environment=PRD&amp;&amp;item_count=8"

    def __init__(self, search_sort='default', *args, **kwargs):
        # All this is to set the site_name since we have several
        # allowed_domains.
        super(PGShopProductSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self.SEARCH_SORT[search_sort],
                start=0,
            ),
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _scrape_total_matches(self, response):
        num_results = response.xpath(
            '//span[@class="number-copy"]/text()').extract()
        if num_results and num_results[0]:
            return int(num_results[0])
        else:
            no_result_div = response.xpath(
                '//div[@class="nosearchresult_div"]')
            if no_result_div:
                self.log("There is no result for this search term.", level=INFO)
                return 0
            else:
                return None

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//li[contains(@class, 'product-tile')]"
            "//p[@class='product-name']"
            "/a[contains(@class, 'name-link')]/@href").extract()
        if not links:
            if not response.xpath('//div[@class="nosearchresult_div"]'):
                self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        total_matches = response.meta.get('total_matches')
        start = response.meta.get('start', 0)

        if total_matches <= start or total_matches <= 40:
            return None

        start += 40
        if start > total_matches:
            start = total_matches
        response.meta['start'] = start

        search_term = response.meta.get('search_term')
        return self.url_formatter.format(
            self.SEARCH_URL,
            search_term=urllib.quote_plus(search_term.encode('utf-8')),
            start=start)

    def parse_product(self, response):
        prod = response.meta['product']
        prod['url'] = response.url
        prod['locale'] = 'en-US'

        title = response.xpath(
            '//*[@itemprop="name"]/text()').extract()
        if title:
            prod['title'] = title[0].strip()

        upc = response.xpath(
            '//*[@itemprop="productID"]/text()').extract()
        if upc:
            prod['upc'] = upc[0].strip()

        img = response.xpath(
            '//div[contains(@class, "x1-target")]/img/@src').extract()
        if img:
            prod['image_url'] = img[0].strip()

        price = response.xpath('//section[contains(@class, "price")]'
                               '//span[contains(@class,"price-sales")'
                               ' or contains(@class,"price-nosale")]'
                               '/text()').extract()
        if price:
            prod['price'] = price[0].strip()

        description = response.xpath(
            'string(//div[contains(@class,"accordion-content")])').extract()
        if description:
            prod['description'] = description[0].strip()

        brand = response.xpath(
            '//a[@class="cta"]/@title').re('Visit the (\w+) brand shop')
        if brand:
            prod['brand'] = brand[0]

        self._unify_price(prod)

        return Request(
            self.RECOMMENDED_URL.format(upc=prod['upc']),
            callback=self.parse_recommended_items,
            meta=response.meta.copy(),
        )

    def parse_recommended_items(self, response):
        prod = response.meta['product']
        data = json.loads(response.body)
        if not data:
            return prod

        data = data[0].get('items', None)
        if not data:
            return prod

        recommendations = []
        for item in data:
            url = item['link']
            title = item['name']
            recommendations.append(RelatedProduct(title, url))

        if recommendations:
            prod['related_products'] = {'recommended': recommendations}

        return prod

    def _unify_price(self, product):
        price = product.get('price')
        if price is None:
            return
        is_usd = not price.find('$')
        price = price[1:].replace(',', '')
        if is_usd and price.replace('.', '').isdigit():
            product['price'] = Price('USD', price)