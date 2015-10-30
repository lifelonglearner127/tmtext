class MaplinValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = ['brand', 'limited_stock']
    ignore_fields = [
        'is_in_store_only', 'is_out_of_stock', 'related_products', 'upc',
        'google_source_site', 'special_pricing',
        'bestseller_rank', 'model', 'description'
    ]
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = True  # ... duplicated requests?
    ignore_log_filtered = True  # ... filtered requests?
    test_requests = {
        'sdfsdgdf': 0,  # should return 'no products' or just 0 products
        'benny benassi': 0,
        'red car': [20, 80],
        'stone': [50, 120],
        'ball': [5, 150],
        'rose': [10, 70],
        'long term black': [1, 12],
        'selling': [15, 40],
        'water proof': [50, 108],
        'long night': [30, 90],
    }

    test_urls = {

        '',
        '',
    }