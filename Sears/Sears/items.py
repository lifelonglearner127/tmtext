# Definition of models for the scraped items

from scrapy.item import Item, Field

class SearsItem(Item):
    text = Field() # name of category
    url = Field() # url of category
    parent_text = Field() # name of parent category
    parent_url = Field() # url of parent category
    grandparent_text = Field() # name of grandparent category
    grandparent_url = Field() # url of grandparent category
    page_text = Field() # name of page (list is spread across many pages)
    page_url = Field() # url of page
    level = Field() # level of category in the nested list (from narrower to broader categories)
    special = Field() # is it a special category? (1 or nothing)