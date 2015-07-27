# -*- coding: utf-8 -*-#
from urlparse import urljoin
import json
import re

from scrapy import Selector
from scrapy.http import FormRequest, Request
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults
from product_ranking.guess_brand import guess_brand_from_first_words

is_empty = lambda x, y=None: x[0] if x else y

def string_insert_char(string, index, char):
    return string[:index] + str(char) + string[index:]

class NextCoUkProductSpider(BaseProductsSpider):

    name = 'nextcouk_products'
    allowed_domains = ["www.next.co.uk",
                       "next.ugc.bazaarvoice.com"]

    SEARCH_URL = "http://www.next.co.uk/search?w={search_term}&isort={search_sort}"

    NEXT_PAGE_URL = "http://www.next.co.uk/search?w=jeans&isort=score&srt={start_pos}"

    REVIEWS_URL = "http://next.ugc.bazaarvoice.com/data/products.json?apiversion=5.3&" \
                  "passkey=2l72hgc4hdkhcc1bqwyj1dt6d&" \
                  "Filter=Id:{product_id}&stats=reviews&callback=bvGetReviewSummaries"

    _SORT_MODES = {
        "RELEVANT": "score",
        "POPULAR": "popular",
        "ALPHABETICAL": "title",
        "LOW_HIGH": "price",
        "HIGH_LOW": "price%20rev",
        "RATING": "rating",
    }

    def __init__(self, search_sort='POPULAR', *args, **kwargs):
        self.start_pos = 0
        super(NextCoUkProductSpider, self).__init__(
            site_name=self.allowed_domains[0],
            url_formatter=FormatterWithDefaults(
                search_sort=self._SORT_MODES[search_sort]
            ),
            *args, **kwargs)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        product_id = is_empty(
            re.findall(r'#(\d+)', product['url']),
            None
        )
        response.meta['product_id'] = product_id

        product['locale'] = 'en_GB'

        # Format product id to get proper section from html body
        item = response.css(
            '.itemsContainer .ProductDetail article.Selected'
        )

        if item:
            #  Getting title
            title = item.xpath('.//div[@class="Title"]//h1/text() |'
                               './/div[@class="Title"]//h2/text()')
            title = is_empty(
                title.extract(), ''
            )
            if title:
                product['title'] = title.strip()

            # Get description
            description = is_empty(
                item.css('.StyleContent').extract(), ''
            )
            if description:
                product['description'] = description.strip().replace('\r', '').replace('\n', '').replace('\t', '')

            # Get variants
            variants = dict()
            variants_selector = item.css('.StyleForm .DropDown')

            if variants_selector:
                for var in variants_selector:
                    var_title = var.xpath('.//label/text()')
                    var_value = var.xpath('.//select/option[@value != ""]/text()')

                    if var_title and var_value:
                        var_title = is_empty(
                            var_title.extract(), ''
                        ).strip().lower()
                        var_list = []
                        for value in var_value:
                            var_list.append(
                                value.extract()
                            )
                        variants[var_title] = var_list
                    else:
                        continue
                product['variants'] = variants

            # Get price
            price_sel = item.css('.Price')

            if price_sel:
                price = is_empty(
                    price_sel.extract()
                ).strip()
                price = is_empty(
                    re.findall(r'(\d+)', price)
                )
                product['price'] = Price(
                    priceCurrency="GBP",
                    price=price
                )
            else:
                product['price'] = None

            # Get image url
            image_sel = item.xpath('.//div[@class="StyleThumb"]//img/@src')

            if image_sel:
                image = is_empty(image_sel.extract())
                product['image_url'] = image.replace('Thumb', 'Shot')
        else:
            self.log(
                "Failed to extract product info from %r." % response.url, ERROR
            )

        # Get related products
        related_items = response.xpath(
            '//section[@class="ProductDetail"]/article[not(contains(@class,"Selected"))]'
        )

        if related_items:
            product['related_products'] = self.parse_related_products(related_items)

        # Get buyer reviews
        buyer_reviews_url = self.REVIEWS_URL.format(product_id=product_id)
        reviews_request = Request(
            url=buyer_reviews_url,
            callback=self.parse_buyer_reviews,
            dont_filter=True,
        )
        reqs.append(reviews_request)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_related_products(self, items):
        related_prods = []

        for item in items:
            # Get title
            title = item.xpath('.//div[@class="Title"]//h1/text() |'
                               './/div[@class="Title"]//h2/text()')
            if title:
                title = is_empty(
                    title.extract()
                ).strip()

            # Get url
            url = item.xpath('.//div[@class="StyleThumb"]/a/img/@src')
            if url:
                url = is_empty(
                    url.extract()
                )

            if url and title:
                related_prods.append(
                    RelatedProduct(
                        title=title,
                        url=url
                    )
                )

        return related_prods

    def parse_buyer_reviews(self, response):
        meta = response.meta.copy()
        reqs = meta.get("reqs")
        product = meta['product']
        data = response.body_as_unicode()
        data = is_empty(
            re.findall(
                r'bvGetReviewSummaries\((.+)\)',
                data
            )
        )

        if data:
            data = json.loads(data)
            results = is_empty(
                data.get('Results', [])
            )

            if results:
                # Buyer reviews
                buyer_review = dict(
                    num_of_reviews=0,
                    average_rating=0,
                    rating_by_star={'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
                )
                # rating_by_star = rating_by_star

                try:
                    buyer_reviews_data = results['ReviewStatistics']
                    buyer_review['num_of_reviews'] = buyer_reviews_data['TotalReviewCount']

                    if buyer_review['num_of_reviews']:
                        buyer_review['average_rating'] = buyer_reviews_data['AverageOverallRating']

                        ratings = buyer_reviews_data['RatingDistribution']
                        for rate in ratings:
                            star = str(rate['RatingValue'])
                            buyer_review['rating_by_star'][star] = rate['Count']
                except (KeyError, ValueError):
                    self.log(
                        "Failed to get buyer reviews from %r." % response.url, WARNING
                    )

                buyer_reviews = BuyerReviews(**buyer_review)
                product['buyer_reviews'] = buyer_reviews

                # Get brand
                try:
                    brand = results['Brand']['Name']
                    product['brand'] = brand
                except (KeyError, ValueError):
                    product['brand'] = None

                # Get department
                try:
                    departments = is_empty(
                        results['Attributes']['department']['Values']
                    )
                    department = departments['Value']
                    product['department'] = department
                except (KeyError, ValueError):
                    product['department'] = None

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """

        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)

    def _scrape_total_matches(self, response):
        """
        Scraping number of resulted product links
        """

        total_matches = response.css("#filters .ResultCount .Count ::text")
        try:
            matches_re = re.compile('(\d+) PRODUCTS')
            total_matches = re.findall(
                matches_re,
                is_empty(
                    total_matches.extract()
                )
            )
            return int(
                is_empty(total_matches, '0')
            )
        except:
            total_matches = None
            self.log(
                "Failed to extract total matches from %r." % response.url, ERROR
            )

        return total_matches

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """

        num = len(
            response.css('[data-pagenumber="1"] article.Item')
        )
        self.items_per_page = num

        if not num:
            num = None
            self.items_per_page = 0
            self.log(
                "Failed to extract results per page from %r." % response.url, ERROR
            )

        return num

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """

        items = response.css(
            'div.Page article.Item'
        )

        if items:
            for item in items:
                link = is_empty(
                    item.css('.Details .Title a ::attr(href)').extract()
                )
                res_item = SiteProductItem()
                yield link, res_item
        else:
            self.log("Found no product links in %r." % response.url, INFO)

    def _scrape_next_results_page_link(self, response):
        url = self.NEXT_PAGE_URL.format(start_pos=self.start_pos)
        self.start_pos += self.items_per_page
        return url