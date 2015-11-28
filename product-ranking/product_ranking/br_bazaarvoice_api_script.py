import re
import json
from itertools import izip
from datetime import datetime

from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import BuyerReviews


is_empty = lambda x, y=None: x[0] if x else y

class BuyerReviewsBazaarApi(object):
    def __init__(self, *args, **kwargs):
        self.called_class = kwargs.get('called_class')

        self.ZERO_REVIEWS_VALUE = {
            'num_of_reviews': 0,
            'average_rating': 0.0,
            'rating_by_star': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
        }

    def parse_buyer_reviews_per_page(self, response):
        """
        return dict for buyer_reviews
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
                    rating_by_star = self.get_rating_by_star(response)

                    buyer_reviews = {
                        'num_of_reviews': num_of_reviews,
                        'average_rating': round(average_rating, 1),
                        'rating_by_star': rating_by_star
                    }
                else:
                    buyer_reviews = self.ZERO_REVIEWS_VALUE

            except (KeyError, IndexError) as exc:
                self.called_class.log(
                    'Unable to parse buyer reviews on {url}: {exc}'.format(
                        url=product['url'],
                        exc=exc
                    ), ERROR
                )
                buyer_reviews = self.ZERO_REVIEWS_VALUE
        else:
            buyer_reviews = self.ZERO_REVIEWS_VALUE

        return buyer_reviews

    def parse_buyer_reviews(self, response):
        """
        Parses buyer reviews from bazaarvoice API
        Create object from dict
        :param response:
        :return:
        """
        meta = response.meta.copy()
        product = meta['product']
        reqs = meta.get('reqs', [])

        product['buyer_reviews'] = BuyerReviews(**self.parse_buyer_reviews_per_page(response))

        if reqs:
            return self.called_class.send_next_request(reqs, response)

        return product

    def get_rating_by_star(self, response):
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

                date = is_empty(
                    re.findall(
                        r'<span class="BVRRValue BVRRReviewDate">(\d+ \w+ \d+).+</span>',
                        histogram_data
                    )
                )

                if not date:
                    date = is_empty(
                        re.findall(
                            r'<span class=\"BVRRValue BVRRReviewDate\">(\w+ \d+. \d+)',
                            histogram_data
                        )
                    )
                if date:
                    try:
                        last_buyer_review_date = datetime.strptime(date.replace('.', '').replace(',', ''), '%d %B %Y')
                    except:
                        last_buyer_review_date = datetime.strptime(date.replace('.', '').replace(',', ''), '%B %d %Y')

                    product['last_buyer_review_date'] = last_buyer_review_date.strftime('%d-%m-%Y')

                stars_data = re.findall(
                    r'<span class="BVRRHistStarLabelText">(\d+) (?:S|s)tars?</span>|'
                    r'<span class="BVRRHistAbsLabel">(\d+)</span>',
                    histogram_data
                )
                if stars_data:
                    # ('5', '') --> '5'
                    item_list = []
                    for star in stars_data:
                        item_list.append(filter(None, list(star))[0])

                    # ['3', '0', '5', '6'] --> {'3': '0', '5': '6'}
                    i = iter(item_list)
                    stars = {k: int(v) for (k, v) in izip(i, i)}
                else:
                    stars_data = re.findall(
                        r'<div itemprop="reviewRating".+>.+<span itemprop="ratingValue" '
                        r'class="BVRRNumber BVRRRatingNumber">(\d+)</span>|'
                        r'<span itemprop=\"ratingValue\" class=\"BVRRNumber BVRRRatingNumber\">(\d+).\d+',
                        histogram_data
                    )
                    stars_data = [x for i in stars_data for x in i if x != '']
                    stars = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
                    for star in stars_data:
                        stars[star] += 1

                return stars



            except (KeyError, IndexError) as exc:
                self.called_class.log(
                    'Unable to parse buyer reviews on {url}: {exc}'.format(
                        url=product['url'],
                        exc=exc
                    ), ERROR
                )
                return self.ZERO_REVIEWS_VALUE['rating_by_star']
        else:
            return self.ZERO_REVIEWS_VALUE['rating_by_star']
