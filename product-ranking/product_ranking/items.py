# vim:fileencoding=UTF-8

from scrapy.item import Item, Field


class SiteProductItem(Item):
    search_term = Field()
    ranking = Field()
    total_matches = Field()

    title = Field()
    upc = Field()
    model = Field()
    url = Field()
    image_url = Field()
    description = Field()
    brand = Field()
    price = Field()
    rating = Field()
    locale = Field()
