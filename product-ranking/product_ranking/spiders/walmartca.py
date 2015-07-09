# coding=utf-8

from __future__ import division, absolute_import, unicode_literals

import json
import pprint
import re
import urlparse
import hjson
import hashlib
import string
from datetime import datetime
import lxml.html
import urllib

from scrapy import Selector
from scrapy.http import Request, FormRequest
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.guess_brand import guess_brand_from_first_words
from product_ranking.items import (SiteProductItem, RelatedProduct,
                                   BuyerReviews, Price)
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set, cond_set_value, FLOATING_POINT_RGEX
from product_ranking.validation import BaseValidator
from spiders_shared_code.walmart_variants import WalmartVariants


is_empty = lambda x, y="": x[0] if x else y


def get_string_from_html(xp, link):
    loc = is_empty(link.xpath(xp).extract())
    return Selector(text=loc).xpath('string()').extract()


class WalmartCaValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = ['model', 'brand', 'description', 'recent_questions',
                       'related_products', 'upc', 'buyer_reviews', 'price']
    ignore_fields = ['google_source_site', 'is_in_store_only', 'bestseller_rank',
                     'is_out_of_stock']
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = False  # ... duplicated requests?
    ignore_log_filtered = False  # ... filtered requests?
    test_requests = {
        'abrakadabrasdafsdfsdf': 0,  # should return 'no products' or just 0 products
        'nothing_found_123': 0,
        'chrysler 300c': [10, 150],
        'swiming dress': [50, 250],
        'macbook air thunderbolt': [10, 150],
        'hexacore': [50, 250],
        '300c': [50, 250],
        'muay': [50, 200],
        '14-pack': [1, 100],
        'voltmeter': [50, 250]
    }


class WalmartCaProductsSpider(BaseValidator, BaseProductsSpider):
    """
    Implements a spider for walmart.ca/en/.
    """

    name = 'walmartca_products'
    allowed_domains = ["walmart.ca", "api.bazaarvoice.com"]

    default_hhl = [404, 500, 502, 520]

    SEARCH_URL = "http://www.walmart.ca/search/{search_term}/" \
                 "?sortBy={search_sort}&" \
                 "orderBy={search_order}"

    PRODUCT_INFO_URL = "http://api.bazaarvoice.com/data/batch.json?passkey=e6wzzmz844l2kk3v6v7igfl6i&" \
                      "apiversion=5.5&displaycode=2036-en_ca&resource.q0=products&" \
                      "filter.q0=id%3Aeq%3A{product_id}&" \
                      "stats.q0=questions%2Creviews&filteredstats.q0=questions%2Creviews&" \
                      "filter_questions.q0=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_answers.q0=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_reviews.q0=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "resource.q1=questions&" \
                      "filter.q1=productid%3Aeq%3A{product_id}&" \
                      "filter.q1=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "sort.q1=hasstaffanswers%3Adesc&stats.q1=questions&" \
                      "filteredstats.q1=questions&include.q1=authors%2Cproducts%2Canswers&" \
                      "filter_questions.q1=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_answers.q1=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "sort_answers.q1=submissiontime%3Aasc&limit.q1=10&offset.q1=0&" \
                      "limit_answers.q1=10&resource.q2=reviews&filter.q2=isratingsonly%3Aeq%3Afalse&" \
                      "filter.q2=productid%3Aeq%3A{product_id}&filter.q2=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "sort.q2=helpfulness%3Adesc%2Ctotalpositivefeedbackcount%3Adesc&" \
                      "stats.q2=reviews&filteredstats.q2=reviews&include.q2=authors%2Cproducts%2Ccomments&" \
                      "filter_reviews.q2=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_reviewcomments.q2=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_comments.q2=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&limit.q2=6&offset.q2=0&" \
                      "limit_comments.q2=3&resource.q3=reviews&filter.q3=productid%3Aeq%3A{product_id}&" \
                      "filter.q3=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&limit.q3=1&resource.q4=reviews&" \
                      "filter.q4=productid%3Aeq%3A{product_id}&filter.q4=isratingsonly%3Aeq%3Afalse&" \
                      "filter.q4=rating%3Agt%3A3&filter.q4=totalpositivefeedbackcount%3Agte%3A3&" \
                      "filter.q4=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&sort.q4=totalpositivefeedbackcount%3Adesc&" \
                      "stats.q4=reviews&filteredstats.q4=reviews&include.q4=authors%2Creviews&" \
                      "filter_reviews.q4=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_reviewcomments.q4=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "limit.q4=1&resource.q5=reviews&filter.q5=productid%3Aeq%3A{product_id}&" \
                      "filter.q5=isratingsonly%3Aeq%3Afalse&filter.q5=rating%3Alte%3A3&" \
                      "filter.q5=totalpositivefeedbackcount%3Agte%3A3&" \
                      "filter.q5=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "sort.q5=totalpositivefeedbackcount%3Adesc&stats.q5=reviews&" \
                      "filteredstats.q5=reviews&include.q5=authors%2Creviews&" \
                      "filter_reviews.q5=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&" \
                      "filter_reviewcomments.q5=contentlocale%3Aeq%3Aen_CA%2Cen_GB%2Cen_US&limit.q5=1"

    QA_LIMIT = 0xffffffff

    _SEARCH_SORT = {
        'best_match': 0,
        'price': 'price',
        'newest': 'newest',
        'rating': 'rating',
        'popular': 'popular'
    }

    _SEARCH_ORDER = {
        'default': 0,
        'asc': 'ASC',
        'desc': 'DESC'
    }

    settings = WalmartCaValidatorSettings

    sponsored_links = []

    _JS_DATA_RE = re.compile(
        r'define\(\s*"product/data\"\s*,\s*(\{.+?\})\s*\)\s*;', re.DOTALL)

    user_agent = 'default'

    def __init__(self, search_sort='best_match', zipcode='M3C',
                 search_order='default', *args, **kwargs):
        if zipcode:
            self.zipcode = zipcode
        # if search_sort == 'best_sellers':
        #     self.SEARCH_URL += '&soft_sort=false&cat_id=0'
        super(WalmartCaProductsSpider, self).__init__(
            site_name=self.allowed_domains[0],
            url_formatter=FormatterWithDefaults(
                search_sort=self._SEARCH_SORT[search_sort],
                search_order=self._SEARCH_ORDER[search_order]
            ),
            *args, **kwargs)

    def parse_product(self, response):

        reqs = []
        meta = response.meta.copy()

        if response.status in self.default_hhl:
            product = response.meta.get("product")
            product.update({"locale": 'en_CA'})
            return product

        if self._search_page_error(response):
            self.log("Got 404 when coming from %r." % response.request.url, ERROR)
            return

        product = response.meta['product']

        self._populate_from_js(response, product)
        self._populate_from_html(response, product)

        cond_set_value(product, 'locale', 'en')  # Default locale.

        id = re.findall('\/(\d+)', response.url)
        response.meta['product_id'] = id[-1] if id else None

        product_info_url = self.PRODUCT_INFO_URL.format(product_id=response.meta['product_id'])
        reqs.append(Request(
            url=product_info_url,
            meta=meta,
            callback=self._parse_product_info
        ))

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    """
    Helps to handle several requests
    """
    def send_next_request(self, reqs, response):
        req = reqs.pop()
        new_meta = response.meta.copy()

        if reqs:
            new_meta['reqs'] = reqs

        return req.replace(meta=new_meta)

    def _parse_product_info(self, response):
        meta = response.meta.copy
        product = response.meta.get('product')
        reqs = response.meta.get('reqs')

        data = json.loads(response.body_as_unicode())

        # Get base info
        try:
            main_info = data['BatchedResults']['q0']['Results'][0]

            # Set brand
            try:
                brand = main_info['Brand']['Name']
                cond_set_value(product, 'brand', brand)
            except (ValueError, KeyError):
                self.log("Impossible to get brand - %r" % response.url, WARNING)

            # No brand
            if not product.get("brand"):
                brand = product.get("title")
                cond_set(
                    product, 'brand', (guess_brand_from_first_words(brand.strip()),)
                )

        except (ValueError, KeyError):
            self.log("Impossible to get product info - %r" % response.url, WARNING)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _search_page_error(self, response):
        path = urlparse.urlsplit(response.url)[2]
        return path == '/FileNotFound.aspx'

    def _populate_from_html(self, response, product):

        reqs = response.meta.get('reqs')

        # Set product url
        cond_set_value(product, 'url', response.url)

        # Get description
        cond_set(
            product,
            'description',
            response.css('.productDescription .description').extract(),
            conv=''.join
        )

        # Get title
        title = is_empty(
            response.xpath("//div[@id='product-desc']/"
                           "h1[@data-analytics-type='productPage-productName']").extract(), "")
        if title:
            title = Selector(text=title).xpath('string()').extract()
            product["title"] = is_empty(title, "").strip()

        if not product.get('price'):
            currency = response.css('.pricing-shipping .price-current sup')
            price = response.css('.pricing-shipping .price-current')

            if price and currency:
                currency = currency.extract()[0]
                price = re.search('[,. 0-9]+', price.extract()[0])
                if price:
                    price = price.group()
                    price = price.replace(',', '').replace(' ', '')
                    cond_set_value(product, 'price',
                                   Price(priceCurrency=currency, price=price))

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _populate_from_js(self, response, product):
        reqs = response.meta.get('reqs')
        self._JS_PROD_INFO_RE = re.compile(r'productPurchaseCartridgeData\[\"\w+\"\]\s+=\s+([^;]*\})', re.DOTALL)
        self._JS_PROD_IMG_RE = re.compile(r'walmartData\.graphicsEnlargedURLS\s+=\s+([^;]*\])', re.DOTALL)

        # Extract base product info from JS
        data = is_empty(
            re.findall(self._JS_PROD_INFO_RE, response.body_as_unicode().encode('utf-8'))
        ).strip()
        if data:
            data = data.decode('utf-8').replace(' :', ':')
            try:
                product_data = hjson.loads(data, object_pairs_hook=dict)
            except ValueError:
                self.log("Impossible to get product data from JS %r." % response.url, WARNING)
                return
        else:
            self.log("No JS for product info matched in %r." % response.url, WARNING)
            return

        product_data['baseProdInfo'] = product_data['variantDataRaw'][0]

        # Set product UPC
        try:
            upc = is_empty(product_data['baseProdInfo']['upc_nbr'])
            cond_set_value(
                product, 'upc', upc, conv=unicode
            )
        except (ValueError, KeyError):
            self.log("Impossible to get UPC" % response.url, WARNING)  # Not really a UPC.

        # Set if special price
        try:
            special_price = product_data['baseProdInfo']['price_store_was_price']
            cond_set_value(product, 'special_pricing', True)
        except (ValueError, KeyError):
            cond_set_value(product, 'special_pricing', False)

        # Set product images urls
        image = re.findall(self._JS_PROD_IMG_RE, response.body_as_unicode())
        if image:
            try:
                image = image[1]
            except:
                image = image[0]

            try:
                image = image.decode('utf-8').replace(' :', ':').replace('//', 'http://')
                data_image = hjson.loads(image, object_pairs_hook=dict)
                image_urls = [value['enlargedURL'] for k, value in enumerate(data_image)]
                cond_set_value(product, 'image_url', image_urls, conv=list)
            except (ValueError, KeyError):
                self.log("Impossible to set image urls in %r." % response.url, WARNING)

        else:
            self.log("No JS for product image matched in %r." % response.url, WARNING)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _scrape_total_matches(self, response):

        matches = response.css('.results ::text').re("Your search for '.+' returned (.+) results.")

        if matches:
            num_results = matches[0].replace(',', '')
            try:
                num_results = int(num_results)
            except:
                return 0
        else:
            num_results = None
            self.log(
                "Failed to extract total matches from %r." % response.url, ERROR
            )

        return num_results

    def _scrape_results_per_page(self, response):
        num = response.css('#loadmore ::text').re(
            'Next (\d+) items')
        if num:
            return int(num[0])
        return None

    def _scrape_product_links(self, response):

        """
        Scraping product links from search page
        """

        items = response.xpath(
            '//article[@class="standard-thumb product"] | '
            '//article[contains(@class, "standard-thumb product")]'
        )

        if not items:
            self.log("Found no product links in %r." % response.url, INFO)

        for item in items:
            link = is_empty(item.css('.details .title a ::attr(href)').extract())

            title = is_empty(item.css('.details .title a ::text').extract())

            res_item = SiteProductItem()
            if title:
                res_item["title"] = title.strip()

            yield link, res_item

    def _scrape_next_results_page_link(self, response):
        next_page = None

        next_page_links = response.css("#loadmore ::attr(href)")
        if len(next_page_links) == 1:
            next_page = next_page_links.extract()[0]
        elif len(next_page_links) > 1:
            self.log(
                "Found more than one 'next page' link in %r." % response.url,
                ERROR
            )
        else:
            self.log(
                "Found no 'next page' link in %r (which could be OK)."
                % response.url,
                INFO
            )

        return next_page
