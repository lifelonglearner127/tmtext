# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse

from product_ranking.items import Price
from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, FLOATING_POINT_RGEX
from product_ranking.spiders import cond_set, cond_set_value
from scrapy.http import Request
from scrapy.log import DEBUG


class HarrodsProductsSpider(BaseProductsSpider):
    name = 'harrods_products'
    allowed_domains = ["harrods.com"]
    start_urls = []
    SEARCH_URL = "http://luxury.harrods.com/search?w={search_term}&view=p"

    SORT_MODES = {
        'relevance': None,
        'lowprice': 'Low Price',
        'highprice': 'High Price'}

    SORTING = None

    def __init__(self, sort_mode=None, *args, **kwargs):
        if sort_mode:
            if sort_mode not in self.SORT_MODES:
                self.log('"%s" not in SORT_MODES')
                sort_mode = 'default'
            self.SORTING = self.SORT_MODES[sort_mode]

        self.pageno = 1
        self.brandvisited = []
        super(HarrodsProductsSpider, self).__init__(
            None,
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def parse(self, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)
        # Sorting
        if '/search?' in response.url and not response.meta.get('set_sorting'):
            sorting = self.SORTING
            slink = response.xpath(
                "//div[@class='sli_sort']/ul/li/a[text()='{sorting}']"
                "/@href".format(sorting=sorting)).extract()
            if slink:
                slink = slink[0]
                # print "SLINK=", slink
                new_meta = response.meta.copy()
                new_meta['set_sorting'] = True
                yield Request(url=slink, meta=new_meta)
        # Brand shop
        if '/brand/' in response.url:
            path = urlparse.urlparse(response.url).path
            self.brandvisited.append(path)
            links = response.xpath("//div/h2/a/@href").extract()
            if links:
                if response.meta.get('plinks'):
                    links.extend(response.meta.get('plinks'))
                    print "extend.links=", links
                    links = [x for x in links if x not in self.brandvisited]
                url = links[0]
                new_meta = response.meta.copy()
                new_meta['plinks'] = links[1:]
                new_meta['links'] = []
                new_meta['pageno'] = 1
                self.brandvisited.append(url)
                yield Request(
                    url=full_url(url), meta=new_meta,
                    callback=self.parse_links)
                return

        for l in super(HarrodsProductsSpider, self).parse(response):
            yield l

    def parse_links(self, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)

        links = response.xpath(
            "//ul[contains(@class,'products_row')]/li[@data-type]"
            "/h3/a/@href").extract()
        if links:
            mlinks = response.meta['links']
            mlinks.extend(links)
            response.meta['links'] = mlinks[:]
        plinks = response.xpath("//div/h2/a/@href").extract()
        if plinks:
            plinks.extend(response.meta['plinks'])
        else:
            plinks = response.meta['plinks']
        plinks = [x for x in plinks if x not in self.brandvisited]
        response.meta['plinks'] = plinks
        if links:
            pageno = response.meta['pageno']
            pageno += 1
            response.meta['pageno'] = pageno
            cpageno = str(pageno)
            pages = response.xpath(
                "//div[@class='pages']/ul[contains(@class,'paging')]"
                "/li/a[text()='{pageno}']"
                "/@href".format(pageno=cpageno)).extract()
            if pages:
                url = pages[0]
                new_meta = response.meta.copy()
                return Request(
                    url=full_url(url), meta=new_meta,
                    callback=self.parse_links)
        if plinks:
            url = plinks[0]
            if url in self.brandvisited:
                raise ValueError("Duplicate %s" % url)
            self.brandvisited.append(url)

            new_meta = response.meta.copy()
            new_meta['plinks'] = plinks[1:]
            new_meta['pageno'] = 1
            return Request(
                url=full_url(url), meta=new_meta,
                callback=self.parse_links)
        paths = set()
        l = response.meta['links']
        ln = []
        for url in l:
            path = urlparse.urlparse(url).path
            if path not in paths:
                ln.append(url)
                paths.add(path)
        # print "LISTS full/filtered", len(l), len(ln)
        response.meta['links'] = ln

        l = list(super(HarrodsProductsSpider, self).parse(response))
        return l

    def parse_product(self, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)

        product = response.meta['product']
        product['url'] = unicode(response.url)

        cond_set(product, 'title', response.xpath(
            "//h1[contains(@class,'product-title')]"
            "/span[@itemprop='name']/text()").extract(),
            conv=string.strip)

        cond_set(product, 'brand', response.xpath(
            "//h1[contains(@class,'product-title')]/span[@itemprop='brand']"
            "/span[@itemprop='name']/text()").extract(),
            conv=string.strip)
        price = response.xpath(
            "//span[contains(@class,'price')]/span[@itemprop='offers']"
            "/span[@itemprop='price']/text()").re(FLOATING_POINT_RGEX)

        if price:
            price = price[0].replace(',', '')
            product['price'] = Price(
                price=price, priceCurrency='GBP')

        cond_set(product, 'upc', response.xpath(
            "//span[@class='product_code' and @data-prodid]"
            "/@data-prodid").extract())

        cond_set(product, 'image_url', response.xpath(
            "//div[@class='f_left']/a[@id='product_img']/img/@src").extract())

        desc = response.xpath(
            "//div[contains(@class,'product_right_box')]/dl").extract()
        cond_set_value(product, 'description', "".join(desc))
        cond_set_value(product, 'locale', "en-GB")

        rel = []
        crst = response.xpath(
            "//div[@id='CrossSellTabs']/div/div/div/ul/li/h3")
        for icrst in crst:
            name = icrst.xpath("text()").extract()
            if name:
                name = name[0]
                href = icrst.xpath("a/@href").extract()
                if href:
                    href = href[0]
                    rel.append(RelatedProduct(name, full_url(href)))
        if rel:
            product['related_products'] = {"recommended": rel}
        return product

    def _check_alert(self, response):
        alert = response.xpath(
            "//div[@id='sli_noresult']"
            "/div[@class='noResult']")
        return alert

    def _scrape_total_matches(self, response):
        if 'links' in response.meta:
            links = response.meta['links']
            return len(links)

        alert = self._check_alert(response)
        if alert:
            return 0
        total = response.xpath(
            "//a[@class='page_view_all']/span"
            "/text()").re("(\d+)")
        if total:
            try:
                return int(total[0])
            except ValueError:
                return
        return 0

    def _scrape_product_links(self, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)
        if 'links' in response.meta:
            links = response.meta['links']
            for link in links:
                yield link, SiteProductItem()
            return
        if self._check_alert(response):
            return
        links = response.xpath(
            "//ul[contains(@class,'products_row')]/li[@data-type]"
            "/h3/a/@href").extract()
        if not links:
            self.log("Found no product links.", DEBUG)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)
        if self._check_alert(response):
            return
        if 'links' in response.meta:
            return
        self.pageno += 1
        cpageno = str(self.pageno)
        pages = response.xpath(
            "//span[@class='pageselectortext']/a[text()='{pageno}']"
            "/@href".format(pageno=cpageno)).extract()
        if pages:
            return pages[0]
        else:
            return
