# Scrapy settings for BJs project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'BJs'

SPIDER_MODULES = ['BJs.spiders']
NEWSPIDER_MODULE = 'BJs.spiders'
ITEM_PIPELINES = ['BJs.pipelines.BJsPipeline']

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'BJs (+http://www.yourdomain.com)'
