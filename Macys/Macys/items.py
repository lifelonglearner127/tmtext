# Definition of models for the scraped items

from scrapy.item import Item, Field

class CategoryItem(Item):
    url = Field() # url of category
    text = Field() # name of category
    parent_text = Field() # name of parent category
    parent_url = Field() # url of parent category
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