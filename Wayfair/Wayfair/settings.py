# Scrapy settings for Wayfair project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'Wayfair'

SPIDER_MODULES = ['Wayfair.spiders']
NEWSPIDER_MODULE = 'Wayfair.spiders'
ITEM_PIPELINES = ['Wayfair.pipelines.WayfairPipeline']

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Wayfair (+http://www.yourdomain.com)'
