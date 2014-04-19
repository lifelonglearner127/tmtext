from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
from future_builtins import *

from itertools import islice
import json
import urlparse

from scrapy.log import ERROR, WARNING
from scrapy.http import Request
from scrapy.selector import Selector

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider


class AsdaProductsSpider(BaseProductsSpider):
    name = 'asda_products'
    allowed_domains = ["asda.com"]
    start_urls = []

    SEARCH_URL = "http://groceries.asda.com/api/items/search" \
        "?pagenum=1&productperpage=32&keyword={}" \
        "&contentid=New_IM_Search_WithResults_promo_1&htmlassociationtype=0" \
        "&listType=12&sortby=relevance+desc&cacheable=true&fromgi=gi" \
        "&requestorigin=gi"

    # TODO Extract common functionality to base.
    def parse(self, response):
        sel = Selector(response)

        remaining = response.meta['remaining']
        search_term = response.meta['search_term']

        if self._search_page_error(sel):
            self.log("For search term '%s' with %d items remaining,"
                     " failed to retrieve search page: %s"
                     % (search_term, remaining, response.request.url),
                     ERROR)
            return

        total_matches = self._scrape_total_matches(sel)
        prods = self._scrape_product_links(sel)
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

        remaining -= i + sum(1 for _ in prods) + 1  # May go negative.
        if remaining >= 0:
            next_page = self._scrape_next_results_page_link(sel)
            if next_page is not None:
                # Callback = self.parse
                yield Request(
                    urlparse.urljoin(response.url, next_page),
                    meta=dict(
                        search_term=response.meta['search_term'],
                        remaining=remaining))

    def parse_product(self, response):
        raise AssertionError("This method should never be called.")

    def _search_page_error(self, sel):
        """_search_page_error(sel:Selector):bool

        Sometimes an error status code is not returned and an error page is
        displayed. This methods detects that case for the search page.
        """
        data = json.loads(sel.xpath('//p/text()').extract()[0])
        if data.get('statusCode') != '0':
            self.log("Site reported error code '%s' and reason: %s"
                     % (data.get('statusCode'), data.get('statusMessage')),
                     WARNING)
            return True
        return False

    def _scrape_total_matches(self, sel):
        data = json.loads(sel.xpath('//p/text()').extract()[0])
        return int(data['totalResult'])

    def _scrape_product_links(self, sel):
        """_scrape_product_links(sel:Selector)
                :iter<tuple<str, SiteProductItem>>

        Returns the products in the current results page and a SiteProductItem
        which may be partially initialized.
        """
        data = json.loads(sel.xpath('//p/text()').extract()[0])
        for item in data['items']:
            prod = SiteProductItem()
            prod['title'] = item['itemName']
            prod['brand'] = item['brandName']
            prod['price'] = item['price']
            # FIXME Verify by comparing a prod in another site.
            prod['upc'] = item['cin']
            prod['model'] = item['id']
            prod['image_url'] = item['imageURL']
            prod['url'] = item['productURL']

            prod['locale'] = "en_GB"

            yield None, prod

    def _scrape_next_results_page_link(self, sel):
        data = json.loads(sel.xpath('//p/text()').extract()[0])
        return data.get('prefetch')
