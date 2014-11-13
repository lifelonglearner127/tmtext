import os


CWD = os.path.dirname(os.path.abspath(__file__))
BRANDS = ()


def _load_brands(fname):
    """ Fills the global BRANDS variable """
    global BRANDS, CWD
    if BRANDS:  # don't perform expensive load operations
        return
    fname = os.path.join(CWD, fname)
    with open(fname, 'r') as fh:
        BRANDS = fh.readlines()
    BRANDS = [b.strip().lower() for b in BRANDS if b.strip()]
    BRANDS = set(BRANDS)  # set lookup is faster than list lookup


def _brand_in_list(brand):
    """ Utility method to check if the given brand is in the list """
    global BRANDS
    return brand.lower() in BRANDS


def guess_brand_from_first_words(text, fname='brands.list', max_words=7):
    """ Tries to guess the brand in the given text, assuming that the
         given text starts with the brand name.
        Example: Apple Iphone 16GB
        Should normally return: Apple
    :param text: str containing brand
    :param max_words: int, longest brand possible
    :return: str or None
    """
    global BRANDS
    _load_brands(fname)
    # prepare the data
    text = text.strip().replace('  ', ' ')
    # take `max_words` first words; `max_words`-1; `max_words`-2; and so on
    for cur_words in list(reversed(range(max_words)))[0:-1]:
        partial_brand = text.split(' ')[0:cur_words]
        partial_brand = ' '.join(partial_brand)
        if _brand_in_list(partial_brand):
            return partial_brand
