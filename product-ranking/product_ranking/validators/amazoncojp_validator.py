class AmazoncojpValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = ['model', 'brand', 'price', 'bestseller_rank',
                       'buyer_reviews']
    ignore_fields = [
        'is_in_store_only', 'is_out_of_stock', 'related_products', 'upc',
        'google_source_site', 'description', 'special_pricing'
    ]
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = True  # ... duplicated requests?
    ignore_log_filtered = True  # ... filtered requests?
    test_requests = {
        'abrakadabrasdafsdfsdf': 0,  # should return 'no products' or just 0 products
        'alhpa beta vinigretto': 0,
        'dandy united': [30, 300],
        'magi yellow': [5, 150],
        'Led Tv screen': [40, 300],
        'red ship coat': [10, 150],
        'trash smash': [20, 250],
        'all for PC now': [15, 150],
        'iphone blast': [10, 200],
        'genius electronics black': [5, 120],
        'batteries 330v': [40, 270]
    }