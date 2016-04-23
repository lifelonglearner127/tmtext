# -*- coding: utf-8 -*-

# TODO:
# image url
# zip code "in stock" check
#

from __future__ import division, absolute_import, unicode_literals

import json
import re
from urllib import urlencode
import urlparse
import datetime
import os
import time

from scrapy import Request
from scrapy.http.request.form import FormRequest
from scrapy.dupefilter import RFPDupeFilter
from scrapy.conf import settings
from scrapy.utils.request import request_fingerprint

from product_ranking.items import SiteProductItem, Price, BuyerReviews, \
    RelatedProduct
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set
from product_ranking.spiders import cond_set_value


is_empty = lambda x, y=None: x[0] if x else y


class CustomHashtagFilter(RFPDupeFilter):
    """ Considers hashtags to be a unique part of URL """

    @staticmethod
    def rreplace(s, old, new, occurrence):
        li = s.rsplit(old, occurrence)
        return new.join(li)

    def _get_unique_url(self, url):
        return self.rreplace(url, '#', '_', 1)

    def request_seen(self, request):
        fp = self._get_unique_url(request.url)
        if fp in self.fingerprints:
            return True
        self.fingerprints.add(fp)
        if self.file:
            self.file.write(fp + os.linesep)


class ATTProductsSpider(BaseProductsSpider):
    name = "att_products"
    allowed_domains = ["att.com",
                       'api.bazaarvoice.com',
                       'recs.richrelevance.com']

    PAGINATE_URL = "https://www.att.com/global-search/search_ajax.jsp?q={search_term}" \
                   "&sort=score%20desc&fqlist=&colPath=--sep--Shop--sep--All--sep--" \
                   "&gspg={page_num}&dt={datetime}"

    SEARCH_URL = "https://www.att.com/global-search/search_ajax.jsp?q={search_term}" \
                 "&sort=score%20desc&fqlist=&colPath=--sep--Shop--sep--All--sep--" \
                 "&gspg=0&dt=" + str(time.time())

    VARIANTS_URL = "https://www.att.com/services/shopwireless/model/att/ecom/api/" \
                   "DeviceDetailsActor/getDeviceProductDetails?" \
                   "includeAssociatedProducts=true&includePrices=true&skuId={sku}"

    BUYER_REVIEWS_URL = "https://api.bazaarvoice.com/data/batch.json?passkey={pass_key}" \
                        "&apiversion=5.5&displaycode=4773-en_us&resource.q0=products" \
                        "&filter.q0=id%3Aeq%3A{sku}&stats.q0=questions%2Creviews" \
                        "&filteredstats.q0=questions%2Creviews&filter_questions.q0" \
                        "=contentlocale%3Aeq%3Aen_US&filter_answers.q0=contentlocale%3Aeq%3Aen_US" \
                        "&filter_reviews.q0=contentlocale%3Aeq%3Aen_US&filter_reviewcomments.q0" \
                        "=contentlocale%3Aeq%3Aen_US&resource.q1=questions&filter.q1" \
                        "=productid%3Aeq%3A{sku}&filter.q1=contentlocale%3Aeq%3Aen_US" \
                        "&sort.q1=lastapprovedanswersubmissiontime%3Adesc&stats.q1" \
                        "=questions&filteredstats.q1=questions&include.q1=authors%2Cproducts%2Canswers" \
                        "&filter_questions.q1=contentlocale%3Aeq%3Aen_US&filter_answers.q1" \
                        "=contentlocale%3Aeq%3Aen_US&sort_answers.q1=submissiontime%3Adesc&limit.q1" \
                        "=10&offset.q1=0&limit_answers.q1=10&resource.q2=reviews&filter.q2" \
                        "=isratingsonly%3Aeq%3Afalse&filter.q2=productid%3Aeq%3A{sku}&filter.q2" \
                        "=contentlocale%3Aeq%3Aen_US&sort.q2=relevancy%3Aa1&stats.q2" \
                        "=reviews&filteredstats.q2=reviews&include.q2=authors%2Cproducts%2Ccomments" \
                        "&filter_reviews.q2=contentlocale%3Aeq%3Aen_US&filter_reviewcomments.q2" \
                        "=contentlocale%3Aeq%3Aen_US&filter_comments.q2=contentlocale%3Aeq%3Aen_US" \
                        "&limit.q2=8&offset.q2=0&limit_comments.q2=3&resource.q3=reviews" \
                        "&filter.q3=productid%3Aeq%3A{sku}&filter.q3=contentlocale%3Aeq%3Aen_US&limit.q3=1" \
                        "&resource.q4=reviews&filter.q4=productid%3Aeq%3A{sku}&filter.q4" \
                        "=isratingsonly%3Aeq%3Afalse&filter.q4=rating%3Agt%3A3&filter.q4" \
                        "=totalpositivefeedbackcount%3Agte%3A3&filter.q4=contentlocale%3Aeq%3Aen_US&sort.q4" \
                        "=totalpositivefeedbackcount%3Adesc&include.q4=authors%2Creviews%2Cproducts" \
                        "&filter_reviews.q4=contentlocale%3Aeq%3Aen_US&limit.q4=1&resource.q5" \
                        "=reviews&filter.q5=productid%3Aeq%3A{sku}&filter.q5=isratingsonly%3Aeq%3Afalse" \
                        "&filter.q5=rating%3Alte%3A3&filter.q5=totalpositivefeedbackcount%3Agte%3A3" \
                        "&filter.q5=contentlocale%3Aeq%3Aen_US&sort.q5=totalpositivefeedbackcount%3Adesc" \
                        "&include.q5=authors%2Creviews%2Cproducts&filter_reviews.q5=contentlocale%3Aeq%3Aen_US" \
                        "&limit.q5=1&callback=BV._internal.dataHandler0"

    BUYER_REVIEWS_PASS = '9v8vw9jrx3krjtkp26homrdl8'

    current_page = 0

    def __init__(self, *args, **kwargs):
        settings.overrides["DUPEFILTER_CLASS"] = 'product_ranking.spiders.att.CustomHashtagFilter'
        super(ATTProductsSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

    def _scrape_product_links(self, response):
        serp_links = response.xpath(
            '//ul[contains(@class, "resultList")]//'
            'a[contains(@class, "resultLink")]/@href').extract()
        #new_meta = response.meta
        #new_meta['product'] = SiteProductItem()
        for link in serp_links:
            #yield Request(link, meta=response.meta, dont_filter=True,
            #              callback=self.parse_product), SiteProductItem()
            yield link, SiteProductItem()

    def _parse_single_product(self, response):
        return self.parse_product(response)

    @staticmethod
    def _get_sku(response):
        sku = re.search(r'skuId=([a-zA-Z0-9]+)', response.url)
        if sku:
            return sku.group(1)
        sku = response.xpath('//meta[contains(@name, "sku")]/@CONTENT').extract()
        if not sku:
            sku = response.xpath('//meta[contains(@name, "sku")]/@content').extract()
        if not sku:
            sku = response.xpath('//div[contains(@id, "prodIdCartItem")]/@data-sku').extract()
        if sku:
            return sku[0]

    @staticmethod
    def _parse_title(response):
        title = response.xpath('//h1[contains(@id, "accPageTitle")]/text()').extract()
        if not title:
            title = response.xpath('//h1//text()').extract()
        if title:
            return title[0].strip()

    @staticmethod
    def _parse_ajax_variants(response):
        # TODO:
        pass

    def _on_buyer_reviews_response(self, response):
        prod = response.meta['product']
        brs = json.loads(response.body.split('(', 1)[1][0:-1])
        try:
            average_rating = brs['BatchedResults']['q2']['Includes']['Products'].items()[0][1][
                'FilteredReviewStatistics']['AverageOverallRating']
        except (IndexError, KeyError):
            prod['buyer_reviews'] = ZERO_REVIEWS_VALUE
            yield prod
            return
        rating_by_star = brs['BatchedResults']['q2']['Includes']['Products'].items()[0][1][
            'FilteredReviewStatistics']['RatingDistribution']
        total_reviews = brs['BatchedResults']['q2']['Includes']['Products'].items()[0][1][
            'FilteredReviewStatistics']['TotalReviewCount']
        prod['buyer_reviews'] = BuyerReviews(
            num_of_reviews=total_reviews,
            average_rating=float(average_rating),
            rating_by_star={v['RatingValue']: v['Count'] for v in rating_by_star}
        )
        yield prod

    def _parse_ajax_product_data(self, response):
        prod = response.meta['product']
        v = json.loads(response.body)
        prod['brand'] = v['result']['methodReturnValue'].get('manufacturer', '')
        prod['variants'] = self._parse_ajax_variants(
            v['result']['methodReturnValue'].get('skuItems', {}))
        # get data of selected (default) variant
        sel_v = v['result']['methodReturnValue'].get('skuItems', {}).get(
            response.meta['selected_sku'])
        prod['is_out_of_stock'] = sel_v['outOfStock']
        prod['model'] = sel_v.get('model', '')
        _price = sel_v.get('priceList', [{}])[0].get('listPrice', None)
        if _price:
            prod['price'] = Price(price=_price, priceCurrency='USD')
        prod['is_in_store_only'] = not sel_v.get('retailAvailable', True)
        prod['title'] = sel_v['displayName']
        prod['sku'] = response.meta['selected_sku']
        yield prod

    def parse_product(self, response):
        product = response.meta['product']
        product['_subitem'] = True
        product['title'] = self._parse_title(response)
        cond_set(
            product, 'description',
            response.xpath('//meta[contains(@property,"og:description")]/@content').extract())
        cond_set(
            product, 'image_url',
            response.xpath('//meta[contains(@property,"og:image")]/@content').extract())
        new_meta = response.meta
        new_meta['product'] = product
        new_meta['selected_sku'] = self._get_sku(response)
        if '{{' in product['title']:
            # we got a bloody AngularJS-driven page, parse it
            yield Request(
                self.VARIANTS_URL.format(sku=self._get_sku(response)),
                callback=self._parse_ajax_product_data,
                meta=new_meta)
        yield Request(
            self.BUYER_REVIEWS_URL.format(pass_key=self.BUYER_REVIEWS_PASS,
                                          sku=self._get_sku(response)),
            callback=self._on_buyer_reviews_response,
            meta=new_meta
        )
        yield product

    def _scrape_next_results_page_link(self, response):
        self.current_page += 1
        if not list(self._scrape_product_links(response)):
            return  # end of pagination reached
        return self.PAGINATE_URL.format(
            search_term=self.searchterms[0], page_num=self.current_page,
            datetime=time.time())

    def _scrape_total_matches(self, response):
        result_count = response.xpath(
            '//span[contains(@class, "topResultCount")]/text()').extract()
        if result_count:
            result_count = result_count[0].replace(',', '').replace('.', '')\
                .replace(' ', '')
            if result_count.isdigit():
                return int(result_count)
        if u"Hmmm....looks like we don't have any results for" \
                in response.body_as_unicode():
            return 0
