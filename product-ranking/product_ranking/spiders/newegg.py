# -*- coding: utf-8 -*-#

import json
import re
import string
import itertools
import urllib
import math

from scrapy.http import FormRequest, Request
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set_value
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi
from product_ranking.settings import ZERO_REVIEWS_VALUE

is_empty = lambda x, y=None: x[0] if x else y


class NeweggProductSpider(BaseProductsSpider):

    name = 'newegg_products'
    allowed_domains = ["www.newegg.com"]

    #SEARCH_URL = "http://www.debenhams.com/webapp/wcs/stores/servlet/" \
    #             "Navigate?langId=-1&storeId=10701&catalogId=10001&txt={search_term}"

    SEARCH_URL = "http://www.newegg.com/Product/ProductList.aspx" \
                 "?Submit=ENE&DEPA=0&Order=BESTMATCH" \
                 "&Description={search_term}&N=-1&isNodeId=1"

    PAGINATE_URL = 'http://www.newegg.com/Product/ProductList.aspx?' \
                   'Submit=ENE&DEPA=0&Order=BESTMATCH&Description={search_term}' \
                   '&N=-1&isNodeId=1&Page={index}'

    # REVIEWS_URL = 'http://www.newegg.com/Product/ProductList.aspx?' \
    #               'Submit=ENE&DEPA=0&Order=BESTMATCH' \
    #               '&Description={search_term}&N=-1&isNodeId=1&Page=1'



    def __init__(self, *args, **kwargs):
        self.br = BuyerReviewsBazaarApi(called_class=self)
        self.index = 0

        super(NeweggProductSpider, self).__init__(*args, **kwargs)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

       #  product_id = is_empty(response.xpath(
       #      '//script[contains(text(), "productId")]/text()').re(
       #      r"productId: '(\d+)'"))
       #  meta['product_id'] = product_id

        # Set locale
        product['locale'] = 'en_US'

        # Parse title
        title = self.parse_title(response)
        cond_set_value(product, 'title', title)

        # Parse brand
        brand = self.parse_brand(response)
        cond_set_value(product, 'brand', brand)

        # Parse model
        model = self.parse_model(response)
        cond_set_value(product, 'model', model)

       # # Parse price
       #  price = self.parse_price(response)
       #  cond_set_value(product, 'price', price)
       #
       #  # # Parse special pricing
       #  # special_pricing = self._parse_special_pricing(response)
       #  # cond_set_value(product, 'special_pricing', special_pricing, conv=bool)

        # Parse image url
        image_url = self.parse_image_url(response)
        cond_set_value(product, 'image_url', image_url)

        # Parse description
        description = self.parse_description(response)
        cond_set_value(product, 'description', description)

        # Parse stock status
        is_out_of_stock = self.parse_stock_status(response)
        cond_set_value(product, 'is_out_of_stock', is_out_of_stock)

       #  # Parse variants
       #  variants = self.parse_variant(response)
       #  cond_set_value(product, 'variants', variants)

        # Parse review
        review = self.parse_buyer_review(response)
        cond_set_value(product, 'buyer_reviews', review)

        # # Parse buyer reviews
        # reqs.append(
        #     Request(
        #         url=self.REVIEWS_URL.format(product_id=product_id),
        #         dont_filter=True,
        #         callback=self.parse_buyer_reviews,
        #         meta=meta
        #     )
        # )

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def parse_buyer_review(self, response):
        num_of_review = is_empty(response.xpath('//*[@id="linkSumRangeAll"]/span//text()').re(r'\d+'))
        res = []
        rating_by_star = {}
        for i in range(1, 6):
            rvm = response.xpath('//span[@id="reviewNumber%s"]//text()' % i).extract()
            if len(rvm) > 0 and (rvm[0]) > 0:
                res.append([i, (rvm[0])])
        if len(res) > 0:
            for item in res:
                rating_by_star[item[0]] = item[1]
        if rating_by_star:
            s = n =0
            for k, v in rating_by_star.iteritems():
                s += int(k) * int(v)
                n += int(v)
            if n > 0:
                average_rating = round(s/float(n),2)

        buyer_reviws = {'num_of_reviews': int(num_of_review),
                        'average_rating': float(average_rating),
                        'rating_by_star': rating_by_star}

        return buyer_reviws

        return None

    def parse_stock_status(self, response):
        stock_status = response.xpath('//script[contains(text(), "product_instock")]/text()').re(r"product_instock:\['(\d+)']")

        if stock_status[0] == '1':
            in_stock = True
        elif stock_status[0] == '0':
            in_stock = False

        return in_stock


    def parse_description(self, response):
        description = response.xpath('//div[@class="grpBullet"]').extract()
        description = [i.strip() for i in description]
        if description:
            return description

    def parse_title(self, response):
        title = is_empty(response.xpath('//h1/span[@itemprop="name"]/text()').extract())

        if title:
            return title

    def parse_brand(self, response):
        brand = is_empty(response.xpath('//dl/dt[contains(text(), "Brand")]/following-sibling::*/text()').extract())

        if brand:
            return brand

    def parse_model(self, response):
        model = is_empty(response.xpath('//dl/dt[contains(text(), "Model")]/following-sibling::*/text()').extract())

        if model:
            return model

    def parse_image_url(self, response):
        image = is_empty(response.xpath('//div[@class="objImages"]/'
                                        'a[@name="gallery"]/'
                                        'span[@class="mainSlide"]'
                                        '/img/@src').extract())

        if image:
            return image

        return None


    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """

        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _scrape_total_matches(self, response):
        """
        Scraping number of resulted product links
        """
        total_matches = is_empty(
            response.xpath(
                '//div[@class="recordCount"]/span[@id="RecordCount_1"]/text()').extract())
        if total_matches:
            return int(total_matches)
        else:
            return 0

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """
        links = response.xpath(
            '//div[@class="itemCell itemCell-ProductList itemCell-ProductGridList"]/'
            'div[@class="itemText"]/div/a/@href'
        ).extract()
        if links:
            per_page = int(len(links))

        if per_page:
            return per_page

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """
        links = response.xpath(
            '//div[@class="itemCell itemCell-ProductList itemCell-ProductGridList"]/'
            'div[@class="itemText"]/div/a/@href'
        ).extract()

        if links:
            for link in links:
                yield link, SiteProductItem()
        else:
            self.log("Found no product links in {url}".format(url=response.url), INFO)

    def _scrape_next_results_page_link(self, response):
        total = self._scrape_total_matches(response)
        size = self._scrape_results_per_page(response)
        pages = int(math.ceil(total/size))
        self.index += 1

        if self.index != int(pages) + 1:
            return self.PAGINATE_URL.format(
                search_term=response.meta['search_term'],
                index=self.index,
                meta=response.meta.copy(),
            )
