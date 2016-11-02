# Scrapy settings for product_ranking project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import os
import sys
import random
import requests
from scrapy import log
from requests.exceptions import (Timeout as ReqTimeout,
                                 ProxyError as ReqProxyError, SSLError,
                                 ContentDecodingError, ConnectionError)


def _install_pip():
    # TODO: a workaround for SQS - fix post_starter_spiders.py and remove
    # install PIP packages for sure?
    os.system('python /home/spiders/repo/post_starter_spiders.py')
    os.system('python /home/spiders/repo/tmtext/deploy/sqs_ranking_spiders/post_starter_spiders.py')
_install_pip()


BOT_NAME = 'product_ranking'

SPIDER_MODULES = ['product_ranking.spiders']
NEWSPIDER_MODULE = 'product_ranking.spiders'

ITEM_PIPELINES = {
    'product_ranking.pipelines.CutFromTitleTagsAndReturnStringOnly': 300,
    'product_ranking.pipelines.SetMarketplaceSellerType': 300,
    'product_ranking.pipelines.AddSearchTermInTitleFields': 300,
    'product_ranking.pipelines.CheckGoogleSourceSiteFieldIsCorrectJson': 400,
    'product_ranking.pipelines.WalmartRedirectedItemFieldReplace': 800,
    'product_ranking.pipelines.SetRankingField': 900,
    'product_ranking.pipelines.MergeSubItems': 1000,
    'product_ranking.pipelines.CollectStatistics': 1300
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'product_ranking (+http://www.yourdomain.com)'

RANDOM_UA_PER_PROXY = True

# Delay between requests not to be blocked (seconds).
DOWNLOAD_DELAY = 0.5

# allow max N seconds to download anything
DOWNLOAD_TIMEOUT = 60

# Maximum URL length
URLLENGTH_LIMIT = 5000

# show all duplicates (makes debugging easier)
DUPEFILTER_DEBUG = True

#AmazonFresh mapping locations and market place id
AMAZONFRESH_LOCATION = {
    "southern_cali": "A241IQ0793UAL2",
    "northern_cali": "A3FX2TOAMS7SFL",
    "seattle": "A83PXQN2224PA"
}

if not 'EXTENSIONS' in globals():
    EXTENSIONS = {}
EXTENSIONS['product_ranking.extensions.StatsCollector'] = 500

EXTENSIONS['product_ranking.extensions.IPCollector'] = 500

EXTENSIONS['product_ranking.extensions.RequestsCounter'] = 500

# memory limit
EXTENSIONS['scrapy.contrib.memusage.MemoryUsage'] = 500
MEMUSAGE_LIMIT_MB = 2048
MEMUSAGE_ENABLED = True



# redefine log foramtter. DropItem exception provided with ERROR level
#LOG_FORMATTER = 'product_ranking.pipelines.PipelineFormatter'

# Value to use for buyer_reviews if no reviews found
ZERO_REVIEWS_VALUE = [0, 0.0, {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}]

# TODO: move out from this file! should be set dynamically in the __init__ method of the BaseValidator class
# The piece of code below is awful, need to get rid of it asap.
# I have warned you. Better don't look there at all.

CWD = os.path.dirname(os.path.abspath(__file__))

# RANDOM PROXY SETTINGS
# Retry many times since proxies often fail
RETRY_TIMES = 15
# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408]

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 90,
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
    'scrapy_crawlera.CrawleraMiddleware': 600  # pip install scrapy-crawlera
}


CRAWLERA_ENABLED = False  # false by default
CRAWLERA_APIKEY = 'eff4d75f7d3a4d1e89115c0b59fab9b2'


_args_names = [arg.split('=')[0] if '=' in arg else arg for arg in sys.argv]
if 'validate' in _args_names:
    if not 'ITEM_PIPELINES' in globals():
        ITEM_PIPELINES = {}
    ITEM_PIPELINES['product_ranking.validation.ValidatorPipeline'] = 99


HTTPCACHE_DIR = os.path.join(CWD, '..', '_http_s3_cache')  # default

if 'save_raw_pages' in _args_names:
    #DOWNLOADER_MIDDLEWARES['scrapy.contrib.downloadermiddleware.httpcache.HttpCacheMiddleware'] = 50
    #DOWNLOADER_MIDDLEWARES['product_ranking.cache.PersistentCacheMiddleware'] = 50
    HTTPCACHE_ENABLED = True
    HTTPCACHE_POLICY = 'product_ranking.cache.CustomCachePolicy'
    HTTPCACHE_STORAGE = 'product_ranking.cache.S3CacheStorage'
    HTTPCACHE_EXPIRATION_SECS = 0  # forever
    EXTENSIONS['product_ranking.extensions.S3CacheUploader'] = 999

if 'load_raw_pages' in _args_names:
    HTTPCACHE_ENABLED = True
    HTTPCACHE_POLICY = 'product_ranking.cache.CustomCachePolicy'
    HTTPCACHE_STORAGE = 'product_ranking.cache.S3CacheStorage'
    HTTPCACHE_EXPIRATION_SECS = 0  # forever
    EXTENSIONS['product_ranking.extensions.S3CacheDownloader'] = 999

if 'enable_cache' in _args_names:  # for local development purposes only!
    HTTPCACHE_ENABLED = True
    HTTPCACHE_POLICY = 'product_ranking.cache.CustomCachePolicy'
    HTTPCACHE_STORAGE = 'product_ranking.cache.CustomFilesystemCacheStorage'
    HTTPCACHE_EXPIRATION_SECS = 0  # forever
    HTTPCACHE_DIR = os.path.join(CWD, '..', '_http_cache')

EXTENSIONS['product_ranking.extensions.SignalsExtension'] = 100

try:
    from settings_local import *
except ImportError:
    pass

# Proxy list containing entries like
# http://host1:port
# http://username:password@host2:port
# http://host3:port
# ...


# TODO: removeme
def _create_http_proxies_list(fpath, host='tprox.contentanalyticsinc.com'):
    BASE_HTTP_PORT = 22100
    NUM_PROXIES = 300
    fh = open(fpath, 'w')
    for i in xrange(NUM_PROXIES):
        proxy = 'http://%s:%s' % (host, str(BASE_HTTP_PORT+i))
        fh.write(proxy+'\n')
    fh.close()
http_proxy_path = '/tmp/http_proxies.txt'
if not os.path.exists(http_proxy_path):
    _create_http_proxies_list(fpath=http_proxy_path)


def _check_if_proxies_available(http_proxy_path, timeout=10):
    if not os.path.exists(http_proxy_path):
        return False

    with open(http_proxy_path, 'r') as fh:
        proxies = [l.strip() for l in fh.readlines() if l.strip()]

    hosts = ['google.com', 'bing.com', 'ya.ru', 'yahoo.com']
    for h in hosts:
        prox = random.choice(proxies)
        try:
            requests.get(
                'http://'+h,
                proxies={'http': prox, 'https': prox},
                timeout=timeout
            )
            print('successfully fetched host %s using proxy %s' % (h, prox))
            return True
        except (ReqTimeout, ConnectionError):
            print('failed to fetch host %s using proxy %s' % (h, prox))
            pass  # got timeout - proxy not available
        except (ReqProxyError, SSLError, ContentDecodingError):
            print('proxy %s - failed to fetch host %s' % (prox, h))

if not os.path.exists('/tmp/_stop_proxies'):
    PROXY_LIST = os.path.join(CWD, 'http_proxies.txt')
    PROXY_LIST2 = '/tmp/http_proxies.txt'
    if not os.path.exists(PROXY_LIST) and os.path.exists(PROXY_LIST2):
        PROXY_LIST = PROXY_LIST2
    if (os.path.exists(PROXY_LIST)
            and not os.path.exists('/tmp/_disable_proxies')
            and _check_if_proxies_available(http_proxy_path)):
        log.msg('USING PROXIES')
        print('USING PROXIES')
        DOWNLOADER_MIDDLEWARES['product_ranking.randomproxy.RandomProxy'] = 100
    else:
        log.msg('NOT USING PROXIES')
        print('NOT USING PROXIES')

# shared CH and SC code
sys.path.append(os.path.join(CWD, '..', '..'))
sys.path.append(os.path.join(CWD, '..', '..', 'spiders_shared_code'))
