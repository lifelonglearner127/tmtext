#!/usr/bin/python
#
import unittest
from extract_walmart_data import WalmartScraper
from extract_tesco_data import TescoScraper
from extract_amazon_data import AmazonScraper
from extract_wayfair_data import WayfairScraper
from extract_pgestore_data import PGEStore
from extract_target_data import TargetScraper
from extract_bestbuy_data import BestBuyScraper
from tests_utils import StoreLogs
import requests
import sys
from lxml import html
import re
import json

# TODO: fix to work with refactored service code

# Test suite that thoroughly tests returned walmart data, its integrity and correctness
class WalmartData_test(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(WalmartData_test, self).__init__(*args, **kwargs)

        # read input urls from file
        try:
            with open("test_input.txt") as f:
                self.urls = f.read().splitlines()
        except Exception, e:
            print "No file to read input from"

        # service address
        self.address = "http://localhost/get_walmart_data/%s"

        # if there was no url as input, use this hardcoded list
        if not self.urls:
            self.urls = ['http://www.walmart.com/ip/Ocuvite-W-Lutein-Antioxidants-Zinc-Tablets-Vitamin-Mineral-Supplement-120-ct/1412', \
                        "http://www.walmart.com/ip/Kitchenaid-4.5-Mixer-White/3215"]

        
    # this is called before every test?
    def setUp(self):
        self.storage = StoreLogs()

    # test a requested data type was not null
    # for a request for a certain datatype
    # exceptions is a list of urls where the not-null rule doesn't apply (on a per-datatype basis)
    def notnull_template(self, datatype, exceptions=[]):
        for url in self.urls:
            if url in exceptions:
                continue
            print "On url ", url, " and datatype ", datatype
            response = requests.get(self.address % url + "?data=" + datatype).json()
            try:
                self.assertTrue(datatype in response)
                self.assertNotEqual(response[datatype], "")
                self.assertIsNotNone(response[datatype])
            # trick to change the exception message (add url)
            except AssertionError, e:
                raise AssertionError(str(e) + " -- on url " + url)


    # test data extracted from product page is never null
    def test_name_notnull(self):
        self.notnull_template("name")

    def test_keywords_notnull(self):
        self.notnull_template("keywords")

    def test_shortdesc_notnull(self):
        # # it can be empty
        # for url in self.urls:
        #     print "On url ", url
        #     response = requests.get(self.address % url + "?data=" + "short_desc").json()
        #     try:
        #         self.assertTrue("short_desc" in response)
        #         self.assertIsNotNone(response["short_desc"])
        #     except AssertionError, e:
        #         raise AssertionError(str(e) + " -- on url " + url)
        self.notnull_template("short_desc")


    def test_longdesc_notnull(self):
        self.notnull_template("long_desc")

    def test_price_notnull(self):
        exceptions = ["http://www.walmart.com/ip/28503697", "http://www.walmart.com/ip/28419207", \
        "http://www.walmart.com/ip/28419216"]
        self.notnull_template("price", exceptions)

    def test_price_format(self):
        for url in self.urls:
            response = requests.get(self.address % url + "?data=" + "price").json()
            price = response["price"]
            if price:
                try:
                    self.assertTrue(not not re.match("[0-9]+\.?[0-9]+", price))
                except AssertionError, e:
                    raise AssertionError(str(e) + " -- on url " + url)

    def extract_meta_price(self, url):
        WS = WalmartScraper(url)
        WS._extract_page_tree()
        tree = WS.tree_html
        meta_price = tree.xpath("//meta[@itemprop='price']/@content")
        if meta_price:
            return meta_price[0]
        else:
            return None

    def extract_page_price(self, url):
        WS = WalmartScraper(url)
        WS._extract_page_tree()
        tree = WS.tree_html
        page_price = "".join(tree.xpath("//*[contains(@class, 'camelPrice')]//text()")).strip()
        if page_price:
            return page_price
        else:
            return None

    # test extracted price matches the one in the meta tags
    def test_price_correct(self):
        for url in self.urls:
            print "On url ", url
            response = requests.get(self.address % url + "?data=" + "price").json()
            meta_price = response["price"]
            # remove $ sign and reduntant zeroes after .
            page_price = self.extract_page_price(url)
            if page_price:
                try:
                    price_clean = re.sub("\.[0]+", ".0", page_price[1:])
                    self.assertEqual(price_clean, meta_price)
                except AssertionError, e:
                    raise AssertionError(str(e) + " -- on url " + url)


    def test_Htags_notnull(self):
        self.notnull_template("htags")

    def test_pageload_notnull(self):
        self.notnull_template("load_time")

    # def test_reviews_notnull(self):
    #     # it can be empty or null
    #     for url in self.urls:
    #         print "On url ", url
    #         response = requests.get(self.address % url + "?data=" + "reviews").json()
    #         try:
    #             self.assertTrue("average_review" in response)
    #             self.assertTrue("total_reviews" in response)
    #         except AssertionError, e:
    #             raise AssertionError(str(e) + " -- on url " + url)

    def test_model_notnull(self):
        exceptions = ["http://www.walmart.com/ip/5027010"]
        self.notnull_template("model", exceptions)

    def extract_meta_model(self, url):
        WS = WalmartScraper(url)
        WS._extract_page_tree()
        tree = WS.tree_html
        meta_model = tree.xpath("//meta[@itemprop='model']/@content")
        if meta_model:
            return meta_model[0] if meta_model[0] else None
        else:
            return None

    # test extracted model number is the same as the one in meta tag
    def test_model_correct(self):
        for url in self.urls:
            print "On url ", url
            response = requests.get(self.address % url + "?data=" + "model").json()
            extracted_model = response["model"]
            meta_model = self.extract_meta_model(url)
            try:
                self.assertEqual(extracted_model, meta_model)
            except AssertionError, e:
                raise AssertionError(str(e) + " -- on url " + url)


    def test_features_notnull(self):
        self.notnull_template("features")

    def test_brand_notnull(self):
        self.notnull_template("brand")

    def test_title_notnull(self):
        self.notnull_template("title")

    def test_seller_notnull(self):
        for url in self.urls:
            print "On url ", url
            response = requests.get(self.address % url + "?data=" + "seller").json()

            try:
                self.assertTrue("seller" in response)
                self.assertNotEqual(response["seller"], "")
                self.assertIsNotNone(response["seller"])
                seller = response["seller"]
                self.assertTrue("owned" in seller)
                self.assertTrue("marketplace" in seller)

                self.assertIn(response["seller"]["owned"], [0, 1])
                self.assertIn(response["seller"]["marketplace"], [0, 1])
            
                self.assertTrue(response["seller"]["owned"] == 1 or response["seller"]["marketplace"] == 1)
            except AssertionError, e:
                raise AssertionError(str(e) + " -- on url " + url)


    # extract seller value from meta tag
    def extract_meta_seller(self, url):
        WS = WalmartScraper(url)
        WS._extract_page_tree()
        tree = WS.tree_html
        meta_seller = tree.xpath("//meta[@itemprop='seller']/@content")[0]
        return meta_seller

    # test if seller in meta tag matches seller returned by service
    def test_seller_correct(self):
        for url in self.urls:
            print "On url ", url
            response = requests.get(self.address % url + "?data=" + "seller").json()
            owned = response["seller"]["owned"]
            extract_meta_seller = self.extract_meta_seller(url)
            try:
                self.assertEqual(owned==1, extract_meta_seller=="Walmart.com")
            except AssertionError, e:
                raise AssertionError(str(e) + " -- on url " + url)        


    # test if extraction of reviews from product page (new version)
    # is consistent with extraction of reviews from separate request (old version)
    def test_reviews_correct(self):
        for url in self.urls:
            WS = WalmartScraper(url)
            print "On url ", url
            response = requests.get(self.address % url + "?data=" + "reviews").json()
            response2 = WS.reviews_for_url()

            try:
                self.assertEqual(u'reviews' in response and response[u'reviews'], 'total_reviews' in response2['reviews'] and response2['reviews']['total_reviews'])
            except AssertionError, e:
                try:
                    nr_reviews = float(str(response[u'reviews']['total_reviews']))
                    average_review = float(str(response[u'reviews']['average_review']))
                except Exception:
                    nr_reviews = average_review = None

                try:
                    nr_reviews2 = float(re.sub(",", "", str(response2['reviews']['total_reviews'])))
                    average_review2 = float(str(response2['reviews']['average_review']))
                except Exception:
                    nr_reviews2 = average_review2 = None


                self.storage.store_reviews_logs(url=url, error_message=str(e),\
                reviews_source=json.dumps(response), reviews_js=json.dumps(response2),\
                average_source=average_review, average_js=average_review2, \
                nr_reviews_source=nr_reviews, nr_reviews_js=nr_reviews2)                # raise AssertionError(str(e) + " -- on url " + url)



            if u'reviews' in response and response[u'reviews']:

                nr_reviews = str(response[u'reviews']['total_reviews'])
                average_review = str(response[u'reviews']['average_review'])

                nr_reviews2 = re.sub(",", "", str(response2['reviews']['total_reviews']))
                average_review2 = str(response2['reviews']['average_review'])
                if "." not in average_review2:
                    average_review2 += '.0'

                try:
                    self.assertEqual(nr_reviews, nr_reviews2)
                    self.assertEqual(average_review, average_review2)
                except AssertionError, e:
                    self.storage.store_reviews_logs(url=url, error_message=str(e),\
                    reviews_source=json.dumps(response), reviews_js=json.dumps(response2),\
                    average_source=float(average_review), average_js=float(average_review2), \
                    nr_reviews_source=float(nr_reviews), nr_reviews_js=float(nr_reviews2))
                    # raise AssertionError(str(e) + " -- on url " + url \
                    #     + "\nReviews old: " + str(response2) + ";\nReviews new: " + str(response) + "\n")

    # # def test_anchors_notnull(self)
    
# Generally test the service, for all available sites
class ServiceSimpleTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ServiceSimpleTest, self).__init__(*args, **kwargs)

        # service address
        self.address = "http://localhost/get_data?url=%s"

    # test all keys are in the response for simple (all-data) request for walmart
    def test_walmart_alldata(self):
        url = "http://www.walmart.com/ip/34335838"
        response = requests.get(self.address % url).json()
        print response

        DATA_TYPES = WalmartScraper.DATA_TYPES.keys() + WalmartScraper.DATA_TYPES_SPECIAL.keys()

        self.assertEqual(sorted(response.keys()), sorted(DATA_TYPES))

    # test all keys are in the response for simple (all-data) request for tesco
    def test_tesco_alldata(self):
        url = "http://www.tesco.com/direct/lindam-adjustable-back-seat-mirror/211-3189.prd"
        response = requests.get(self.address % url).json()
        print response

        DATA_TYPES = TescoScraper.DATA_TYPES.keys() + TescoScraper.DATA_TYPES_SPECIAL.keys()

        self.assertEqual(sorted(response.keys()), sorted(DATA_TYPES))

    # test all keys are in the response for simple (all-data) request for amazon
    def test_amazon_alldata(self):
        url = "http://www.amazon.com/dp/product/B0000AUWQ4"
        response = requests.get(self.address % url).json()
        print response

        DATA_TYPES = AmazonScraper.DATA_TYPES.keys() + AmazonScraper.DATA_TYPES_SPECIAL.keys()

        self.assertEqual(sorted(response.keys()), sorted(DATA_TYPES))        

    # test all keys are in the response for simple (all-data) request for wayfair
    def test_wayfair_alldata(self):
        url = "http://www.wayfair.com/daily-sales/p/Yard-Clean-Up-Essentials-Eden-Storage-Bench-in-Beige~KTR1108~E13616.html"
        response = requests.get(self.address % url).json()
        print response

        DATA_TYPES = WayfairScraper.DATA_TYPES.keys() + WayfairScraper.DATA_TYPES_SPECIAL.keys()

        self.assertEqual(sorted(response.keys()), sorted(DATA_TYPES))        

    # test all keys are in the response for simple (all-data) request for pgestore
    def test_pgestore_alldata(self):
        url = "http://www.pgestore.com/health/oral-care/toothpaste/crest-pro-health-cinnamon-toothpaste-6-oz/037000062240,default,pd.html"
        response = requests.get(self.address % url).json()
        print response

        DATA_TYPES = PGEStore.DATA_TYPES.keys() + PGEStore.DATA_TYPES_SPECIAL.keys()

        self.assertEqual(sorted(response.keys()), sorted(DATA_TYPES))        

    # # test all keys are in the response for simple (all-data) request for target
    # def test_target_alldata(self):
    #     url = "http://www.target.com/p/iphone-6-plus-16gb-gold-verizon-with-2-year-contract/-/A-16481467#prodSlot=_1_1"
    #     response = requests.get(self.address % url).json()
    #     print response

    #     DATA_TYPES = TargetScraper.DATA_TYPES.keys() + TargetScraper.DATA_TYPES_SPECIAL.keys()

    #     self.assertEqual(sorted(response.keys()), sorted(DATA_TYPES))        

    def test_bestbuy_alldata(self):
        url = "http://www.bestbuy.com/site/insignia-48-class-47-5-8-diag--led-1080p-60hz-hdtv/2563138.p?id=1219074400922&skuId=2563138"
        response = requests.get(self.address % url).json()
        print response

        DATA_TYPES = BestBuyScraper.DATA_TYPES.keys() + BestBuyScraper.DATA_TYPES_SPECIAL.keys()

        self.assertEqual(sorted(response.keys()), sorted(DATA_TYPES))        


if __name__=='__main__':
    unittest.main()