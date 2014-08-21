from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set, FormatterWithDefaults
from scrapy.log import ERROR


class MorrisonsProductsSpider(BaseProductsSpider):
    name = 'morrisons_products'
    allowed_domains = ["morrisons.com"]
    start_urls = []

    # SEARCH_URL = "https://groceries.morrisons.com/webshop/getSearchProducts.do?clearTabs=yes" \
    #              "&isFreshSearch=true&entry={search_term}"

    SEARCH_URL = "https://groceries.morrisons.com/webshop/getSearchProducts.do?" \
                 "groupSimilarProducts=y&sortBy={search_sort}&itemsPerPage=See+all&" \
                 "clearTabs=yes&entry={search_term}"

    SEARCH_SORT = {
        'best_match': 'default',
        'product_name_ascending': 'name_asc',
        'product_name_descending': 'name_desc',
        'high_price': 'price_desc',
        'low_price': 'price_asc',
        'best_sellers': 'default',
        'rating': 'customer_rating',
        'shelf_life': 'shelf_life',
    }

    def __init__(self, search_sort='best_sellers', *args, **kwargs):
        super(MorrisonsProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self.SEARCH_SORT[search_sort]
            ),
            *args,
            **kwargs)

    def parse_product(self, response):
        product = response.meta['product']

        self._populate_from_open_graph(response, product)

        brand = response.xpath(
            "//span[@itemprop='name']/text()").extract()
        cond_set(product, 'brand', brand)

        price = response.xpath(
            "//meta[@itemprop='price']/@content").extract()
        cond_set(product, 'price', price)

        upc = response.xpath(
            "//meta[@itemprop='sku']/@content").extract()
        cond_set(product, 'upc', upc)

        product['locale'] = "en-GB"

        return product

    def _populate_from_open_graph(self, response, product):
        """See about the Open Graph Protocol at http://ogp.me/"""
        # Extract all the meta tags with an attribute called property.
        metadata_dom = response.xpath("/html/head/meta[@property]")
        props = metadata_dom.xpath("@property").extract()
        conts = metadata_dom.xpath("@content").extract()

        # Create a dict of the Open Graph protocol.
        metadata = {p[3:]: c for p, c in zip(props, conts)
                    if p.startswith('og:')}

        if metadata.get('type') != 'product':
            # This response is not a product?
            self.log("Page of type '%s' found." % metadata.get('type'), ERROR)
            raise AssertionError("Type missing or not a product.")

        # Basic Open Graph metadata.
        product['url'] = metadata['url']  # Canonical URL for the product.
        product['image_url'] = metadata['image']
        product['description'] = metadata['description']
        product['title'] = metadata['title']

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

