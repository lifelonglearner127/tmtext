# ~~coding=utf-8~~


import re
import urlparse

from scrapy.http import Request
from scrapy.http.request.form import FormRequest
from scrapy.log import msg, ERROR, WARNING, INFO, DEBUG

from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    cond_set_value, FLOATING_POINT_RGEX
from product_ranking.amazon_tests import AmazonTests
from product_ranking.amazon_bestsellers import amazon_parse_department


is_empty = lambda x, y=None: x[0] if x else y


class AmazonBaseClass(BaseProductsSpider):

    # String from html body that means there's no results ( "no results.", for example)
    total_matches_str = 'did not match any products.'
    # For regexp for total matches to parse a number from html body ( "sur", for example for French)
    total_matches_re = 'of'

    def _scrape_total_matches(self, response):
        """
        Overrides BaseProductsSpider method to scrape total result matches. total_matches_str
        and total_matches_re need to be set for every concrete amazon spider.
        :param response:
        :return: Number of total matches (int)
        """

        if unicode(self.total_matches_str) in response.body_as_unicode():
            total_matches = 0
        else:
            count_matches = is_empty(
                response.xpath(
                    '//h2[@id="s-result-count"]/text()').re(
                    u'{0}\s?([\d,.\s?]+)'.format(unicode(self.total_matches_re))
                )
            )
            if count_matches:
                total_matches = int(count_matches.replace(
                    ' ', '').replace(u'\xa0', '').replace(',', '').replace('.', ''))
            else:
                total_matches = None

        if not total_matches:
            total_matches = int(is_empty(response.xpath(
                '//h2[@id="s-result-count"]/text()'
            ).re(FLOATING_POINT_RGEX), 0))

        return total_matches

    def _scrape_product_links(self, response):
        """
        Overrides BaseProductsSpider method to scrape product links.
        """

        lis = response.xpath('//ul/li[contains(@class, "s-result-item")] |'
                             '//*[contains(@id, "results")] |'
                             '//*[contains(@class, "sx-table-item")]')
        links = []

        for no, li in enumerate(lis):
            href = li.xpath(
                ".//a[contains(@class,'s-access-detail-page')]/@href |"
                ".//a/@href")

            if href:
                href = is_empty(href.extract())
                is_prime = li.xpath(
                    "*/descendant::i[contains(concat(' ',@class,' '),' a-icon-premium ')] |"
                    "*/descendant::i[contains(@class, 'a-icon-prime]')]").extract()
                is_prime_pantry = li.xpath(
                    "*/descendant::i[contains(concat(' ',@class,' '),' a-icon-premium-pantry ')] |"
                    "*/descendant::i[contains(@class, 'a-icon-prime-pantry')] |"
                    "*/descendant::i[contains(@class, 'a-icon-primepantry')]").extract()
                links.append((href, is_prime, is_prime_pantry))

        if not links:
            self.log("Found no product links.", WARNING)

        for link, is_prime, is_prime_pantry in links:
            prime = None
            if is_prime:
                prime = 'Prime'
            if is_prime_pantry:
                prime = 'PrimePantry'
            yield link, SiteProductItem(prime=prime)
