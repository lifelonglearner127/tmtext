import re
import json
import inspect
from itertools import izip

from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import BuyerReviews


is_empty = lambda x, y=None: x[0] if x else y

ZERO_REVIEWS_VALUE = {
    'num_of_reviews': 0,
    'average_rating': 0.0,
    'rating_by_star': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
}


def parse_buyer_reviews(response):
    """
    Parses buyer reviews from bazaarvoice API
    """
    meta = response.meta.copy()
    product = meta['product']
    reqs = meta.get('reqs', [])

    stack = inspect.stack()
    called_class = stack[1][0].f_locals["self"].__class__()

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
                rating_by_star = get_rating_by_star(called_class, response)

                buyer_reviews = {
                    'num_of_reviews': num_of_reviews,
                    'average_rating': average_rating,
                    'rating_by_star': rating_by_star
                }
            else:
                buyer_reviews = ZERO_REVIEWS_VALUE

        except (KeyError, IndexError) as exc:
            called_class.log(
                'Unable to parse buyer reviews on {url}: {exc}'.format(
                    url=product['url'],
                    exc=exc
                ), ERROR
            )
            buyer_reviews = ZERO_REVIEWS_VALUE
    else:
        buyer_reviews = ZERO_REVIEWS_VALUE

    product['buyer_reviews'] = BuyerReviews(**buyer_reviews)

    if reqs:
        return called_class.send_next_request(reqs, response)

    return product


def get_rating_by_star(called_class, response):
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
                called_class.log(
                    'Unable to parse buyer reviews on {url}: {exc}'.format(
                        url=product['url'],
                        exc=exc
                    ), ERROR
                )
                return ZERO_REVIEWS_VALUE['rating_by_star']
        else:
            return ZERO_REVIEWS_VALUE['rating_by_star']
