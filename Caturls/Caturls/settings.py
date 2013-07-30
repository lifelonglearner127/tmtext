# Scrapy settings for Caturls project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'Caturls'

SPIDER_MODULES = ['Caturls.spiders']
NEWSPIDER_MODULE = 'Caturls.spiders'
ITEM_PIPELINES = ['Caturls.pipelines.CaturlsPipeline']

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Caturls (+http://www.yourdomain.com)'
