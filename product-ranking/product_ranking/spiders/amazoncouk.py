# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

from scrapy.log import ERROR
from scrapy.selector import Selector

from scrapy.http import Request
from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FormatterWithDefaults

# scrapy crawl amazoncouk_products -a searchterms_str="iPhone"


class AmazonCoUkProductsSpider(BaseProductsSpider):
    name = "amazoncouk_products"
    allowed_domains = ["www.amazon.co.uk"]
    start_urls = []
    
    SEARCH_URL = ("http://www.amazon.co.uk/s/ref=nb_sb_noss?"
                  "url=search-alias=aps&field-keywords={search_term}&rh=i:aps,"
                  "k:{search_term}&ajr=0")

    def __init__(self, *args, **kwargs):
        # locations = settings.get('AMAZONFRESH_LOCATION')
        # loc = locations.get(location, '')
        print 'debug init:'
        super(AmazonCoUkProductsSpider, self).__init__(*args, **kwargs)

    def parse_product(self, response):
        prod = response.meta['product']

        title = response.xpath('//span[@id="productTitle"]/text()').extract()
        cond_set(prod, 'title', title)

        brand = response.xpath('//a[@id="brand"]/text()').extract()
        cond_set(prod, 'brand', brand)

        price = response.xpath(
            '//span[@id="priceblock_ourprice"]/text()').extract()
        cond_set(prod, 'price', price)

        if prod.get('price', None):
            if not u'£' in prod.get('price', ''):
                self.log('Invalid price at: %s' % response.url, level=ERROR)
            else:
                prod['price'] = Price(
                    price=prod['price'].replace(u'£', '').replace(
                        ' ', '').replace(',', '').strip(),
                    priceCurrency='GBP'
                )

        des = response.xpath(
            '//div[@id="detail_bullets_id"]/div[@class="content"]/text()'
        ).extract()
        cond_set(prod, 'description', des)

        img_url = response.xpath(
            '//div[@id="imgTagWrapperId"]/img/@src').extract()
        cond_set(prod, 'image_url', img_url)

        cond_set(prod, 'locale', ['en-US'])

        prod['url'] = response.url
        return prod

    def _search_page_error(self, response):
        sel = Selector(response)

        try:
            found1 = sel.xpath('//div[@class="warning"]/p/text()').extract()[0]
            found2 = sel.xpath(
                '//div[@class="warning"]/p/strong/text()'
            ).extract()[0]
            found = found1 + " " + found2
            if 'did not match any products' in found:
                self.log(found, ERROR)
                return True
            return False
        except IndexError:
            return False

    def _scrape_total_matches(self, response):
        if 'did not match any products.' in response.body_as_unicode():
            total_matches = 0
        else:
            count_matches = response.xpath(
                '//h2[@id="s-result-count"]/text()').re('of ([\d,]+)')
            if count_matches and count_matches[-1]:
                total_matches = int(count_matches[-1].replace(',', ''))
            else:
                total_matches = None
        return total_matches

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[contains(@class, "s-item-container")]'
            '//a[contains(@class, "s-access-detail-page")]/@href'
        ).extract()
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        links = response.xpath(
            '//a[@id="pagnNextLink"]/@href'
        )
        if links:
            return links.extract()[0].strip()
        return None
