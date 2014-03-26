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
                 captcha_retries='10', *args, **kwargs):
        super(UrlServiceSpider, self).__init__(*args, **kwargs)

        self.limit = limit
        self.list_urls = list_urls
        self.captcha_retries = int(captcha_retries)

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

            if self.list_urls:
                print url

            req = Request(url, callback=self.parse_target,
                          errback=self.parse_target_err)
            req.meta['url_data'] = row
            yield req

    def parse_target(self, response):
        if not self._has_captcha(response.body):
            result = self._parse_target(response)
        elif response.meta.get('captch_solve_try', 0) >= self.captcha_retries:
            # We already tried to solve the captcha, give up.

            result = RequestErrorItem(
                id=response.meta['url_data'][1],
                http_code=response.status,
                error_string="Failed to solve captcha.")
        else:
            result = self._handle_captcha(response)
        return result

    def _parse_target(self, response):
        url, url_id, imported_data_id, category_id = response.meta['url_data']

        item = PageItem(
            id=url_id,
            url=url,
            imported_data_id=imported_data_id,
            category_id=category_id, body=response.body)
        return item

    def _handle_captcha(self, response):
        url, url_id, imported_data_id, category_id = response.meta['url_data']
        captch_solve_try = response.meta.get('captch_solve_try', 0)

        scrapy.log.msg("Captcha challenge for %s (try %d)."
                       % (url, captch_solve_try),
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
            err_msg = "Failed to guess captcha for '%s' (id: %s, try: %d)." % (
                response.url, url_id, captch_solve_try)
            scrapy.log.msg(err_msg, level=scrapy.log.ERROR)
            result = RequestErrorItem(
                id=url_id,
                http_code=response.status,
                error_string=err_msg)
        else:
            scrapy.log.msg("Submitting captcha '%s' for '%s' (try %d)."
                           % (captcha, captcha_img, captch_solve_try),
                           level=scrapy.log.INFO)
            result = FormRequest.from_response(
                response,
                formname='',
                formdata={
                    'amzn[0]': hidden_value1,
                    'amzn-r[0]': hidden_value2,
                    'field-keywords[0]': captcha,
                },
                callback=self.parse_target,
                errback=self.parse_target_err)
            result.meta['captch_solve_try'] = captch_solve_try + 1
            result.meta['url_data'] = response.meta['url_data']

        return result

    def parse_target_err(self, failure):
        url_id = failure.request.meta['url_data'][1]
        error_string = failure.getErrorMessage()
        if isinstance(failure.value, HttpError):
            status = failure.value.response.status
        else:
            status = 0
            scrapy.log.msg("Unhandled failure type '%s'. Will continue"
                           % type(failure.value), level=scrapy.log.ERROR)

        item = RequestErrorItem(
            id=url_id,
            http_code=status,
            error_string=error_string)
        return item

    def _has_captcha(self, body):
        return '.images-amazon.com/captcha/' in body

    def _solve_captcha(self, captcha_url):
        return self._cbw.solve_captcha(captcha_url)
