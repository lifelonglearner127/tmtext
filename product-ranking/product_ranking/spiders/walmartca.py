# coding=utf-8

from __future__ import division, absolute_import, unicode_literals

import json
import re
import urlparse, urllib
import hjson
from itertools import izip
from datetime import datetime

from scrapy import Selector
from scrapy.http import Request, FormRequest
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.guess_brand import guess_brand_from_first_words
from product_ranking.items import (SiteProductItem, RelatedProduct,
                                   BuyerReviews, Price)
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set, cond_set_value
from product_ranking.validation import BaseValidator
from product_ranking.walmartca_related_product import RR

is_empty = lambda x, y="": x[0] if x else y

def handle_date_from_json(date):
    """
    Handles date in format "2013-09-15T06:45:34.000+00:00"
    Returns date in format "15-09-2013"
    """

    dateconv = lambda date: datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f').date()

    if date and isinstance(date, basestring):
        timezone_id = date.index('+')
        date = date.replace(date[timezone_id:-1], '')
        conv_date = dateconv(date)
        return str(conv_date.strftime('%d-%m-%Y'))

    return ''

class WalmartCaProductsSpider(BaseValidator, BaseProductsSpider):
    """
    Implements a spider for walmart.ca/en/.
    """

    name = 'walmartca_products'
    allowed_domains = [
        "walmart.ca",
        "api.bazaarvoice.com",
        "om.ordergroove.com",
        "media.richrelevance.com",
        "recs.richrelevance.com"
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

    _JS_DATA_RE = re.compile(
        r'define\(\s*"product/data\"\s*,\s*(\{.+?\})\s*\)\s*;', re.DOTALL)

    user_agent = 'default'

    def __init__(self, search_sort='best_match', zip_code='M3C',
                 search_order='default', *args, **kwargs):
        if zip_code:
            self.zip_code = zip_code
        super(WalmartCaProductsSpider, self).__init__(
            site_name=self.allowed_domains[0],
            url_formatter=FormatterWithDefaults(
                search_sort=self._SEARCH_SORT[search_sort],
                search_order=self._SEARCH_ORDER[search_order]
            ),
            *args, **kwargs)

    def start_requests(self):
        """Generate Requests from the SEARCH_URL and the search terms."""
        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=urllib.quote_plus(st.encode('utf-8')),
                ),
                callback=self.set_cookie,
                meta={'search_term': st, 'remaining': self.quantity},
            )

        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            prod['url'] = self.product_url
            prod['search_term'] = ''
            yield Request(
                self.product_url,
                self._parse_single_product,
                meta={'product': prod},
                cookies={
                    'deliveryCatchment': 2000,
                    'marketCatchment': 2001,
                    'walmart.shippingPostalCode': 'V5M2G7',
                    'ENV': 'origin-edc-torbit-www',
                    'userSegment': '10-percent'
                })

        if self.products_url:
            urls = self.products_url.split('||||')
            for url in urls:
                prod = SiteProductItem()
                prod['url'] = url
                prod['search_term'] = ''
                yield Request(url,
                              self._parse_single_product,
                              meta={'product': prod})

    def set_cookie(self, response):
        """This function create same Request for setting right Cookie."""
        return Request(
                response.request.url,
                    callback = self.parse,
                    meta=response.meta,
                    dont_filter = True,
            )

    def parse_product(self, response):
        """
        Main parsing product method
        """

        reqs = []
        product = response.meta['product']

        #self._populate_from_html(response, product)
        #self._populate_from_js(response, product)

        # Product ID
        id = re.findall('\/(\d+)', response.url)
        product_id = id[-1] if id else None
        response.meta['product_id'] = product_id

        if response.status in self.default_hhl:
            product = response.meta.get("product")
            product.update({"locale": 'en_CA'})
            return product

        self._populate_from_js(response, product)

        # Send request to get if limited online status
        try:
            skus = [{"skuid": sku} for sku in response.meta['skus']]
            request_data = [{
                "productid": product_id,
                "skus": [skus]
            }]

            request_data = json.dumps(request_data).replace(' ', '')

            reqs.append(FormRequest(
                url="http://www.walmart.ca/ws/online/products",
                formdata={"products": request_data},
                callback=self._parse_online_status,
                headers={
                    'X-Requested-With': 'XMLHttpRequest'
                }
            ))
        except KeyError:
            pass
        if response.xpath('//span[@class="infoText"]/' \
                          'text()').re('This product is not available'):
            product['no_longer_available'] = True

        self._populate_from_html(response, product)

        cond_set_value(product, 'locale', 'en_CA')  # Default locale.

        # Get featured products from generated JS script, evaluating parent script
        RR_entity = RR(
            response.url,
            product_id,
            response
        )
        featured_products_url = RR_entity.js()

        reqs.append(Request(
            url=featured_products_url,
            callback=self._parse_related_products
        ))

        # Get product base info, QA and reviews straight from JS script
        product_info_url = self.PRODUCT_INFO_URL.format(product_id=product_id)
        reqs.append(Request(
            url=product_info_url,
            callback=self._parse_product_info
        ))

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_single_product(self, response):
        """
        For a single product_url mode
        """
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

            # Set buyer reviews info
            self._build_buyer_reviews(main_info['ReviewStatistics'], response)
        except (ValueError, KeyError, IndexError):
            product['buyer_reviews'] = ZERO_REVIEWS_VALUE
            self.log("Impossible to get product info - %r" % response.url, WARNING)

        # Get QA statistics
        try:
            qa_info = data['BatchedResults']['q1']

            if qa_info['Results']:
                # Set QA info
                self._build_qa_info(qa_info, response)

                # Get date of last question
                last_data_question = main_info['QAStatistics']['LastQuestionTime']

                if last_data_question:
                    last_data_question = handle_date_from_json(last_data_question)
                    product['date_of_last_question'] = last_data_question
            else:
                product['recent_questions'] = []

        except (ValueError, KeyError):
            self.log("Impossible to get QA info - %r" % response.url, WARNING)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _build_buyer_reviews(self, data, response):
        """
        Gets buyer reviews from JS script
        """

        buyer_reviews = {
            'num_of_reviews': 0,
            'average_rating': 0,
            'rating_by_star': {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0}
        }
        meta = response.meta.copy()
        product = meta['product']

        try:
            num_of_reviews = data['TotalReviewCount']  # Buyer reviews count

            if num_of_reviews:
                average_rating = round(data['AverageOverallRating'], 1)  # Average rating

                for rate in data['RatingDistribution']:  # Rating by stars
                    star = rate['RatingValue']
                    star_count = rate['Count']
                    buyer_reviews['rating_by_star'][str(star)] = star_count

                buyer_reviews['num_of_reviews'] = num_of_reviews
                buyer_reviews['average_rating'] = average_rating

                # Get date of last review
                last_data_buyer_review = data['LastSubmissionTime']
                last_data_buyer_review = handle_date_from_json(last_data_buyer_review)

                product['last_buyer_review_date'] = last_data_buyer_review

        except (KeyError, ValueError):
            pass

        product['buyer_reviews'] = BuyerReviews(**buyer_reviews)

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
                        answer['submissionTime'] = handle_date_from_json(
                            answ.get('SubmissionTime')
                        )
                        answer['lastModifiedTime'] = handle_date_from_json(
                            answ.get('LastModificationTime')
                        )
                        answers.append(answer)
                question_info['answers'] = answers

            question_info['totalAnswersCount'] = question.get('TotalAnswerCount')
            question_info['submissionDate'] = handle_date_from_json(
                question.get('SubmissionTime')
            )

            questions.append(question_info)

        product['recent_questions'] = questions

    def _parse_related_products(self, response):
        meta = response.meta.copy()
        product = meta['product']
        related_products = product.get('related_products', {})
        reqs = meta.get('reqs')
        body = response.body_as_unicode()

        data = re.findall(
            r'"(message)":\s*"(.*?)\^.*?"|"(name)":\s*"(.*?)"|"(linkurl)":\s*"(.*?)"',
            body
        )

        if data:
            feat_prod_list = []
            featured_prods = dict()
            url_ready = name_ready = False
            last_message = False
            forbidden_featured_names = ['also_viewed', 'top_sellers']

            for item in data:
                # Make a dir of two tuples
                item_list = filter(None, list(item))
                i = iter(item_list)
                values_dict = dict(izip(i, i))
                keys = values_dict.keys()

                if 'message' in keys:
                    if feat_prod_list:
                        if last_message not in forbidden_featured_names:
                            featured_prods[last_message] = feat_prod_list
                        feat_prod_list = []

                    last_message = values_dict['message'].lower()
                    last_message = '_'.join(
                        last_message.split(' ')[-2:]
                    )
                elif 'name' in keys:
                    title = values_dict['name']
                    name_ready = True
                elif 'linkurl' in keys:
                    url = values_dict['linkurl']
                    url_ready = True

                if url_ready and name_ready:
                    feat_prod_list.append(
                        RelatedProduct(**{'url': url, 'title': title})
                    )
                    url_ready = name_ready = False

            if last_message not in forbidden_featured_names:
                featured_prods[last_message] = feat_prod_list

            related_products.update(featured_prods)

            product['related_products'] = related_products

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _populate_from_html(self, response, product):
        """
        Gets data straight from html body
        """
        reqs = response.meta.get('reqs', [])

        # Set product url
        cond_set_value(product, 'url', response.url)
        try:
            if product['no_longer_available']:
                image = response.xpath('//img[@itemprop="image"]/@src')
                image = is_empty(image.extract())
                image = image.replace('//','http://').replace('Large','Enlarge')
                product['image_url'] = image

                brand = response.xpath('//span[@itemprop="brand"]/text()')
                brand = is_empty(brand.extract())
                product['brand'] = brand
        except KeyError:
            pass

        # Get title from html
        title = is_empty(
            response.xpath("//div[@id='product-desc']/"
                           "h1[@data-analytics-type='productPage-productName']").extract(), "")
        if title:
            title = Selector(text=title).xpath('string()').extract()
            product["title"] = is_empty(title, "").strip()

        # Get price
        price = response.xpath('//div[contains(@class, "microdata-price")]/'
                               '*[@itemprop="price"]/text() |'
                               '//div[contains(@class, "microdata-price")]/'
                               '*[@itemprop="lowPrice"]/text()')
        currency = response.xpath('//div[contains(@class, "microdata-price")]/'
                                '*[@itemprop="priceCurrency"]/@content')

        if price and currency:
            currency = is_empty(currency.extract())
            price = is_empty(price.extract())
            price = price.replace('$', '')
            product['price'] = Price(priceCurrency=currency, price=price)
        else:
            product['price'] = None

        # Get description
        desc = response.css(
            '.productDescription [itemprop="description"]'
        )
        if desc:
            description = desc.extract()
            product["description"] = is_empty(description, "").strip()

        # Get department and category
        category_list = response.xpath('//nav[@id="breadcrumb"]/./'
                                       '/a[@data-analytics-type="cat"]'
                                       '/span[@itemprop="title"]/text()').extract()

        if category_list:
            department = category_list[-1]
            product['department'] = department

            product['category'] = category_list

        # Get model
        model_sel = response.xpath(
            '//div[@id="specGroup"]/./'
            '/span[@itemprop="model"]/text()'
        ).extract()
        model = is_empty(
            model_sel, ''
        )

        # Get related products
        related_sel = response.xpath('//section[@aria-label="Featured Products: Related Products"]/./'
                                     '/article[contains(@class, "product")]')
        if related_sel:
            related_products = product.get('related_products', {})
            final_rel_prods = []
            for rel in related_sel:
                title = is_empty(
                    rel.xpath('.//div[@class="title"]/./'
                              '/a/text()').extract(),
                    ''
                )
                url = is_empty(
                    rel.xpath('.//div[@class="title"]/./'
                              '/a/@href').extract(),
                    ''
                )
                if title and url:
                    url_base = 'http://www.' + self.allowed_domains[0]
                    url = urlparse.urljoin(url_base, url)
                    final_rel_prods.append({
                        'title': title.strip(),
                        'url': url
                    })
            related_products['related'] = final_rel_prods

            product['related_products'] = related_products

        if model:
            product['model'] = model.strip()

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _populate_from_js(self, response, product):
        """
        Gets data out of JS script straight from html body
        """

        self._JS_PROD_IMG_RE = re.compile(r'walmartData\.graphicsEnlargedURLS\s+=\s+([^;]*\])', re.DOTALL)
        meta = response.meta.copy()
        reqs = meta.get('reqs', [])

        # Extract base product info from JS
        data = is_empty(
            re.findall(
                r'productPurchaseCartridgeData\["\d+"\]\s*=\s*(\{(.|\n)*?\});',
                response.body_as_unicode().encode('utf-8')
            )
        )

        if data:
            data = list(data)[0]
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

        # Set product sku
        try:
            sku_id = is_empty(product_data['baseProdInfo']['sku_id'])
            response.meta['sku_id'] = sku_id

        except (ValueError, KeyError):
            self.log("Impossible to get sku id - %r." % response.url, WARNING)

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
            online_status = product_data['baseProdInfo']['online_status'][0]

            if online_status != u'90':
                cond_set_value(product, 'special_pricing', True)
            else:
                cond_set_value(product, 'special_pricing', False)
        except (ValueError, KeyError):
            cond_set_value(product, 'special_pricing', False)

        # Set variants
        number_of_variants = product_data.get('numberOfVariants', 0)
        data_variants = product_data['variantDataRaw']
        skus = []
        if number_of_variants:
            try:
                variants = {}

                for var in data_variants:
                    variant = dict()
                    properties = dict()

                    sku_id = is_empty(
                        var.get('sku_id', ''),
                        ''
                    )
                    skus.append(sku_id)

                    price = var.get('price_store_price')
                    if price:
                        price = is_empty(price, None)
                        price = price.replace(',', '')
                        price = format(float(price), '.2f')
                    variant['price'] = price

                    color = is_empty(var.get('variantKey_en_Colour', []))
                    size = is_empty(var.get('variantKey_en_Size', []))
                    waist_size = is_empty(var.get('variantKey_en_Waist_size_-_inches'),[])
                    if size:
                        properties['size'] = size
                    if color:
                        properties['color'] = color
                    if waist_size:
                        properties['waist_size'] = waist_size
                    variant['properties'] = properties

                    variants[sku_id] = variant
            except (KeyError, ValueError):
                variants = []

        else:
            skus = [sku_id]
            variants = []

        product['variants'] = variants
        response.meta['skus'] = skus

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
                if image_urls and isinstance(image_urls, (tuple, list)):
                    image_urls = [image_urls[0]]
                cond_set(product, 'image_url', image_urls)
            except (ValueError, KeyError):
                self.log("Impossible to set image urls in %r." % response.url, WARNING)

        else:
            self.log("No JS for product image matched in %r." % response.url, WARNING)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_online_status(self, response):
        """
        Gets limited_stock and is_out_of_stock fields for product and its variants
        """
        meta = response.meta.copy()
        reqs = meta.get('reqs')
        product = meta['product']
        data = json.loads(
            response.body_as_unicode()
        )

        try:
            product_info = data['products'][0]
            variants_info = product_info['skus']
            variants = product['variants']
            final_variants = []
            list_out_of_stock = ['70', '80', '85', '87', '90']
            list_not_sold_online = ['85', '87', '90']

            # Set limited status for main product
            availability = product_info['availability']
            product['is_out_of_stock'] = availability in list_out_of_stock
            product['is_in_store_only'] = availability in list_not_sold_online

            if product_info['isLimitedStock']:
                product['limited_stock'] = True
            else:
                product['limited_stock'] = False

            #Taking right amount of price and availability status
            try:
                currency = re.findall('priceCurrency=(.*?),',str(product['price']))[0]
            except:
                currency = 'CAD'

            price = product_info['minCurrentPrice']
            if not price:
                prod_data = [{"productid":response.meta['product_id'],
                            "skus":[{"skuid":str(product['upc']),"storeeligible":True}]
                }]
                prod_data = json.dumps(prod_data).replace(' ', '')
                store_data = json.dumps(['1104','3057','1192','5777']).replace(' ', '')
                reqs.append(FormRequest(
                    url="http://www.walmart.ca/ws/store/products",
                    formdata={'stores':store_data, 'products':prod_data},
                    callback=self._parse_store_status,
                    headers={'X-Requested-With': 'XMLHttpRequest'}
                ))
            else:
                product['price'] = Price(priceCurrency=currency, price=price)

            # Set limited status for product variants
            if variants:
                for var in variants_info:
                    sku_id = var['skuId']

                    availability = var['availability']
                    variants[sku_id]['is_out_of_stock'] = availability in list_out_of_stock
                    variants[sku_id]['is_in_store_only'] = availability in list_not_sold_online

                    final_variants.append(variants[sku_id])

                product['variants'] = final_variants
        except (KeyError, ValueError):
            self.log(
                "Failed to extract limited stock info from %r." % response.url, WARNING
            )

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
        except ValueError:
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

    def _parse_store_status(self, response):
        """Checking availability in stores and adding store price to product"""
        reqs = response.meta['reqs']
        product = response.meta['product']
        try:
            currency = re.findall('priceCurrency=(.*?),',str(product['price']))[0]
        except:
            currency = 'CAD'
        data = json.loads(response.body_as_unicode())
        for store in data['products'][0]['results']:
            try:
                if store['availability'] != '70': #Not in store status
                    price = store['minCurrentPrice']
                else:
                    price = None
            except KeyError:
                price = None
                continue

            if price:
                product['price'] = Price(priceCurrency=currency, price=str(price))
                break

        if price:
            if product['is_out_of_stock']:
                    product['is_in_store_only'] = True
        else:
            product['is_in_store_only'] = False

        if reqs:
            return self.send_next_request(reqs, response)

        return product
