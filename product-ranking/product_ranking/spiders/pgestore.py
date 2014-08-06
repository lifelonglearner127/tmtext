from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set

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
        sel = Selector(response)

        prod = response.meta['product']

        self._populate_from_html(response.url, sel, prod)

        related_product_link = sel.xpath(
            "//*[@id='crossSell']/script[1]/@src").extract()[0]
        return Request(
            related_product_link,
            self.parse_related_products,
            meta=response.meta.copy(),
        )

    def _populate_from_html(self, url, sel, product):
        brands = sel.xpath("//*[@id='pdpMain']/div[1]/script[2]/text()").re(
            '.*?(\'(.*\w))')
        if brands:
            product['brand'] = brands[0]
        else:
            self.log("Found no brand name in: %s" % url, ERROR)

        cond_set(product, 'title',
                 sel.xpath("//*[@id='pdpMain']/div[2]/h1/text()").extract())
        cond_set(product, 'upc',
                 sel.xpath("//*[@id='prodSku']/text()").extract())
        cond_set(
            product,
            'image_url',
            sel.xpath("//*[@id='pdpMain']/div[1]/div[2]/img/@src").extract()
        )
        # FIXME Can't this XPath be made more resilient by not depending on so much of the document's structure? For example, ''.join(sel.css('.price ::text').extract()).strip().
        product['price'] = sel.xpath(
            "//*[@id='pdpATCDivpdpMain']/div[1]/div[7]/div[1]/div/div/div/"
            "text()"
        ).extract()[0].strip()

        # FIXME The description look strange. Why not just take the node()?
        description = sel.xpath("//*[@id='pdpTab1']/div/text()").extract()
        description.extend(
            sel.xpath("//*[@id='pdpTab1']/div/ul/li/text()").extract())
        cond_set(product, 'description', description)

        cond_set(product, 'locale', ['en-US'])  # Default locale.

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

    def _scrape_product_links(self, sel):
        links = sel.xpath("//*[@class='description']/a/@href").extract()
        if not links:
            self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_total_matches(self, sel):
        # FIXME Please review the changes on bestbuy and perform them here where they apply.
        mynum = sel.xpath("//*[@id='deptmainheaderinfo']/text()").extract()
        words = mynum[0].split(" ")
        if words[2]:
            return int(words[2])
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_next_results_page_link(self, sel):
        next_pages = sel.xpath(
            "//*[@id='pdpTab1']/div[3]/div[1]/ul/li[6]/a/@href").extract()
        next_page = None
        if len(next_pages) == 1:
            next_page = next_pages[0]
        elif len(next_pages) == 0:
            self.log("Found no 'next page' link.", ERROR)
        return next_page
