from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value

from scrapy.http import Request
from scrapy.log import ERROR
from scrapy.selector import Selector


class PGEStoreProductSpider(BaseProductsSpider):
    name = 'pgestore_products'
    allowed_domains = ["pgestore.com", "igodigital.com"]

    SEARCH_URL = "http://www.pgestore.com/on/demandware.store/Sites-PG-Site/" \
        "default/Search-Show?q={search_term}"

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
        super(PGEStoreProductSpider, self).__init__(
            url_formatter,
            quantity,
            searchterms_str,
            searchterms_fn,
            site_name,
            *args,
            **kwargs)

    def parse_product(self, response):
        prod = response.meta['product']

        self._populate_from_html(response, prod)

        cond_set_value(prod, 'locale', 'en-US')  # Default locale.

        related_product_link = response.xpath(
            "//*[@id='crossSell']/script/@src").extract()[0]
        return Request(
            related_product_link,
            self.parse_related_products,
            meta=response.meta.copy(),
        )

    def _populate_from_html(self, response, product):
        brands = response.xpath(
            "//*[@id='pdpMain']/div[1]/script[2]/text()").re('.*?(\'(.*\w))')[1]
        cond_set(product, 'brand', [brands])
        if 'brand' not in product:
            self.log("Found no brand name in: %s" % response.url, ERROR)

        cond_set(
            product,
            'title',
            response.xpath("//*[@id='pdpMain']/div[2]/h1/text()").extract()
        )
        cond_set(product, 'upc',
                 response.xpath("//*[@id='prodSku']/text()").extract())
        cond_set(
            product,
            'image_url',
            response.xpath(
                "//*[@id='pdpMain']/div[1]/div[2]/img/@src").extract()
        )
        cond_set_value(product, 'price',
                       ''.join(response.css('.price ::text').extract()).strip())

        cond_set(
            product,
            'description',
            response.xpath(
                "//*[@id='pdpTab1']//*[@class='tabContent']").extract()
        )

    def parse_related_products(self, response):
        """The page parsed here is a JavaScript file with HTML in two variables.
        """
        product = response.meta['product']

        others_purchased_html = Selector(text=response.selector.re(
            r'if \(id == "igdrec_2"\)\s*{\s*div\.innerHTML = "(.*?)";')[0])
        others_purchased_links = others_purchased_html.xpath(
            "//*[@class='igo_product']/a[2]")
        if others_purchased_links:
            product['related_products'] = {
                "buyers_also_bought": list(
                    RelatedProduct(
                        link.xpath('text()').extract()[0],
                        link.xpath('@href').extract()[0])
                    for link in others_purchased_links
                )
            }

        also_like_html = Selector(text=response.selector.re(
            r'if \(id == "igdrec_1"\)\s*{\s*div\.innerHTML = "(.*?)";')[0])
        also_like_links = also_like_html.xpath("//*[@class='igo_product']/a[2]")
        if also_like_links:
            product.setdefault('related_products', {})["recommended"] = list(
                RelatedProduct(
                    link.xpath('text()').extract()[0],
                    link.xpath('@href').extract()[0])
                for link in also_like_links
            )

        return product

    def _scrape_product_links(self, response):
        links = response.xpath("//*[@class='description']/a/@href").extract()
        if not links:
            self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_total_matches(self, response):
        num_results = response.xpath(
            "//*[@id='deptmainheaderinfo']/text()").extract()
        if num_results and num_results[0]:
            num_results = num_results[0].split(" ")
            return int(num_results[2])
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_next_results_page_link(self, response):
        next_pages = response.xpath(
            "//*[@id='pdpTab1']/div[3]/div[1]/ul/li[6]/a/@href").extract()
        next_page = None
        if len(next_pages) == 1:
            next_page = next_pages[0]
        elif len(next_pages) == 0:
            self.log("Found no 'next page' link.", ERROR)
        return next_page
