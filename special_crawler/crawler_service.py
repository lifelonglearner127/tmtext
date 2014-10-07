#!/usr/bin/python

import datetime
import logging
from logging import StreamHandler
import re
import json

from flask import Flask, jsonify, request

from extract_walmart_data import WalmartScraper
from extract_tesco_data import TescoScraper
from extract_amazon_data import AmazonScraper
from extract_pgestore_data import PGEStore
from extract_wayfair_data import WayfairScraper
from extract_argos_data import ArgosScraper


app = Flask(__name__)

# dictionary containing supported sites as keys
# and their respective scrapers as values
SUPPORTED_SITES = {"walmart" : WalmartScraper,
                   "tesco" : TescoScraper,
                   "amazon" : AmazonScraper,
                   "pgestore" : PGEStore,
                   "wayfair": WayfairScraper,
                   "argos": ArgosScraper,
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

# validate input and raise exception with message for client if necessary
def check_input(url, is_valid_url, invalid_url_message=""):
    # TODO: complete these error messages with more details specific to the scraped site
    if not url:
        raise InvalidUsage("No input URL was provided.", 400)

    if not is_valid_url:
        raise InvalidUsage(\
            "Invalid URL: " + str(url) + " " + str(invalid_url_message),\
            400)

# infer domain from input URL
def extract_domain(url):
    m = re.match("^http://www\.([^/\.]+)\..*$", url)
    if m:
        return m.group(1)
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
        raise InvalidUsage("Unsupported site: " + str(site_argument))
    

# validate request "data" parameters
def validate_data_params(arguments, DATA_TYPES, DATA_TYPES_SPECIAL):
    # Validate data

    if 'data' in arguments:
        # TODO: do the arguments need to be flattened?
        data_argument_values = map(lambda s: str(s), arguments['data'])
        data_permitted_values = map(lambda s: str(s), DATA_TYPES.keys() + DATA_TYPES_SPECIAL.keys())

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
    # create scraper class for requested site
    site_scraper = SUPPORTED_SITES[site](url)

    # validate parameter values
    # url
    is_valid_url = site_scraper.check_url_format()
    if hasattr(site_scraper, "INVALID_URL_MESSAGE"):
        check_input(url, is_valid_url, site_scraper.INVALID_URL_MESSAGE)
    else:
        check_input(url, is_valid_url)

    # data
    validate_data_params(request_arguments, site_scraper.DATA_TYPES, site_scraper.DATA_TYPES_SPECIAL)

    # return all data if there are no "data" parameters
    if 'data' not in request_arguments:
        ret = site_scraper.product_info()

        return jsonify(ret)

    # return only requested data
    ret = site_scraper.product_info(request_arguments['data'])
    
    return jsonify(ret)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    #TODO: not leave this as json output? error format should be consistent
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