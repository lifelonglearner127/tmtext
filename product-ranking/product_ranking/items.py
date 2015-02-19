# vim:fileencoding=UTF-8

import collections
import decimal

from scrapy.item import Item, Field


RelatedProduct = collections.namedtuple("RelatedProduct", ['title', 'url'])

BuyerReviews = collections.namedtuple(
    "BuyerReviews",
    ['num_of_reviews',  # int
     'average_rating',  # float
     'rating_by_star']  # dict, {star: num_of_reviews,}, like {1: 45, 2: 234}
)


valid_currency_codes = """AED AFN ALL AMD ANG AOA ARS AUD AWG AZN BAM BBD BDT
 BGN BHD BIF BMD BND BOB BOV BRL BSD BTN BWP BYR BZD CAD CDF CHE CHF CHW CLF
 CLP CNH CNY COP COU CRC CUC CUP CVE CZK DJF DKK DOP DZD EGP ERN ETB EUR FJD
 FKP GBP GEL GHS GIP GMD GNF GTQ GYD HKD HNL HRK HTG HUF IDR ILS INR IQD IRR
 ISK JMD JOD JPY KES KGS KHR KMF KPW KRW KWD KYD KZT LAK LBP LKR LRD LSL LTL
 LYD MAD MDL MGA MKD MMK MNT MOP MRO MUR MVR MWK MXN MXV MYR MZN NAD NGN NIO
 NOK NPR NZD OMR PAB PEN PGK PHP PKR PLN PYG QAR RON RSD RUB RWF SAR SBD SCR
 SDG SEK SGD SHP SLL SOS SRD SSP STD SYP SZL THB TJS TMT TND TOP TRY TTD TWD
 TZS UAH UGX USD USN USS UYI UYU UZS VEF VND VUV WST XAF XAG XAU XBA XBB XBC
 XBD XCD XDR XFU XOF XPD XPF XPT XSU XTS XUA XXX YER ZAR ZMW ZWD
""".split(' ')
valid_currency_codes = [c.strip() for c in valid_currency_codes if c.strip()]


class Price:

    price = None
    priceCurrency = None

    def __init__(self, priceCurrency, price):
        self.priceCurrency = priceCurrency
        if self.priceCurrency not in valid_currency_codes:
            raise ValueError('Invalid currency: %s' % priceCurrency)
        # Remove comma(s) in price string if needed (i.e: '1,254.09')
        self.price = decimal.Decimal(str(price).replace(',', ''))

    def __repr__(self):
        return u'%s(priceCurrency=%s, price=%s)' % (
            self.__class__.__name__,
            self.priceCurrency, format(self.price, '.2f')
        )

    def __str__(self):
        return self.__repr__()


def scrapy_price_serializer(value):
    """ This method is required to correctly dump values while using JSON
        output (otherwise we'd have "can not serialize to JSON" error).
        `value` can be a string, number, or a `Price` instance.
    :param value: str, float, int, or a `Price` instance
    :return: str
    """
    if isinstance(value, Price):
        return value.__str__()
    else:
        return value


class SiteProductItem(Item):
    # Search metadata.
    site = Field()          # String.
    search_term = Field()   # String.
    ranking = Field()       # Integer.
    total_matches = Field()  # Integer.
    results_per_page = Field()  # Integer.
    scraped_results_per_page = Field() # Integer.
    # Indicates whether this Item comes from scraping single product url
    is_single_result = Field() # Bool

    # Product data.
    title = Field()         # String.
    upc = Field()           # Integer.
    model = Field()         # String, alphanumeric code.
    url = Field()           # String, URL.
    image_url = Field()     # String, URL.
    description = Field()   # String with HTML tags.
    brand = Field()         # String.
    price = Field(serializer=scrapy_price_serializer)  # see Price obj
    locale = Field()        # String.
    # Dict of RelatedProducts. The key is the relation name.
    related_products = Field()
    # Available in-store only
    is_in_store_only = Field()
    # Out of stock
    is_out_of_stock = Field()
    # Feedback from the buyers (with ratings etc.)
    buyer_reviews = Field()  # see BuyerReviews obj

    # Calculated data.
    search_term_in_title_partial = Field()  # Bool
    search_term_in_title_exactly = Field()  # Bool
    search_term_in_title_interleaved = Field()  # Bool

    # For google.co.uk, google.com products
    google_source_site = Field()
