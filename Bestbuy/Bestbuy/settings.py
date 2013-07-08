# Scrapy settings for Bestbuy project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'Bestbuy'

SPIDER_MODULES = ['Bestbuy.spiders']
NEWSPIDER_MODULE = 'Bestbuy.spiders'
ITEM_PIPELINES = ['Bestbuy.pipelines.BestbuyPipeline']

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Bestbuy (+http://www.yourdomain.com)'
