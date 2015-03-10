# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import urlparse
from datetime import datetime
import re
import json

from product_ranking.items import Price
from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, FLOATING_POINT_RGEX
from product_ranking.spiders import cond_set, cond_set_value
from scrapy.log import DEBUG
from scrapy.http import Request


class PlayProductsSpider(BaseProductsSpider):
    name = 'play_products'
    allowed_domains = ["play.com"]
    start_urls = []
    SEARCH_URL = (
        "http://www.play.com/Search.html?searchstring={search_term}"
        "&searchsource=0&searchtype=allproducts")
    API_URL = (
        "http://api.play.com/product/{upc}/recommendations"
        "?minvalues=12&maxvalues=12&callback=callback&_={sess}")

    SORT_MODES = {
        'default': '',
        'bestselling': '',
        'pricehl': '&ob=3',
        'pricelh': '&ob=4',
        'releasedate': '&ob=6',
        'az': '&ob=1',
        'za': '&ob=2',
        'customerrating': '&ob=5'}

    def __init__(self, sort_mode=None, *args, **kwargs):
        if sort_mode:
            if sort_mode:
                if sort_mode not in self.SORT_MODES:
                    self.log('"%s" not in SORT_MODES')
                    sort_mode = 'default'
                self.SEARCH_URL += self.SORT_MODES[sort_mode]

        super(PlayProductsSpider, self).__init__(
            None,
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def parse_product(self, response):
        product = response.meta['product']
        prodid = response.xpath(
            "//script[contains(text(),'productId')]"
            "/text()").re(r"productId=\"(\d+)\"")
        if prodid:
            prodid = prodid[0]
            if prodid != '0':
                cond_set_value(product, 'upc', prodid)
        parentprodid = response.xpath(
            "//script[contains(text(),'productId')]"
            "/text()").re(r"parentProductId=\"(\d+)\"")
        if parentprodid:
            parentprodid = parentprodid[0]
            if parentprodid != '0':
                cond_set_value(product, 'upc', parentprodid)

        cond_set(product, 'title', response.xpath(
            "//h1[@itemprop='name']/text()").extract())
        cond_set(product, 'title', response.xpath(
            "//h1[@itemprop='name']/strong/text()").extract())
        cond_set_value(product, 'locale', "en-GB")

        cond_set(product, 'brand', response.xpath(
            "//p[contains(@id,'bodycontent') and contains(text(),'Brand:')]"
            "/a/text() ").extract())

        mprice = response.xpath(
            "//span[contains(@class,'price')][1]/descendant-or-self::*"
            "/text()").extract()
        if mprice:
            mprice = ''.join(mprice)
            m = re.search(FLOATING_POINT_RGEX, mprice)
            if m:
                price = m.group(0)
                if price:
                    product['price'] = Price(
                        price=price, priceCurrency='GBP')

        cond_set(product, 'image_url', response.xpath(
            "//figure[@class='product-images']/a/img/@src").extract())
        # TODO:  desctiption
        # cond_set(product, 'description', response.xpath(
        #     "//div[@class='product-info']").extract())

        # cond_set_value(product, 'description', ' ')

        # print "PROD=", prodid, "PARENT=", parentprodid
        if prodid or parentprodid:
            sess = int((datetime.utcnow() - datetime(
                1970, 1, 1)).total_seconds())
            upc = product['upc']
            url = self.API_URL.format(sess=sess, upc=upc)
            new_meta = response.meta.copy()
            new_meta['handle_httpstatus_list'] = [404]
            return Request(
                url,
                meta=new_meta,
                callback=self._related_parse,
                dont_filter=True)

        return product

    def _related_parse(self, response):
        product = response.meta['product']
        if response.status == 200:
            text = response.body_as_unicode().encode('utf-8')
            m = re.search(r"callback\((.*)\)", text)
            related = []
            if m:
                jt = m.group(1)
                try:
                    jdata = json.loads(jt)
                    for itm in jdata['DisplayProducts']:
                        title = itm['Title']
                        href = itm['ProductUrl']
                        related.append(RelatedProduct(title, href))
                    # print related
                    if related:
                        product['related_products'] = {
                            'recommendations': related}
                except ValueError:
                    pass
        return product

    def _scrape_total_matches(self, response):
        # alert = response.xpath(
        #     "//div[contains(@class,'search')]"
        #     "/div[contains(@class,'alert-suggested-results')]")
        # if alert:
        #     return 0
        total = response.xpath(
            "//p[contains(text(),'Results')]/strong").re(r"\(of (\d+)\)")
        if total:
            try:
                return int(total[0])
            except ValueError:
                return
        return 0

    def _scrape_product_links(self, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)
        # alert = response.xpath(
        #     "//div[contains(@class,'search')]"
        #     "/div[contains(@class,'alert-suggested-results')]")
        links = response.xpath(
            "//ul[contains(@class,'line')]"
            "/li/article/a[@class='img']"
            "/@href").extract()
        print "LINKS=", len(links)
        # if alert:
        #     return
        if not links:
            self.log("Found no product links.", DEBUG)
        for link in links:
            yield link, SiteProductItem()
            # yield None, SiteProductItem(url=full_url(link))

    def _scrape_next_results_page_link(self, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)
        next_page_links = response.xpath(
            "//ul[@class='paging']"
            "/li[@class='paging-arrow']/a[contains(text(),'\u203a')]"
            "/@href").extract()
        if next_page_links:
            return full_url(next_page_links[0])
