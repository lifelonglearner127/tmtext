# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class CategoryItem(Item):
    # define the fields for your item here like:
    # name = Field()
    page = Field()
    url = Field()
    text = Field()
    parent_text = Field()
    parent_url = Field()

class ProductItem(Item):
	url = Field() # url of product page
	list_name = Field() # name of product - from bestsellers list
	product_name = Field() # name of product - from product page
	page_title = Field() # title (title tag text) of product page
	department = Field() # department of product - its name
	price = Field() # price of product - a string like "29.5$"
	listprice = Field() # "list price" of product - a string like "29.5$"
	rank = Field() # rank of the product in the bestsellers list
	SKU = Field() # SKU code of product (where available)
	UPC = Field() # UPC code of product (where available)