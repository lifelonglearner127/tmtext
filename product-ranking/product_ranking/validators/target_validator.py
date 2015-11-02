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
        'http://www.target.com/p/striped-ruched-midi-dress-mossimo/-/A-16860280#prodSlot=medium_1_1&term=dress',
        'http://www.target.com/p/woven-challis-maxi-dress-mossimo-supply-co/-/A-16645319#prodSlot=medium_1_7&term=dress',
        'http://www.target.com/p/women-s-woven-scallop-a-line-dress-isani/-/A-16711290#prodSlot=medium_1_13&term=dress',
        'http://www.target.com/p/women-s-shirt-dress-merona/-/A-17257480#prodSlot=medium_1_19&term=dress',
        'http://www.target.com/p/lattice-back-paisley-shift-dress-3hearts/-/A-18759199#prodSlot=medium_1_23&term=dress',
        'http://www.target.com/p/xhil-belted-shift-dress-rust/-/A-18781135#prodSlot=medium_1_34&term=dress'

    }