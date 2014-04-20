from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

from itertools import islice
import urllib
import urlparse

from scrapy.log import ERROR, INFO
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

    def __init__(self, quantity=None,
                 searchterms_str=None, searchterms_fn=None,
                 *args, **kwargs):
        super(BaseProductsSpider, self).__init__(*args, **kwargs)

        if quantity is None:
            self.log("No quantity specified. Will retrieve all products.",
                     INFO)
            import sys
            self.quantity = sys.maxint
        else:
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
            yield Request(
                self.SEARCH_URL.format(urllib.quote(st)),
                meta={'search_term': st, 'remaining': self.quantity})

    def parse(self, response):
        remaining = response.meta['remaining']
        search_term = response.meta['search_term']

        if self._search_page_error(response):
            self.log("For search term '%s' with %d items remaining,"
                     " failed to retrieve search page: %s"
                     % (search_term, remaining, response.request.url),
                     ERROR)
            return

        sel = Selector(response)
        total_matches = self._scrape_total_matches(sel)
        prods = self._scrape_product_links(sel)
        i = -1  # "i" is also used after the loop.
        for i, (prod_url, prod_item) in enumerate(islice(prods, 0, remaining)):
            # Initialize the product as much as possible.
            prod_item['search_term'] = search_term
            prod_item['total_matches'] = total_matches
            # The ranking is the position in this page plus the number of
            # products from other pages.
            prod_item['ranking'] = (i + 1) + (self.quantity - remaining)

            if prod_url is None:
                # The product is complete, no need for another request.
                yield prod_item
            else:
                # Another request is necessary to complete the product.
                yield Request(
                    urlparse.urljoin(response.url, prod_url),
                    callback=self.parse_product,
                    meta={'product': prod_item})

        remaining -= i + 1
        if remaining > 0:
            next_page = self._scrape_next_results_page_link(sel)
            if next_page is not None:
                yield Request(
                    urlparse.urljoin(response.url, next_page),
                    self.parse,
                    meta=dict(
                        search_term=response.meta['search_term'],
                        remaining=remaining))

    def parse_product(self, response):
        """parse_product(response:Response)

        Handles parsing of a product page.
        """
        raise NotImplementedError

    def _search_page_error(self, response):
        """_search_page_error(response:Response):bool

        Sometimes an error status code is not returned and an error page is
        displayed. This methods detects that case for the search page.
        """
        # Defaul implementation for sites that send proper status codes.
        return False

    def _scrape_total_matches(self, sel):
        """_scrape_total_matches(sel:Selector):int

        Scrapes the total number of matches of the search term.
        """
        raise NotImplementedError

    def _scrape_product_links(self, sel):
        """_scrape_product_links(sel:Selector)
                :iter<tuple<str, SiteProductItem>>

        Returns the products in the current results page and a SiteProductItem
        which may be partially initialized.
        """
        raise NotImplementedError

    def _scrape_next_results_page_link(self, sel):
        """_scrape_next_results_page_link(sel:Selector):str

        Scrapes the URL for the next results page.
        It should return None if no next page is available.
        """
        raise NotImplementedError
