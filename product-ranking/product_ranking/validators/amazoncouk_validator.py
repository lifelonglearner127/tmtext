class AmazoncoukValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = ['model', 'brand', 'description', 'price', 'bestseller_rank']
    ignore_fields = [
        'is_in_store_only', 'is_out_of_stock', 'related_products', 'upc',
        'buyer_reviews', 'google_source_site', 'special_pricing',
    ]
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = False  # ... duplicated requests?
    ignore_log_filtered = False  # ... filtered requests?
    test_requests = {
        'abrakadabrasdafsdfsdf': 0,  # should return 'no products' or just 0 products
        'nothing_found_1234654654': 0,
        'nothing_fou': [5, 50],
        'kaspersky total': [5, 70],
        'gold sold fold': [5, 200],  # spider should return from 5 to 200 products
        'yamaha drums midi': [5, 100],
        'black men shoes size 8 red stripes': [5, 80],
        'antoshka': [5, 200],
        'apple ipod nano sold': [100, 300],
        'avira 2': [20, 300],
    }