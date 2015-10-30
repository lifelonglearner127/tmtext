class TargetValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = ['brand', 'price']
    ignore_fields = [
        'is_in_store_only', 'is_out_of_stock', 'related_products', 'upc',
        'google_source_site', 'description', 'special_pricing', "model",
        "bestseller_rank",
    ]
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = True  # ... duplicated requests?
    ignore_log_filtered = True  # ... filtered requests?
    test_requests = {
        'abrakadabrasdafsdfsdf': 0,  # should return 'no products' or just 0 products
        'nothing_found_1234654654': 0,
        'sold': [15, 150],
        'cola': [60, 210],
        'vacation': [50, 175],
        'sort': [7, 100],
        'navigator': [10, 110],
        'manager': [15, 130],
        'IPhone-6': [1, 50],
        'air conditioner': [60, 170],
    }

    test_urls = {
        '',
        '',

    }