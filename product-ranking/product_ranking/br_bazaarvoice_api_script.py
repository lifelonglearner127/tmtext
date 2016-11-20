import re
import json
from itertools import izip
from datetime import datetime

from scrapy.log import ERROR
import lxml.html

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

    def parse_buyer_reviews_products_json(self, response):
        meta = response.meta.copy()
        product = meta['product']
        try:
            json_data = json.loads(response.body_as_unicode())
            product_reviews = json_data["Results"][0].get('ReviewStatistics',{})

            if product_reviews:
                rating_by_stars = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}

                for rating_distribution in product_reviews.get('RatingDistribution',[]):
                    rating_by_stars[str(rating_distribution['RatingValue'])] = rating_distribution['Count']

                if product_reviews.get('LastSubmissionTime', False):
                    last_buyer_review_date = product_reviews.get('LastSubmissionTime').split('.')[0]
                    product[u'last_buyer_review_date'] = datetime.strptime(last_buyer_review_date, "%Y-%m-%dT%H:%M:%S").strftime('%d-%m-%Y')

                return {'num_of_reviews': product_reviews.get('TotalReviewCount',0),
                        'average_rating': round(product_reviews.get('AverageOverallRating',0),1),
                        'rating_by_star': rating_by_stars
                }

        except:
            pass

        return self.ZERO_REVIEWS_VALUE

    def parse_buyer_reviews_per_page(self, response, body_data=None):
        """
        return dict for buyer_reviews
        """
        meta = response.meta.copy()
        product = meta['product']
        reqs = meta.get('reqs', [])

        if body_data is None:
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
            rating_by_star = self.get_rating_by_star(response)
            if rating_by_star:
                num_of_reviews = response.xpath(
                    '//*[contains(@class, "BVRRCount")]/*[contains(@class, "BVRRNumber")]/text()').extract()
                average_rating = response.xpath(
                    '//*[contains(@class, "BVRRSReviewsSummaryOutOf")]/*[contains(@class, "BVRRNumber")]/text()'
                ).extract()
                if num_of_reviews and average_rating:
                    invalid_reviews = False
                    try:
                        num_of_reviews = int(num_of_reviews[0])
                        average_rating = float(average_rating[0])
                    except Exception as e:
                        print('Invalid reviews: [%s] at %s' % (str(e), response.url))
                        invalid_reviews = True
                    if not invalid_reviews:
                        buyer_reviews = {
                            'num_of_reviews': num_of_reviews,
                            'average_rating': round(average_rating, 1),
                            'rating_by_star': rating_by_star
                        }
                        return buyer_reviews
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

        yield product
        if reqs:
            yield self.called_class.send_next_request(reqs, response)

    @staticmethod
    def _scrape_alternative_rating_by_star(response):
        rating_by_star = {}
        for i in xrange(1, 6):
            num_reviews = response.xpath(
                '//*[contains(@class, "BVRRHistogramContent")]//*[contains(@class, "BVRRHistogramBarRow%i")]'
                '/*[contains(@class, "BVRRHistAbsLabel")]//text()' % i).extract()
            if num_reviews:
                num_reviews = int(num_reviews[0])
                rating_by_star[str(i)] = num_reviews
        return rating_by_star

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
                dates = re.findall(
                    r'<span class="BVRRValue BVRRReviewDate">(\d+ \w+ \d+).+</span>',
                    histogram_data
                )

                if not dates:
                    dates = re.findall(
                        r'<span class=\"BVRRValue BVRRReviewDate\">(\w+ \d+. \d+)',
                        histogram_data
                    )

                new_dates = []
                if dates:
                    for date in dates:
                        try:
                            new_date = datetime.strptime(date.replace('.', '').replace(',', ''), '%d %B %Y')
                        except:
                            try:
                                new_date = datetime.strptime(date.replace('.', '').replace(',', ''), '%B %d %Y')
                            except:
                                new_date = datetime.strptime(date.replace('.', '').replace(',', ''), '%b %d %Y')
                        new_dates.append(new_date)

                if new_dates:
                    product['last_buyer_review_date'] = max(new_dates).strftime(
                        '%d-%m-%Y')

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

                    # check if stars values == br_count
                    if hasattr(self, 'br_count'):
                        result = {}
                        if self.br_count != sum([k for k in stars.values()]):
                            lxml_doc = lxml.html.fromstring(data.get('BVRRRatingSummarySourceID', ''))
                            for stars_num in range(1, 6):
                                stars_element = lxml_doc.xpath(
                                    '//*[contains(@class, "BVRRHistogramBarRow")]'
                                    '[contains(@class, "BVRRHistogramBarRow%s")]' % stars_num)
                                if stars_element:
                                    num_reviews = re.search(r'\((\d+)\)', stars_element[0].text_content())
                                    if num_reviews:
                                        num_reviews = num_reviews.group(1)
                                        result[str(stars_num)] = int(num_reviews)
                            return result
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
            if not data:
                # try to scrape alternative rating by star data
                alternative_rating_by_star = self._scrape_alternative_rating_by_star(response)
                if alternative_rating_by_star:
                    return alternative_rating_by_star
            return self.ZERO_REVIEWS_VALUE['rating_by_star']
