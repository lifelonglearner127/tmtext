# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals

import json
import re
from urllib import urlencode
import urlparse

from scrapy import Request
from scrapy.http.request.form import FormRequest

from product_ranking.items import SiteProductItem, Price, BuyerReviews, \
    RelatedProduct
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set
from product_ranking.spiders import cond_set_value


is_empty = lambda x, y=None: x[0] if x else y

class WaitroseProductsSpider(BaseProductsSpider):
    name = "waitrose_products"
    allowed_domains = ["waitrose.com",
                       'api.bazaarvoice.com',
                       'recs.richrelevance.com']
    start_urls = []


    SEARCH_URL = "http://www.waitrose.com/shop/BrowseAjaxCmd"
    _DATA = "Groceries/refined_by/search_term/{search_term}/sort_by/{order}" \
            "/sort_direction/{direction}/page/{page}"

    _PRODUCT_TO_DATA_KEYS = {
        'title': 'name',
        'image_url': 'image',
        'url': 'url',
        'price': 'price',
        'description': 'summary',
    }

    SORT_MODES = {
        'default': ('NONE', 'descending'),
        'popularity': ('popularity', 'descending'),
        'rating': ('averagerating', 'descending'),
        'name_asc': ('name', 'ascending'),
        'name_desc': ('name', 'descending'),
        'price_asc': ('price', 'ascending'),
        'price_desc': ('price', 'descending')
    }

    REVIEW_API_URL = "http://api.bazaarvoice.com/data/batch.json" \
                     "?passkey={apipass}&apiversion=5.5" \
                     "&displaycode=17263-en_gb&resource.q0=products" \
                     "&filter.q0=id%3Aeq%3A{model}&stats.q0=reviews" \
                     "&filteredstats.q0=reviews"

    REVIEW_API_PASS = "ixky61huptwfdsu0v9cclqjuj"

    RR_URL = "http://recs.richrelevance.com/rrserver/p13n_generated.js" \
             "?a=141924517b5442cd" \
             "&p={model}" \
             "&n={title}" \
             "&pt=|item_page.recs_1" \
             "&cts=http%3A%2F%2Fwww.waitrose.com" \
             "&flv=0.0.0&l=1"

    PROD_LOOKUP_URL = "http://www.waitrose.com/shop/LineLookUp?%s"


    def __init__(self, order='default', *args, **kwargs):
        cond_set_value(kwargs, 'site_name', 'waitrose.com')
        super(WaitroseProductsSpider, self).__init__(*args, **kwargs)
        if order not in self.SORT_MODES:
            raise Exception('Sort mode %s not found' % order)
        self._sort_order = order

    @staticmethod
    def _get_data(response):
        return json.loads(response.body_as_unicode())

    def _create_request(self, meta):
        order, direction = self.SORT_MODES[self._sort_order]
        return FormRequest(
            url=WaitroseProductsSpider.SEARCH_URL,
            formdata={
                'browse': WaitroseProductsSpider._DATA.format(
                    search_term=meta['search_term'],
                    page=meta['current_page'],
                    order=order,
                    direction=direction)
            },
            meta=meta,
        )

    def start_requests(self):
        """Generates POSTs instead of GETs."""
        for st in self.searchterms:
            yield self._create_request(
                meta={
                    'search_term': st,
                    'remaining': self.quantity,
                    'current_page': 1,
                },
            )

    def parse_product(self, response):
        product = response.meta['product']
        xpath = '//div[@class="product_disclaimer"]/node()[normalize-space()]'
        cond_set_value(product, 'description', response.xpath(xpath).extract(),
                       ''.join)
        cond_set(product, 'brand',
                 response.css('.at-a-glance span::text').re('Brand (.+)'))
        cond_set_value(product, 'locale', u'en-GB')

        model = response.css('.product-detail::attr(partnumber)').extract()
        if not model:
            model = response.css('.product-detail::attr(partNumber)').extract()
        if not model:
            self.log('Could not find partNumber')
            return
        if model:
            product["model"] = is_empty(model)

        url = self.REVIEW_API_URL.format(model=model[0],
                                         apipass=self.REVIEW_API_PASS)
        if url:
            meta = {"product": product}
            return Request(
                url,
                callback=self.parse_buyer_reviews,
                dont_filter=True,
                meta=meta,
            )
        else:
            cond_set_value(product, 'buyer_reviews', ZERO_REVIEWS_VALUE)
        return product

    def parse_buyer_reviews(self, response):
        product = response.meta["product"]
        data = json.loads(response.body_as_unicode())
        data = data.get('BatchedResults', {}).get('q0', {})
        data = (data.get('Results') or [{}])[0]
        
        if "ImageUrl" in data:
            product["image_url"] = data["ImageUrl"]
        
        data = data.get('FilteredReviewStatistics', {})
        average = data.get('AverageOverallRating')
        total = data.get('TotalReviewCount')
        distribution = data.get('RatingDistribution', [])
        distribution = {d['RatingValue']: d['Count']
                        for d in data.get('RatingDistribution', [])}
        reviews = BuyerReviews(total, average, distribution)

        # sanity check
        assert sum(distribution.values()) == total
        if total:
            avg = sum([k * v for k, v
                       in distribution.items()]) / float(total)
            assert round(avg, 1) == round(float(average), 1)

        cond_set_value(product, 'buyer_reviews',
                       reviews if total else ZERO_REVIEWS_VALUE)
        
        url = ""
        model = product.get("model", None)
        title = product.get("title", None).strip()
        if model and title:
            url = self.RR_URL.format(model=model, title='')
        if url:
            meta = {"product": product}
            return Request(
                url, self.parse_related_products,
                dont_filter=True, meta=meta
            )

        return product

    def parse_related_products(self, response):
        product = response.meta["product"]

        relation = is_empty(re.findall('"message": *"([^"]+)', response.body))
        ids = re.findall('"id": "([^"]+)', response.body)
        args = {'lineNumber_%i' % (i + 1): pid for i, pid in enumerate(ids)}
        args.update({'_method': 'GET'})
        args = urlencode(args)
        url = self.PROD_LOOKUP_URL % args

        if url:
            meta = {'relation': relation, "product": product}
            return Request(url, self.parse_rp_lookup, dont_filter=True,
                          meta=meta)

        return product

    def parse_rp_lookup(self, response):
        baseurl = 'http://waitrose.com'
        jsondata = json.loads(response.body_as_unicode())
        products = [
            RelatedProduct(title=p['name'],
                           url=urlparse.urljoin(baseurl, p['url']))
            for p in jsondata['products']
        ]
        cond_set_value(response.meta['product'], 'related_products',
                       {response.meta['relation']: products})

        return response.meta['product']

    def _scrape_total_matches(self, response):
        data = WaitroseProductsSpider._get_data(response)
        return data['totalCount']

    def _scrape_product_links(self, response):
        data = WaitroseProductsSpider._get_data(response)
        for product_data in data['products']:
            product = SiteProductItem()

            for product_key, data_key in self._PRODUCT_TO_DATA_KEYS.items():
                value = product_data.get(data_key, 'null')
                if value != 'null':
                    product[product_key] = product_data[data_key]

            image_url = product.get('image_url', 'None')
            if image_url:
                product['image_url'] = urlparse.urljoin('http://', image_url)

            # This one is not in the mapping since it requires transformation.
            #product['upc'] = int(product_data['productid'])

            if product.get('price', None):
                price = product['price']
                price = price.replace('&pound;', 'p')
                price = re.findall('(p? *[\d ,.]+ *p?) *', price)
                price = price[0] if price else ''
                if price.endswith('p'):
                    price = '0.' + price.strip()
                if 'p' in price:
                    price = re.sub('[p ,]', '', price)
                    product['price'] = Price(
                        priceCurrency='GBP',
                        price=price
                    )
                else:
                    self.log('Unknown price format at %s' % response)

            if not product.get('url', '').startswith('http'):
                product['url'] = urlparse.urljoin(
                    'http://www.waitrose.com', product['url'])

            yield product['url'], product

    def _scrape_next_results_page_link(self, response):
        data = WaitroseProductsSpider._get_data(response)
        if response.meta['current_page'] >= data['numberOfPages']:
            request = None
        else:
            meta = response.meta.copy()
            meta['current_page'] += 1
            request = self._create_request(meta)

        return request
