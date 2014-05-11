#!/usr/bin/python

from flask import Flask, jsonify, abort, request
from extract_walmart_media import media_for_url, _check_url_format

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
        rv['message'] = self.message
        return rv

@app.route('/get_media/<path:url>', methods=['GET'])
def get_media_urls(url):
	if not url:
		raise InvalidUsage("No Walmart URL was provided. API must be called with URL like <host>/get_media/<walmart_url>"), 404

	if not check_url_format(url):
		raise InvalidUsage(\
			"Parameter must be a Walmart URL of the form: http://www.walmart.com/ip/<product_id>",\
			404)

	ret = media_for_url(url)
	return jsonify(ret)

@app.route('/get_media', methods=['GET'])
def get_media_urls_params():
	args_dict = request.args
	if 'product_page' not in args_dict:
		raise InvalidUsage("Invalid Usage: 'product_page' parameter must be provided in the query string.", 404)

	url = args_dict['product_page']

	if not url:
		raise InvalidUsage("No Walmart URL was provided."), 404

	if not _check_url_format(url):
		raise InvalidUsage(\
			"Invalid parameter " + url + ". Parameter must be a Walmart URL must be of the form: http://www.walmart.com/ip/<product_id>",\
			404)

	ret = media_for_url(url)
	return jsonify(ret)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
	#TODO: not leave this as json output? error format should be consistent
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

if __name__ == '__main__':
	#TODO: change port to 80, host to 0.0.0.0 (so it can be used externally) and debug to false (not safe in production environment)
    app.run(debug = True)