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
        if isinstance(price, unicode):
            price = price.encode('utf8')
        price = str(price)
        price = ''.join(s for s in price if s.isdigit() or s in [',', '.'])
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
        #import pdb; pdb.set_trace()
        if isinstance(rec, Price):
            converted = {u'price': float(rec.price),
                         u'currency': unicode(rec.priceCurrency),
                         u'name': None}
        elif isinstance(rec, dict):
            if rec.get('price', None) and rec.get('currency', None):
                converted = rec
            else:
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
    asin = Field()
    model = Field()  # String, alphanumeric code.
    sku = Field()  # product SKU, if any
    url = Field()  # String, URL.
    image_url = Field()  # String, URL.
    description = Field()  # String with HTML tags.
    brand = Field()  # String.
    price = Field(serializer=scrapy_price_serializer)  # see Price obj
    price_with_discount = Field(serializer=scrapy_price_serializer)
    marketplace = Field(serializer=scrapy_marketplace_serializer)  # see marketplace obj
    # See bugzilla #11492
    reseller_id = Field()

    locale = Field()  # String.
    # Dict of RelatedProducts. The key is the relation name.
    related_products = Field()
    # Dict of SponsoredLinks. The key is the relation name.
    sponsored_links = Field()
    # whether or not this product has been scraped coming from a sponsored link
    is_sponsored_product = Field()
    # Available in-store only
    is_in_store_only = Field()
    # Out of stock
    is_out_of_stock = Field()
    # Feedback from the buyers (with ratings etc.)
    buyer_reviews = Field()  # see BuyerReviews obj

    bestseller_rank = Field()
    department = Field()  # now for Amazons only; may change in the future
    category = Field()  # now for Amazons only; may change in the future
    categories = Field()  # now for amazon and maybe walmart
    categories_full_info = Field()  # for Walmart, see BZ 5828

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
    all_questions = Field()  # contains all questions (and answers if applicable)

    special_pricing = Field()  # True/False/None for TPC, Rollback; target, walmart

    price_subscribe_save = Field()  # Amazon
    price_original = Field()  # a price without discount (if applicable)

    variants = Field()

    shipping = Field()  # now for Walmart only; may change in the future
    shipping_included = Field()
    shipping_cost = Field(serializer=scrapy_price_serializer)

    img_count = Field()   # now for Walmart only; may change in the future
    video_count = Field()   # now for Walmart only; may change in the future

    _walmart_redirected = Field()  # for Walmart only; see #2126
    _walmart_original_id = Field()
    _walmart_current_id = Field()
    _walmart_original_price = Field()
    _walmart_original_oos = Field()  # oos = out of stock

    last_buyer_review_date = Field()

    response_code = Field()  # for 404, 500 etc.

    deliver_in = Field()  # now for Jet.com only;

    assortment_url = Field()

    _statistics = Field()  # for server and spider stats (RAM, CPU, disk etc.)

    no_longer_available = Field()  # no longer available, for Walmart
    not_found = Field()  # product not found (sometimes that's just 404 server error)

    shelf_name = Field()  # see https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c8
    shelf_path = Field()

    price_details_in_cart = Field()  # returns True if the price is available
                                     # only after you put the product in cart

    seller_ranking = Field()  # for Walmart

    _subitem = Field()

    minimum_order_quantity = Field() # Costco.com

    available_online = Field()
    available_store = Field()
    subscribe_and_save = Field() # Samclub.com

    walmart_url = Field()  # For amazon_top_categories_products spider, url of product on Walmart, if found
    walmart_category = Field()  # For amazon_top_categories_products spider, category of product on Walmart, if found
    walmart_exists = Field()  # For amazon_top_categories_products - True/False

    target_url = Field()  # For amazon_top_categories_products spider, url of product on Target, if found
    target_category = Field()  # For amazon_top_categories_products spider, category of product on Target, if found
    target_exists = Field()  # For amazon_top_categories_products - True/False

    price_club = Field(serializer=scrapy_price_serializer) # Samclub.com
    price_club_with_discount = Field(serializer=scrapy_price_serializer) # Samclub.com

    _jcpenney_has_size_range = Field()  # see BZ 9913
    level1 = Field()
    level2 = Field()
    level3 = Field()
    level4 = Field()
    level5 = Field()
    level6 = Field()
    level7 = Field()
    level8 = Field()
    level9 = Field()
    level10 = Field()

    dpci = Field()  # Target.com unique item identifier, example - 008-09-1171
    tcin = Field()  # Target.com online item number, for example - Online Item #: 16390220
    origin = Field()  # Target.com origin field, describes if item is imported or not

    temporary_unavailable = Field()  # 12696, returns true if 'We're having technical difficulties..' text on the page


class DiscountCoupon(Item):
    # Search metadata.
    site = Field()  # String.
    search_term = Field()  # String.
    ranking = Field()  # Integer.
    total_matches = Field()  # Integer.
    results_per_page = Field()  # Integer.
    scraped_results_per_page = Field()  # Integer.
    search_term_in_title_exactly = Field()
    search_term_in_title_partial = Field()
    search_term_in_title_interleaved = Field()
    _statistics = Field()

    category = Field()  # (Jewelry, Home, etc.)
    description = Field()  # (What it applies to (Riedel, Mattresses, etc.)
    start_date = Field()  # (10/15/2015)
    end_date = Field()  # (10/31/2015)
    discount = Field()  # (Discount value or Percentage (20% OFF)
    conditions = Field()  # (Applies to select items priced $50 or more...)
    promo_code = Field()  # (For ex: ALL4KIDS, 3BUYMORE, etc)


class CheckoutProductItem(Item):
    name = Field()
    id = Field()
    price = Field()             # In-cart Product Value
    price_on_page = Field()     # On-Page Product Value
    quantity = Field()
    requested_color = Field()
    requested_color_not_available = Field()
    requested_quantity_not_available = Field()  # True if quantity not available, else False
    no_longer_available = Field()  # True if item no longer available, else False
    not_found = Field()  # True if item not found, else False
    color = Field()
    order_subtotal = Field()    # Pre-tax & shipping Cart Value
    order_total = Field()       # Post-tax & shipping Cart Value
    promo_order_subtotal = Field()  # Pre-tax & shipping Cart Value - promo, ticket 10585
    promo_order_total = Field() # Post-tax & shipping Cart Value - promo, ticket 10585
    promo_price = Field() # # In-cart Product Value - promo, ticket 10585
    promo_code = Field() # In-cart Product Code, ticket 11599
    is_promo_code_valid = Field() # True if promo_code changed _order_total price, else False
    promo_invalid_message = Field() # Message returned by website if promo code is invalid, ticket #11720
    url = Field()


class ScreenshotItem(Item):
    url = Field()
    image = Field()
    via_proxy = Field()  # IP via webdriver
    site_settings = Field()  # site-specified settings that were activated (if any)
    creation_datetime = Field()

    def __repr__(self):
        return '[image data]'  # don't dump image data into logs
