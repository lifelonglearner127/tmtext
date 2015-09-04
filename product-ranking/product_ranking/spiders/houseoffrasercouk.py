# -*- coding: utf-8 -*-#

import json
import re
import urllib2
from itertools import izip

from scrapy.http import FormRequest, Request
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set_value

is_empty = lambda x, y=None: x[0] if x else y


class HouseoffraserProductSpider(BaseProductsSpider):

    name = 'houseoffraser_products'
    allowed_domains = [
        "houseoffraser.co.uk",
        "houseoffraser.ugc.bazaarvoice.com"
    ]

    SEARCH_URL = "http://www.houseoffraser.co.uk/on/demandware.store/" \
                 "Sites-hof-Site/default/Search-Show?q={search_term}" \
                 "&srule={sort_mode}"
    NEXT_PAGE_URL = "http://www.next.co.uk/search?w=jeans&isort=score" \
                    "&srt={start_pos}"
    BUYER_REVIEWS_URL = "http://houseoffraser.ugc.bazaarvoice.com/" \
                        "6017-en_gb/{product_id}/reviews.djs?format=embeddedhtml"

    ZERO_REVIEWS_VALUE = {
        'num_of_reviews': 0,
        'average_rating': 0.0,
        'rating_by_star': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
    }

    _SORT_MODES = {
        "NAME_ASC": "product-name-asc",
        "NAME_DESC": "product-name-desc",
        "PRICE_ASC": "price-asc",
        "PRICE_DESC": "price-desc",
        "BRAND_ASC": "brand-asc",
        "BRAND_DESC": "brand-desc",
        "NEWEST": "Newness",
        "RATING": "bv-ratings",
    }

    def __init__(self, search_sort='NEWEST', *args, **kwargs):
        super(HouseoffraserProductSpider, self).__init__(
            site_name=self.allowed_domains[0],
            url_formatter=FormatterWithDefaults(
                sort_mode=self._SORT_MODES[search_sort]
            ),
            *args, **kwargs)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        # Get real product ID
        product_id = is_empty(response.xpath(
            '//input[@name="masterproduct_pid"]/@value'
        ).extract())
        response.meta['product_id'] = product_id

        # Get base product info from HTML body
        base_product_info = self._get_base_product_info(response)

        # Set price from base product info
        price = self._parse_price(base_product_info)
        cond_set_value(product, 'price', price)

        # Set special pricing from base product info
        special_pricing = self._parse_special_pricing(base_product_info)
        cond_set_value(product, 'special_pricing', special_pricing)

        # Set brand from base product info
        brand = self._parse_brand(base_product_info)
        cond_set_value(product, 'brand', brand)

        # Set categories from base product info
        category = self._parse_category(base_product_info)
        cond_set_value(product, 'category', category)

        # Set department
        if category:
            department = category[-1]
            cond_set_value(product, 'department', department)

        # Set title from base product info
        title = self._parse_title(base_product_info)
        cond_set_value(product, 'title', title)

        # Parse description
        description = self._parse_description(response)
        cond_set_value(product, 'description', description)

        # Parse image url
        image_url = self._parse_image_url(response)
        cond_set_value(product, 'image_url', image_url)

        # Parse product variants
        variants = self._parse_variants(response)
        cond_set_value(product, 'variants', variants)

        # Parse buyer reviews
        reqs.append(
            Request(
                url=self.BUYER_REVIEWS_URL.format(product_id=product_id),
                dont_filter=True,
                callback=self._parse_buyer_reviews
            )
        )

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _get_base_product_info(self, response):
        data = is_empty(re.findall(
            r'var\s+_DCSVariables\s+=\s+(.[^;]+)',
            response.body_as_unicode()
        ))

        if data:
            try:
                base_product_info = json.loads(data)
            except Exception as exc:
                self.log(
                    "Failed to extract base product info from {url}: {exc}".format(
                        url=response.url, exc=exc
                    ), WARNING
                )
                return None
        else:
            self.log(
                "Failed to extract base product info from {url}".format(response.url),
                WARNING
            )
            return None

        return base_product_info

    def _parse_price(self, data):
        price = data.get('currentPrice')

        if price:
            price = Price(priceCurrency="GBP", price=price)

        return price

    def _parse_special_pricing(self, data):
        special_pricing = data.get('previousPrice')

        if special_pricing:
            return True
        else:
            return False

    def _parse_brand(self, data):
        brand = data.get('productBrand')

        if brand:
            brand = urllib2.unquote(brand)

        return brand

    def _parse_title(self, data):
        brand = data.get('productBrand')
        name = data.get('productName')

        if brand:
            brand = urllib2.unquote(brand)
        else:
            brand = ''

        if name:
            name = urllib2.unquote(name)
        else:
            name = ''

        title = brand + ' ' + name

        return title

    def _parse_category(self, data):
        category = []

        for key, value in data.iteritems():
            if 'productCat' in key and value:
                category.append(value)

        if category:
            return category

        return None

    def _parse_description(self, response):
        description = is_empty(
            response.xpath('//div[@class="hof-description"]').extract()
        )

        return description

    def _parse_image_url(self, response):
        image_url = is_empty(
            response.xpath('//li[@class="coach"]/img/@src').extract()
        )

        return image_url

    def _parse_variants(self, response):
        """
        Parses variants using RegExp from HTML body
        """
        variants_data = is_empty(
            re.findall(r'var\s+variations\s+=\s+\((.+)\).variations;', response.body_as_unicode())
        )

        if variants_data:
            variants = []
            try:
                data = json.loads(variants_data)
                for variation in data['variations'].itervalues():
                    for size, value in variation['sizes'].iteritems():
                        single_variant = {}
                        properties = {}

                        properties['color'] = variation['colourname']
                        properties['size'] = size
                        single_variant['properties'] = properties

                        stock = value.values()[0]
                        if stock == 'true':
                            single_variant['out_of_stock'] = False
                        else:
                            single_variant['out_of_stock'] = True

                        size_id = value.keys()[0]  # Size variant id
                        single_variant['price'] = format(
                            float(variation['priceValues'][size_id]),
                            '.2f'
                        )

                        variants.append(single_variant)

                return variants
            except Exception as exc:
                self.log(
                    "Failed to extract variants from {url}: {exc}".format(
                        url=response.url, exc=exc), WARNING
                )
                return []
        else:
            self.log(
                "Failed to extract variants from {url}".format(response.url),
                WARNING
            )
            return []

    def _parse_buyer_reviews(self, response):
        """
        Parses buyer reviews
        """
        meta = response.meta.copy()
        product = meta['product']
        reqs = meta.get('reqs', [])

        body_data = response.body_as_unicode()

        # Get dictionary for BR analytics data from response body
        base_reviews_data = is_empty(
            re.findall(
                r'webAnalyticsConfig:({.+})',
                body_data
            )
        )
        if base_reviews_data:
            try:
                base_reviews_data = json.loads(base_reviews_data)
                base_reviews_data = base_reviews_data['jsonData']
                num_of_reviews = int(
                    base_reviews_data['attributes']['numReviews']
                )

                if num_of_reviews:
                    average_rating = base_reviews_data['attributes']['avgRating']
                    rating_by_star = self._get_rating_by_star(response)

                    buyer_reviews = {
                        'num_of_reviews': num_of_reviews,
                        'average_rating': average_rating,
                        'rating_by_star': rating_by_star
                    }
                else:
                    buyer_reviews = self.ZERO_REVIEWS_VALUE

            except (KeyError, IndexError) as exc:
                self.log(
                    'Unable to parse buyer reviews on {url}: {exc}'.format(
                        url=product['url'],
                        exc=exc
                    ), ERROR
                )
                buyer_reviews = self.ZERO_REVIEWS_VALUE
        else:
            buyer_reviews = self.ZERO_REVIEWS_VALUE

        product['buyer_reviews'] = BuyerReviews(**buyer_reviews)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _get_rating_by_star(self, response):
        meta = response.meta.copy()
        product = meta['product']

        data = is_empty(
            re.findall(
                r'materials=({.+})',
                response.body_as_unicode()
            )
        )
        if data:
            try:
                data = json.loads(data)
                histogram_data = data['BVRRSourceID'].replace('\\ ', '')\
                    .replace('\\', '').replace('\\"', '')

                stars = re.findall(
                    r'<span class="BVRRHistStarLabelText">(\d+) stars?<\/span>|'
                    r'<span class="BVRRHistAbsLabel">(\d+)<\/span>',
                    histogram_data
                )

                # ('5', '') --> '5'
                item_list = []
                for star in stars:
                    item_list.append(filter(None, list(star))[0])

                # ['3', '0', '5', '6'] --> {'3': '0', '5': '6'}
                i = iter(item_list)
                stars = {k: int(v) for (k, v) in izip(i, i)}
                return stars
            except (KeyError, IndexError) as exc:
                self.log(
                    'Unable to parse buyer reviews on {url}: {exc}'.format(
                        url=product['url'],
                        exc=exc
                    ), ERROR
                )
                return self.ZERO_REVIEWS_VALUE['rating_by_star']
        else:
            return self.ZERO_REVIEWS_VALUE['rating_by_star']

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

        num = is_empty(
            response.xpath('//p[@class="paging-items-summary"]/text()').extract(),
            '0'
        )

        if not num:
            self.log(
                "Failed to extract total matches from {url}".format(response.url),
                ERROR
            )
        else:
            num = is_empty(re.findall(r'of\s+(\d+)', num), '0')

        return int(num)

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """

        num = is_empty(
            response.xpath('//*[@class="paging-links"]/span/text()').extract(),
            '0'
        )

        if not num:
            self.log(
                "Failed to extract results per page from {url}".format(response.url), ERROR
            )

        self.items_per_page = int(num)

        return num

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """

        items = response.xpath('//*[@class="product-list-element"]')

        if items:
            for item in items:
                link = is_empty(
                    item.xpath('.//div[@class="product-description"]/./'
                               '/a/@href').extract()
                )
                res_item = SiteProductItem()
                yield link, res_item
        else:
            self.log("Found no product links in {url}".format(response.url), WARNING)

    def _scrape_next_results_page_link(self, response):
        next_page_url = response.xpath('//a[contains(@class, "nextPage")]/@href').extract()

        if len(next_page_url) == 1:
            next_page_url = next_page_url[0]
        elif len(next_page_url) > 1:
            self.log("Found more than one 'next page' link.", ERROR)

        return next_page_url