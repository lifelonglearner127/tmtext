# Definition of models for the scraped items

from scrapy.item import Item, Field

class BestbuyItem(Item):
    url = Field() # url of category
    text = Field() # name of category
    parent_url = Field() # url of parent category (if any)
    parent_text = Field() # name of parent category (if any)
    grandparent_url = Field() # url of grandparent category (if any)
    grandparent_text = Field() # name of grandparent category (if any)
    level = Field() # level of category in the nested list (from narrower to broader categories)
    special = Field() # is it a special category? (1 or nothing)
