from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json
import re
import string
import urllib
import urlparse

from scrapy.http import Request
from scrapy.log import ERROR, WARNING, INFO
from scrapy.selector import Selector

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    compose, cond_set, cond_set_value, populate_from_open_graph


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
                search_sort=self.SEARCH_SORT[search_sort]
            ),
            *args, **kwargs)

    def start_requests(self):
        for request in super(WalmartProductsSpider, self).start_requests():
            request.meta['dont_redirect'] = True
            request.meta['handle_httpstatus_list'] = [302]
            yield request

    def _create_from_redirect(self, response):
        # Create comparable URL tuples.
        redirect_url = response.headers['Location']
        redirect_url_split = urlparse.urlsplit(redirect_url)
        redirect_url_split = redirect_url_split._replace(
            query=urlparse.parse_qs(redirect_url_split.query))
        original_url_split = urlparse.urlsplit(response.request.url)
        original_url_split = original_url_split._replace(
            query=urlparse.parse_qs(original_url_split.query))

        if redirect_url_split == original_url_split:
            self.log("Found identical redirect!", INFO)
            request = response.request.replace(dont_filter=True)
        else:
            self.log("Found legit redirect!", INFO)
            request = response.request.replace(url=redirect_url)
        request.meta['dont_redirect'] = True
        request.meta['handle_httpstatus_list'] = [302]

        return request

    def parse(self, response):
        if response.status == 302:
            yield self._create_from_redirect(response)
        else:
            for request in super(WalmartProductsSpider, self).parse(response):
                request.meta['dont_redirect'] = True
                request.meta['handle_httpstatus_list'] = [302]
                yield request

    def _get_products(self, response):
        if response.status == 302:
            yield self._create_from_redirect(response)
        else:
            for request_or_item in super(
                    WalmartProductsSpider, self)._get_products(response):
                if isinstance(request_or_item, Request):
                    request_or_item.meta['dont_redirect'] = True
                    request_or_item.meta['handle_httpstatus_list'] = [302]
                yield request_or_item

    def parse_product(self, response):
        if response.status == 302:
            return self._create_from_redirect(response)

        if self._search_page_error(response):
            self.log(
                "Got 404 when coming from %s." % response.request.url, ERROR)
            return

        p = response.meta['product']

        self._populate_from_open_graph(response, p)

        item_id, category_id = self._populate_from_js(response, p)

        self._populate_from_html(response, p)

        cond_set_value(p, 'locale', 'en-US')  # Default locale.

        if item_id is None or category_id is None:
            result = p
        else:
            meta = response.meta.copy()
            meta['dont_redirect'] = True
            meta['handle_httpstatus_list'] = [302]

            result = Request(
                self.RELATED_PRODUCTS_URL.format(
                    item_id=item_id,
                    category_id=urllib.quote(category_id),
                    # It's unknown how the following value is generated but it
                    # looks like a UUID. Also, it changes on every request.
                    client_guid="f3f03064-bede-45f2-b2f1-7b35cdb5e5ed",
                ),
                self.parse_related_products,
                meta=meta,
                priority=100,
            )
        return result

    def parse_related_products(self, response):
        if response.status == 302:
            return self._create_from_redirect(response)

        product = response.meta['product']

        m = re.match(r'.*?\((.+)\)', response.body_as_unicode())
        if not m:
            self.log("Failed to parse related products.", WARNING)
        else:
            data = json.loads(m.group(1))
            module_list = data.get('result', {}).get('moduleList', [])
            for module in module_list:
                if module['moduleTitle'] \
                        == "People who bought this item also bought":
                    product['related_products'] = {
                        "buyers_also_bought": [
                            RelatedProduct(
                                self._generate_title_from_url(url),
                                urlparse.urljoin(response.url, url)
                            )
                            for url in Selector(text=module['html']).css(
                                'a.irs-title ::attr(href)').extract()
                        ],
                    }
                    break
        return product

    @staticmethod
    def _generate_title_from_url(url):
        slug = url.rsplit('/', 2)[-2]
        return ' '.join(map(string.capitalize, slug.split('-')))

    def _search_page_error(self, response):
        path = urlparse.urlsplit(response.url)[2]
        return path == '/FileNotFound.aspx'

    def _populate_from_html(self, response, product):
        # Since different chunks of invalid HTML keep appearing in this
        # element, I'll just dump whatever is in there.
        cond_set(product, 'title',
                 response.xpath('//meta[@name="title"]/@content').extract())
        # TODO This source for the description is not reliable.
        cond_set(
            product,
            'description',
            response.xpath('//*[@class="ql-details-short-desc"]/*').extract(),
            conv=compose(string.strip, ''.join)
        )
        # Smaller but good description as fallback.
        cond_set(
            product,
            'description',
            response.xpath(
                '//meta[@name="twitter:description"]/@content').extract(),
        )
        # Lower quality description as last resort.
        cond_set(
            product,
            'description',
            response.xpath('//meta[@name="Description"]/@content').extract(),
        )

    def _populate_from_js(self, response, product):
        # This fails with movies.
        scripts = response.xpath(
            "//script[contains(text(), 'var DefaultItem =')]")
        if not scripts:
            self.log("No JS matched in %s" % response.url, WARNING)
            return None, None
        if len(scripts) > 1:
            self.log(
                "Matched multiple script blocks in %s" % response.url, WARNING)

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

    def _populate_from_open_graph(self, response, product):
        """Uses the generic function but removes some fields which are not good.
        """
        populate_from_open_graph(response, product)

        # The title is excluded as it contains a "Walmart: " prefix.
        try:
            del product['title']
        except KeyError:
            pass

    def _scrape_total_matches(self, response):
        num_results = None

        # We get two different types of pages.
        multiple_matches = [
            response.css(".numResults ::text").extract(),
            response.css('.result-summary-container ::text').re(
                'Showing \d+ of (\d+) results'),
        ]
        for i, matches in enumerate(multiple_matches):
            if matches:
                num_results = int(matches[0].split()[0])
                break
            else:
                self.log(
                    "Failed to extract total matches using method %d from %s"
                    % (i, response.url),
                    INFO
                )
        else:
            self.log(
                "Failed to extract total matches from: %s" % response.url,
                ERROR
            )
        return num_results

    def _scrape_product_links(self, response):
        links = []

        # We get two different types of pages.
        css_expressions = [
            'a.prodLink.ListItemLink ::attr(href)',
            'a.js-product-title ::attr(href)',
        ]
        for i, expr in enumerate(css_expressions):
            links = response.css(expr).extract()
            if links:
                break
            else:
                self.log(
                    "Found no product links using method %d in %s."
                    % (i, response.url),
                    INFO
                )
        else:
            self.log("Found no product links %s." % response.url, ERROR)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next_page = None

        multiple_links = [
            response.css('li.btn-nextResults > a ::attr(href)'),
            response.xpath(
                # [1] is to get just the next sibling.
                "//a[@class='active']/../following-sibling::li[1]/a/@href"
            ),
        ]
        for i, next_page_links in enumerate(multiple_links):
            if len(next_page_links) == 1:
                next_page = next_page_links.extract()[0]
                break
            elif len(next_page_links) > 1:
                self.log(
                    "Found more than one 'next page' link using method %d"
                    " in %s." % (i, response.url),
                    WARNING
                )
            else:
                self.log(
                    "Found no 'next page' link using method %d in %s"
                    " (which could be OK)." % (i, response.url),
                    INFO
                )
        else:
            self.log(
                "Found no 'next page' link in %s (which could be OK)."
                % response.url,
                INFO
            )
        return next_page
