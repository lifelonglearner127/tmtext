# Scrapy settings for Walmart project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'Walmart'

SPIDER_MODULES = ['Walmart.spiders']
NEWSPIDER_MODULE = 'Walmart.spiders'
ITEM_PIPELINES = ['Walmart.pipelines.WalmartPipeline']
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Walmart (+http://www.yourdomain.com)'
