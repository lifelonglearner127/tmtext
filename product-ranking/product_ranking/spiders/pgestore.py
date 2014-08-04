from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set

from scrapy.http import Request
from scrapy.log import ERROR
from scrapy.selector import Selector

from bs4 import BeautifulSoup


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
        re1 = '.*?(\'(.*\w))'
        rg = re.compile(re1, re.IGNORECASE | re.DOTALL)
        m = rg.search(sel.xpath("//*[@id='pdpMain']/div[1]/script[2]/text()").extract()[0])
        if m:
            brand = m.group(2)
        else:
            self.log("Found no brand name.", ERROR)

        cond_set(product, 'title',
                 sel.xpath("//*[@id='pdpMain']/div[2]/h1/text()").extract())
        cond_set(product, 'upc',
                 sel.xpath("//*[@id='prodSku']/text()").extract())
        cond_set(product, 'image_url',
                 sel.xpath("//*[@id='pdpMain']/div[1]/div[2]/img/@src").extract())
        product['brand'] = brand
        product['price'] = sel.xpath("//*[@id='pdpATCDivpdpMain']/div[1]/div[7]/div[1]/div/div/div/text()") \
            .extract()[0].strip()
        description = sel.xpath("//*[@id='pdpTab1']/div/text()").extract()
        description.extend(sel.xpath("//*[@id='pdpTab1']/div/ul/li/text()").extract())
        cond_set(product, 'description',
                 description)
        cond_set(product, 'locale', ['en-US'])  # Default locale.

        # self.parse_related_products(sel.response)

    def parse_related_products(self, response):
        sel = Selector(response)
        product = response.meta['product']

        soup = BeautifulSoup(response.body)

        igdrecs = soup.find_all('h2')

        links = igdrecs[1].find_all_next("a", href=True)
        urls = [links[1].attrs['href'], links[3].attrs['href'], links[5].attrs['href'],
                links[7].attrs['href'], links[9].attrs['href']]
        titles = [str(links[1].string), str(links[3].string), str(links[5].string),
                  str(links[7].string), str(links[9].string)]
        rec_links = igdrecs[0].find_all_next("a", href=True)

        rec_urls = [rec_links[0].attrs['href'], rec_links[2].attrs['href'], rec_links[4].attrs['href'],
                    rec_links[6].attrs['href'], rec_links[8].attrs['href']]
        rec_titles = [str(rec_links[0].next_element.next_element.next_element.next_element.string),
                      str(rec_links[2].next_element.next_element.next_element.next_element.string),
                      str(rec_links[4].next_element.next_element.next_element.next_element.string),
                      str(rec_links[6].next_element.next_element.next_element.next_element.string),
                      str(rec_links[8].next_element.next_element.next_element.next_element.string)]

        if len(urls) > 0:
            product['related_products'] = {
                "buyers_also_bought": list(
                    RelatedProduct(title, url)
                    for title in titles
                    for url in urls
                ),
                "recommended": list(
                    RelatedProduct(title, url)
                    for title in rec_titles
                    for url in rec_urls
                ),
            }

        return product

    def _scrape_product_links(self, sel):
        links = sel.xpath("//*[@class='description']/a/@href").extract()
        if not links:
            self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_total_matches(self, sel):
        mynum = sel.xpath("//*[@id='deptmainheaderinfo']/text()").extract()
        words = mynum[0].split(" ")
        if words[2]:
            return int(words[2])
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_next_results_page_link(self, sel):
        # next_pages = sel.css(".padbar ul.pagination a.next::attr(href)").extract()
        next_pages = sel.xpath("//*[@id='pdpTab1']/div[3]/div[1]/ul/li[6]/a/@href").extract()
        next_page = None
        if len(next_pages) == 1:
            next_page = next_pages[0]
        elif len(next_pages) == 0:
            self.log("Found no 'next page' link.", ERROR)
        return next_page
