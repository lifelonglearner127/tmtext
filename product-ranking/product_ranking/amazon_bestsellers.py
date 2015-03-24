#
# See http://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=285
#

# list of departments and their categories
DEPARTMENTS_CATEGORIES = [
    'Books',
    'Home & Kitchen',
    'Electronics',
    'Sports & Outdoors',
    'Cell Phones & Accessories',
    'Collectibles & Fine Art',
    'Industrial & Scientific',
    'Automotive',
    'Clothing & Accessories',
    'Tools & Home Improvement',
    'Jewelry',
    'Office Products',
    'CDs & Vinyl',
    'Health & Personal Care',
    'Kindle Store',
    'Toys & Games',
    'Patio, Lawn & Garden',
    'Arts, Crafts & Sewing',
    'Beauty',
    'Movies & TV',
    'Grocery & Gourmet Food',
    'Pet Supplies',
    'Shoes',
    'Baby',
    'Musical Instruments',
    'Watches',
    'Appliances',
    'Software',
    'Video Games',
    'Apps & Games',
    'Kindle Accessories',
    'Gift Cards',
]


def amazon_parse_department(cats):
    for r in cats:
        cat = r.get('category')
        rank = r.get('rank')
        # first, try to match the full category
        if cat in DEPARTMENTS_CATEGORIES:
            return {cat: rank}
        cats = [_c.strip() for _c in cat.split('>')]
        if cats:
            if cats[0] in DEPARTMENTS_CATEGORIES:
                return {cats[0]: rank}
            if len(cats) > 1:
                if cats[1] in DEPARTMENTS_CATEGORIES:
                    return {cats[1]: rank}