# Scrapy settings for product_ranking project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
from scrapy import log

BOT_NAME = 'product_ranking'

SPIDER_MODULES = ['product_ranking.spiders']
NEWSPIDER_MODULE = 'product_ranking.spiders'

ITEM_PIPELINES = {
    'product_ranking.pipelines.CutFromTitleTagsAndReturnStringOnly': 300,
    'product_ranking.pipelines.AddSearchTermInTitleFields': 300,
    'product_ranking.pipelines.CheckGoogleSourceSiteFieldIsCorrectJson': 400,
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'product_ranking (+http://www.yourdomain.com)'

# Delay between requests not to be blocked (seconds).
DOWNLOAD_DELAY = 0.1

#AmazonFresh mapping locations and market place id
AMAZONFRESH_LOCATION = {
    "southern_cali": "A241IQ0793UAL2",
    "northern_cali": "A3FX2TOAMS7SFL",
    "seattle": "A83PXQN2224PA"
}

if not 'EXTENSIONS' in globals():
    EXTENSIONS = {}
EXTENSIONS['product_ranking.extensions.StatsCollector'] = 500

# memory limit
EXTENSIONS['scrapy.contrib.memusage.MemoryUsage'] = 500
MEMUSAGE_LIMIT_MB = 768
MEMUSAGE_ENABLED = True


# redefine log foramtter. DropItem exception provided with ERROR level
LOG_FORMATTER = 'product_ranking.pipelines.PipelineFormatter'

# Value to use for buyer_reviews if no reviews found
ZERO_REVIEWS_VALUE = [0, 0.0, {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}]


# TODO: move out from this file! should be set dynamically in the __init__ method of the BaseValidator class
# The piece of code below is awful, need to get rid of it asap.
# I have warned you. Better don't look there at all.
import sys
import os

CWD = os.path.dirname(os.path.abspath(__file__))

_args_names = [arg.split('=')[0] if '=' in arg else arg for arg in sys.argv]
if 'validate' in _args_names:
    ITEM_PIPELINES = {
        'product_ranking.validation.ValidatorPipeline': 100,
    }

if 'enable_cache' in _args_names:
    HTTPCACHE_ENABLED = True
    HTTPCACHE_POLICY = 'scrapy.contrib.httpcache.DummyPolicy'
    HTTPCACHE_STORAGE = 'product_ranking.cache.CustomFilesystemCacheStorage'
    HTTPCACHE_EXPIRATION_SECS = 0  # forever
    HTTPCACHE_DIR = os.path.join(CWD, '..', '_http_cache')


try:
    from settings_local import *
except ImportError:
    pass

# RANDOM PROXY SETTINGS
# Retry many times since proxies often fail
RETRY_TIMES = 15
# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408]

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 90,
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
}

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


PROXY_LIST = os.path.join(CWD, 'http_proxies.txt')
PROXY_LIST2 = '/tmp/http_proxies.txt'
if not os.path.exists(PROXY_LIST) and os.path.exists(PROXY_LIST2):
    PROXY_LIST = PROXY_LIST2
if os.path.exists(PROXY_LIST):
    log.msg('USING PROXIES')
    DOWNLOADER_MIDDLEWARES['product_ranking.randomproxy.RandomProxy'] = 100
else:
    log.msg('NOT USING PROXIES')