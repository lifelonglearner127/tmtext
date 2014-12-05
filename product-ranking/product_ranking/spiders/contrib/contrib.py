from decimal import Decimal, InvalidOperation
from itertools import ifilter

from product_ranking.items import BuyerReviews, Price
from product_ranking.spiders import cond_set_value


def unify_decimal(ignored, float_dots):
    """ Create a function to convert various floating point textual
    representations to it's equivalent that can be converted to float directly.

    Usage:
       unify_float([ignored, float_dots])(string_:str) -> string

    Arguments:
       ignored - list of symbols to be removed from string
       float_dots - decimal/real parts separator

    Raises:
       `ValueError` - resulting string cannot be converted to float.
    """

    def unify_float_wr(string_):
        try:
            result = ''.join(['.' if c in float_dots else c for c in
                              string_ if c not in ignored])
            return str(Decimal(result))
        except InvalidOperation:
            raise ValueError('Cannot convert to decimal')

    return unify_float_wr


def unify_price(currency_codes, currency_signs, unify_decimal,
                default_currency=None):
    """Convert textual price representation to `Price` object.

    Usage:
       unify_price(currency_codes, currency_signs, unify_float,
       [default_currency])(string_) -> Price

    Arguments:
       currency_codes - list of possible currency codes (like ['EUR', 'USD'])
       currency_signs - dictionary to convert substrings to currency codes
       unify_decimal - function to convert price part into decimal
       default_currency - default currency code

    Raises:
       `ValueError` - no currency code found and default_curreny is None.
    """

    def unify_price_wr(string_):
        string_ = string_.strip()
        sorted_ = sorted(currency_signs.keys(), None, len, True)
        sign = next(ifilter(string_.startswith, sorted_), '')
        string_ = currency_signs.get(sign, '') + string_[len(sign):]
        sorted_ = sorted(currency_codes, None, len, True)
        currency = next(ifilter(string_.startswith, sorted_), None)

        if currency is None:
            currency = default_currency
        else:
            string_ = string_[len(currency):]

        if currency is None:
            raise ValueError('Could not get currency code')

        float_string = unify_decimal(string_.strip())

        return Price(currency, float_string)

    return unify_price_wr


def populate_reviews(response, reviews):
    """ Populate `buyer_reviews` from list of user ratings as floats """
    if reviews:
        by_star = {rating: reviews.count(rating) for rating in reviews}
        reviews = BuyerReviews(num_of_reviews=len(reviews),
                               average_rating=sum(reviews) / len(reviews),
                               rating_by_star=by_star)
        cond_set_value(response.meta['product'], 'buyer_reviews', reviews)


def populate_reviews_from_regexp(regexp, response, string_):
    """ Populate `buyer_reviews` from regular expression.

     The regular expression should return a list of digits.
     """
    reviews = map(float, regexp.findall(string_))
    populate_reviews(response, reviews)