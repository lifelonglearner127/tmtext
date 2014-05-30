from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json
import re
import string
import urllib
import urlparse

from scrapy.http import Request
from scrapy.log import ERROR, WARNING
from scrapy.selector import Selector

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import (BaseProductsSpider, FormatterWithDefaults,
                                     cond_set, compose)


class WalmartProductsSpider(BaseProductsSpider):
    name = 'walmart_products'
    allowed_domains = ["walmart.com"]

    SEARCH_URL = "http://www.walmart.com/search/search-ng.do?Find=Find" \
        "&_refineresult=true&ic=16_0&search_constraint=0" \
        "&search_query={search_term}&search_sort={search_sort}"

    RELATED_PRODUCTS_URL = \
        "http://irsws.walmart.com/irs-ws/irs/2.0" \
        "?callback=irs_process_response" \
        "&modules_bit_field=0000000" \
        "&api_key=01" \
        "&visitor_id=78348875473" \
        "&category={category_id}" \
        "&client_guid={client_guid}" \
        "&config_id=0" \
        "&parent_item_id={item_id}"

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

        item_id, category_id = self._populate_from_js(response.url, sel, p)

        self._populate_from_html(response.url, sel, p)

        cond_set(p, 'locale', ['en-US'])  # Default locale.

        if item_id is None or category_id is None:
            result = p
        else:
            result = Request(
                self.RELATED_PRODUCTS_URL.format(
                    item_id=item_id,
                    category_id=urllib.quote(category_id),
                    # It's unknown how the following value is generated but it
                    # looks like a UUID. Also, it changes on every request.
                    client_guid="f3f03064-bede-45f2-b2f1-7b35cdb5e5ed",
                ),
                self.parse_related_products,
                meta=response.meta.copy(),
            )
        return result

    def parse_related_products(self, response):
        m = re.match(r'.*?\((.+)\)', response.body)  # Extract JSON.
        product = response.meta['product']
        if not m:
            self.log("Failed to parse related products.", WARNING)
        else:
            data = json.loads(m.group(1))
            module_list = data.get('result', {}).get('moduleList')
            if module_list:
                product['related_products'] = {
                    "buyers_also_bought":
                        [RelatedProduct(self._generate_title_from_url(url), url)
                         for ml in module_list[::-1]
                         for url in Selector(text=ml['html']).css(
                             'a.irs-title ::attr(href)').extract()],
                }
        return product

    def _generate_title_from_url(self, url):
        slug = url.rsplit('/', 2)[-2]
        return ' '.join(map(string.capitalize, slug.split('-')))

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
        # Smaller but good description as fallback.
        cond_set(
            product,
            'description',
            sel.xpath('//meta[@name="twitter:description"]/@content').extract()
        )
        # Lower quality description as last resort.
        cond_set(product, 'description',
                 sel.xpath('//meta[@name="Description"]/@content').extract())

    def _populate_from_js(self, url, sel, product):
        # This fails with movies.
        scripts = sel.xpath("//script[contains(text(), 'var DefaultItem =')]")
        if not scripts:
            self.log("No JS matched in %s" % url, WARNING)
            return None, None
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

        item_id_list = scripts.re("itemId:\s*(\d+),")
        category_id_list = scripts.re("primaryCategoryPath:\s*'([\d:]+)',")
        return (
            item_id_list[0] if item_id_list else None,
            category_id_list[0] if category_id_list else None,
        )

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
            self.log("Found no product links in %r." % sel.response, ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, sel):
        next_pages = sel.css('li.btn-nextResults > a ::attr(href)').extract()
        if len(next_pages) == 1:
            return next_pages[0]
        elif len(next_pages) > 1:
            self.log(
                "Found more than one 'next page' link in %r." % sel.response,
                ERROR
            )
        return None
