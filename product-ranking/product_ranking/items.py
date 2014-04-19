# vim:fileencoding=UTF-8

from scrapy.item import Item, Field


class SiteProductItem(Item):
    search_term = Field()   # String.
    ranking = Field()       # Integer.
    total_matches = Field()  # Integer.

    title = Field()         # String.
    upc = Field()           # Integer.
    model = Field()         # String, alphanumeric code.
    url = Field()           # String, URL.
    image_url = Field()     # String, URL.
    description = Field()   # String with HTML tags.
    brand = Field()         # String.
    price = Field()         # String, number with currency sign.
    rating = Field()        # Tuple of 2 integers, numerator and denominator.
    locale = Field()        # String.
