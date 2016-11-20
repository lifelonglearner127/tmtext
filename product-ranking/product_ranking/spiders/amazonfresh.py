from __future__ import division, absolute_import, unicode_literals

import re
<<<<<<< HEAD
import random
import copy
=======
import json

import string
>>>>>>> 551a62fc9763bdbee1d93e6722ae51e55389d61b

from scrapy.http import Request
from scrapy.conf import settings
from scrapy import FormRequest
from scrapy.log import ERROR
from scrapy.dupefilter import BaseDupeFilter
from scrapy.utils.request import request_fingerprint

from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set


is_empty = lambda x, y=None: x[0] if x else y


class CustomDupeFilter(BaseDupeFilter):
    """ Custom dupefilter - counts attempts """

    urls = {}

    def __init__(self, max_attempts=50, *args, **kwargs):
        self.max_attempts = max_attempts
        super(CustomDupeFilter, self).__init__(*args, **kwargs)

    def request_seen(self, request):
        if not request.url in self.urls:
            self.urls[request.url] = 0
        self.urls[request.url] += 1
        if self.urls[request.url] > self.max_attempts:
            self.log('Too many dupe attempts for url %s' % request.url, ERROR)
            return True


class AmazonFreshProductsSpider(BaseProductsSpider):
    """Spider for fresh.amazon.com site.

    Allowed search sort:
    'relevance'
    'bestselling'
    'price_lh'
    'price_hl'

    to run:
    scrapy crawl -a searchterms_str=banana [-a zip_code=12345]
    [-a order=relevance]

    related_products, upc, is_in_stock_only fields don't populated
    Note: if item marked as 'out_of_stock' price can not be parsed.
    """
    name = "amazonfresh_products"
    allowed_domains = ["www.amazon.com"]
    start_urls = []

    SEARCH_URL = "https://www.amazon.com/s/ref=nb_sb_noss_2?" \
                 "url=search-alias%3Damazonfresh&field-keywords={search_term}"

    WELCOME_URL = "https://www.amazon.com/b?node=10329849011"

    CSRF_TOKEN_URL = "https://www.amazon.com/afx/nc/zipcodemodal"

    ZIP_URL = "https://www.amazon.com/afx/regionlocationselector/ajax/" \
              "updateZipcode"

<<<<<<< HEAD
    zip_codes_to_recrawl = {
        'Seattle': 98101,
        'San Francisco': 94107,
        'New York': 10128,
        'Santa Monica': 90404
    }

    def __init__(self, zip_code='94117', order='relevance', *args, **kwargs):
        settings.overrides['DUPEFILTER_CLASS'] = 'product_ranking.spiders.amazonfresh.CustomDupeFilter'
        search_sort = self.search_sort.get(order, 'relevance')
=======
    def __init__(self, zip_code='94117', *args, **kwargs):
>>>>>>> 551a62fc9763bdbee1d93e6722ae51e55389d61b
        self.zip_code = zip_code
        super(AmazonFreshProductsSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        yield Request(
            self.WELCOME_URL,
            callback=self.pre_login_handler
        )

    def pre_login_handler(self, response):
        return FormRequest(
            self.CSRF_TOKEN_URL,
            method="GET",
            callback=self.login_handler,
            dont_filter=True,
        )

    def login_handler(self, response):
<<<<<<< HEAD
        data = {'refer': '',
                'zip': self.zip_code}
        return FormRequest(self.ZIP_URL, formdata=data, callback=self.after_login)
=======
        csrf_token = re.findall(r'csrfToken\":\"([^\"]+)', response.body)
        if not csrf_token:
            self.log('Can\'t find csrf token.', ERROR)
            return None
        return FormRequest(
            self.ZIP_URL,
            formdata={
                'token': csrf_token[0],
                'zipcode': self.zip_code
            },
            callback=self.after_login,
            dont_filter=True
        )
>>>>>>> 551a62fc9763bdbee1d93e6722ae51e55389d61b

    def after_login(self, response):
        return super(AmazonFreshProductsSpider, self).start_requests()

    def _scrape_title(self, response):
        return response.xpath('//div[@class="buying"]/h1/text()').extract()

    def parse_product(self, response):
        prod = response.meta['product']
<<<<<<< HEAD

        # check if we have a previously scraped product, and we got a 'normal' title this time
        _title = self._scrape_title(response)
        if _title and isinstance(_title, (list, tuple)):
            _title = _title[0]
            if 'Not Available in Your Area' not in _title:
                if getattr(self, 'original_na_product', None):
                    prod = self.original_na_product
                    prod['title'] = _title
                    return prod

        query_string = urlparse.parse_qs(urlparse.urlsplit(response.url).query)
        cond_set(prod, 'model', query_string.get('asin', ''))

        brand = response.xpath('//div[@class="byline"]/a/text()').extract()
        cond_set(prod, 'brand', brand)
        price = response.xpath(
            '//div[@class="price"]/span[@class="value"]/text()').extract()
        cond_set(prod, 'price', price)
        if prod.get('price', None):
            if '$' not in prod['price']:
                self.log('Unknown currency at %s' % response.url, level=ERROR)
            else:
                prod['price'] = Price(
                    price=prod['price'].replace('$', '').replace(
                        ',', '').replace(' ', '').strip(),
                    priceCurrency='USD'
                )

        seller_all = response.xpath('//div[@class="messaging"]/p/strong/a')

        if seller_all:
            seller = seller_all.xpath('text()').extract()
            other_products = seller_all.xpath('@href').extract()
            if other_products:
                other_products = "https://fresh.amazon.com/" + other_products[0]
            else:
                other_products = []
            if seller:
                prod["marketplace"] = [{
                    "name": seller[0], 
                    "price": prod["price"],
                }]

        des = response.xpath('//div[@id="productDescription"]').extract()
        cond_set(prod, 'description', des)
        img_url = response.xpath(
            '//div[@id="mainImgWrapper"]/img/@src').extract()
        cond_set(prod, 'image_url', img_url)
=======
        cond_set(prod, 'url', [response.url])
>>>>>>> 551a62fc9763bdbee1d93e6722ae51e55389d61b
        cond_set(prod, 'locale', ['en-US'])
        cond_set(
            prod,
            'title',
            response.xpath('//h1[@id="title"]/span/text()').extract(),
            string.strip
        )
        cond_set(
            prod,
            'brand',
            response.xpath('//span[@id="brand"]/text()').extract()
        )
        cond_set(
            prod,
            'price',
            response.xpath(
                '//span[@id="priceblock_ourprice"]/text()').extract(),
            self.__convert_to_price
        )
        cond_set(
            prod,
            'description',
            response.xpath(
                '//div[@id="productDescription"]/p/text()').extract(),
            string.strip
        )
        cond_set(
            prod,
            'image_url',
            response.xpath(
                '//div[@id="imgTagWrapperId"]/img/@data-a-dynamic-image'
            ).extract(),
            self.__parse_image_url
        )
        rating = response.xpath('//span[@class="crAvgStars"]')
        cond_set(
            prod,
            'model',
            rating.xpath(
                '/span[contains(@class, "asinReviewsSummary")]/@name'
            ).extract()
        )
        reviews = self.__parse_rating(rating)
        if not reviews:
            cond_set(
                prod,
                'buyer_reviews',
                ZERO_REVIEWS_VALUE
            )
        else:
            prod['buyer_reviews'] = reviews
        prod['is_out_of_stock'] = bool(response.xpath(
            '//div[@class="itemUnavailableText"]/span').extract())

        title = self._scrape_title(response)
        cond_set(prod, 'title', title)
        if 'Not Available in Your Area' in prod.get('title', ''):
            new_zip_code = str(random.choice(self.zip_codes_to_recrawl.values()))
            self.log('Product not available for ZIP %s - retrying with %s' % (
                self.zip_code, new_zip_code))
            self.zip_code = new_zip_code
            if not getattr(self, 'original_na_product', None):
                self.original_na_product = copy.deepcopy(prod)
            return Request(self.WELCOME_URL, callback=self.login_handler)

        return prod

    def __convert_to_price(self, x):
        price = re.findall(r'(\d+\.?\d*)', x)
        if not price:
            self.log('Error while parse price.', ERROR)
            return None
        return Price(
            priceCurrency='USD',
            price=float(price[0])
        )

    def __parse_image_url(self, x):
        try:
            images = json.loads(x)
            return images.keys()[0]
        except Exception as e:
            self.log('Error while parse image url. ERROR: %s.' % str(e), ERROR)
            return None

    def __parse_rating(self, rating):
        try:
            total_reviews = int(rating.xpath(
                '//span[@class="crAvgStars"]/a/text()'
            ).extract()[0].split()[0].replace(',', ''))
            average_rating = float(rating.xpath(
                'span//span/span[contains(text(), "stars")]/text()'
            ).extract()[0].split()[0])
            return BuyerReviews(
                num_of_reviews=total_reviews,
                average_rating=average_rating,
                rating_by_star={}
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.log('Error while parse rating. ERROR: %s.' % str(e), ERROR)
            return None

    def _search_page_error(self, response):
        try:
            found1 = response.xpath(
                '//div[@class="warning"]/p/text()').extract()[0]
            found2 = response.xpath(
                '//div[@class="warning"]/p/strong/text()').extract()[0]
            found = found1 + " " + found2
            if 'did not match any products' in found:
                self.log(found, ERROR)
                return True
            return False
        except IndexError:
            return False

    def _scrape_total_matches(self, response):
        count_text = is_empty(response.xpath(
            '//h2[@id="s-result-count"]/text()'
        ).extract())
        if not count_text:
            return 0
        count = re.findall(r'of\s([\d,]+)', count_text)
        if not count:
            return 0
        return int(count[0].replace(',', ''))

    def _scrape_product_links(self, response):
        ul = response.xpath('//li[contains(@class, "s-result-item")]')
        if not ul:
            return
        for li in ul:
            link = is_empty(li.xpath(
                './/a[contains(@class, "s-access-detail-page")]/@href'
            ).extract())
            if not link:
                continue
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        link = is_empty(response.xpath(
            '//a[@id="pagnNextLink"]/@href'
        ).extract())
        if not link:
            return None
        return "https://www.amazon.com" + link \
            if link.startswith('/') else link

    def _parse_single_product(self, response):
        return self.parse_product(response)
