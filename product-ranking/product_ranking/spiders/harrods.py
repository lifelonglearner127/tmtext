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
        super(HarrodsProductsSpider, self).__init__(
            None,
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def parse(self, response):
    #     def full_url(url):
    #         return urlparse.urljoin(response.url, url)
        print "PARSE", response.url
        if '/search?' in response.url and not response.meta.get('set_sorting'):
            print " SEARCH DETECTED"
            sorting = self.SORTING

            slink = response.xpath(
                "//div[@class='sli_sort']/ul/li/a[text()='{sorting}']"
                "/@href".format(sorting=sorting)).extract()
            if slink:
                slink = slink[0]
                print "SLINK=", slink
                new_meta = response.meta.copy()
                new_meta['set_sorting'] = True
                yield Request(url=slink, meta=new_meta)

    #     if '/brand/' in response.url:
    #         print "-" * 20
    #         print "PARSE BRAND", response.url
    #         links = response.xpath("//div/h2/a/@href").extract()
    #         print "add plinks=", links
    #         if links:
    #             if response.meta.get('plinks'):
    #                 links.extend(response.meta.get('plinks'))
    #                 print "extend.links=", links
    #             link = links[0]
    #             new_meta = response.meta.copy()
    #             new_meta['plinks'] = links[1:]
    #             print "REQUEST",link
    #             print "new_meta=",new_meta
    #             yield Request(url=full_url(link), meta=new_meta, callback=self.parse)
    #     print "PARSE NO-BRAND"
        for l in super(HarrodsProductsSpider, self).parse(response):
            yield l
    #         # print "REMAINING=", response.meta.get('remaining')
    #     print "parse end-FOR",response.meta.get('plinks')
    #     # print "META=", response.meta

    # def _parse_brand(self, response):
    #     print "_PARSE_BRAND", response.url
    #     print "_parse_brand FOR"
    #     for l in super(HarrodsProductsSpider, self).parse(response):
    #         print "l2=", type(l), l
    #         yield l
    #     print "_parse_brand END-FOR"

    def parse_product(self, response):
        # with open("/tmp/harrods-item.html", "w") as f:
        #     f.write(response.body_as_unicode().encode('utf-8'))
        def full_url(url):
            return urlparse.urljoin(response.url, url)

        product = response.meta['product']
        product['url'] = unicode(response.url)

        cond_set(product, 'title', response.xpath(
            "//h1[contains(@class,'product-title')]/span[@itemprop='name']/text()").extract(),
            conv=string.strip)

        cond_set(product, 'brand', response.xpath(
            "//h1[contains(@class,'product-title')]/span[@itemprop='brand']/span[@itemprop='name']/text()").extract(),
            conv=string.strip)
        price = response.xpath(
            "//span[contains(@class,'price')]/span[@itemprop='offers']"
            "/span[@itemprop='price']/text()").re(FLOATING_POINT_RGEX)

        if price:
            price = price[0].replace(',', '')
            product['price'] = Price(
                price=price, priceCurrency='GBP')

        cond_set(product, 'upc', response.xpath(
            "//span[@class='product_code' and @data-prodid]/@data-prodid").extract())

        cond_set(product, 'image_url', response.xpath(
            "//div[@class='f_left']/a[@id='product_img']/img/@src").extract())

        desc = response.xpath("//div[contains(@class,'product_right_box')]/dl").extract()
        cond_set_value(product, 'description', "".join(desc))
        cond_set_value(product, 'locale', "en-GB")

        rel = []
        crst = response.xpath("//div[@id='CrossSellTabs']/div/div/div/ul/li/h3")
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
        alert = self._check_alert(response)
        if alert:
            return 0
        total = response.xpath(
            "//a[@class='page_view_all']/span"
            "/text()").re("(\d+)")
        print "TOTAL=", total
        if total:
            try:
                return int(total[0])
            except ValueError:
                return
        return 0

    def _scrape_product_links(self, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)
        print "_SCRAPE_PRODUCT_LINKS", response.url
        if "http://www.harrods.com/brand/gucci/shoes" == response.url:

            with open("/tmp/harrods-links-men.html", "w") as f:
                f.write(response.body_as_unicode().encode('utf-8'))
            exit(1)                
        if self._check_alert(response):
            return
        links = response.xpath(
            "//ul[contains(@class,'products_row')]/li[@data-type]"
            "/h3/a/@href").extract()
        print "LINKS=", len(links), links
        #exit(1)

        if not links:
            self.log("Found no product links.", DEBUG)
        for link in links:
            #yield None, SiteProductItem(url=full_url(link))
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)
        if self._check_alert(response):
            return
        # Stop this path    
        if 0 and "/brand/" in response.url:
            self.pageno += 1
            pages = response.xpath("//ul[contains(@class,'paging')]/li/a[text()='{pageno}']/@href".format(pageno=self.pageno)).extract()
            if pages:
                return pages[0]

            self.pageno = 1
            plinks = response.meta.get('plinks')
            if not plinks:
                return
            link = plinks[0]
            new_meta = response.meta.copy()
            new_meta['plinks'] = plinks[1:]
            # print "mew_meta=", new_meta
            del new_meta['total_matches']
            print "NEXT BAND",link
            return Request(url=full_url(link), meta=new_meta)

        self.pageno += 1
        cpageno = str(self.pageno)
        pages = response.xpath("//span[@class='pageselectortext']/a[text()='{pageno}']/@href".format(pageno=cpageno)).extract()
        if pages:
            return pages[0]
        else:
            return
