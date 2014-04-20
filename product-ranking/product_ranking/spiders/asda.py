from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
from future_builtins import *

import json

from scrapy.log import WARNING
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

    def parse_product(self, response):
        raise AssertionError("This method should never be called.")

    def _search_page_error(self, response):
        sel = Selector(response)
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
            prod['upc'] = int(item['cin'])
            prod['model'] = item['id']
            prod['image_url'] = item['imageURL']
            prod['url'] = item['productURL']

            prod['locale'] = "en_GB"

            yield None, prod

    def _scrape_next_results_page_link(self, sel):
        data = json.loads(sel.xpath('//p/text()').extract()[0])
        return data.get('prefetch')
