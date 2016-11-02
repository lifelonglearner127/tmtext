import re
import base64

from scrapy.http import HtmlResponse
from scrapy.utils.response import get_meta_refresh
from scrapy.contrib.downloadermiddleware.redirect import MetaRefreshMiddleware
from scrapy.contrib.downloadermiddleware.redirect import RedirectMiddleware
from scrapy import log
from urlparse import urljoin
import random

class VerizonMetaRefreshMiddleware(MetaRefreshMiddleware):
    def process_response(self, request, response, spider):
        request.meta['dont_filter'] = True
        if 'dont_redirect' in request.meta or request.method == 'HEAD' or \
                not isinstance(response, HtmlResponse) or request.meta.get('redirect_times') >= 1:
            request.meta['dont_redirect'] = True
            return response

        if isinstance(response, HtmlResponse):
            interval, url = get_meta_refresh(response)
            if url and interval < self._maxdelay:
                redirected = self._redirect_request_using_get(request, url)
                redirected.dont_filter = True
                return self._redirect(redirected, request, spider, 'meta refresh')

        return response

class VerizonRedirectMiddleware(RedirectMiddleware):
    def process_response(self, request, response, spider):
        if (request.meta.get('dont_redirect', False) or
                response.status in getattr(spider, 'handle_httpstatus_list', []) or
                response.status in request.meta.get('handle_httpstatus_list', []) or
                request.meta.get('handle_httpstatus_all', False)):
            return response

        allowed_status = (301, 302, 303, 307)
        if 'Location' not in response.headers or response.status not in allowed_status:
            return response

        # HTTP header is ascii or latin1, redirected url will be percent-encoded utf-8
        location = response.headers['location'].decode('latin1')
        search_final_location = re.search('actualUrl=(.*)', location)

        if search_final_location:
            redirected_url = urljoin(request.url, search_final_location.group(1))
        else:
            redirected_url = urljoin(request.url, location)

        if response.status in (301, 307) or request.method == 'HEAD':
            redirected = request.replace(url=redirected_url)
            return self._redirect(redirected, request, spider, response.status)

        redirected = self._redirect_request_using_get(request, redirected_url)
        return self._redirect(redirected, request, spider, response.status)


class AmazonProxyMiddleware(object):
    def change_proxy(self, request):
        request.meta['503_retry'] = request.meta.get('503_retry', 0)
        if request.meta['503_retry'] < 10:
            log.msg('PROXY {}'.format(request.url))
            proxy_address = 'http://proxy.crawlera.com:8010'
            proxy_user_pass = 'eff4d75f7d3a4d1e89115c0b59fab9b2:'
            request.meta['503_retry'] += 1
            request.meta['proxy'] = proxy_address
            basic_auth = 'Basic ' + base64.encodestring(proxy_user_pass)
            request.headers['Proxy-Authorization'] = basic_auth
            request.headers.pop('Referer', '')
            request.cookies = {}
            request.dont_filter = True
            return request
        return None

    def process_exception(self, request, exception, spider):
        return_request = self.change_proxy(request)
        if return_request:
            return return_request

    def process_response(self, request, response, spider):
        proxy_status_list = [503]
        if response.status in proxy_status_list:
            return_request = self.change_proxy(request)
            if return_request:
                return return_request
        return response

class WalmartRetryMiddleware(RedirectMiddleware):
    def process_response(self, request, response, spider):
        if response.status in [301, 302, 307]:
            location = response.headers.get('Location')
            location = urljoin('https://www.walmart.com/', location)
            if not location.startswith('https://www.walmart.com/'):
                log.msg('RETRY: {}'.format(request.url))
                request.dont_filter = True
                return request
            else:
                request = request.replace(url=location)
                return request
        return response


class LuminatiProxy(object):
    def __init__(self, settings):
        self.squid_proxy = "http://52.200.249.157:7708"
        self.squid_proxy_connector = "http://10.0.5.241:7708"

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def _insert_proxy_into_request(self, request):
        request.meta['proxy'] = self.squid_proxy
        # Debug
        log.msg('Using Luminati proxy via Squid {}'.format(self.squid_proxy_connector))

    def process_request(self, request, spider):
        # Don't overwrite existing
        if 'proxy' in request.meta:
            return
        self._insert_proxy_into_request(request)

    def process_exception(self, request, exception, spider):
        log.msg('Error {} getting url {} using Luminati proxy'.format(exception, request.url))


class ProxyrainProxy(object):
    def __init__(self, settings):
        self.rain_proxy = "https://proxy-002.proxyrain.net:80"
        self.squid_proxy_connector = "https://10.0.5.241:7708"

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def _insert_proxy_into_request(self, request):
        request.meta['proxy'] = self.squid_proxy_connector
        #request.meta['proxy'] = self.squid_proxy_connector
        # Debug
        log.msg('Using Proxyrain proxy via Squid {}'.format(self.rain_proxy))

    def process_request(self, request, spider):
        # Don't overwrite existing
        if 'proxy' in request.meta:
            return
        self._insert_proxy_into_request(request)

    def process_exception(self, request, exception, spider):
        log.msg('Error {} getting url {} using Proxyrain proxy'.format(exception, request.url))

