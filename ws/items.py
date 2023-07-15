from scrapy.item import Item, Field


class BookItem(Item):
    url = Field()
    title = Field()
    upc = Field()
    product_type = Field()
    price_excl_tax = Field()
    price_incl_tax = Field()
    tax = Field()
    price = Field()
    availability = Field()
    num_of_reviews = Field()
    num_of_stars = Field()
    category = Field()
    description = Field()
