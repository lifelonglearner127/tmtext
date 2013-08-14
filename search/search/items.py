# Definition of the models for the scraped items

from scrapy.item import Item, Field

class SearchItem(Item):
    product_name = Field() # name of the search result product
    site = Field() # site result was found on
    product_url = Field() # url of result product page
    origin_url = Field() # original product url
