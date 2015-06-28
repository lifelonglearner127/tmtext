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
from exceptions import OSError

from scrapy.contrib.httpcache import *
from scrapy.contrib.downloadermiddleware.httpcache import HttpCacheMiddleware
from scrapy.utils import gz

from extensions import amazon_public_key, amazon_secret_key, bucket_name

UTC_NOW = datetime.datetime.utcnow()  # we don't init it in a local method
                                      # to avoid spreading one job across
                                      #  2 dates, if it runs for too long


def get_cache_map():
    from boto.s3.connection import S3Connection
    conn = S3Connection(amazon_public_key, amazon_secret_key)
    bucket = conn.get_bucket(bucket_name)
    cache_map = {}  # spider -> date -> searchterm
    for f in bucket.list():
        if len(f.key.split('/')) < 4:
            continue  # invalid key?
        spider, date, searchterm = f.key.split('/')[0:3]
        if not spider in cache_map:
            cache_map[spider] = {}
        if not date in cache_map[spider]:
            cache_map[spider][date] = []
        if not searchterm in cache_map[spider][date]:
            cache_map[spider][date].append(searchterm)
    return cache_map


def _get_searchterms_str():
    args = [a for a in sys.argv if 'searchterms_str' in a]
    if not args:
        return
    arg_name, arg_value = args[0].split('=')
    return arg_value


def _slugify(value, replaces='\'"~@#$%^&*()[] _-/\:\?\=\,'):
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
    result = os.path.join(
        get_partial_request_path(cache_dir, spider),
        _slugify(request.url),
        key[0:2], key
    )
    # check max filename length and truncate it if needed
    if not os.path.exists(result):
        try:
            os.makedirs(result)
        except OSError as e:
            if 'too long' in str(e).lower():
                result = result[0:235]  # depends on OS! Works for Linux
                print('Cache filename truncated to 235 chars!', result)
    return result


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
        # all gzipped strings start with this symbols
        gzip_line_start = '\037\213'
        if response.body.startswith(gzip_line_start):
            body = gz.gunzip(response.body)
            if '.images-amazon.com/captcha/' in body:
                return False
        return super(CustomCachePolicy, self).should_cache_response(
            response, request)
