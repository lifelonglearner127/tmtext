class AmazonValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = ['model', 'brand', 'price', 'bestseller_rank',
                       'buyer_reviews']
    ignore_fields = [
        'is_in_store_only', 'is_out_of_stock', 'related_products', 'upc',
        'google_source_site', 'description', 'special_pricing'
    ]
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = True  # ... duplicated requests?
    ignore_log_filtered = True  # ... filtered requests?
    test_requests = {
        'abrakadabrasdafsdfsdf': 0,  # should return 'no products' or just 0 products
        'nothing_found_1234654654': 0,
        'samsung t9500 battery 2600 li-ion warranty': [30, 250],
        'water pump bronze inch apollo': [2, 30],
        'ceiling fan industrial white system': [5, 50],
        'kaspersky total': [20, 100],
        'car navigator garmin maps 44LM': [1, 20],
        'yamaha drums midi': [50, 300],
        'black men shoes size 8  red stripes': [40, 100],
        'car audio equalizer pioneer mp3': [20, 100]
    }

    test_urls = [
        'http://www.amazon.com/Fallout-Vault-Dwellers-Survival-Collectors/dp/0744016312/ref=sr_1_5/183-3389897-3704802?'
        's=books&ie=UTF8&qid=1438956241&sr=1-5&keywords=book',
        'http://www.amazon.com/pediped-Flex-Ann-Mary-Jane/dp/B00RY8466U/ref=lp_3420851011_1_1?s=apparel&ie=UTF8&'
        'qid=1439192177&sr=1-1',
        'http://www.amazon.com/gp/product/B0083KGXGY/ref=s9_hps_bw_g504_i4?pf_rd_m=ATVPDKIKX0DER&'
        'pf_rd_s=merchandised-search-7&pf_rd_r=1FDV0BPD0JEWQ012A20F&pf_rd_t=101&pf_rd_p=2008399862&pf_rd_i=1266092011',
        'http://www.amazon.com/gp/product/B00AEV8HI2/ref=s9_acsd_al_bw_ft_x_1_i?pf_rd_m=ATVPDKIKX0DER&'
        'pf_rd_s=merchandised-search-3&pf_rd_r=0CSB6BY1GNB9G23T6TB1&pf_rd_t=101&pf_rd_p=2155979882&pf_rd_i=468642',
        'http://www.amazon.com/Sierra-Tools-Battery-Operated-Liquid-Transfer/dp/B000HEBR3I/ref=lp_15707701_1_20?'
        's=automotive&ie=UTF8&qid=1439192599&sr=1-20',
        'http://www.amazon.com/Toddler-Pillow-13-Hypoallergenic-Guarantee/dp/B00KDKKD1I/ref=lp_1057794_1_20?'
        's=furniture&ie=UTF8&qid=1439193230&sr=1-20',
        'http://www.amazon.com/gp/product/B00PHNE4X4/ref=br_asw_pdt-2?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=desktop-7&'
        'pf_rd_r=021EWZ932J1KH41J3J8H&pf_rd_t=36701&pf_rd_p=2155610662&pf_rd_i=desktop',
        'http://www.amazon.com/gp/product/B00WREOEEA/ref=s9_hps_bw_g15_i6?pf_rd_m=ATVPDKIKX0DER&'
        'pf_rd_s=merchandised-search-7&pf_rd_r=1A00TDQQCY28VYPHYZBD&pf_rd_t=101&pf_rd_p=2155968262&pf_rd_i=5174',
        'http://www.amazon.com/gp/product/B00BXKET7Q/ref=s9_acss_bw_cg_luxt1_r5_c5?pf_rd_m=ATVPDKIKX0DER&'
        'pf_rd_s=merchandised-search-6&pf_rd_r=0JDRRHSS372VWSNWEFMD&pf_rd_t=101&pf_rd_p=2157928762&pf_rd_i=7175545011'
    ]