#!/usr/bin/python
import os
import sys

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CWD, '..'))

from flask import Flask, jsonify, abort, request
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
from extract_target_data import TargetScraper
from extract_chicago_data import ChicagoScraper
from extract_samsclub_data import SamsclubScraper
from extract_babysecurity_data import BabysecurityScraper
from extract_staples_data import StaplesScraper
from extract_soap_data import SoapScraper
from extract_drugstore_data import DrugstoreScraper
from extract_staplesadvantage_data import StaplesAdvantageScraper
from extract_souq_data import SouqScraper
from extract_freshdirect_data import FreshDirectScraper
from extract_peapod_data import PeapodScraper
from extract_quill_data import QuillScraper
from extract_hersheys_data import HersheysScraper
from extract_freshamazon_data import FreshAmazonScraper
from extract_george_data import GeorgeScraper
from extract_bloomingdales_data import BloomingdalesScraper
from extract_macys_data import MacysScraper
from extract_frys_data import FrysScraper
from extract_newegg_data import NeweggScraper
from extract_costco_data import CostcoScraper
from extract_proswimwear_data import ProswimwearScraper
from extract_amazonde_data import AmazonDEScraper
from extract_ulta_data import UltaScraper
from extract_asda_data import AsdaScraper
from extract_kohls_data import KohlsScraper
from extract_jcpenney_data import JcpenneyScraper
from extract_amazoncn_data import AmazonCNScraper
from extract_wiggle_data import WiggleScraper
from extract_snapdeal_data import SnapdealScraper
from extract_walmartca_data import WalmartCAScraper
from extract_marksandspencer_data import MarksAndSpencerScraper
from extract_nextcouk_data import NextCoUKScraper
from extract_amazonin_data import AmazonINScraper
from extract_uniqlo_data import UniqloScraper
from extract_deliverywalmart_data import DeliveryWalmartScraper
from extract_flipkart_data import FlipkartScraper
from extract_pepperfry_data import PepperfryScraper
from extract_cvs_data import CVSScraper
from extract_hairshop24_data import HairShop24Scraper
from extract_hagelshop_data import HagelShopScraper
from extract_levi_data import LeviScraper
from extract_dockers_data import DockersScraper
from extract_houseoffraser_data import HouseoffraserScraper
from extract_schuh_data import SchuhScraper
from extract_boots_data import BootsScraper
from extract_clarkscouk_data import ClarksCoUkScraper


from urllib2 import HTTPError
import datetime
import logging
from logging import StreamHandler
import re
import json

app = Flask(__name__)

# dictionary containing supported sites as keys
# and their respective scrapers as values
SUPPORTED_SITES = {
                    "amazon" : AmazonScraper,
                    "bestbuy" : BestBuyScraper,
                    "homedepot" : HomeDepotScraper,
                    "statelinetack" : StateLineTackScraper,
                    "tesco" : TescoScraper,
                    "walmart" : WalmartScraper,
                    "argos": ArgosScraper,
                    "kmart" : KMartScraper,
                    "ozon" : OzonScraper,
                    "pgestore" : PGEStore,
                    "pgshop" : PGEStore,
                    "vitadepot": VitadepotScraper,
                    "wayfair" : WayfairScraper,
                    "impactgel" : ImpactgelScraper,
                    "chicksaddlery" : ChicksaddleryScraper,
                    "bhinneka" : BhinnekaScraper,
                    "maplin" : MaplinScraper,
                    "hersheysstore" : HersheysScraper,
                    "target" : TargetScraper,
                    "chicago" : ChicagoScraper,
                    "samsclub" : SamsclubScraper,
                    "babysecurity" : BabysecurityScraper,
                    "staples" : StaplesScraper,
                    "soap" : SoapScraper,
                    "drugstore" : DrugstoreScraper,
                    "staplesadvantage" : StaplesAdvantageScraper,
                    "freshamazon" : FreshAmazonScraper,
                    "souq": SouqScraper,
                    "freshdirect" : FreshDirectScraper,
                    "quill" : QuillScraper,
                    "george" : GeorgeScraper,
                    "peapod" : PeapodScraper,
                    "bloomingdales" : BloomingdalesScraper,
                    "macys": MacysScraper,
                    "frys": FrysScraper,
                    "newegg": NeweggScraper,
                    "costco": CostcoScraper,
                    "proswimwear": ProswimwearScraper,
                    "amazonde": AmazonDEScraper,
                    "ulta": UltaScraper,
                    "groceries": AsdaScraper,
                    "kohls": KohlsScraper,
                    "jcpenney": JcpenneyScraper,
                    "amazoncn": AmazonCNScraper,
                    "wiggle": WiggleScraper,
                    "snapdeal": SnapdealScraper,
                    "walmartca": WalmartCAScraper,
                    "marksandspencer": MarksAndSpencerScraper,
                    "nextcouk": NextCoUKScraper,
                    "amazonin": AmazonINScraper,
                    "uniqlo": UniqloScraper,
                    "deliverywalmart": DeliveryWalmartScraper,
                    "flipkart": FlipkartScraper,
                    "pepperfry": PepperfryScraper,
                    "cvs": CVSScraper,
                    "hairshop24": HairShop24Scraper,
                    "hagelshop": HagelShopScraper,
                    "levi": LeviScraper,
                    "dockers": DockersScraper,
                    "houseoffraser": HouseoffraserScraper,
                    "schuh": SchuhScraper,
                    "boots": BootsScraper,
                    "clarkscouk": ClarksCoUkScraper
                    }

# add logger
# using StreamHandler ensures that the log is sent to stderr to be picked up by uwsgi log
fh = StreamHandler()
fh.setLevel(logging.DEBUG)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(fh)

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv

class GatewayError(Exception):
    status_code = 502

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv

# validate input and raise exception with message for client if necessary
def check_input(url, is_valid_url, invalid_url_message=""):
    # TODO: complete these error messages with more details specific to the scraped site
    if not url:
        raise InvalidUsage("No input URL was provided.", 400)

    if not is_valid_url:
        try:
            error_message = "Invalid URL: " + str(url) + " " + str(invalid_url_message)
        except UnicodeEncodeError:
            error_message = "Invalid URL: " + url.encode("utf-8") + str(invalid_url_message)
        raise InvalidUsage(error_message, 400)

# infer domain from input URL
def extract_domain(url):
    if 'chicago.doortodoororganics.com' in url:
        # for chicago scraper
        # https://chicago.doortodoororganics.com/shop/products/rudis-white-hamburger-buns
        return 'chicago'
    if 'fresh.amazon.com' in url:
        # for freshamazon scraper
        return 'freshamazon'
    if 'uae.souq.com' in url:
        # for souq scraper
        # http://uae.souq.com/ae-en/samsung-galaxy-s3-mini-i8190-8gb-3g-+-wifi-white-4750807/i/
        return 'souq'
    if 'direct.asda.com' in url:
        return 'george'
    if 'costco.com' in url:
        return 'costco'
    if 'amazon.de' in url:
        return 'amazonde'
    if 'amazon.cn' in url:
        return 'amazoncn'
    if 'amazon.in' in url:
        return 'amazonin'
    if 'groceries.asda.com' in url:
        return 'groceries'
    if 'walmart.ca' in url:
        return 'walmartca'
    if 'next.co.uk' in url:
        return 'nextcouk'
    if 'delivery.walmart' in url:
        return "deliverywalmart"
    if 'hair-shop24' in url:
        return "hairshop24"
    if 'hagel-shop' in url:
        return "hagelshop"
    if "www.levi.com" in url:
        return "levi"
    if "www.boots.com" in url:
        return "boots"
    if "www.clarks.co.uk" in url:
        return "clarkscouk"

    m = re.match("^https?://(www|shop|www1)\.([^/\.]+)\..*$", url)
    if m:
        return m.group(2)
    # TODO: return error message about bad URL if it does not match the regex



# validate request mandatory arguments
def validate_args(arguments):
    # normalize all arguments to str
    argument_keys = map(lambda s: str(s), arguments.keys())

    mandatory_keys = ['url']

    # If missing any of the needed arguments, throw exception
    for argument in mandatory_keys:
        if argument not in argument_keys:
            raise InvalidUsage("Invalid usage: missing GET parameter: " + argument)

    # Validate site
    # If no "site" argument was provided, infer it from the URL
    if 'site' in arguments:
        site_argument = arguments['site'][0]
    else:
        site_argument = extract_domain(arguments['url'][0])

        # If site could not be extracted the URL was invalid
        if not site_argument:
            raise InvalidUsage("Invalid input URL: " + arguments['url'][0] + ". Domain could not be extracted")

        # Add the extracted site to the arguments list (to be used in get_data)
        arguments['site'] = [site_argument]

    if site_argument not in SUPPORTED_SITES.keys():
        raise InvalidUsage("Unsupported site: " + site_argument)

# validate request "data" parameters
def validate_data_params(arguments, ALL_DATA_TYPES):
    # Validate data

    if 'data' in arguments:
        # TODO: do the arguments need to be flattened?
        data_argument_values = map(lambda s: str(s), arguments['data'])
        data_permitted_values = map(lambda s: str(s), ALL_DATA_TYPES.keys())

        # if there are other keys besides "data" or other values outside of the predefined data types (DATA_TYPES), return invalid usage
        if set(data_argument_values).difference(set(data_permitted_values)):
            # TODO:
            #      improve formatting of this message
            raise InvalidUsage("Invalid usage: Request arguments must be of the form '?url=<url>?site=<site>?data=<data_1>&data=<data_2>&data=<data_2>...,\n \
                with the <data_i> values among the following keywords: \n" + str(data_permitted_values))


# general resource for getting data.
# needs "url" and "site" parameters. optional parameter: "data"
# can be used without "data" parameter, in which case it will return all data
# or with arguments like "data=<data_type1>&data=<data_type2>..." in which case it will return the specified data
# the <data_type> values must be among the keys of DATA_TYPES imported dictionary
@app.route('/get_data', methods=['GET'])
def get_data():

    # this is used to convert an ImmutableMultiDictionary into a regular dictionary. will be left with only one "data" key
    request_arguments = dict(request.args)

    # validate request parameters
    validate_args(request_arguments)

    url = request_arguments['url'][0]
    site = request_arguments['site'][0]
    if 'bot' in request_arguments:
        bot = request_arguments['bot'][0]
    else:
        bot = None

    # create scraper class for requested site
    site_scraper = SUPPORTED_SITES[site](url=url, bot=bot)

    # validate parameter values
    # url
    is_valid_url = site_scraper.check_url_format()
    if hasattr(site_scraper, "INVALID_URL_MESSAGE"):
        check_input(url, is_valid_url, site_scraper.INVALID_URL_MESSAGE)
    else:
        check_input(url, is_valid_url)

    # data
    validate_data_params(request_arguments, site_scraper.ALL_DATA_TYPES)

    # return all data if there are no "data" parameters
    if 'data' not in request_arguments:
        try:
            ret = site_scraper.product_info()

        except HTTPError as ex:
            raise GatewayError("Error communicating with site crawled.")

        return jsonify(ret)

    # return only requested data
    try:
        ret = site_scraper.product_info(request_arguments['data'])
    except HTTPError:
        raise GatewayError("Error communicating with site crawled.")


    return jsonify(ret)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    #TODO: not leave this as json output? error format should be consistent
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.errorhandler(GatewayError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.errorhandler(404)
def handle_not_found(error):
    response = jsonify({"error" : "Not found"})
    response.status_code = 404
    return response

@app.errorhandler(500)
def handle_internal_error(error):
    response = jsonify({"error" : "Internal server error"})
    response.status_code = 500
    return response

# post request logger
@app.after_request
def post_request_logging(response):

    app.logger.info(json.dumps({
        "date" : datetime.datetime.today().ctime(),
        "remote_addr" : request.remote_addr,
        "request_method" : request.method,
        "request_url" : request.url,
        "response_status_code" : str(response.status_code),
        "request_headers" : ', '.join([': '.join(x) for x in request.headers])
        })
    )

    return response

if __name__ == '__main__':

    app.run('0.0.0.0', port=80, threaded=True)
