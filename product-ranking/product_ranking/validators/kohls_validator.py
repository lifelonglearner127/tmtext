class KohlsValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = ['brand']
    ignore_fields = [
        'is_in_store_only', 'is_out_of_stock', 'related_products', 'upc',
        'google_source_site', 'special_pricing', 'ranking',
        'bestseller_rank', 'model', 'image_url'
    ]
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = True  # ... duplicated requests?
    ignore_log_filtered = True  # ... filtered requests?
    test_requests = {
        'sdfsdgdf': 0,  # should return 'no products' or just 0 products
        'benny benassi': 0,
        'red car': [100, 200],
        'black stone': [50, 200],
        'red ball': [5, 150],
        'green rose': [10, 100],
        'long term black': [1, 50],
        'yellow ion': [15, 100],
        'water proof': [50, 85],
        'long night': [30, 200],
    }

    test_urls = {

        '',
        '',
    }