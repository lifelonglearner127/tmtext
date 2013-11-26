# Definition of the models for the scraped items

from scrapy.item import Item, Field

class SearchItem(Item):
    product_name = Field() # name of the search result product
    site = Field() # site result was found on
    product_url = Field() # url of result product page
    product_model = Field() # product model of product as extracted from its page or the results page (if found somewhere other that inside its name)
    product_brand = Field() # product brand as extracted from special element in product page
    origin_url = Field() # original product url
    origin_id = Field() # original (source) product id (for walmart products)

# items used in walmart_fullurls spider to match walmart ids to their product pages full URLs
class WalmartItem(Item):
	walmart_id = Field()
	walmart_short_url = Field() # like http://www/walmart.com/ip/<id>
	walmart_full_url = Field()