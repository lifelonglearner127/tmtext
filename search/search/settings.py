# Scrapy settings for search project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'search'

SPIDER_MODULES = ['search.spiders']
NEWSPIDER_MODULE = 'search.spiders'
ITEM_PIPELINES = ['search.pipelines.SearchPipeline']


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'search (+http://www.yourdomain.com)'
