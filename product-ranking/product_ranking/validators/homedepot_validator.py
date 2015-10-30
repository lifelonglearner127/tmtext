class HomedepotValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = ['brand', 'price']
    ignore_fields = [
        'is_in_store_only', 'is_out_of_stock', 'related_products', 'upc',
        'google_source_site', 'description', 'special_pricing',
        'bestseller_rank',
    ]
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = True  # ... duplicated requests?
    ignore_log_filtered = True  # ... filtered requests?
    test_requests = {
        'sdfsdgdf': 0,  # should return 'no products' or just 0 products
        'benny benassi': 0,
        'red car': [20, 150],
        'red stone': [40, 150],
        'musci': [110, 210],
        'funky': [10, 110],
        'bunny': [7, 90],
        'soldering iron': [30, 120],
        'burger': [1, 40],
        'hold': [30, 200],
    }

    test_urls = {
        '',
        '',
        '',
    }