#!/usr/bin/python

from flask import Flask, jsonify, abort, request
from extract_walmart_data import media_for_url, check_url_format, reviews_for_url, \
pdf_for_url, video_for_url, product_info, DATA_TYPES, DATA_TYPES_SPECIAL

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

# validate URL parameter
def check_input(url):
	if not url:
		raise InvalidUsage("No Walmart URL was provided. API must be called with URL like <host>/get_media/<walmart_url>"), 400

	if not check_url_format(url):
		raise InvalidUsage(\
			"Invalid parameter " + str(url) + " Parameter must be a Walmart URL of the form: http://www.walmart.com/ip/<product_id> or http://www.walmart.com/cp/<fraction_of_product_name>/<product_id>",\
			400)

# validate request arguments
def validate_args(arguments):
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
def get_data(url):

	# validate URL
	check_input(url)

	# this is used to convert an ImmutableMultiDictionary into a regular dictionary. will be left with only one "data" key
	# TODO:
	#      test this
	request_arguments = dict(request.args)

	# return all data if there are no arguments
	if not request_arguments:
		ret = product_info(url)

		return jsonify(ret)

	# there are request arguments, validate them
	validate_args(request_arguments)

	ret = product_info(url, request_arguments['data'])
	
	return jsonify(ret)


# The routes below are deprecated:
# use /get_walmart_data/<URL>/data=... instead (see above - get_data method)

@app.route('/get_walmart_data/reviews/<path:url>', methods=['GET'])
def get_reviews(url):
	check_input(url)

	ret = reviews_for_url(url)
	return jsonify(ret)

@app.route('/get_walmart_data/media/<path:url>', methods=['GET'])
def get_media_urls(url):
	check_input(url)

	ret = media_for_url(url)
	return jsonify(ret)

@app.route('/get_walmart_data/PDF/<path:url>', methods=['GET'])
def get_pdf_url(url):
	check_input(url)

	ret = pdf_for_url(url)
	return jsonify(ret)

@app.route('/get_walmart_data/video/<path:url>', methods=['GET'])
def get_video_url(url):
	check_input(url)

	ret = video_for_url(url)
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

if __name__ == '__main__':
    app.run('0.0.0.0', port=80)