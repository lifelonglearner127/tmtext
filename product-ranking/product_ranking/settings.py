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
MEMUSAGE_LIMIT_MB = 256
MEMUSAGE_ENABLED = True

# TODO: move out from this file! should be set dynamically in the __init__ method of the BaseValidator class
# The piece of code below is awful, need to get rid of it asap.
# I have warned you. Better don't look there at all.
import sys
_args_names = [arg.split('=')[0] if '=' in arg else arg for arg in sys.argv]
if 'validate' in _args_names:
    ITEM_PIPELINES = {
        'product_ranking.validation.ValidatorPipeline': 100,
    }

try:
    from settings_local import *
except ImportError:
    pass