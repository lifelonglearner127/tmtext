from __future__ import division, absolute_import, unicode_literals

import urlparse

from scrapy.log import ERROR

from product_ranking.items import SiteProductItem, RelatedProduct, Price
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FormatterWithDefaults, populate_from_open_graph


class StatelinetackProductsSpider(BaseProductsSpider):
    name = 'statelinetack_products'
    allowed_domains = ["statelinetack.com"]
    start_urls = []

    SEARCH_URL = "http://www.statelinetack.com/Search.aspx" \
        "?query={search_term}&page=1&hits=48&sort={search_sort}"

    URL = "http://www.statelinetack.com"

    SEARCH_SORT = {
        'best_match': '',
        'high_price': 'pricehigh',
        'low_price': 'pricelow',
        'best_sellers': 'bestselling',
        'avg_review': 'avgreview',
    }

    def __init__(self, search_sort='best_sellers', *args, **kwargs):
        super(StatelinetackProductsSpider, self).__init__(
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

        brand = response.xpath(
            "//*[@id='ctl00_ctl00_CenterContentArea_MainContent_lblBreadCrumb']"
            "/a[3]/text()"
        ).extract()
        cond_set(product, 'brand', brand)

        price = response.xpath("//*[@id='lowPrice']/text()").extract()
        cond_set(product, 'price', price)

        if product.get('price', None):
            product['price'] = Price(
                priceCurrency='USD',
                price=product['price'].replace(',', '').replace(
                    ' ', '').strip()
            )

        upc = response.xpath(
            "//*[@id='ctl00_ctl00_CenterContentArea_MainContent_HidBaseNo']"
            "/@value"
        ).extract()
        cond_set(product, 'upc', upc)

        cond_set(product, 'reseller_id', upc)

        title = response.xpath("//h2[@itemprop='name']/text()").extract()
        cond_set(product, 'title', title)

        description = response.xpath(
            "//*[@id='ctl00_ctl00_CenterContentArea_MainContent_lblDescriptionLong']/node()"
        ).extract()
        cond_set(product, 'description', [description])

        product['locale'] = "en-US"

        related = response.xpath("//*[@class='scroller']/ul/li//a[contains(@class, 'product-title')]")
        lrelated = []
        for rel in related:
            link = urlparse.urljoin(self.URL, rel.xpath('@href').extract()[0])

            ltitle = rel.xpath('text()').extract()[0]

            lrelated.append(RelatedProduct(ltitle.strip(), link))

        if lrelated:
            product['related_products'] = {"recommended": lrelated}

        return product

    def _scrape_total_matches(self, response):
        num_results = response.xpath(
            "//label[@class='search-page-label']/strong/text()").extract()
        if num_results and num_results[0]:
            return int(num_results[0])
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//a[@class='search-page-image-link']/@href").extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next_pages = response.xpath("//a[@class='next-button']/@href").extract()
        next_page = None
        if len(next_pages) == 2:
            next_page = next_pages[0]
        elif len(next_pages) == 0:
            self.log("Found no 'next page' link.", ERROR)
        return next_page
