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
        'black stone': [50, 250],
        'red ball': [5, 150],
        'green rose': [10, 100],
        'long term black': [1, 50],
        'yellow ion': [15, 100],
        'water ball': [3, 85],
        'levis 511': [10, 100],
    }

    test_urls = {

        'http://www.kohls.com/product/prd-2201224/chaps-surplice-faux-wrap-dress-womens.jsp?color=Heirloom%20Teal',
        'http://www.kohls.com/product/prd-2244381/chaps-georgette-empire-evening-gown-womens.jsp?color=Black',
        'http://www.kohls.com/product/prd-2196752/mudd-smocked-bodice-skater-dress-girls-6-16-girls-plus.jsp?color=Beach%20Floral',
        'http://www.kohls.com/product/prd-2206901/simply-vera-vera-wang-print-shift-dress-womens.jsp?color=Diva%20A',
        'http://www.kohls.com/product/prd-2040118/chaps-surplice-drape-front-full-length-dress-womens.jsp?color=Lakehouse%20Red',
        'http://www.kohls.com/product/prd-2363926/knitworks-girls-7-16-plus-size-fairisle-sweaterdress-scarf.jsp?color=Gray%20Blue',
        'http://www.kohls.com/product/prd-2209931/emily-west-girls-7-16-glitter-mesh-dress.jsp?color=Black%20Multi',
    }