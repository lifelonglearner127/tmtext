import string
import urlparse

from scrapy.log import (ERROR, WARNING, INFO)
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.spider import Spider

from product_ranking.items import SiteProductItem


def _compose(*funcs):
    def _c(*args):
        res = args
        for f in funcs[::-1]:
            res = [f(*res)]
        return res
    return _c


def _set(item, key, values, conv=lambda l: l[0]):
    values = list(values)
    if not item.get(key) and values:
        item[key] = conv(values)


class WalmartProductsSpider(Spider):
    name = 'walmart_products'
    allowed_domains = ["walmart.com"]
    start_urls = []

    SEARCH_URL = "http://www.walmart.com/search/search-ng.do?ic=16_0&" \
        "Find=Find&search_query={}&Find=Find&search_constraint=0"

    def __init__(self, quantity='20',
                 searchterms_str=None, searchterms_fn=None,
                 *args, **kwargs):
        super(WalmartProductsSpider, self).__init__(*args, **kwargs)

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
        raise AssertionError("Need a search term.")

    def start_requests(self):
        for st in self.searchterms:
            r = Request(self.SEARCH_URL.format(st))
            r.meta['search_term'] = st
            r.meta['remaining'] = self.quantity
            yield r

    def parse(self, response):
        sel = Selector(response)

        remaining = response.meta['remaining']
        total_matches = self._scrape_total_matches(sel)

        prod_urls = sel.css('a.prodLink.GridItemLink').xpath('@href').extract()
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
            next_pages = sel.css('li.btn-nextResults > a').xpath('@href') \
                .extract()
            if not next_pages:
                pass  # Reached the end.
            elif len(next_pages) > 1:
                self.log("More than one 'next' page.", ERROR)
            else:
                next_page, = next_pages

                # Callback = self.parse
                r = Request(urlparse.urljoin(response.url, next_page))
                r.meta['search_term'] = response.meta['search_term']
                r.meta['remaining'] = remaining
                yield r

    def parse_product(self, response):
        sel = Selector(response)

        if self._is_404(response.url):
            self.log("Got 404 when coming from %s." % response.request.url,
                     ERROR)
            return

        p = SiteProductItem()
        p['search_term'] = response.meta['search_term']
        p['ranking'] = response.meta['ranking']
        p['total_matches'] = response.meta['total_matches']

        self._populate_from_open_graph(response.url, sel, p)

        self._populate_from_js(response.url, sel, p)

        self._populate_from_html(response.url, sel, p)

        return p

    def _is_404(self, url):
        path = urlparse.urlsplit(url)[2]
        return path == 'FileNotFound.aspx'

    def _populate_from_html(self, url, sel, product):
        # Since different chunks of invalid HTML keep appearing in this
        # element, I'll just dump whatever is in there.
        _set(product, 'title',
             sel.xpath('//meta[@name="title"]/@content').extract())
        # TODO This source for the description is not reliable.
        _set(product, 'description',
             sel.xpath('//*[@class="ql-details-short-desc"]/*').extract(),
             conv=_compose(string.strip, ''.join))
        # Lower quality description as fallback.
        _set(product, 'description',
             sel.xpath('//meta[@name="Description"]/@content').extract())

    def _populate_from_js(self, url, sel, product):
        # This fails with movies.
        scripts = sel.xpath("//script[contains(text(), 'var DefaultItem =')]")
        if not scripts:
            self.log("No JS matched in %s" % url, WARNING)
        if len(scripts) > 1:
            self.log("Matched multiple script blocks in %s" % url, WARNING)

        _set(product, 'upc', map(int, scripts.re("upc:\s*'(\d+)',")))
        _set(product, 'brand', filter(None, scripts.re("brand:\s*'(.+)',")))
        _set(product, 'model', scripts.re("model:\s*'(.+)',"))
        _set(product, 'title', scripts.re("friendlyName:\s*'(.+)',"))
        _set(product, 'price',
             map(float, scripts.re("currentItemPrice:\s*'(\d+)',")))
        _set(product, 'rating',
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
        """Extracts the total number of matches for the search term."""
        return int(sel.css(".numResults ::text").extract()[0].split()[0])
