# Scrapy settings for product_ranking project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

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
DOWNLOAD_DELAY = 0.5

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
ZERO_REVIEWS_VALUE = 0

# TODO: move away these emails settings
AMAZON_SES_KEY = "AKIAIB35OIAQMWDZ45GA"
AMAZON_SES_SECRET = "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"
AMAZON_SES_TO_ADDRESSES = [
    'Klaus Hoffmann <klaus.gehoffmann@gmail.com>',
    'Content Analytics Support Team<support@contentanalyticsinc.com>',
]
AMAZON_SES_BCC_ADDRESSES = []
# TODO: move away these Postgres settings
AUTO_TEST_POSTGRES_DB_CONN_STR = "dbname='page_ranking_auto_test' user='pruser' host='52.1.13.180' password='password'"

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
    HTTPCACHE_STORAGE = 'scrapy.contrib.httpcache.FilesystemCacheStorage'
    HTTPCACHE_EXPIRATION_SECS = 0  # forever
    HTTPCACHE_DIR = os.path.join(CWD, '..', '_http_cache')


try:
    from settings_local import *
except ImportError:
    pass