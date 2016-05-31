import re

from scrapy.http import HtmlResponse
from scrapy.utils.response import get_meta_refresh
from scrapy.contrib.downloadermiddleware.redirect import MetaRefreshMiddleware
from scrapy.contrib.downloadermiddleware.redirect import RedirectMiddleware

from urlparse import urljoin

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