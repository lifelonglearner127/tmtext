#!/usr/bin/python
#
import unittest
import requests
from crawler_service import SUPPORTED_SITES
from extract_walmart_data import WalmartScraper
from extract_tesco_data import TescoScraper
from extract_amazon_data import AmazonScraper
from extract_pgestore_data import PGEStore
from extract_wayfair_data import WayfairScraper
from extract_bestbuy_data import BestBuyScraper
from extract_kmart_data import KMartScraper
from extract_ozon_data import OzonScraper
from extract_vitadepot_data import VitadepotScraper
from extract_argos_data import ArgosScraper
from extract_homedepot_data import HomeDepotScraper
from extract_statelinetack_data import StateLineTackScraper
from extract_impactgel_data import ImpactgelScraper
from extract_chicksaddlery_data import ChicksaddleryScraper
from extract_bhinneka_data import BhinnekaScraper
from extract_maplin_data import MaplinScraper
from crawler_service import SUPPORTED_SITES


class ServiceScraperTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ServiceScraperTest, self).__init__(*args, **kwargs)

        # read input urls from file
        try:
            with open("test_input.txt") as f:
                self.urls = f.read().splitlines()
                self.urls_by_scraper = {}
                for site, scraper in SUPPORTED_SITES.items():
                    self.urls_by_scraper[site] = []
                    for url in self.urls:
                        site_scraper = scraper(url=url, bot=None)
                        if site_scraper.check_url_format():
                            self.urls_by_scraper[site].append(url)
        except Exception, e:
            print e

        # service address
        self.address = "http://localhost/get_data?url=%s"

    # template function:
    # test all keys are in the response for simple (all-data) request
    # for given input site
    def _test_alldata(self, site, url):
        response = requests.get(self.address % url).json()
        print response

        # initialize the scraper object for this specific site
        scraper = SUPPORTED_SITES[site]

        # all data types (keys) for this scraper
        DATA_TYPES = scraper.BASE_DATA_TYPES.keys()

        # flatten it into a list
        response_keys = response.keys()
        for top_key in ["product_info", "page_attributes", "reviews", "sellers", "classification"]:
            if top_key in response.keys():
                response_keys += response[top_key].keys()
                response_keys.remove(top_key)


        # verify all keys are in the output structure
        print "*********Verify all keys are in the output JSON of " + site + " scraper**********"
        print sorted(DATA_TYPES)
        self.assertEqual(sorted(response_keys), sorted(DATA_TYPES))

    # template function:
    # test requests for specific data (one type at once):
    # test the expected key is in the returned object (instead of an error message for example)
    def _test_specificdata(self, site, url):
        # initialize the scraper object for this specific site
        scraper = SUPPORTED_SITES[site]

        # all data types (keys) for this scraper
        DATA_TYPES = scraper.BASE_DATA_TYPES.keys()

        for data_type in DATA_TYPES:
            request_url = (self.address % url) + ("&data=%s" % data_type)
            print request_url
            response = requests.get(request_url).json()

            # flatten it into a list
            response_keys = response.keys()
            for top_key in ["product_info", "page_attributes", "reviews", "sellers", "classification"]:
                if top_key in response.keys():
                    response_keys += response[top_key].keys()
                    response_keys.remove(top_key)

            print "*********Check " + data_type + " field in the output JSON of " + site + " scraper**********"
            print response

            self.assertEqual(response_keys, [data_type])

    # template function:
    # test that returned data is not null
    # accepts "data" parameter that is a list
    # containing the types of data that should be tested
    # to be not null
    def _test_notnull(self, site, url, data=None):

        scraper = SUPPORTED_SITES[site]
        DATA_TYPES = scraper.BASE_DATA_TYPES.keys()

        response = requests.get(self.address % url).json()

        # set default value for data to assert not null for

        if not data:

            data = [
                "url", "date", "status", \
                "product_name", "product_title", "title_seo",\
                "model", "upc", "features", "feature_count", "model_meta", \
                "description", "long_description", \
                "image_count", "image_urls", \
                # "video_count", "pdf_count", \
                "webcollage", "htags", "loaded_in_seconds", \
                "keywords", \
                "price", \
                # "in_stores", "in_stores_only", "owned_out_of_stock", "marketplace_sellers", "marketplace_lowest_price", \
                "owned", "marketplace", \
                "categories", "category_name", "brand"
                ]

        # flatten it into flat dictionary
        response_flat = response
        for top_key in ["product_info", "page_attributes", "reviews", "sellers", "classification"]:
            if top_key in response.keys():
                response_flat.update(response[top_key])
                del response_flat[top_key]

        # check these data types were not null
        for data_type in data:
            if "error" in response_flat:
                print response_flat["error"], " for ", url
                break
            # if not response_flat[data_type]:
            #     print "None for ", url
            #     break
            print "Testing ", data_type, " for ", url, "... ", response_flat[data_type]
            self.assertTrue(data_type in response_flat)
            self.assertIsNotNone(response_flat[data_type])
            self.assertNotEquals(response_flat[data_type], "")
            self.assertNotEquals(response_flat[data_type], [])


    # test all keys are in the response for simple (all-data) request for walmart
    # (using template function)
    def test_walmart_alldata(self):
        for url in self.urls_by_scraper["walmart"]:
            self._test_alldata("walmart", url)

    # test requests for each specific type of data for walmart
    # (using template function)
    def test_walmart_specificdata(self):
        for url in self.urls_by_scraper["walmart"]:
            self._test_specificdata("walmart", url)

    # test all keys are in the response for simple (all-data) request for tesco
    # (using template function)
    def test_tesco_alldata(self):
        for url in self.urls_by_scraper["tesco"]:
            self._test_alldata("tesco", url)

    # test requests for each specific type of data for tesco
    # (using template function)
    def test_tesco_specificdata(self):
        for url in self.urls_by_scraper["tesco"]:
            self._test_specificdata("tesco", url)

    # test all keys are in the response for simple (all-data) request for amazon
    # (using template function)
    def test_amazon_alldata(self):
        for url in self.urls_by_scraper["amazon"]:
            self._test_alldata("amazon", url)

    # test requests for each specific type of data for amazon
    # (using template function)
    def test_amazon_specificdata(self):
        for url in self.urls_by_scraper["amazon"]:
            self._test_specificdata("walmart", url)

    # test all keys are in the response for simple (all-data) request for wayfair
    # (using template function)
    def test_wayfair_alldata(self):
        for url in self.urls_by_scraper["wayfair"]:
            self._test_alldata("wayfair", url)

    # test requests for each specific type of data for wayfair
    # (using template function)
    def test_wayfair_specificdata(self):
        for url in self.urls_by_scraper["wayfair"]:
            self._test_specificdata("wayfair", url)

    # test all keys are in the response for simple (all-data) request for pgestore
    # (using template function)
    def test_pgestore_alldata(self):
        for url in self.urls_by_scraper["pgestore"]:
            self._test_alldata("pgestore", url)

    # test requests for each specific type of data for pgestore
    # (using template function)
    def test_pgestore_specificdata(self):
        for url in self.urls_by_scraper["pgestore"]:
            self._test_specificdata("pgestore", url)

    # # test all keys are in the response for simple (all-data) request for target
    # # (using template function)
    # def test_target_alldata(self):
    #     self._test_alldata("target", "http://www.target.com/p/iphone-6-plus-16gb-gold-verizon-with-2-year-contract/-/A-16481467#prodSlot=_1_1")

    # test all keys are in the response for simple (all-data) request for bestbuy
    # (using template function)
    def test_bestbuy_alldata(self):
        for url in self.urls_by_scraper["bestbuy"]:
            self._test_alldata("bestbuy", url)

    # test requests for each specific type of data for bestbuy
    # (using template function)
    def test_bestbuy_specificdata(self):
        for url in self.urls_by_scraper["bestbuy"]:
            self._test_specificdata("bestbuy", url)

    # test all keys are in the response for simple (all-data) request for statelinetack
    # (using template function)
    def test_statelinetack_alldata(self):
        for url in self.urls_by_scraper["statelinetack"]:
            self._test_alldata("statelinetack", url)

    # test requests for each specific type of data for statelineattack
    # (using template function)
    def test_statelinetack_specificdata(self):
        for url in self.urls_by_scraper["statelinetack"]:
            self._test_specificdata("statelinetack", url)

    # test all keys are in the response for simple (all-data) request for homedepot
    # (using template function)
    def test_homedepot_alldata(self):
        for url in self.urls_by_scraper["homedepot"]:
            self._test_alldata("homedepot", url)

    # test requests for each specific type of data for homedepot
    # (using template function)
    def test_homedepot_specificdata(self):
        for url in self.urls_by_scraper["homedepot"]:
            self._test_specificdata("homedepot", url)

if __name__=='__main__':
    unittest.main()