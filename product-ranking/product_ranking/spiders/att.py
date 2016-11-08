# -*- coding: utf-8 -*-

# TODO:
# image url
# zip code "in stock" check
#

from __future__ import division, absolute_import, unicode_literals

import json
import re
import itertools
import os
import copy
import time

from scrapy import Request
from scrapy.dupefilter import RFPDupeFilter

from product_ranking.items import SiteProductItem, Price, BuyerReviews, \
    RelatedProduct
from product_ranking.guess_brand import guess_brand_from_first_words
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set


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

    VARIANTS_ANGULAR_URL = "https://www.att.com/services/shopwireless/model/att/ecom/api/" \
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
        #settings.overrides["DUPEFILTER_CLASS"] = 'product_ranking.spiders.att.CustomHashtagFilter'
        super(ATTProductsSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

    def _scrape_product_links(self, response):
        serp_links = []
        serp_imgs = response.xpath(
            '//ul[contains(@class, "resultList")]//img[contains(@class, "icon")]')
        for img in serp_imgs:
            if not 'icon_doc.png' in str(is_empty(img.xpath('./@src').extract())):
                serp_link = is_empty(
                    img.xpath('../../a[contains(@class, "resultLink")]/@href').extract())
                if serp_link:
                    if not serp_link in serp_links:
                        serp_links.append(serp_link)
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
    def _parse_ajax_variants(response, variants):
        prod = response.meta['product']
        result_variants = []
        for v in variants.values():
            variant = copy.copy({})
            variant['in_stock'] = not v.get('outOfStock', None)
            # get the lowest price
            price_list_options = v.get('priceList', [])
            price_list_options = sorted(price_list_options, key=lambda val: val.get('listPrice', 0))
            variant['price'] = price_list_options[0].get('listPrice', None)
            variant['sku'] = v.get('skuId', None)
            variant['selected'] = v.get('selectedSku', False)
            props = copy.copy({})
            if v.get('color', None):
                props['color'] = v['color']
            if v.get('size', None):
                props['size'] = v['size']
            variant['properties'] = props
            result_variants.append(variant)
        return result_variants

    def _get_brs_type_for_this_product(self, brs_sku, response):
        """ Returns the BRs used in this product
            (can be "FilteredReviewStatistics" and "ReviewStatistics")
        :param response:
        :return:
        """
        brs_types = ['FilteredReviewStatistics', 'ReviewStatistics']
        prod = response.meta['product']
        num_of_reviews_ = response.meta.get('num_of_reviews_', None)
        if not num_of_reviews_:
            return brs_types[0]  # fall back to this type
        total_reviews_filt = brs_sku[brs_types[0]]['TotalReviewCount']
        total_reviews_unfilt = brs_sku[brs_types[1]]['TotalReviewCount']
        # find the number which is closer to the on-page scraped one
        if abs(num_of_reviews_ - total_reviews_filt) \
                < (num_of_reviews_ - total_reviews_unfilt):
            return brs_types[0]
        else:
            return brs_types[1]

    def _on_buyer_reviews_response(self, response):
        prod = response.meta['product']
        brs = json.loads(response.body.split('(', 1)[1][0:-1])
        # get brand name if empty
        try:
            if not prod.get('brand'):
                prod['brand'] = brs.get(
                    'BatchedResults').get('q0').get('Results')[0].get('Brand').get('Name')
        except IndexError:
            pass
        try:
            brs_sku = brs['BatchedResults']['q2']['Includes']['Products'][prod['sku']]
        except (IndexError, KeyError):
            try:
                brs_sku_id = brs['BatchedResults']['q0']['Results'][0]['Id']
                brs_sku = brs['BatchedResults']['q0']['Results'][0]
                if brs_sku_id != prod['sku']:
                    raise IndexError  # invalid SKU - assume we have no buyer reviews
            except (IndexError, KeyError):
                prod['buyer_reviews'] = ZERO_REVIEWS_VALUE
                yield prod
                return
        # get appropriate BRs type (used in this product)
        review_stat_key = self._get_brs_type_for_this_product(brs_sku, response)
        try:
            average_rating = brs_sku[review_stat_key]['AverageOverallRating']
        except (IndexError, KeyError):
            prod['buyer_reviews'] = ZERO_REVIEWS_VALUE
            yield prod
            return
        if average_rating is None:
            prod['buyer_reviews'] = ZERO_REVIEWS_VALUE
            yield prod
            return
        rating_by_star = brs_sku[review_stat_key]['RatingDistribution']
        total_reviews = brs_sku[review_stat_key]['TotalReviewCount']
        prod['buyer_reviews'] = BuyerReviews(
            num_of_reviews=total_reviews,
            average_rating=float(average_rating),
            rating_by_star={v['RatingValue']: v['Count'] for v in rating_by_star}
        )
        yield prod

    def _parse_ajax_product_data(self, response):
        prod = response.meta['product']
        v = json.loads(response.body)
        try:
            is_oos = v['result']['serviceErrors'][0]['errorCode'] == 'SHOPERR_GENERAL_0001'
        except (IndexError, KeyError):
            is_oos = False
        if is_oos:
            if '{{' in prod.get('title'):
                prod['title'] = response.meta['title_no_sku']
                prod['is_out_of_stock'] = True
                prod['sku'] = response.meta['selected_sku']
                yield prod
                return
        prod['brand'] = v['result']['methodReturnValue'].get('manufacturer', '')
        prod['variants'] = self._parse_ajax_variants(
            response, v['result']['methodReturnValue'].get('skuItems', {}))
        # There is something wrong with sku for some smartphones with one variation
        # (maybe broken js on page?), so we take sku from what we have
        if len(prod['variants']) == 1:
            only_sku = prod['variants'][0]['sku']
            sel_v = v['result']['methodReturnValue'].get('skuItems', {}).get(only_sku)
        # get data of selected (default) variant
        else:
            sel_v = v['result']['methodReturnValue'].get('skuItems', {}).get(
                response.meta['selected_sku'])
        prod['is_out_of_stock'] = sel_v['outOfStock']
        prod['model'] = sel_v.get('model', '')
        # get the lowest price
        price_list_options = sel_v.get('priceList', [])
        price_list_options = sorted(price_list_options, key=lambda val: val.get('listPrice', 0))
        _price = price_list_options[0].get('listPrice', None)
        if _price or _price == 0:
            prod['price'] = Price(price=_price, priceCurrency='USD')
        if sel_v.get('retailAvailable', None) is False:
            prod['available_store'] = 0
        prod['title'] = sel_v['displayName']
        prod['sku'] = response.meta['selected_sku']
        yield prod

    def _on_variants_response_url2(self, response):
        variants = []
        prod = response.meta['product']
        variants_block = response.css('#pbDeviceVariants')
        if variants_block:
            colors = variants_block.css('#variantColor #colorInput a')
            sizes = variants_block.css('#variantSize #sizeInput a')
            if colors:
                colors = [c.xpath('./@title').extract()[0] for c in colors]
                colors = [{'color': c} for c in colors]
            if sizes:
                sizes = [s.xpath('./text()').extract()[0].strip() for s in sizes]
                sizes = [{'size': s} for s in sizes]
            if colors and sizes:
                variants_combinations = list(itertools.product(sizes, colors))
            elif colors:
                variants_combinations = colors
            else:
                variants_combinations = sizes
            for variant_combo in variants_combinations:
                new_variant = copy.copy({})
                new_variant['properties'] = variant_combo
                variants.append(new_variant)
            prod['variants'] = variants
        if u'available online - web only' in response.body_as_unicode().lower():
            prod['available_store'] = 0
        yield prod

    def _scrape_related_products_links(self, response, product):
        # v1 links
        rex_url = re.search(r'rexURL.*?"(.+)?";', response.body_as_unicode())
        if rex_url:
            rex_url = rex_url.group(1)
            if rex_url.startswith('/'):
                rex_url = 'http://att.com' + rex_url
            yield rex_url, 'viewed'
        # v2 links
        viewed_url = re.search(
            r'jQuery.ajax\(\{.*?url: "(.+)"\+deviceSkuId, .{5,200}ViewXViewedY',
            response.body_as_unicode())
        if viewed_url:
            viewed_url = viewed_url.group(1)
            if viewed_url.startswith('/'):
                viewed_url = 'http://att.com' + viewed_url
            yield viewed_url+self._get_sku(response), 'viewed'
        bought_url = re.search(
            r'jQuery.ajax\(\{.*?url: "(.+)"\+deviceSkuId, .{5,200}ViewXBoughtY',
            response.body_as_unicode())
        if bought_url:
            bought_url = bought_url.group(1)
            if bought_url.startswith('/'):
                bought_url = 'http://att.com' + bought_url
            yield bought_url+self._get_sku(response), 'bought'

    def _on_related_product_response(self, response):
        rpl_type = response.meta['_rel_type']
        prod = response.meta['product']
        try:
            resp_json = json.loads(response.body)
        except:
            resp_json = None
        related_list = []
        if resp_json:  # json response
            for related in resp_json:
                try:
                    prod_url = related['productUrl']
                except KeyError:
                    continue
                if prod_url.startswith('//'):
                    prod_url = 'http:' + prod_url
                related_list.append(RelatedProduct(related['name'], prod_url))
        else:
            for rel_prod in response.xpath('//td//div[contains(@class, "_result_title")]/a'):
                related_list.append(RelatedProduct(rel_prod.xpath('./text()').extract()[0],
                                                   rel_prod.xpath('./@href').extract()[0]))
        if not 'related_products' in prod:
            prod['related_products'] = {}
        if rpl_type == 'bought':
            prod['related_products']['buyers_also_bought'] = related_list
        else:
            prod['related_products']['related_products'] = related_list
        yield prod

    def parse_product(self, response):
        product = response.meta['product']
        product['_subitem'] = True
        product['title'] = self._parse_title(response)
        if product['title']:
            # this needed only for att.com, mostly for headsets
            split_title = product['title'].split(' - ') if ' - ' in product['title'] else None
            if split_title:
                split_title = [s.strip() for s in split_title if s.strip()]
                brand_list = []
                for section in split_title:
                    brand_list.append(guess_brand_from_first_words(section))
                brand_list = [b for b in brand_list if b]
                product['brand'] = brand_list[0] if brand_list else None
            else:
                product['brand'] = guess_brand_from_first_words(product['title'])
        cond_set(
            product, 'description',
            response.xpath('//meta[contains(@name,"og:description")]/@content').extract())
        if not product.get('description', None):
            cond_set(
                product, 'description',
                response.xpath('//meta[contains(@property,"og:description")]/@content').extract())
        cond_set(
            product, 'image_url',
            response.xpath('//meta[contains(@name,"og:image")]/@content').extract())
        cond_set(
            product, 'image_url',
            response.xpath('//meta[contains(@property,"og:image")]/@content').extract())
        if not product.get('image_url', None):
            cond_set(
                product, 'image_url',
                response.xpath('//img[contains(@id,"deviceHeroImage")]/@src').extract())
        _price = response.xpath('//div[contains(@id,"prodIdCartItem")]/@data-nocommitmentprice').extract()
        if not _price:
            _price = response.xpath('//*[contains(@class, "listItemPriceRt")]/text()').extract()
        if _price:
            product['price'] = Price(price=_price[0].replace('$', ''), priceCurrency='USD')
        product['sku'] = self._get_sku(response)
        if not product['sku']:
            return
        new_meta = response.meta
        new_meta['product'] = product
        new_meta['selected_sku'] = self._get_sku(response)
        # response.xpath does not work here for some reasons
        num_of_reviews_ = re.search('<meta itemprop="reviewCount" content="(\d+)"',
                                    response.body_as_unicode())
        if num_of_reviews_:
            new_meta['num_of_reviews_'] = int(num_of_reviews_.group(1))
        if not product.get('title', None):
            return
        if '{{' in product['title']:
            # we got a bloody AngularJS-driven page, parse it
            for title_no_sku in response.xpath(
                    '//h1[contains(@ng-if,"(!selectedSku.preOwned")]/text()').extract():
                if not '{{' in title_no_sku:
                    new_meta['title_no_sku'] = title_no_sku
            yield Request(
                self.VARIANTS_ANGULAR_URL.format(sku=self._get_sku(response)),
                callback=self._parse_ajax_product_data,
                meta=new_meta)
        yield Request(
            self.BUYER_REVIEWS_URL.format(pass_key=self.BUYER_REVIEWS_PASS,
                                          sku=self._get_sku(response)),
            callback=self._on_buyer_reviews_response,
            meta=new_meta
        )
        # construct variants url #2
        variants_url2 = response.url.split('#', 1)[0].replace('.html', '.pricearea.xhr.html', 1)
        variants_url2 += '?locale=en_US&skuId={sku}&pageType=accessoryDetails&_={time}'.format(
            sku=self._get_sku(response), time=str(time.time()))
        yield Request(
            variants_url2, callback=self._on_variants_response_url2, meta=new_meta)
        for rpl, rel_type in self._scrape_related_products_links(response, product):
            new_meta['_rel_type'] = rel_type
            yield Request(
                rpl, callback=self._on_related_product_response, meta=new_meta)
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
