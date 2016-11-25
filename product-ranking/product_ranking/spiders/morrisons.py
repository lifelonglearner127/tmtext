# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals

from scrapy.log import ERROR

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FormatterWithDefaults, populate_from_open_graph


class MorrisonsProductsSpider(BaseProductsSpider):
    name = 'morrisons_products'
    allowed_domains = ["morrisons.com"]
    start_urls = []

    SEARCH_URL = "https://groceries.morrisons.com/webshop" \
        "/getSearchProducts.do?groupSimilarProducts=y&sortBy={search_sort}" \
        "&itemsPerPage=See+all&clearTabs=yes&entry={search_term}"

    SEARCH_SORT = {
        'best_match': 'default',
        'product_name_ascending': 'name_asc',
        'product_name_descending': 'name_desc',
        'high_price': 'price_desc',
        'low_price': 'price_asc',
        'best_sellers': 'customer_rating',
        'shortest_shelf_life': 'shelf_life',
    }

    def __init__(self, search_sort='best_sellers', *args, **kwargs):
        super(MorrisonsProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self.SEARCH_SORT[search_sort]
            ),
            *args,
            **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        product = response.meta['product']

        populate_from_open_graph(response, product)

        brand = response.xpath("//span[@itemprop='name']/text()").extract()
        cond_set(product, 'brand', brand)

        price = response.xpath("//meta[@itemprop='price']/@content").extract()
        cond_set(product, 'price', price)

        if product.get('price', None):
            if not u'£' in product.get('price', ''):
                if product['price'].strip().endswith('p'):
                    product['price'] = u'£0.%s' % product['price'].replace(
                        'p', '').strip()
                elif product['price'].strip() == '0.0':
                    product['price'] = '£0.0'
                else:
                    self.log('Invalid price at: %s' % response.url,
                             level=ERROR)
            if u'£' in product['price']:
                product['price'] = Price(
                    price=product['price'].replace(u'£', '').replace(
                        ',', '').replace(' ', '').strip(),
                    priceCurrency='GBP'
                )

        upc = response.xpath("//meta[@itemprop='sku']/@content").extract()
        cond_set(product, 'upc', upc, conv=int)

        title = response.xpath("//strong[@itemprop='name']/text()").extract()
        cond_set(product, 'title', title)

        product['locale'] = "en-GB"

        return product

    def _scrape_total_matches(self, response):
        num_results = response.xpath(
            "//input[@id='itemsTotal']/@value").extract()
        if num_results and num_results[0]:
            num_results = num_results[0]
            return int(num_results)
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//h4[@class='productTitle']/a/@href").extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next_pages = response.xpath("//a[@class='next']/@href").extract()
        next_page = None
        if len(next_pages) == 2:
            next_page = next_pages[0]
        elif len(next_pages) == 0:
            self.log("Found no 'next page' link.", ERROR)
        return next_page
