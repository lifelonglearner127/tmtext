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
        'http://www.homedepot.com/p/Kraftware-Fishnet-24-oz-Walnut-Insulated-Drinkware-Set-of-4-38024/203171306',
        'http://www.homedepot.com/p/Unbranded-Global-Goodwill-Jazz-23-oz-4-3-4-in-Mug-in-Pearl-1-Piece-849851027541/204615618',
        'http://www.homedepot.com/p/Carlisle-32-oz-SAN-Plastic-Stackable-Tumbler-in-Ruby-Case-of-48-553210/204658635',
        'http://www.homedepot.com/p/BonJour-Coffee-2-Piece-Insulated-Glass-Cappuccino-Cup-Set-51285/205450204',
        'http://www.homedepot.com/p/ORE-International-5-gal-Water-Bottle-in-Clear-WS50GH-48/206022555?MERCH=REC-_-NavPLPHorizontal1_rr-_-NA-_-206022555-_-N',
        'http://www.homedepot.com/p/The-Folding-Table-Cloth-6-ft-Table-Cloth-Made-for-Folding-Tables-Natural-3072NAT/203335976',
        'http://www.homedepot.com/p/Kraftware-Fishnet-Wedge-Placemat-in-Tan-Set-of-12-34139/203171295',
        'http://www.homedepot.com/p/Old-Dutch-13-in-Antique-Embossed-Victoria-Charger-Plates-Set-of-6-OS421/203757467',
        'http://www.homedepot.com/p/Unbranded-Kingston-and-Grace-13-in-x-18-in-Frame-Placemat-in-Brown-Set-of-12-QPR00961/206529322',
    }