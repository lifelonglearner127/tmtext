# Definition of the models for the scraped items

from scrapy.item import Item, Field

class SearchItem(Item):
    name = Field()
