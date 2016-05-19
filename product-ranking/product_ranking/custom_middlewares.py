from scrapy.http import HtmlResponse
from scrapy.utils.response import get_meta_refresh
from scrapy.contrib.downloadermiddleware.redirect import MetaRefreshMiddleware


class VerizonMetaRefreshMiddleware(MetaRefreshMiddleware):
    def process_response(self, request, response, spider):
        request.meta['dont_filter'] = True
        print request.meta.get('redirect_times')
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
