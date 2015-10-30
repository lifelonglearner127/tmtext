class AmazoncaValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
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
        'transformator': [50, 300],
        'kaspersky total': [3, 50],
        'gold sold fold': [5, 200],  # spider should return from 5 to 200 products
        'yamaha drums midi': [5, 100],
        'black men shoes size 8 red': [5, 100],
        'antoshka': [5, 150],
        'apple ipod nano gold': [50, 300],
        'programming product best': [5, 100],
    }

test_url = {
    'http://www.amazon.ca/Vince-Camuto-Womens-Sleeve-Organza/dp/B00WMERBOA/ref=sr_1_4?ie=UTF8&qid=1444651527&sr=8-4&keywords=dress',

}