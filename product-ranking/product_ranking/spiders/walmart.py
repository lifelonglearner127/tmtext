from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json
import pprint
import re
import urlparse

from scrapy.log import ERROR, WARNING, INFO

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set, cond_set_value


class WalmartProductsSpider(BaseProductsSpider):
    """Implements a spider for Walmart.com.

    This spider has 2 very peculiar things.
    First, it receives 2 types of pages so it need 2 rules for every action.
    Second, the site sometimes redirects a request to the same URL so, by
    default, Scrapy would discard it. Thus we override everything to handle
    redirects.

    FIXME: Currently we redirect infinitely, which could be a problem.
    """
    name = 'walmart_products'
    allowed_domains = ["walmart.com"]

    # Options search_sort and cat_id are added when a search sort exclusively
    # for the criteria requested is wanted.
    SEARCH_URL = "http://www.walmart.com/search/?query={search_term}" \
        "&sort={search_sort}&soft_sort=false&cat_id=0"

    _SEARCH_SORT = {
        'best_match': 0,
        'high_price': 'price_high',
        'low_price': 'price_low',
        'best_sellers': 'best_seller',
        'newest': 'new',
        'rating': 'rating_high',
    }

    _JS_DATA_RE = re.compile(
        r'define\(\s*"product/data\"\s*,\s*(\{.+?\})\s*\)\s*;', re.DOTALL)

    def __init__(self, search_sort='best_match', *args, **kwargs):
        super(WalmartProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self._SEARCH_SORT[search_sort]
            ),
            *args, **kwargs)

    def parse_product(self, response):
        if self._search_page_error(response):
            self.log(
                "Got 404 when coming from %r." % response.request.url, ERROR)
            return

        product = response.meta['product']

        self._populate_from_js(response, product)

        self._populate_from_html(response, product)

        cond_set_value(product, 'locale', 'en-US')  # Default locale.

        return product

    def _search_page_error(self, response):
        path = urlparse.urlsplit(response.url)[2]
        return path == '/FileNotFound.aspx'

    def _build_related_products(self, url, related_product_nodes):
        also_considered = []
        for node in related_product_nodes:
            link = urlparse.urljoin(url, node.xpath('../@href').extract()[0])
            title = node.xpath('text()').extract()[0]
            also_considered.append(RelatedProduct(title, link))
        return also_considered

    def _populate_from_html(self, response, product):
        cond_set(
            product,
            'description',
            response.css('.about-product-section').extract(),
            conv=''.join
        )

        also_considered = self._build_related_products(
            response.url,
            response.css('.top-product-recommendations .tile-heading'),
        )
        if also_considered:
            product.setdefault(
                'related_products', {})["buyers_also_bought"] = also_considered

        recommended = self._build_related_products(
            response.url,
            response.xpath(
                "//p[contains(text(), 'Check out these related products')]/.."
                "//*[contains(@class, 'tile-heading')]"
            ),
        )
        if recommended:
            product.setdefault(
                'related_products', {})['recommended'] = recommended

    def _populate_from_js(self, response, product):
        scripts = response.xpath("//script").re(
            WalmartProductsSpider._JS_DATA_RE)
        if not scripts:
            self.log("No JS matched in %r." % response.url, ERROR)
            return
        if len(scripts) > 1:
            self.log(
                "Matched multiple script blocks in %r." % response.url,
                ERROR
            )

        data = json.loads(scripts[0])
        cond_set_value(product, 'title', data['productName'])
        available = data['buyingOptions']['available']
        cond_set_value(
            product,
            'is_out_of_stock',
            not available,
        )
        cond_set_value(
            product,
            'is_in_store_only',
            data['buyingOptions']['storeOnlyItem'],
        )

        # This value is not available for packs and if there's no stock.
        cond_set_value(
            product,
            'price',
            data['buyingOptions'].get('price', {}).get('displayPrice'),
        )

        # This is for packs but will not be available is there's no stock.
        cond_set_value(
            product,
            'price',
            data['buyingOptions'].get('maxPrice', {}).get('displayPrice'),
        )

        if available and 'price' not in product:
            self.log(
                "Product with unknown buyingOptions structure: %s\n%s"
                % (response.url, pprint.pformat(data)),
                ERROR
            )

        try:
            cond_set_value(
                product, 'upc', data['analyticsData']['upc'], conv=int)
        except ValueError:
            # Not really a UPC.
            self.log(
                "Invalid UPC, %r, in %r."
                % (data['analyticsData']['upc'], response.url),
                WARNING
            )
        cond_set_value(product, 'image_url', data['primaryImageUrl'])
        cond_set_value(
            product,
            'brand',
            data['analyticsData']['brand'],
            conv=lambda s: None if not s else s,
        )

    def _scrape_total_matches(self, response):
        if response.css('.no-results'):
            return 0

        matches = response.css('.result-summary-container ::text').re(
            'Showing \d+ of (\d+) results')
        if matches:
            num_results = int(matches[0])
        else:
            num_results = None
            self.log(
                "Failed to extract total matches from %r." % response.url,
                ERROR
            )
        return num_results

    def _scrape_product_links(self, response):
        links = response.css('a.js-product-title ::attr(href)').extract()
        if not links:
            self.log("Found no product links in %r." % response.url, INFO)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next_page = None

        next_page_links = response.css(".paginator-btn-next ::attr(href)")
        if len(next_page_links) == 1:
            next_page = next_page_links.extract()[0]
        elif len(next_page_links) > 1:
            self.log(
                "Found more than one 'next page' link in %r." % response.url,
                ERROR
            )
        else:
            self.log(
                "Found no 'next page' link in %r (which could be OK)."
                % response.url,
                INFO
            )

        return next_page
