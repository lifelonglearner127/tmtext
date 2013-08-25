# Scrapy settings for Macys project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'Macys'

SPIDER_MODULES = ['Macys.spiders']
NEWSPIDER_MODULE = 'Macys.spiders'

ITEM_PIPELINES = ['Macys.pipelines.MacysPipeline']
DUPEFILTER_CLASS = 'scrapy.dupefilter.BaseDupeFilter'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Macys (+http://www.yourdomain.com)'
