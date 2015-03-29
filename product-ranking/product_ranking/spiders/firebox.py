# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

import json
import re

from scrapy.http import FormRequest

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set


class FireboxProductSpider(BaseProductsSpider):
    name = 'firebox_products'
    allowed_domains = ["www.firebox.com"]
    start_urls = []
    SEARCH_URL = "http://www.firebox.com/firebox/search?searchstring={search_term}"

    convert_currency = {
        u'\u00a3':  'GBP',
        u'\u20ac':  'EUR',
        u'$':       'USD'
    }

    currency = 1

    def parse_product(self, response):
        prod = response.meta['product']
        reviews = response.xpath('//div[@id="review_loading"]/'
                                 'following::div[contains(@id, "review_")]')
        if reviews and len(reviews) > 0:
            total = len(reviews)
            stars = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            sum = 0

            for review in reviews:
                stars_count = len(review.xpath('./i[@class="icon-star"]'))
                if stars_count == 0:
                    total -= 1
                    continue
                stars[stars_count] += 1
                sum += stars_count
            avg = float(sum)/float(total)
            prod['buyer_reviews'] = BuyerReviews(total, avg, stars)

        title = response.xpath(
            '//h2[@class="product_name product_title"]/span[@itemprop="name"]/text()'
        ).extract()
        cond_set(prod, 'title', title)

        price = re.findall('(.?)(\d+.\d+)',
                           response.xpath('//div[@class="price"]/text() |'
                                          ' //div[@class="price"]/div/text()')[0]
                           .extract())[0]
        if price:
            priceCurrency = self.convert_currency[price[0]]
            prod["price"] = Price(priceCurrency=priceCurrency,
                                  price=price[1])

        des = response.xpath(
            '//div[@class="clearfix text_box margin_after bg_white"]'
            '| //div[@class="wide_page"]'
        ).extract()
        cond_set(prod, 'description', des)

        img_url = response.xpath(
            '//img[@id="product_image"]/@src'
        ).extract()
        cond_set(prod, 'image_url', img_url)

        cond_set(prod, 'locale', ['en-US'])

        prod['url'] = response.url

        items = response.xpath('//a[contains(@class,"g-med")] | //a[contains(@class,"g-large")]')
        related = []
        for item in items:
            name = item.xpath('.//img/@title').extract()
            link = item.xpath('.//@href').extract()
            if name and link:
                name = name[0]
                link = link[0]
                related.append(RelatedProduct(title=name, url=link))

        prod['related_products'] = {'Similar Products': related}

        available = response.xpath(
            '//meta[@property="og:price:availability"]/@content'
        ).extract()
        if 'preorder' in available:
            prod['is_out_of_stock'] = True
        elif 'instock' in available:
            prod['is_out_of_stock'] = False

        return prod

    def _scrape_total_matches(self, response):
        total_matches = None
        if response.xpath(
                '//div[@class="searchtitle"]/text()[contains(., "No result")]'):
            print 'Not found'
            return 0
        total = response.xpath('//div[@class="searchtitle"]/text()').extract()
        if total:
            total = re.findall("(\d+)", total[0])
        total_matches = int(total[0])

        return total_matches

    def _scrape_product_links(self, response):
        if self._scrape_total_matches(response) == 0:
            return
        xpath = '//div[@class="page"]/script/text()'
        items = json.loads(re.findall('\[.*\]',
                                      response.xpath(xpath)[0].extract())[0])
        for item in items:
            url = item['link']
            meta = response.meta.copy()
            meta['product'] = SiteProductItem()
            formdata = {'new_currency_id': str(self.currency)}
            request = FormRequest(url=url, formdata=formdata,
                                  callback=self.parse_product, meta=meta)
            yield request, meta['product']

    def _scrape_next_results_page_link(self, response):
        return None