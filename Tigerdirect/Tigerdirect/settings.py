# Scrapy settings for Tigerdirect project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'Tigerdirect'

SPIDER_MODULES = ['Tigerdirect.spiders']
NEWSPIDER_MODULE = 'Tigerdirect.spiders'
ITEM_PIPELINES = ['Tigerdirect.pipelines.CommaSeparatedLinesPipeline']

# allow duplicates
DUPEFILTER_CLASS = 'scrapy.dupefilter.BaseDupeFilter'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Tigerdirect (+http://www.yourdomain.com)'
