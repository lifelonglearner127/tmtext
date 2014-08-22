#!/usr/bin/python

from flask import Flask, jsonify, abort, request
from extract_walmart_data import WalmartScraper
import datetime
import logging
from logging import FileHandler
import re

app = Flask(__name__)

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
def check_input(url, is_valid_url):
    # TODO: complete these error messages with more details specific to the scraped site
    if not url:
        raise InvalidUsage("No input URL was provided."), 400

    if not is_valid_url:
        raise InvalidUsage(\
            "Invalid parameter " + str(url),\
            400)

# validate request arguments
def validate_args(arguments, DATA_TYPES, DATA_TYPES_SPECIAL):
    # normalize all arguments to unicode (no str)
    argument_keys = map(lambda s: unicode(s), arguments.keys())

    # also flatten list of lists arguments
    argument_values = map(lambda s: unicode(s), sum(arguments.values(), []))
    permitted_values = map(lambda s: unicode(s), DATA_TYPES.keys() + DATA_TYPES_SPECIAL.keys())
    permitted_keys = [u'data']

    # if there are other keys besides "data" or other values outside of the predefined data types (DATA_TYPES), return invalid usage
    if argument_keys != permitted_keys or set(argument_values).difference(set(permitted_values)):
        # TODO:
        #      improve formatting of this message
        raise InvalidUsage("Invalid usage: Request arguments must be of the form '?data=<data_1>&data=<data_2>&data=<data_2>...,\n \
            with the <data_i> values among the following keywords: \n" + str(permitted_values))


# general resource for getting walmart data.
# can be used without arguments, in which case it will return all data
# or with arguments like "data=<data_type1>&data=<data_type2>..." in which case it will return the specified data
# the <data_type> values must be among the keys of DATA_TYPES imported dictionary
@app.route('/get_walmart_data/<path:url>', methods=['GET'])
def get_walmart_data(url):

    # create walmart scraper class
    WS = WalmartScraper(url)

    is_valid_url = WS.check_url_format()

    # validate input
    check_input(url, is_valid_url)

    # this is used to convert an ImmutableMultiDictionary into a regular dictionary. will be left with only one "data" key
    request_arguments = dict(request.args)

    # return all data if there are no arguments
    if not request_arguments:
        ret = WS.product_info()

        return jsonify(ret)

    # there are request arguments, validate them
    validate_args(request_arguments, WS.DATA_TYPES, WS.DATA_TYPES_SPECIAL)

    ret = WS.product_info(request_arguments['data'])
    
    return jsonify(ret)

# TODO: deduplicate this code by adding <site> parameter to request
# TODO: change url parameter to GET query string parameter

# TODO: import TescoScraper after it is implemented
# general resource for getting tesco data.
# can be used without arguments, in which case it will return all data
# or with arguments like "data=<data_type1>&data=<data_type2>..." in which case it will return the specified data
# the <data_type> values must be among the keys of DATA_TYPES imported dictionary
@app.route('/get_tesco_data/<path:url>', methods=['GET'])
def get_tesco_data(url):

    # create walmart scraper class
    TS = TescoScraper(url)

    is_valid_url = TS.check_url_format()

    # validate input
    check_input(url, is_valid_url)

    # this is used to convert an ImmutableMultiDictionary into a regular dictionary. will be left with only one "data" key
    request_arguments = dict(request.args)

    # return all data if there are no arguments
    if not request_arguments:
        ret = TS.product_info()

        return jsonify(ret)

    # there are request arguments, validate them
    validate_args(request_arguments, TS.DATA_TYPES, TS.DATA_TYPES_SPECIAL)

    ret = TS.product_info(request_arguments['data'])
    
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

@app.after_request
def post_request_logging(response):
    app.logger.info('\t'.join([
        datetime.datetime.today().ctime(),
        request.remote_addr,
        request.method,
        request.url,
        str(response.status_code),
        request.data,
        ', '.join([': '.join(x) for x in request.headers])])
    )
    return response

if __name__ == '__main__':
    
    fh = FileHandler("special_crawler_log.txt")
    fh.setLevel(logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(fh)

    app.run('0.0.0.0', port=80)