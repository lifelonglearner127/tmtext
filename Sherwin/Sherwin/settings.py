# Scrapy settings for Sherwin project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'Sherwin'

SPIDER_MODULES = ['Sherwin.spiders']
NEWSPIDER_MODULE = 'Sherwin.spiders'

ITEM_PIPELINES = ['Sherwin.pipelines.CommaSeparatedLinesPipeline']

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Sherwin (+http://www.yourdomain.com)'
