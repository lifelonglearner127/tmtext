# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class SearsItem(Item):
    # define the fields for your item here like:
    # name = Field()
    text = Field()
    url = Field()
    parent_text = Field()
    parent_url = Field()
    page_text = Field()
    page_url = Field()