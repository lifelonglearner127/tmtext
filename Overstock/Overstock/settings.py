# Scrapy settings for Overstock project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'Overstock'

SPIDER_MODULES = ['Overstock.spiders']
NEWSPIDER_MODULE = 'Overstock.spiders'
ITEM_PIPELINES = ['Overstock.pipelines.OverstockPipeline']

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Overstock (+http://www.yourdomain.com)'
