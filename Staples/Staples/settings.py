# Scrapy settings for Staples project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'Staples'

SPIDER_MODULES = ['Staples.spiders']
NEWSPIDER_MODULE = 'Staples.spiders'
ITEM_PIPELINES = ['Staples.pipelines.StaplesPipeline']


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Staples (+http://www.yourdomain.com)'
