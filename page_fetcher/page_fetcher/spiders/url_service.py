import json

import scrapy.log
from scrapy.spider import Spider
from scrapy.http import (Request, FormRequest)
from scrapy.selector import Selector
from scrapy.contrib.spidermiddleware.httperror import HttpError

from captcha_solver import CaptchaBreakerWrapper

from page_fetcher.items import PageItem, RequestErrorItem


class FailedToSolveCaptcha(Exception):

    def __init__(self, captcha_img_url, *args, **kwargs):
        super(FailedToSolveCaptcha, self).__init__(*args, **kwargs)

        self.message = "Failed to solve captcha " + captcha_img_url
        self.url = captcha_img_url


class UrlServiceSpider(Spider):

    name = "url_service"
    allowed_domains = []
    start_urls = []

    SERVICE_URL = "http://localhost:8080/get_queued_urls/"

    def __init__(self, limit='100', list_urls=False, service_url=None,
                 *args, **kwargs):
        super(UrlServiceSpider, self).__init__(*args, **kwargs)

        self.urls = {}
        self.limit = limit
        self.list_urls = list_urls

        if service_url is not None:
            self.service_url = service_url
        else:
            self.service_url = self.SERVICE_URL
        self.service_url += '?limit=%d'

        self._cbw = CaptchaBreakerWrapper()

        self.start_urls.append(self.service_url % int(limit))

    def parse(self, response):
        for row in json.loads(response.body):
            url = row[0]

            self.urls[url] = row

            if self.list_urls:
                print url

            yield Request(url, callback=self.parse_target,
                          errback=self.parse_target_err)

    def parse_target(self, response):
        if self._has_captcha(response.body):
            return self._handle_captcha(response)
        else:
            return self._parse_target(response)

    def parse_target_after_captcha(self, response):
        if self._has_captcha(response.body):
            # We already tried to solve the captcha, give up.

            original_url = response.request.headers['Referer']
            item = RequestErrorItem(
                id=self.urls[original_url][1],
                http_code=response.status,
                error_string="Failed to solve captcha.")
            return item
        else:
            return self._parse_target(response)

    def _parse_target(self, response):
        url, url_id, imported_data_id, category_id = \
            self.urls[response.request.url]

        item = PageItem(
            id=url_id,
            url=url,
            imported_data_id=imported_data_id,
            category_id=category_id, body=response.body)
        return item

    def _handle_captcha(self, response):
        scrapy.log.msg("Captcha challenge for %s." % response.request.url,
                       level=scrapy.log.INFO)

        forms = Selector(response).xpath('//form')
        assert len(forms) == 1, "More than one form found."
        hidden_value1 = forms[0].xpath(
            '//input[@name="amzn"]/@value').extract()[0]
        hidden_value2 = forms[0].xpath(
            '//input[@name="amzn-r"]/@value').extract()[0]
        captcha_img = forms[0].xpath(
            '//img[contains(@src, "/captcha/")]/@src').extract()[0]

        scrapy.log.msg(
            "Extracted capcha values: (%s) (%s) (%s)"
            % (hidden_value1, hidden_value2, captcha_img),
            level=scrapy.log.DEBUG)
        captcha = self._solve_captcha(captcha_img)

        if captcha is None:
            scrapy.log.msg("Failed to solve captcha %s." % captcha_img,
                           level=scrapy.log.WARNING)
            item = RequestErrorItem(
                id=self.urls[response.request.url][1],
                http_code=response.status,
                error_string="Failed to solve captcha for %s." % response.url)
            return item
        else:
            scrapy.log.msg("Submitting captcha %s for %s."
                           % (captcha, captcha_img),
                           level=scrapy.log.INFO)
            return FormRequest.from_response(
                response,
                formname='',
                formdata={
                    'amzn[0]': hidden_value1,
                    'amzn-r[0]': hidden_value2,
                    'field-keywords[0]': captcha,
                },
                callback=self.parse_target_after_captcha,
                errback=self.parse_target_after_captcha_err)

    def parse_target_after_captcha_err(self, failure):
        return self._handle_error(failure, "After trying to solve captcha: ")

    def parse_target_err(self, failure):
        return self._handle_error(failure)

    def _handle_error(self, failure, error_string_prefix=''):
        url_id = self.urls[failure.request.url][1]
        error_string = failure.getErrorMessage()
        if isinstance(failure.value, HttpError):
            status = failure.value.response.status
        else:
            status = 0
            scrapy.log.msg(
                "Unhandled failure type '%s'." % type(failure.value),
                level=scrapy.log.ERROR)

        item = RequestErrorItem(
            id=url_id,
            http_code=status,
            error_string=error_string_prefix + error_string)
        return item

    def _has_captcha(self, body):
        return '.images-amazon.com/captcha/' in body

    def _solve_captcha(self, captcha_url):
        return self._cbw.solve_captcha(captcha_url)
