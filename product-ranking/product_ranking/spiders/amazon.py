# -*- coding: utf-8 -*-#
from __future__ import (division, absolute_import, unicode_literals,
                        print_function)
import re

from datetime import datetime
from scrapy import Request

from product_ranking.amazon_tests import AmazonTests
from product_ranking.amazon_base_class import AmazonBaseClass
from product_ranking.validators.amazon_validator import AmazonValidatorSettings


class AmazonProductsSpider(AmazonTests, AmazonBaseClass):
    name = 'amazon_products'
    allowed_domains = ["www.amazon.com"]

    user_agent = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:35.0) Gecko'
                  '/20100101 Firefox/35.0')



    QUESTIONS_URL = "https://www.amazon.com/ask/questions/inline/{asin_id}/{page}"

    def __init__(self, *args, **kwargs):
        super(AmazonProductsSpider, self).__init__(*args, **kwargs)

        self.settings = AmazonValidatorSettings(spider_class=self)

        # String from html body that means there's no results ( "no results.", for example)
        self.total_match_not_found_re = 'did not match any products.'
        # Regexp for total matches to parse a number from html body
        self.total_matches_re = r'of\s?([\d,.\s?]+)'

        # Default price currency
        self.price_currency = 'USD'
        self.price_currency_view = '$'

        self.scrape_questions = kwargs.get('scrape_questions', None)
        if self.scrape_questions not in ('1', 1, True, 'true'):
            self.scrape_questions = False

        # Locale
        self.locale = 'en-US'

        # update validator settings

    def _format_last_br_date(self, date):
        """
        Parses date that is gotten from HTML.
        """
        date = self._is_empty(
            re.findall(
                r'on (\w+ \d+, \d+)', date
            ), ''
        )

        if date:
            date = date.replace(',', '').replace('.', '')

            try:
                d = datetime.strptime(date, '%B %d %Y')
            except ValueError:
                d = datetime.strptime(date, '%b %d %Y')

            return d

        return None

    def _search_page_error(self, response):
        body = response.body_as_unicode()
        return "Your search" in body \
            and "did not match any products." in body

    def is_nothing_found(self, response):
        txt = response.xpath('//h1[@id="noResultsTitle"]/text()').extract()
        txt = ''.join(txt)
        return 'did not match any products' in txt

    def _parse_questions(self, response):
        asin_id = response.xpath(
            '//input[@id="ASIN"]/@value').extract() or \
            re.findall('"ASIN":"(.*?)"', response.body)
        if asin_id:
            return Request(self.QUESTIONS_URL
                               .format(asin_id=asin_id[0], page="1"),
                           callback=self._parse_recent_questions, dont_filter=True)

        return None

    def _parse_recent_questions(self, response):
        product = response.meta['product']
        reqs = response.meta.get('reqs', [])

        if not self.scrape_questions:
            if reqs:
                return self.send_next_request(reqs, response)
            else:
                return product

        recent_questions = product.get('recent_questions', [])
        questions = response.css('.askTeaserQuestions > div')
        for question in questions:
            q = {}

            question_summary = self._is_empty(
                question.xpath('.//div[span[text()="Question:"]]'
                               '/following-sibling::div[1]/a/text()')
                .extract())
            question_summary = (question_summary.strip()
                                if question_summary
                                else question_summary)
            q['questionSummary'] = question_summary

            questoin_id = self._is_empty(
                question.xpath('.//div[span[text()="Question:"]]/'
                               'following-sibling::div[1]/a/@href')
                .re('/forum/-/(.*)?/'))

            q['questionId'] = questoin_id
            q['voteCount'] = self._is_empty(
                question.xpath('.//@data-count').extract())

            q['answers'] = []
            answers = question.xpath(
                './/div[span[text()="Answer:"]]/following-sibling::div')
            for answer in answers:
                a = {}
                name = self._is_empty(
                    question.xpath('.//*[@class="a-color-tertiary"]/text()')
                    .re('By (.*) on '))
                name = name.strip() if name else name
                a['userNickname'] = name

                date = self._is_empty(
                    question.xpath('.//*[@class="a-color-tertiary"]/text()')
                    .re(' on (\w+ \d+, \d+)'))
                a['submissionDate'] = date
                q['submissionDate'] = date

                answer_summary = ''.join(
                    answer.xpath('span[1]/text()|'
                                 'span/span[@class="askLongText"]/text()')
                    .extract())

                a['answerSummary'] = (answer_summary.strip()
                                      if answer_summary
                                      else answer_summary)

                q['answers'].append(a)

            q['totalAnswersCount'] = len(q['answers'])

            recent_questions.append(q)

        if recent_questions:
            product['recent_questions'] = recent_questions

        if questions:
            try:
                current_page = int(re.search('/(\d+)$', response.url).group(1))
                url = re.sub('/\d+$', "/%d" % (current_page + 1), response.url)
                reqs.append(
                    Request(url, callback=self._parse_recent_questions, dont_filter=True))
            except:
                pass

        if reqs:
            return self.send_next_request(reqs, response)

        return product
