from __future__ import division, absolute_import, unicode_literals
from .samsclub_shelf_pages import SamsclubShelfPagesSpider
from .samsclub import SamsclubProductsSpider
import re
from scrapy.http import Request, FormRequest
from product_ranking.items import SiteProductItem
from scrapy.log import DEBUG, WARNING
import urlparse
import json
from math import ceil
from product_ranking.spiders import cond_set, cond_set_value
from product_ranking.items import SiteProductItem, Price, BuyerReviews
is_empty = lambda x: x[0] if x else None

class SamsclubCpPagesSpider(SamsclubShelfPagesSpider):
    name = 'samsclub_cp_urls_products'

    def _get_shelf_path_from_firstpage(self, response):
        shelf_categories = [c.strip() for c in response.xpath('.//ol[@id="breadCrumbs"]/li//a/text()').extract()
                            if len(c.strip()) > 1]

        shelf_category = response.xpath('//h1[contains(@class, "catLeftTitle")]/text()').extract()
        shelf_category = shelf_category[0] if shelf_category else None
        total_matches = self._scrape_total_matches(response)
        if total_matches:
            try:
                # determining final amount of pages to scrape
                self.num_pages = min(ceil(int(total_matches)/float(self.prods_per_page)),self.num_pages)
            except BaseException:
                pass
        return Request(self._NEXT_SHELF_URL.format(
            category_id=self._get_category_id(response),
            offset=0,
            prods_per_page=self.prods_per_page), meta={
            'shelf_path': shelf_categories,
            'shelf_name': shelf_category,
            'total_matches':total_matches,
            'search_term': '',
            'remaining': self.quantity,
            'club': 4},
            dont_filter=True)

    def _scrape_product_links(self, response):
        if response.url.find('ajaxSearch') > 0:
            shelf_category = response.meta.get('shelf_name')
            shelf_categories = response.meta.get('shelf_path')
            total_matches = response.meta.get('total_matches', 0)
            urls = response.xpath("//body/ul/li/a/@href").extract()
            if not urls:
                urls = response.xpath('//*[contains(@href, ".ip") and contains(@href, "/sams/")]/@href').extract()
            if urls:
                urls = [urlparse.urljoin(response.url, x) for x in urls if x.strip()]
            for url in urls:
                item = response.meta.get('product', SiteProductItem())
                item['total_matches'] = total_matches
                if shelf_category:
                    item['shelf_name'] = shelf_category
                if shelf_categories:
                    for category_index, category_value in enumerate(shelf_categories[:10]):
                        item['level{}'.format(category_index+1)] = category_value
                yield url, item
        else:
            self.log("This method should not be called with such url {}".format(
                response.url), WARNING)

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(
            product,
            'title',
            response.xpath(
                "//div[contains(@class,'prodTitle')]/h1/span[@itemprop='name']"
                "/text()"
            ).extract())

        # Title key must be present even if it is blank
        cond_set_value(product, 'title', "")
        return product
