from __future__ import division, absolute_import, unicode_literals

import re

from scrapy.log import ERROR, WARNING, INFO

from product_ranking.items import SiteProductItem, Price, LimitedStock
from product_ranking.spiders import BaseProductsSpider, cond_set


class HepsiburadaProductsSpider(BaseProductsSpider):
    name = 'hepsiburada_products'
    allowed_domains = ["hepsiburada.com"]
    start_urls = []

    SEARCH_URL = "http://www.hepsiburada.com/liste/search.aspx?sText={search_term}"

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):

        product = response.meta['product']

        available = response.xpath(
            '//span[@id="ctl00_ContentPlaceHolder1_ProductControl1_'\
            'MainControl1_ProductMain1_spanLimitedStockCount"]/text()'
        ).extract()
        if available:
            quantity = re.findall("(\d+)", available[0])
            if quantity:
                lim = LimitedStock(is_limited=True,
                                   items_left=int(quantity[0]))
                cond_set(product, 'limited_stock', [lim])

        self._populate_from_open_graph(response, product)

        self._populate_from_js(response, product)

        #title = response.xpath("//title/text()").extract()[0]

        product['locale'] = "tr-TR"

        return product

    def _populate_from_js(self, response, product):
        scripts = response.xpath(
            "//script[contains(text(), 'var utag_data=')]")
        if not scripts:
            self.log("No JS matched in %s." % response.url, WARNING)
            return

        cond_set(product, 'upc', scripts.re("product_sku:'(.+)[']"))
        cond_set(product, 'brand', scripts.re("product_brand:'(.+)[']"))
        price = scripts.re("product_price:'(.+)[']")
        if price:
            product['price'] = Price(price=price[0],
                                     priceCurrency='TRY')

    def _populate_from_open_graph(self, response, product):
        """See about the Open Graph Protocol at http://ogp.me/"""
        # Extract all the meta tags with an attribute called property.
        metadata_dom = response.xpath("/html/head/meta[@property]")
        props = metadata_dom.xpath("@property").extract()
        conts = metadata_dom.xpath("@content").extract()

        # Create a dict of the Open Graph protocol.
        metadata = {p[3:]: c for p, c in zip(props, conts)
                    if p.startswith('og:')}

        # There are many types for this site so here we just log what type was encountered.
        if metadata.get('type') != 'product':
            # This response is not a product?
            self.log("Page of type '%s' found." % metadata.get('type'), INFO)

        # Basic Open Graph metadata.
        product['url'] = metadata['url']  # Canonical URL for the product.
        product['image_url'] = metadata['image']
        product['title'] = metadata['title']
        product['description'] = metadata['description']

    def _scrape_total_matches(self, response):
        num_results = response.xpath(
            "//span[@id='ctl00_ContentPlaceHolder1_IdsUIControl1_spnTotalProductCount_"
            "FoundInAllCatalogs']/text()").extract()[0]

        if num_results:
            return int(num_results.replace(".", ""))
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//div[@class='fleft w220 mt10']/a/@href").extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next_pages = response.xpath(
            "//link[@rel='next']/@href").extract()
        next_page = None
        if len(next_pages) == 1:
            next_page = next_pages[0]
        elif len(next_pages) == 0:
            self.log("Found no 'next page' link.", ERROR)
        return next_page

