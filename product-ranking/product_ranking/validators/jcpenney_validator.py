class JcpenneyValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = []
    ignore_fields = [
        'is_in_store_only', 'is_out_of_stock', 'related_products', 'upc',
        'google_source_site', 'description', 'special_pricing',
        'bestseller_rank', 'model',
    ]
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = True  # ... duplicated requests?
    ignore_log_filtered = True  # ... filtered requests?
    test_requests = {
        'sdfsdgdf': 0,  #+ should return 'no products' or just 0 products
        'benny benassi': 0,
        'water proof': [110, 210],
        'peace': [10, 70],
        'hot': [100, 300],
        'drink': [30, 130],
        'term': [30, 130],
        'tiny': [10, 80],
        'selling': [20, 100],
        'night': [40, 140],
    }

    test_urls = {
        '',
        '',
    }