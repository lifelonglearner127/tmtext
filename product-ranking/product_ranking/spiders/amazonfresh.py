from __future__ import division, absolute_import, unicode_literals

import urllib
import urlparse
import re
import random
import copy

from scrapy.http import Request
from scrapy.conf import settings
from scrapy import FormRequest
from scrapy.log import ERROR
from scrapy.dupefilter import BaseDupeFilter
from scrapy.utils.request import request_fingerprint

from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FormatterWithDefaults, cond_set_value


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
    allowed_domains = ["fresh.amazon.com"]
    start_urls = []

    SEARCH_URL = "https://fresh.amazon.com/Search?" \
        "resultsPerPage=50&predictiveSearchFlag=true&recipeSearchFlag=false" \
        "&comNow=&input={search_term}&sort={search_sort}"

    WELCOME_URL = "https://fresh.amazon.com/welcome"

    ZIP_URL = "https://fresh.amazon.com/zipEntrySubmit"

    search_sort = {
        'relevance': 'relevance',  # default
        'bestselling': 'bestselling',
        'price_lh': 'price_low_to_high',
        'price_hl': 'price_high_to_low',
    }

    zip_codes_to_recrawl = {
        'Seattle': 98101,
        'San Francisco': 94107,
        'New York': 10128,
        'Santa Monica': 90404
    }

    def __init__(self, zip_code='94117', order='relevance', *args, **kwargs):
        settings.overrides['DUPEFILTER_CLASS'] = 'product_ranking.spiders.amazonfresh.CustomDupeFilter'
        search_sort = self.search_sort.get(order, 'relevance')
        self.zip_code = zip_code
        super(AmazonFreshProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(search_sort=search_sort),
            *args,
            **kwargs
        )

    def start_requests(self):
        yield Request(self.WELCOME_URL, callback=self.login_handler)

    def login_handler(self, response):
        data = {'refer': '',
                'zip': self.zip_code}
        return FormRequest(self.ZIP_URL, formdata=data, callback=self.after_login)

    def after_login(self, response):
        return super(AmazonFreshProductsSpider, self).start_requests()

    def _scrape_title(self, response):
        return response.xpath('//div[@class="buying"]/h1/text()').extract()

    def parse_product(self, response):
        prod = response.meta['product']

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
        cond_set(prod, 'locale', ['en-US'])
        prod['url'] = response.url
        out_of_stock_span = response.xpath(
            '//div[@class="itemUnavailableText"]/span'
        )
        if out_of_stock_span:
            prod['is_out_of_stock'] = True
        else:
            prod['is_out_of_stock'] = False
        rating_quantity = response.xpath(
            '//div[@class="ratingMinimal"]/node()[normalize-space()]'
        ).extract()
        rating_pict = response.xpath(
            '//div[@class="ratingMinimal"]/img/@src'
        ).extract()
        if rating_quantity and rating_pict:
            rating_pict = rating_pict[0]
            rating_quantity = rating_quantity[0]
            num_of_reviews = int(re.findall(r'(\d+)', rating_quantity)[0])
            if num_of_reviews != 0:
                avg = float(re.findall(r'search/(.*)-star', rating_pict)[0])
                br = BuyerReviews(num_of_reviews, avg, {})
                prod['buyer_reviews'] = br
        cond_set_value(prod, 'buyer_reviews', ZERO_REVIEWS_VALUE)

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
        if 'did not match any products.' in response.body_as_unicode():
            total_matches = 0
        else:
            count_matches = response.xpath(
                '//div[@class="numberOfResults"]/text()').re('(\d+)')
            if count_matches and count_matches[-1]:
                total_matches = int(count_matches[-1])
            else:
                total_matches = None
        return total_matches

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[@class="itemDetails"]/h4/a/@href').extract()
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        links = response.xpath(
            '//div[@class="pagination"]/a[contains(text(), "Next")]/@href'
        )
        if links:
            return links.extract()[0].strip()
        return None

    def _parse_single_product(self, response):
        return self.parse_product(response)
