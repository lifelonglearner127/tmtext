from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

from itertools import islice
import string
import urllib
import urlparse

from scrapy.log import ERROR, WARNING, INFO
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


class FormatterWithDefaults(string.Formatter):

    def __init__(self, **defaults):
        self.defaults = defaults

    def get_field(self, field_name, args, kwargs):
        # Handle a key not found
        try:
            val = super(FormatterWithDefaults, self).get_field(
                field_name, args, kwargs)
        except (KeyError, AttributeError):
            val = self.defaults[field_name], field_name
        return val


class BaseProductsSpider(Spider):
    start_urls = []

    SEARCH_URL = None  # Override.

    def __init__(self,
                 url_formatter=None,
                 quantity=None,
                 searchterms_str=None, searchterms_fn=None,
                 site_name=None,
                 *args, **kwargs):
        super(BaseProductsSpider, self).__init__(*args, **kwargs)

        if site_name is None:
            assert len(self.allowed_domains) == 1, \
                "A single allowed domain is required to auto-detect site name."
            self.site_name = self.allowed_domains[0]
        else:
            self.site_name = site_name

        if url_formatter is None:
            self.url_formatter = string.Formatter()
        else:
            self.url_formatter = url_formatter

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

        self.log("Created for %s with %d search terms."
                 % (self.site_name, len(self.searchterms)), INFO)

    def make_requests_from_url(self, _):
        """This method does not apply to this type of spider so it is overriden
        and "disabled" by making it raise an exception unconditionally.
        """
        raise AssertionError("Need a search term.")

    def start_requests(self):
        """Generate Requests from the SEARCH_URL and the search terms."""
        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(self.SEARCH_URL,
                                          search_term=urllib.quote(st)),
                meta={'search_term': st, 'remaining': self.quantity})

    def parse(self, response):
        if self._search_page_error(response):
            remaining = response.meta['remaining']
            search_term = response.meta['search_term']

            self.log("For search term '%s' with %d items remaining,"
                     " failed to retrieve search page: %s"
                     % (search_term, remaining, response.request.url),
                     ERROR)
        else:
            prods_count = -1  # Also used after the loop.
            for prods_count, request_or_prod in enumerate(
                    self._get_products(response)):
                yield request_or_prod
            prods_count += 1  # Fix counter.
    
            request = self._get_next_products_page(response, prods_count)
            if request is not None:
                yield request

    def _get_products(self, response):
        sel = Selector(response)

        remaining = response.meta['remaining']
        search_term = response.meta['search_term']
        prods_per_page = response.meta.get('products_per_page')
        total_matches = response.meta.get('total_matches')

        prods = self._scrape_product_links(sel)

        if prods_per_page is None:
            # Materialize prods to get its size.
            prods = list(prods)
            prods_per_page = len(prods)

        if total_matches is None:
            total_matches = self._scrape_total_matches(sel)

        for i, (prod_url, prod_item) in enumerate(islice(prods, 0, remaining)):
            # Initialize the product as much as possible.
            prod_item['site'] = self.site_name
            prod_item['search_term'] = search_term
            prod_item['total_matches'] = total_matches
            prod_item['results_per_page'] = prods_per_page
            # The ranking is the position in this page plus the number of
            # products from other pages.
            prod_item['ranking'] = (i + 1) + (self.quantity - remaining)

            if prod_url is None:
                # The product is complete, no need for another request.
                yield prod_item
            else:
                # Another request is necessary to complete the product.
                url = urlparse.urljoin(response.url, prod_url)
                prod_item['url'] = url  # Tentative.
                yield Request(
                    url,
                    callback=self.parse_product,
                    meta={'product': prod_item},
                )

    def _get_next_products_page(self, response, prods_found):
        link_page_attempt = response.meta.get('link_page_attempt', 1)

        result = None
        if prods_found > 0:
            # This was a real product listing page.
            remaining = response.meta['remaining']
            remaining -= prods_found
            if remaining > 0:
                next_page = self._scrape_next_results_page_link(
                    Selector(response))
                if next_page is not None:
                    url = urlparse.urljoin(response.url, next_page)
                    new_meta = dict(response.meta)
                    new_meta['remaining'] = remaining
                    result = Request(url, self.parse, meta=new_meta, priority=1)
        elif link_page_attempt > 2:
            self.log(
                "Giving up on results page after %d attempts: %s" % (
                    link_page_attempt, response.request.url),
                ERROR
            )
        else:
            self.log(
                "Will retry to get results page (attempt %d): %s" % (
                    link_page_attempt, response.request.url),
                WARNING
            )

            # Found no product links. Probably a transient error, lets retry.
            new_meta = dict(response.meta)
            new_meta['link_page_attempt'] = link_page_attempt + 1
            # Add an attribute so that Scrapy doesn't discard as duplicate.
            url = response.request.url + "&_=%d" % link_page_attempt
            result = Request(url, self.parse, meta=new_meta, priority=1)

        return result

    ## Abstract methods.

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
