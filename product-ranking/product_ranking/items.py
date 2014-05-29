# vim:fileencoding=UTF-8

from scrapy.item import Item, Field


class SiteProductItem(Item):
    # Search metadata.
    site = Field()          # String.
    search_term = Field()   # String.
    ranking = Field()       # Integer.
    total_matches = Field()  # Integer.
    results_per_page = Field()  # Integer.

    # Product data.
    title = Field()         # String.
    upc = Field()           # Integer.
    model = Field()         # String, alphanumeric code.
    url = Field()           # String, URL.
    image_url = Field()     # String, URL.
    description = Field()   # String with HTML tags.
    brand = Field()         # String.
    price = Field()         # String, number with currency sign.
    locale = Field()        # String.

    # Calculated data.
    search_term_in_title_partial = Field()  # Bool
    search_term_in_title_exactly = Field()  # Bool
    search_term_in_title_interleaved = Field()  # Bool