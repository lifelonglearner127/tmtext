# Scrapy settings for Toysrus project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'Toysrus'

SPIDER_MODULES = ['Toysrus.spiders']
NEWSPIDER_MODULE = 'Toysrus.spiders'
ITEM_PIPELINES = ['Toysrus.pipelines.ToysrusPipeline']

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Toysrus (+http://www.yourdomain.com)'
