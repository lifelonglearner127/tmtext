# Scrapy settings for Newegg project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'Newegg'

SPIDER_MODULES = ['Newegg.spiders']
NEWSPIDER_MODULE = 'Newegg.spiders'

ITEM_PIPELINES = ['Newegg.pipelines.NeweggPipeline']

# # allow duplicates
#DUPEFILTER_CLASS = 'scrapy.dupefilter.BaseDupeFilter'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Newegg (+http://www.yourdomain.com)'
