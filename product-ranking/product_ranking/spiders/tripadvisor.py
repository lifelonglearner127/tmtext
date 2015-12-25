#
# ttripadvisor.com spider
#

import re
import urlparse

import scrapy
from scrapy.conf import settings
from scrapy.http import Request, FormRequest
from scrapy.log import INFO, WARNING, ERROR, DEBUG
from dateutil.parser import parse as parse_date


class TripAdvisorItem(scrapy.Item):
    _subitem = scrapy.Field()
    url = scrapy.Field()
    reviews = scrapy.Field()


class TripAdvisorSpider(scrapy.Spider):
    name = 'tripadvisor_products'  # "_products" left for compatibility only
    allowed_domains = ['tripadvisor.com', 'www.tripadvisor.com']  # do not remove comment - used in find_spiders()

    def __init__(self, *args, **kwargs):
        self.product_url = kwargs['product_url']
        self.user_agent = kwargs.get(
            'user_agent',
            ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
             "(KHTML, like Gecko) Chrome/15.0.87")
        )
        settings.overrides['ITEM_PIPELINES'] = {'product_ranking.pipelines.MergeSubItems': 1000}
        super(TripAdvisorSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        req = Request(self.product_url)
        req.headers.setdefault('User-Agent', self.user_agent)
        yield req

    def _page_has_reviews(self, response):
        """ Returns true if the page has comments
            (i.e. they aren't loaded dynamically) """
        return bool(
            response.css('.reviewSelector .innerBubble .rating').extract()
        )

    @staticmethod
    def _join_list_str(lst):
        return ' '.join([q for q in lst if q.strip()]).strip()

    def _parse_reviews(self, response):
        reviews = []
        for review_block in response.css('.reviewSelector .innerBubble .rating'):
            review = {}
            rating = review_block.xpath('.//img/@alt').extract()
            quote = review_block.xpath('./../*[contains(@class, "quote")]//text()').extract()
            text = review_block.xpath('./../*[contains(@class, "entry")]//text()').extract()
            date = review_block.xpath('./..//*[contains(@class, "ratingDate")]/@title').extract()
            if not date:
                date = review_block.xpath('./..//*[contains(@class, "ratingDate")]/text()').extract()
            if not quote and not date:
                continue  # little useless sub-review
            date = date[0].replace('Reviewed', '').strip()
            review['rating'] = int(re.search('(\d+) of.', rating[0]).group(1).strip())
            review['quote'] = self._join_list_str(quote)
            review['text'] = TripAdvisorSpider._join_list_str(text)
            review['datetime'] = parse_date(date)
            reviews.append(review)
        return reviews

    def _next_page_link(self, response):
        if response.xpath(
                '//*[contains(@class, "pagination")]'
                '//*[contains(@class, "next")][contains(@class, "disabled")]'
        ).extract():
            return  # end of pagination
        link = response.xpath('//*[contains(@class, "pagination")]'
                              '//a[contains(@class, "next")]/@href').extract()
        if not link:
            self.log("Could not get next link @ %s" % response.url, ERROR)
        return Request(
            urlparse.urljoin('http://'+self.allowed_domains[0], link[0]),
            callback=self.parse, meta=response.meta
        )

    def parse(self, response):
        item = response.meta.get('item', TripAdvisorItem())
        item['_subitem'] = True
        if not 'url' in item:
            item['url'] = response.url
        _reviews = item.get('reviews', [])

        if self._page_has_reviews(response):
            # parse static page
            _reviews.extend(self._parse_reviews(response))
            item['reviews'] = _reviews
        else:
            review_selectors = response.xpath(
                '//div[contains(@class, "review")][contains(@id, "review_")]/@id'
            ).extract()
            # TODO: dynamic ajax requests
            #assert False, review_selectors

        response.meta['item'] = item
        yield item

        _next_page = self._next_page_link(response)
        if _next_page:
            yield _next_page  # scrape goes on