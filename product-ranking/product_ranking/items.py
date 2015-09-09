# vim:fileencoding=UTF-8

import collections
import decimal

from scrapy.item import Item, Field


RelatedProduct = collections.namedtuple("RelatedProduct", ['title', 'url'])

#SponsoredLinks = collections.namedtuple("SponsoredLinks", ['ad_text', 'ad_url'])

LimitedStock = collections.namedtuple("LimitedStock",
                                      ['is_limited',   # bool
                                       'items_left'])  # int

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


class MarketplaceSeller:

    seller = None
    other_products = None

    def __init__(self, seller, other_products):
        self.seller = seller
        self.other_products = other_products
        if not self.other_products:
            self.other_products = None

    def __repr__(self):
        return {
            'seller': self.seller,
            'other_products': self.other_products
        }

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


def scrapy_marketplace_serializer(value):
    """ This method is required to correctly dump values while using JSON
        output (otherwise we'd have "can not serialize to JSON" error).
        `value` can be a string, number, or a `MarketplaceSeller` instance.
    :param value: str, url or a `MarketplaceSeller` instance
    :return: str
    """
    def conv_or_none(val, conv):
        return conv(val) if val is not None else val

    def get(rec, key, attr, conv):
        return conv_or_none(getattr(rec.get(key), attr, None), conv)

    try:
        iter(value)
    except TypeError:
        value = [value]
    result = []

    for rec in value:
        if isinstance(rec, Price):
            converted = {u'price': float(rec.price),
                         u'currency': unicode(rec.priceCurrency),
                         u'name': None}
        elif isinstance(rec, dict):
            converted = {
                u'price': get(rec, 'price', 'price', float),
                u'currency': get(rec, 'price', 'priceCurrency', unicode),
                u'name': conv_or_none(rec.get('name'), unicode),
                u'seller_type': rec.get('seller_type', None)
            }
        else:
            converted = {u'price': None, u'currency': None,
                         u'name': unicode(rec)}

        result.append(converted)
    return result


def scrapy_upc_serializer(value):
    """ This method is required to correctly dump values while using JSON
        output (otherwise we'd have "can not serialize to JSON" error).
        `value` can be a string, number, or a `MarketplaceSeller` instance.
    :param value: int, str
    :return: unicode
    """
    value = unicode(value)
    if len(value) > 12 and value.startswith('0'):
        return '0' + value.lstrip('0')
    return value


class SiteProductItem(Item):
    # Search metadata.
    site = Field()  # String.
    search_term = Field()  # String.
    ranking = Field()  # Integer.
    total_matches = Field()  # Integer.
    results_per_page = Field()  # Integer.
    scraped_results_per_page = Field()  # Integer.
    # Indicates whether this Item comes from scraping single product url
    is_single_result = Field()  # Bool

    # Product data.
    title = Field()  # String.
    upc = Field(serializer=scrapy_upc_serializer)  # Integer.
    model = Field()  # String, alphanumeric code.
    url = Field()  # String, URL.
    image_url = Field()  # String, URL.
    description = Field()  # String with HTML tags.
    brand = Field()  # String.
    price = Field(serializer=scrapy_price_serializer)  # see Price obj
    marketplace = Field(serializer=scrapy_marketplace_serializer)  # see marketplace obj
    locale = Field()  # String.
    # Dict of RelatedProducts. The key is the relation name.
    related_products = Field()
    # Dict of SponsoredLinks. The key is the relation name.
    sponsored_links = Field()
    # Available in-store only
    is_in_store_only = Field()
    # Out of stock
    is_out_of_stock = Field()
    # Feedback from the buyers (with ratings etc.)
    buyer_reviews = Field()  # see BuyerReviews obj

    bestseller_rank = Field()
    department = Field()  # now for Amazons only; may change in the future
    category = Field()  # now for Amazons only; may change in the future
    categories = Field() # now for amazon and maybe walmart

    # Calculated data.
    search_term_in_title_partial = Field()  # Bool
    search_term_in_title_exactly = Field()  # Bool
    search_term_in_title_interleaved = Field()  # Bool

    # For google.co.uk, google.com products
    # Should be provided in valid JSON format
    google_source_site = Field()

    is_mobile_agent = Field()  # if the spider was in the mobile mode

    limited_stock = Field()   # see LimitedStock obj

    prime = Field()  # amazon Prime program: Prime/PrimePantry/None

    is_pickup_only = Field()   # now for Walmart only; may change in the future
    shelf_page_out_of_stock = Field()  # now for Walmart only;

    date_of_last_question = Field()  # now for Walmart only
    recent_questions = Field()  # now for Walmart only; may change in the future

    special_pricing = Field()  # 1/0 for TPC, Rollback; target, walmart

    price_subscribe_save = Field()  # Amazon
    price_original = Field()  # a price without discount (if applicable)

    variants = Field()

    shipping = Field()  # now for Walmart only; may change in the future

    _walmart_redirected = Field()  # for Walmart only; see #2126
    _walmart_original_id = Field()
    _walmart_current_id = Field()
    _walmart_original_price = Field()
    _walmart_original_oos = Field()  # oos = out of stock

    last_buyer_review_date = Field()

    response_code = Field()  # for 404, 500 etc.

    deliver_in = Field()  # now for Jet.com only;

    assortment_url = Field()