class AmazonfrValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
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
        'nothing_found_1234654654': 0,
        'samsung t9500 battery 2600 li-ion warranty': [5, 175],
        'water pump mini': [5, 150],
        'ceiling fan industrial white system': [5, 50],
        'kaspersky total': [5, 75],
        'car navigator garmin maps 44LM': [1, 30],
        'yamaha drums midi': [1, 300],
        'black men shoes size 8 red': [20, 200],
        'car audio equalizer': [5, 150]
    }