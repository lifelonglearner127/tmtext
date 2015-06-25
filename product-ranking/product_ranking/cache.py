#
# This is a slightly modified version of the FilesystemCacheStorage class
# from scrapy.contrib. We separate cache folders by search terms.
#

# TODO:
# - packing appropriate cache dirs;
# - uploading them to S3 on spider close;
# - downloading cache dirs and unpacking them;
# - executing the crawler against the cached dir;
# - error handling (blank page?); solving captcha issues at amazon
# - CH support

import os
import sys
import datetime

from scrapy.contrib.httpcache import *
from scrapy.contrib.downloadermiddleware.httpcache import HttpCacheMiddleware


UTC_NOW = datetime.datetime.utcnow()  # we don't init it in a local method
                                      # to avoid spreading one job across
                                      #  2 dates, if it runs for too long


def _get_searchterms_str():
    args = [a for a in sys.argv if 'searchterms_str' in a]
    if not args:
        return
    arg_name, arg_value = args[0].split('=')
    return arg_value


def _slugify(value, replaces='\'"~@#$%^&*()[] _-/\:\?\='):
    for char in replaces:
        value = value.replace(char, '-')
    return value


def get_partial_request_path(cache_dir, spider):
    global UTC_NOW
    searchterms_str = _slugify(_get_searchterms_str())
    utc_today = UTC_NOW.strftime('%Y-%m-%d')
    if searchterms_str:
        return os.path.join(
            cache_dir, spider.name, utc_today, searchterms_str)
    else:
        return os.path.join(
            cache_dir, spider.name, utc_today, 'url')


def get_request_path_with_date(cache_dir, spider, request):
    key = request_fingerprint(request)
    return os.path.join(cache_dir, spider.name, key[0:2], key)


class CustomFilesystemCacheStorage(FilesystemCacheStorage):
    """ For local spider usage (mostly for development purposes) """

    def _get_request_path(self, spider, request):
        key = request_fingerprint(request)
        searchterms_str = _slugify(_get_searchterms_str())
        if searchterms_str:
            return os.path.join(self.cachedir, spider.name, searchterms_str,
                                key[0:2], key)
        else:
            return os.path.join(self.cachedir, spider.name, key[0:2], key)


class S3CacheStorage(FilesystemCacheStorage):
    """ For uploading cache to S3 """

    def _get_request_path(self, spider, request):
        return get_request_path_with_date(self.cachedir, spider, request)


class CustomCachePolicy(DummyPolicy):
    """ For not caching amazon captcha """

    def should_cache_response(self, response, request):
        if 2000 >= len(response.body) >= 1850:
            return False
        return super(CustomCachePolicy, self).should_cache_response(
            response, request)