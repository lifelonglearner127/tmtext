# Scrapy settings for Bloomingdales project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'Bloomingdales'

SPIDER_MODULES = ['Bloomingdales.spiders']
NEWSPIDER_MODULE = 'Bloomingdales.spiders'
ITEM_PIPELINES = ['Bloomingdales.pipelines.BloomingdalesPipeline']

# allow for duplicates
DUPEFILTER_CLASS = 'scrapy.dupefilter.BaseDupeFilter'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Bloomingdales (+http://www.yourdomain.com)'
