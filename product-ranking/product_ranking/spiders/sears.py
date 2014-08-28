from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json

from scrapy.log import ERROR, WARNING

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set


class SearsProductsSpider(BaseProductsSpider):
    name = "sears_products"
    allowed_domains = ["sears.com", "om.sears.com"]
    start_urls = []

    SEARCH_URL = "http://www.sears.com/search={search_term}"

    def __init__(
            self,
            url_formatter=None,
            quantity=None,
            searchterms_str=None,
            searchterms_fn=None,
            site_name=allowed_domains[0],
            *args,
            **kwargs):
        # All this is to set the site_name since we have several
        # allowed_domains.
        super(SearsProductsSpider, self).__init__(
            url_formatter,
            quantity,
            searchterms_str,
            searchterms_fn,
            site_name,
            *args,
            **kwargs)

    def parse_product(self, response):
        prod = response.meta['product']

        data = json.loads(response.body_as_unicode())

        product = data['data'].get('product')

        brand = product.get('brand').get('name')
        cond_set(prod, 'brand', brand)

        title = product.get('seo').get('title')
        prod['title'] = title

        model = product.get('mfr').get('modelNo')
        cond_set(prod, 'model', model)

        upc = product.get('id')
        cond_set(prod, 'upc', upc)

        desc = product.get('desc')[1].get('val')
        cond_set(prod, 'description', desc)

        img_url = product.get('assets').get('imgs')[0].get('vals')[0].get('src')
        prod['image_url'] = img_url

        prod['url'] = response.url

        prod['locale'] = 'en-US'

        return prod

    def _scrape_total_matches(self, response):
        count = response.xpath(
            '//span[@class="tab-filters-count"]/text()'
        ).re('(\d+)')
        if count:
            return int(count[0])
        return 0

    def _scrape_product_links(self, sel):

        product_ids = sel.xpath("//input[@id='pId']/@value").extract()

        if not product_ids:
            self.log("Found no product ids.", ERROR)
        for prod_id in product_ids:
            link = "http://www.sears.com/content/pdp/config/products" \
                "/v1/products/%s" % prod_id
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, sel):
        next_pages = sel.xpath(
            "//div[contains(@class,'srchPagination')]/a//@href").extract()
        next_page = None
        if next_pages:
            next_page = 'http://www.target.com/%s' % next_pages[0]
            if len(next_pages) > 2:
                self.log("Found more than two 'next page' links.", WARNING)
        return next_page

