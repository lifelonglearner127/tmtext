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
        'zollinger atlas of surgical operations': [10, 50],
        'assassins creed golden edition': [180, 380],
        'ceiling fan industrial white system': [100, 400],
        'kaspersky total': [20, 150],
        'car navigator garmin maps 44LM': [1, 20],
        'yamaha drums midi': [50, 300],
        'black men shoes size 8  red stripes': [300, 500],
        'equalizer pioneer': [100, 400]
    }

    test_urls = [
        'https://www.amazon.com/Pioneer-TSW311S4-12-Inch-Champion-Equalizer/dp/B00O8B7BAO/ref=sr_1_3?ie=UTF8&qid=1473370036&sr=8-3&keywords=equalizer+pioneer',
        'http://www.amazon.com/pediped-Flex-Ann-Mary-Jane/dp/B00RY8466U/ref=lp_3420851011_1_1?s=apparel&ie=UTF8&qid=1439192177&sr=1-1',
        'http://www.amazon.com/gp/product/B0083KGXGY/ref=s9_hps_bw_g504_i4?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-7&pf_rd_r=1FDV0BPD0JEWQ012A20F&pf_rd_t=101&pf_rd_p=2008399862&pf_rd_i=1266092011',
        'https://www.amazon.com/LG-Electronics-55LB6300-55-Inch-1080p/dp/B00II6VW3M/ref=pd_sim_sbs_504_8?ie=UTF8&psc=1&refRID=M3YSYV77N18HZZ3JXMRD',
        'http://www.amazon.com/Sierra-Tools-Battery-Operated-Liquid-Transfer/dp/B000HEBR3I/ref=lp_15707701_1_20?s=automotive&ie=UTF8&qid=1439192599&sr=1-20',
        'http://www.amazon.com/Toddler-Pillow-13-Hypoallergenic-Guarantee/dp/B00KDKKD1I/ref=lp_1057794_1_20?s=furniture&ie=UTF8&qid=1439193230&sr=1-20',
        'http://www.amazon.com/gp/product/B00PHNE4X4/ref=br_asw_pdt-2?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=desktop-7&pf_rd_r=021EWZ932J1KH41J3J8H&pf_rd_t=36701&pf_rd_p=2155610662&pf_rd_i=desktop',
        'http://www.amazon.com/Calvin-Klein-Jeans-Medium-30x32/dp/B014EEIHPC',
        'http://www.amazon.com/gp/product/B00BXKET7Q/ref=s9_acss_bw_cg_luxt1_r5_c5?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-6&pf_rd_r=0JDRRHSS372VWSNWEFMD&pf_rd_t=101&pf_rd_p=2157928762&pf_rd_i=7175545011',
        'https://www.amazon.com/dp/B00MJMV0GU/ref=sxr_pa_click_within_right_3?pf_rd_m=ATVPDKIKX0DER&pf_rd_p=2329824862&pf_rd_r=JD0YSB3CNP61WXQQ4MTC&pd_rd_wg=myuU5&pf_rd_s=desktop-rhs-carousels&pf_rd_t=301&pd_rd_w=Byp4z&pf_rd_i=equalizer+pioneer&pd_rd_r=M0WCZPQG96B8RMVFXQS0&psc=1'
    ]