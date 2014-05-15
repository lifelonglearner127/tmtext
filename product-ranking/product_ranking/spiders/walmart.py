from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse

from scrapy.log import ERROR, WARNING
from scrapy.selector import Selector

from product_ranking.items import SiteProductItem
from product_ranking.spiders import (BaseProductsSpider, FormatterWithDefaults,
                                     cond_set, compose)


class WalmartProductsSpider(BaseProductsSpider):
    name = 'walmart_products'
    allowed_domains = ["walmart.com"]

    SEARCH_URL = "http://www.walmart.com/search/search-ng.do?Find=Find" \
        "&_refineresult=true&ic=16_0&search_constraint=0" \
        "&search_query={search_term}&search_sort={search_sort}"

    SEARCH_SORT = {
        'best_match': 0,
        'high_price': 3,
        'low_price': 4,
        'best_sellers': 5,
        'newest': 6,
        'rating': 7,
    }

    def __init__(self, search_sort='best_match', *args, **kwargs):
        super(WalmartProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self.SEARCH_SORT[search_sort]),
            *args, **kwargs)

    def parse_product(self, response):
        sel = Selector(response)

        if self._search_page_error(response):
            self.log("Got 404 when coming from %s." % response.request.url,
                     ERROR)
            return

        p = response.meta['product']

        self._populate_from_open_graph(response.url, sel, p)

        self._populate_from_js(response.url, sel, p)

        self._populate_from_html(response.url, sel, p)

        cond_set(p, 'locale', ['en-US'])  # Default locale.

        return p

    def _search_page_error(self, response):
        path = urlparse.urlsplit(response.url)[2]
        return path == '/FileNotFound.aspx'

    def _populate_from_html(self, url, sel, product):
        # Since different chunks of invalid HTML keep appearing in this
        # element, I'll just dump whatever is in there.
        cond_set(product, 'title',
                 sel.xpath('//meta[@name="title"]/@content').extract())
        # TODO This source for the description is not reliable.
        cond_set(product, 'description',
                 sel.xpath('//*[@class="ql-details-short-desc"]/*').extract(),
                 conv=compose(string.strip, ''.join))
        # Lower quality description as fallback.
        cond_set(product, 'description',
                 sel.xpath('//meta[@name="Description"]/@content').extract())

    def _populate_from_js(self, url, sel, product):
        # This fails with movies.
        scripts = sel.xpath("//script[contains(text(), 'var DefaultItem =')]")
        if not scripts:
            self.log("No JS matched in %s" % url, WARNING)
        if len(scripts) > 1:
            self.log("Matched multiple script blocks in %s" % url, WARNING)

        cond_set(product, 'upc', map(int, scripts.re("upc:\s*'(\d+)',")))
        cond_set(product, 'brand',
                 filter(None, scripts.re("brand:\s*'(.+)',")))
        cond_set(product, 'model', scripts.re("model:\s*'(.+)',"))
        cond_set(product, 'title', scripts.re("friendlyName:\s*'(.+)',"))
        cond_set(product, 'price',
                 map(float, scripts.re("currentItemPrice:\s*'(\d+)',")))
        cond_set(product, 'rating',
                 map(float, scripts.re("currentRating:\s*'(.+)',")))

    def _populate_from_open_graph(self, url, sel, product):
        """See about the Open Graph Protocol at http://ogp.me/"""
        # Extract all the meta tags with an attribute called property.
        metadata_dom = sel.xpath("/html/head/meta[@property]")
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
        # The title is excluded as it contains a "Walmart: " prefix.
        product['url'] = metadata['url']  # Canonical URL for the product.
        product['image_url'] = metadata['image']

        # Optional Open Graph metadata.
        if 'upc' in metadata:
            product['upc'] = int(metadata['upc'])
        product['description'] = metadata.get('description')
        product['locale'] = metadata.get('locale')

    def _scrape_total_matches(self, sel):
        return int(sel.css(".numResults ::text").extract()[0].split()[0])

    def _scrape_product_links(self, sel):
        links = sel.css('a.prodLink.GridItemLink ::attr(href)').extract()
        if not links:
            self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, sel):
        next_pages = sel.css('li.btn-nextResults > a ::attr(href)').extract()
        if len(next_pages) == 1:
            return next_pages[0]
        elif len(next_pages) > 1:
            self.log("Found more than one 'next page' link.", ERROR)
        return None
