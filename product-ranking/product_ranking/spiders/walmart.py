from __future__ import division, absolute_import, unicode_literals

import json
import pprint
import re
import urlparse

from scrapy.log import ERROR, INFO

from product_ranking.items import (SiteProductItem, RelatedProduct,
                                   BuyerReviews, Price)
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

    SEARCH_URL = "http://www.walmart.com/search/search-ng.do?Find=Find" \
        "&_refineresult=true&ic=16_0&search_constraint=0" \
        "&search_query={search_term}&sort={search_sort}"

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
        if search_sort == 'best_sellers':
            self.SEARCH_URL += '&soft_sort=false&cat_id=0'
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
        product['buyer_reviews'] = self._build_buyer_reviews(response)

        cond_set_value(product, 'locale', 'en-US')  # Default locale.
        return product

    def _parse_single_product(self, response):
        return self.parse_product(response)

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

    def _build_buyer_reviews(self, response):
        overall_block = response.xpath(
            '//*[contains(@class, "review-summary")]'
            '//p[contains(@class, "heading")][contains(text(), "|")]//text()'
        ).extract()
        overall_text = ' '.join(overall_block)
        if not overall_text.strip():
            return
        buyer_reviews = {}
        buyer_reviews['num_of_reviews'] = int(
            overall_text.split('review')[0].strip())
        buyer_reviews['average_rating'] = float(
            overall_text.split('|')[1].split('out')[0].strip())
        buyer_reviews['rating_by_star'] = {}
        for _revs in response.css('.review-histogram .rating-filter'):
            _star = _revs.css('.meter-inline ::text').extract()[0].strip()
            _reviews = _revs.css('.rating-val ::text').extract()[0].strip()
            _star = (_star.lower().replace('stars', '').replace('star', '')
                     .strip())
            buyer_reviews['rating_by_star'][int(_star)] = int(_reviews)
        return BuyerReviews(**buyer_reviews)

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
        if not product.get('price'):
            currency = response.css('[itemprop=priceCurrency]::attr(content)')
            price = response.css('[itemprop=price]::attr(content)')
            if price and currency:
                currency = currency.extract()[0]
                price = re.search('[,. 0-9]+', price.extract()[0])
                if price:
                    price = price.group()
                    price = price.replace(',', '').replace(' ', '')
                    cond_set_value(product, 'price',
                                   Price(priceCurrency=currency, price=price))

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
        if available:
            price_block = None
            try:
                price_block = data['buyingOptions']['price']
            except KeyError:
                # Packs of products have different buyingOptions.
                try:
                    price_block =\
                        data['buyingOptions']['maxPrice']
                except KeyError:
                    self.log(
                        "Product with unknown buyingOptions structure: %s\n%s"
                        % (response.url, pprint.pformat(data)),
                        ERROR
                    )
            if price_block:
                _price = Price(
                    priceCurrency=price_block['currencyUnit'],
                    price=price_block['currencyAmount']
                )
                cond_set_value(product, 'price', _price)
        try:
            cond_set_value(
                product, 'upc', data['analyticsData']['upc'], conv=int)
        except ValueError:
            pass  # Not really a UPC.
        cond_set_value(product, 'image_url', data['primaryImageUrl'])
        cond_set_value(product, 'brand', data['analyticsData']['brand'])

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
