# Scrapy settings for Sears project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'Sears'

SPIDER_MODULES = ['Sears.spiders']
NEWSPIDER_MODULE = 'Sears.spiders'
ITEM_PIPELINES = ['Sears.pipelines.SearsPipeline']

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:24.0) Gecko/20100101 Firefox/24.0"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Sears (+http://www.yourdomain.com)'
