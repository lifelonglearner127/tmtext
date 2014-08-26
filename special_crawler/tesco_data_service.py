#!/usr/bin/python

from flask import Flask, jsonify, abort, request
from extract_tesco_data import TescoScraper
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

def check_url_format(url):
    m = re.match("http://www\.tesco\.com/direct/.*?/[0-9\-]+\.prd$", url)
    return not not m

# validate URL parameter
def check_input(url):
    #ex: http://www.tesco.com/direct/intel-4th-generation-core-i5-4670-34ghz-quad-core-processor-6mb-l3-cache-boxed/518-7080.prd
    if not url:
        raise InvalidUsage("No Tesco URL was provided. API must be called with URL like <host>/get_tesco_data/<tesco_url>"), 400

    if not check_url_format(url):
        raise InvalidUsage(\
            "Invalid parameter " + str(url) + " Parameter must be a Tesco URL of the form: http://www.tesco.com/direct/<fraction_of_product_name>/<product_id>.prd",\
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



# general resource for getting Tesco data.
# can be used without arguments, in which case it will return all data
# or with arguments like "data=<data_type1>&data=<data_type2>..." in which case it will return the specified data
# the <data_type> values must be among the keys of DATA_TYPES imported dictionary
@app.route('/get_tesco_data/<path:url>', methods=['GET'])
def get_data(url):

    TS = TescoScraper(url)

    # validate URL
    check_input(url)

    # this is used to convert an ImmutableMultiDictionary into a regular dictionary. will be left with only one "data" key
    # TODO:
    #      test this
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

    app.run('127.0.0.1', port=80)