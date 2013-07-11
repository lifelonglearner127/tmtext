# Definition of models for the scraped items

from scrapy.item import Item, Field

class AmazonItem(Item):
    url = Field()
    text = Field()
    parent_text = Field()
    level = Field()
