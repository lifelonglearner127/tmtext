#
# This is a slightly modified version of the FilesystemCacheStorage class
# from scrapy.contrib. We separate cache folders by search terms.
#

import os
import sys

from scrapy.contrib.httpcache import *


class CustomFilesystemCacheStorage(FilesystemCacheStorage):

    def _get_searchterms_str(self):
        args = [a for a in sys.argv if 'searchterms_str' in a]
        if not args:
            return
        arg_name, arg_value = args[0].split('=')
        return arg_value

    def _slugify(self, value, replaces='\'"~@#$%^&*()[] _-'):
        for char in replaces:
            value = value.replace(char, '-')
        return value

    def _get_request_path(self, spider, request):
        key = request_fingerprint(request)
        searchterms_str = self._slugify(self._get_searchterms_str())
        if searchterms_str:
            return os.path.join(self.cachedir, spider.name, searchterms_str,
                                key[0:2], key)
        else:
            return os.path.join(self.cachedir, spider.name, key[0:2], key)