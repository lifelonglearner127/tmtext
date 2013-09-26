# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class TigerdirectItem(Item):
    url = Field()
    text = Field()
    parent_text = Field() # name of parent category
    parent_url = Field() # url of parent category
    grandparent_text = Field() # name of grandparent category
    grandparent_url = Field() # url of grandparent category
    level = Field() # level of category in the nested list (from narrower to broader categories)
    special = Field() # is it a special category? (1 or nothing)
    description_text = Field() # text of category description (if any)
    description_title = Field() # title of category description (if any)
    description_wc = Field() # number of words in description text, 0 if no description
    keyword_count = Field()
    keyword_density = Field()
    nr_products = Field() # number of items in the category
    department_text = Field() # name of the department it belongs to
    department_url = Field() # url of the department it belongs to
    department_id = Field() # unique id of the department it belongs to
