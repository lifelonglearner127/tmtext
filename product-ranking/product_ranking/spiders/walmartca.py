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
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

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
    allowed_domains = [
        "walmart.ca",
        "api.bazaarvoice.com",
        "om.ordergroove.com"
    ]

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

    IN_STOCK_URL = "https://om.ordergroove.com/offer/af0a84f8847311e3b233bc764e1107f2/pdp?" \
                   "session_id=af0a84f8847311e3b233bc764e1107f2.262633.1436277025&" \
                   "page_type=1&p=%5B%22{product_id}%22%5D&module_view=%5B%22regular%22%5D"

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
        super(WalmartCaProductsSpider, self).__init__(
            site_name=self.allowed_domains[0],
            url_formatter=FormatterWithDefaults(
                search_sort=self._SEARCH_SORT[search_sort],
                search_order=self._SEARCH_ORDER[search_order]
            ),
            *args, **kwargs)

    def parse_product(self, response):
        """
        Main parsing product method
        """

        reqs = []
        meta = response.meta.copy()
        product = response.meta['product']

        id = re.findall('\/(\d+)', response.url)
        product_id = id[-1] if id else None
        response.meta['product_id'] = product_id

        if response.status in self.default_hhl:
            product = response.meta.get("product")
            product.update({"locale": 'en_CA'})
            return product

        self._populate_from_js(response, product)
        self._populate_from_html(response, product)

        cond_set_value(product, 'locale', 'en_CA')  # Default locale.

        # Get product base info, QA and reviews straight from JS script
        product_info_url = self.PRODUCT_INFO_URL.format(product_id=response.meta['product_id'])
        reqs.append(Request(
            url=product_info_url,
            meta=meta,
            callback=self._parse_product_info
        ))

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """

        req = reqs.pop()
        new_meta = response.meta.copy()

        if reqs:
            new_meta['reqs'] = reqs

        return req.replace(meta=new_meta)

    def _parse_product_info(self, response):
        """
        Handles JS script with base product info, buyer reviews and QA statistics
        """
        meta = response.meta.copy()
        product = meta.get('product')
        reqs = meta.get('reqs')

        data = json.loads(response.body_as_unicode())

        # Get base info
        try:
            main_info = data['BatchedResults']['q0']['Results'][0]

            # Set description
            # try:
            #     description = main_info['Description']
            #     cond_set_value(product, 'description', description)
            # except (ValueError, KeyError):
            #     cond_set_value(product, 'description', None)
            #     self.log("Impossible to get description - %r" % response.url, WARNING)

            # Set buyer reviews info
            self._build_buyer_reviews(main_info['ReviewStatistics'], response)

        except:
            product['buyer_reviews'] = ZERO_REVIEWS_VALUE
            self.log("Impossible to get product info - %r" % response.url, WARNING)

        # Get QA statistics
        try:
            qa_info = data['BatchedResults']['q1']

            # Set QA info
            self._build_qa_info(qa_info, response)

        except (ValueError, KeyError):
            self.log("Impossible to get QA info - %r" % response.url, WARNING)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _build_buyer_reviews(self, data, response):
        """
        Gets buyer reviews from JS script
        """

        buyer_reviews = ZERO_REVIEWS_VALUE
        meta = response.meta.copy()
        product = meta['product']

        try:
            num_of_reviews = data['TotalReviewCount']  # Buyer reviews count

            if num_of_reviews:
                average_rating = data['AverageOverallRating']  # Average rating

                for rate in data['RatingDistribution']:  # Rating by stars
                    star = rate['RatingValue']
                    star_count = rate['Count']
                    buyer_reviews[2][str(star)] = star_count

                buyer_reviews[0] = num_of_reviews
                buyer_reviews[1] = average_rating

                # Get date of last review
                last_data_buyer_review = data['LastSubmissionTime']
                last_data_buyer_review = self._handle_date_from_json(last_data_buyer_review)

                product['last_buyer_review_date'] = last_data_buyer_review

        except (KeyError, ValueError):
            pass

        product['buyer_reviews'] = buyer_reviews

    def _build_qa_info(self, data, response):
        """
        Gets QA info from JS script
        """

        meta = response.meta.copy()
        product = meta.get('product')
        question_data = data.get('Results')
        answer_data = data.get('Includes')
        if answer_data:
            answer_data = answer_data.get('Answers')
        questions = []

        # TODO: handle exceptions
        for question in question_data:
            question_info = dict()

            question_info['questionId'] = question.get('Id')
            question_info['userNickname'] = question.get('UserNickname')
            question_info['questionSummary'] = question.get('QuestionSummary')

            # Get answers by answer_ids
            answer_ids = question.get('AnswerIds')
            if answer_ids:
                answers = []
                for answer_id in answer_ids:
                    answ = answer_data.get(answer_id)
                    if answ:
                        answer = dict()
                        answer['answerText'] = answ.get('AnswerText')
                        answer['negativeVoteCount'] = answ.get('TotalNegativeFeedbackCount')
                        answer['positiveVoteCount'] = answ.get('TotalPositiveFeedbackCount')
                        answer['answerId'] = answ.get('Id')
                        answer['userNickname'] = answ.get('UserNickname')
                        answer['submissionTime'] = self._handle_date_from_json(
                            answ.get('SubmissionTime')
                        )
                        answer['lastModifiedTime'] = self._handle_date_from_json(
                            answ.get('LastModificationTime')
                        )
                        answers.append(answer)
                question_info['answers'] = answers

            question_info['totalAnswersCount'] = question.get('TotalAnswerCount')
            question_info['submissionDate'] = self._handle_date_from_json(
                question.get('SubmissionTime')
            )

            questions.append(question_info)

        product['recent_questions'] = questions

    def _handle_date_from_json(self, date):
        """
        Handles date in format "2013-09-12T06:45:34.000+00:00"
        Returns date in format "2013-09-12"
        """

        dateconv = lambda date: datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f').date()

        if date and isinstance(date, basestring):
            timezone_id = date.index('+')
            date = date.replace(date[timezone_id:-1], '')
            conv_date = dateconv(date)
            return str(conv_date)

        return ''

    def _populate_from_html(self, response, product):
        """
        Gets data straight from html body
        """

        reqs = response.meta.get('reqs', [])

        # Set product url
        cond_set_value(product, 'url', response.url)

        # Get title from html
        title = is_empty(
            response.xpath("//div[@id='product-desc']/"
                           "h1[@data-analytics-type='productPage-productName']").extract(), "")
        if title:
            title = Selector(text=title).xpath('string()').extract()
            product["title"] = is_empty(title, "").strip()

        # Get price
        price = response.css('.pricing-shipping .microdata-price [itemprop="price"]::text')
        currency = response.css('.pricing-shipping .microdata-price [itemprop="priceCurrency"]::attr(content)')

        if price and currency:
            currency = is_empty(currency.extract())
            price = is_empty(price.extract())
            price = price.replace('$', '')
            cond_set_value(product, 'price',
                           Price(priceCurrency=currency, price=price))
        else:
            product['price'] = None

        # Get description
        desc = response.css(
            '.productDescription [itemprop="description"]'
        )
        if desc:
            description = desc.extract()
            product["description"] = is_empty(description, "").strip()

        # Get related products
        related_prod_sections = response.css(".spotlightType-products"
                                             "[aria-label='Featured Products: Featured Products']")

        if related_prod_sections:
            related_prod_sections = related_prod_sections.extract()
            related_prod_title = ['ultimately_bought', 'also_bought', 'top_sellers']
            related_products = dict()

            for k, value in enumerate(related_prod_sections):
                print('-'*50)
                print value
                print('-'*50)
                sel = Selector(text=value)
                builded_products = self._build_related_products(sel)
                if builded_products:
                    related_products[related_prod_title[k]] = builded_products

            product['related_products'] = related_products
        else:
            product['related_products'] = None

        # Get department
        department_list = response.css('#breadcrumb li[itemscope] span[itemprop="title"]::text')

        if department_list:
            department = department_list[-1].extract()
            product['department'] = department

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _build_related_products(self, selector):
        related_products = []

        rel_prod = selector.css('.product')
        if rel_prod:
            rel_prod = rel_prod.extract()

            print('-'*50)
            print len(rel_prod)
            print('-'*50)

            # TODO: rewrite selectors
            for product in rel_prod:
                selector = Selector(text=product)

                title = is_empty(
                    selector.css('.title a::text').extract()
                )
                title = title.strip()

                url = is_empty(
                    selector.css('.title a::attr(href)').extract()
                )
                url = url.strip()

                if title and url:
                    related_products.append([title, url])

            return related_products

        return None

    def _populate_from_js(self, response, product):
        """
        Gets data out of JS script straight from html body
        """

        self._JS_PROD_INFO_RE = re.compile(r'productPurchaseCartridgeData\[\"\w+\"\]\s+=\s+([^;]*\})', re.DOTALL)
        self._JS_PROD_IMG_RE = re.compile(r'walmartData\.graphicsEnlargedURLS\s+=\s+([^;]*\])', re.DOTALL)
        meta = response.meta.copy()
        reqs = meta.get('reqs', [])

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

        # Set brand
        try:
            brand = is_empty(product_data['baseProdInfo']['brand_name_en'])
            cond_set_value(product, 'brand', brand)
        except (ValueError, KeyError):
            self.log("Impossible to get brand - %r" % response.url, WARNING)

        # No brand - trying to get it from product title
        if not product.get("brand"):
            brand = product.get("title")
            cond_set(
                product, 'brand', (guess_brand_from_first_words(brand.strip()),)
            )

        # Set if special price
        try:
            special_price = product_data['baseProdInfo']['price_store_was_price']
            cond_set_value(product, 'special_pricing', True)
        except (ValueError, KeyError):
            cond_set_value(product, 'special_pricing', False)

        # Set variants
        number_of_variants = product_data.get('numberOfVariants', 0)
        if number_of_variants:
            # try:
            data_variants = product_data['variantDataRaw']
            variants = []

            for var in data_variants:
                variant = dict()
                properties = dict()

                price = var.get('price_store_price')
                if price:
                    price = is_empty(price, None)
                    price = price.replace(',', '')
                    price = format(float(price), '.2f')
                variant['price'] = price

                properties['color'] = is_empty(var.get('variantKey_en_Colour', []))
                properties['size'] = is_empty(var.get('variantKey_en_Size', []))
                variant['properties'] = properties
                # variant['in_stock'] = self._parse_stock_shipping_info()

                variants.append(variant)

            # except (KeyError, ValueError):
            #     variants = None

        else:
            variants = None
        product['variants'] = variants

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
        """
        Scraping number of resulted product links
        """

        num_results = is_empty(
            response.css('#shelf-page .total-num-recs::text').extract(), '0'
        )

        try:
            num_results = int(num_results)
        except:
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

