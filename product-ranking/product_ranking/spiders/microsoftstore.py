# -*- coding: utf-8 -*-#

import json
import re
import string
import itertools
import urllib

from scrapy.http import FormRequest, Request
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set_value
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi
from product_ranking.settings import ZERO_REVIEWS_VALUE

is_empty = lambda x, y=None: x[0] if x else y


class MicrosoftStoreProductSpider(BaseProductsSpider):

    name = 'microsoftstore_products'
    allowed_domains = ["www.microsoftstore.com"]

    SEARCH_URL = "http://www.microsoftstore.com/store?keywords={search_term}" \
                 "&SiteID=msusa&Locale=en_US" \
                 "&Action=DisplayProductSearchResultsPage&" \
                 "result=&sortby=score%20descending&filters="

    PAGINATE_URL = 'http://www.microsoftstore.com/store/msusa/en_US/filterSearch/' \
                   'categoryID.{category_id}/startIndex.{start_index}/size.{size}/sort.score%' \
                   '20descending?keywords={search_term}&' \
                   'Env=BASE&callingPage=productSearchResultPage'

    REVIEWS_URL = 'http://api.bazaarvoice.com/data/batch.json' \
                  '?passkey=291coa9o5ghbv573x7ercim80&apiversion=5.5' \
                  '&displaycode=5681-en_us&resource.q0=reviews' \
                  '&filter.q0=isratingsonly%3Aeq%3Afalse' \
                  '&filter.q0=productid%3Aeq%3A{product_id}' \
                  '&filter.q0=contentlocale%3Aeq%3Aen_US' \
                  '&sort.q0=helpfulness%3Adesc%' \
                  '2Ctotalpositivefeedbackcount%3Adesc' \
                  '&stats.q0=reviews&filteredstats.q0=reviews' \
                  '&include.q0=authors%2Cproducts%2Ccomments' \
                  '&filter_reviews'



    def __init__(self, *args, **kwargs):
        self.br = BuyerReviewsBazaarApi(called_class=self)
        self.start_index = 0

        super(MicrosoftStoreProductSpider, self).__init__(*args, **kwargs)

    def parse_product(self, response):
        reqs = []
        meta = response.meta
        product = meta['product']

        product_id = is_empty(response.xpath(
            '//script[contains(text(), "productId")]/text()').re(
            r"productId: '(\d+)'"))
        meta['product_id'] = product_id

        # Set locale
        product['locale'] = 'en_US'

        # Parse title
        title = self.parse_title(response)
        cond_set_value(product, 'title', title)

        # Parse brand
        brand = self.parse_brand(response)
        cond_set_value(product, 'brand', brand)

       # Parse price
        price = self.parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse image url
        image_url = self.parse_image_url(response)
        cond_set_value(product, 'image_url', image_url, conv=string.strip)

        # Parse description
        description = self.parse_description(response)
        cond_set_value(product, 'description', description, conv=string.strip)

        # Parse sku
        sku = self.parse_sku(response)
        cond_set_value(product, 'sku', sku)

        # Parse variants
        variants = self.parse_variant(response)
        cond_set_value(product, 'variants', variants)

        # Parse buyer reviews
        reqs.append(
            Request(
                url=self.REVIEWS_URL.format(product_id=product_id),
                dont_filter=True,
                callback=self.parse_buyer_reviews,
                meta=meta
            )
        )

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def parse_sku(self, response):
        sku = is_empty(response.xpath('//script[contains(text(), "sku")]').re(r"sku : \[(.*)\]"))
        return sku

    def parse_buyer_reviews(self, response):
        meta = response.meta
        product = meta['product']
        product_id = meta['product_id']
        data = response.body

        rating_by_star = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}

        if data:
            data = json.loads(data)

            if data:
                try:
                    js = data["BatchedResults"]['q0']['Includes']['Products'][product_id]['ReviewStatistics']
                    total = js['TotalReviewCount']
                    average = js['AverageOverallRating']
                    stars = data["BatchedResults"]['q0']['Includes']['Products'][product_id]['ReviewStatistics']['RatingDistribution']

                    for star in stars:
                       rating_by_star[str(star['RatingValue'])] = star['Count']

                    if total and average and stars:
                        buyer_reviews = {
                            'num_of_reviews': int(total),
                            'average_rating': round(average, 1),
                            'rating_by_star': rating_by_star
                        }

                    product['buyer_reviews'] = BuyerReviews(**buyer_reviews)

                except:
                    product['buyer_reviews'] = ZERO_REVIEWS_VALUE



        return product


    def parse_title(self, response):
        title = is_empty(response.xpath(
            '//h1[@itemprop="name"]/text()').extract())
        if title:
            return title

    def parse_brand(self, response):
        brand = is_empty(response.xpath(
            '//div[@class="shell-header-brand"]/a/@title').extract())

        return brand

    def parse_price(self, response):
        price = is_empty(response.xpath(
            '//p[@class="current-price"]/span/text()').re(r'(\d+\.?\d+)'))

        currency = is_empty(response.xpath(
            '//meta[@itemprop="priceCurrency"]/@content').extract())
        if not price:
            price = is_empty(response.xpath(
                '//span[@itemprop="price"]/text()').re(r'(\d+\.?\d+)'))
        if not price:
            price = is_empty(response.xpath(
                                   '//span[@itemprop="price"]/text()').re(r'Starting from .(\d+\.?\d+)'))

        if price and currency:
            price = Price(price=price, priceCurrency=currency)
        else:
            price = Price(price=0.00, priceCurrency="USD")
        return price

    def parse_image_url(self, response):
        image_url = is_empty(response.xpath(
            '//div[@class="image-container"]/@data-src').extract())
        if not image_url:
            image_url = is_empty(response.xpath(
                './/*[@class="product-hero base-hero"]/li[1]/img/@src').extract())
        if not image_url:
            image_url = is_empty(response.xpath(
                './/*[@data-class="poster"]/@data-src').extract())
        if image_url:
            return image_url

    def parse_description(self,response):
        description = is_empty(response.xpath(
            '//div[@class="short-desc"]').extract())

        return description

    def parse_variant(self, response):
        # options = {}
        # color ={}
        # color_list = response.xpath('//ul[contains(@class, "product-colors")]/li[contains(@class, "selected")]/a/@title').extract()
        # print '*****************',color_list
        # color_pid = response.xpath('//ul[contains(@class, "product-colors")]/li/a/@var-pid').extract()
        # data4 = response.xpath('//ul[contains(@class, "option-list")]/li/a//text()').extract()
        # data4 = [i for i in data4 if i != u'\n' and i != u'*']
        # data_pid = response.xpath('//ul[contains(@class, "option-list")]/li/@data-pid').extract()
        # # print data_pid, data4
        # if color_list:
        #     for i, items in enumerate(color_pid):
        #         color[items] = color_list[i]
        # if data_pid:
        #     for i, items in enumerate(data_pid):
        #         options[items] = data4[i]
        # print options, color

        return 'variant'

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
                '//span[@class="product-count"]/text()').re(r'\d+'))
        if total_matches:
            total_matches = total_matches.replace(',', '')
            return int(total_matches)
        else:
            return 0

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """
        links = response.xpath(
            '//div[@class="product-row"]/a/@href'
        ).extract()

        per_page = len(links)
        return per_page

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """
        links = response.xpath(
            '//div[@class="product-row"]/a/@href'
        ).extract()

        if links:
            for link in links:
                yield 'http://www.microsoftstore.com/' + link, SiteProductItem()
        else:
            self.log("Found no product links in {url}".format(url=response.url), INFO)

    def _scrape_next_results_page_link(self, response):
        total = self._scrape_total_matches(response)
        size = self._scrape_results_per_page(response)
        self.start_index += size
        if self.start_index != total:
            category_id = is_empty(
                response.xpath(
                    "//div[@id='productListContainer']/@category-id").extract())
            return Request(
                self.PAGINATE_URL.format(
                    search_term=response.meta['search_term'],
                    size=size,
                    start_index=self.start_index,
                    category_id=category_id),
                    meta=response.meta
                )