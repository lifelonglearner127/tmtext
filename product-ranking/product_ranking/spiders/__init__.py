from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import urlparse

from scrapy.log import (ERROR, INFO)
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.spider import Spider


def compose(*funcs):
    """Composes function calls.

    All functions save the last one must take a single argument.
    """
    def _c(*args):
        res = args
        for f in reversed(funcs):
            res = [f(*res)]
        return res
    return _c


def cond_set(item, key, values, conv=lambda l: l[0]):
    """Helper function to ease conditionally setting a value in a dict."""
    values = list(values)  # Copy and materialize values.
    if not item.get(key) and values:
        item[key] = conv(values)


class BaseProductsSpider(Spider):
    start_urls = []

    SEARCH_URL = None  # Override.

    def __init__(self, quantity='20',
                 searchterms_str=None, searchterms_fn=None,
                 *args, **kwargs):
        super(BaseProductsSpider, self).__init__(*args, **kwargs)

        if quantity is None:
            raise AssertionError("Quantity parameter is mandatory.")

        self.quantity = int(quantity)
        self.searchterms = []
        if searchterms_str is not None:
            self.searchterms = searchterms_str.split(',')
        elif searchterms_fn is not None:
            with open(searchterms_fn) as f:
                self.searchterms = f.readlines()
        else:
            self.log("No search terms provided!", ERROR)

        self.log("Created with %d search terms." % len(self.searchterms), INFO)

    def make_requests_from_url(self, _):
        """This method does not apply to this type of spider so it is overriden
        and "disabled" by making it raise an exception unconditionally.
        """
        raise AssertionError("Need a search term.")

    def start_requests(self):
        """Generate Requests from the SEARCH_URL and the search terms."""
        for st in self.searchterms:
            r = Request(self.SEARCH_URL.format(st))
            r.meta['search_term'] = st
            r.meta['remaining'] = self.quantity
            yield r

    def parse(self, response):
        sel = Selector(response)

        remaining = response.meta['remaining']
        total_matches = self._scrape_total_matches(sel)

        prod_urls = self._scrape_product_links(sel)
        for i, prod_url in enumerate(prod_urls[:remaining]):
            r = Request(
                urlparse.urljoin(response.url, prod_url),
                callback=self.parse_product)
            r.meta['search_term'] = response.meta['search_term']
            r.meta['total_matches'] = total_matches
            # The ranking is the position in this page plus the number of
            # products from other pages.
            r.meta['ranking'] = (i + 1) + (self.quantity - remaining)
            yield r

        remaining -= len(prod_urls)  # May go negative.
        if remaining >= 0:
            next_page = self._scrape_next_results_page_link(sel)
            if next_page is not None:
                # Callback = self.parse
                r = Request(urlparse.urljoin(response.url, next_page))
                r.meta['search_term'] = response.meta['search_term']
                r.meta['remaining'] = remaining
                yield r

    def parse_product(self, response):
        """parse_product(response:Response)

        Handles parsing of a product page.
        """
        raise NotImplementedError

    def _scrape_total_matches(self, sel):
        """_scrape_total_matches(sel:Selector):int

        Scrapes the total number of matches of the search term.
        """
        raise NotImplementedError

    def _scrape_product_links(self, sel):
        """_scrape_product_links(sel:Selector):iter<str>

        Returns the products in the current results page.
        """
        raise NotImplementedError

    def _scrape_next_results_page_link(self, sel):
        """_scrape_next_results_page_link(sel:Selector):str

        Scrapes the URL for the next results page.
        It should return None if no next page is available.
        """
        raise NotImplementedError
