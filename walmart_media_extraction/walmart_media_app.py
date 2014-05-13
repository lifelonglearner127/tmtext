#!/usr/bin/python

from flask import Flask, jsonify, abort, request
from extract_walmart_media import media_for_url, check_url_format

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

@app.route('/get_walmart_media/<path:url>', methods=['GET'])
def get_media_urls(url):
	if not url:
		raise InvalidUsage("No Walmart URL was provided. API must be called with URL like <host>/get_media/<walmart_url>"), 404

	if not check_url_format(url):
		raise InvalidUsage(\
			"Parameter must be a Walmart URL of the form: http://www.walmart.com/ip/<product_id>",\
			404)

	ret = media_for_url(url)
	return jsonify(ret)

# @app.route('/get_walmart_media', methods=['GET'])
# def get_media_urls_params():
# 	args_dict = request.args
# 	if 'product_page' not in args_dict:
# 		raise InvalidUsage("Invalid Usage: 'product_page' parameter must be provided in the query string.", 404)

# 	url = args_dict['product_page']

# 	if not url:
# 		raise InvalidUsage("No Walmart URL was provided."), 404

# 	if not _check_url_format(url):
# 		raise InvalidUsage(\
# 			"Invalid parameter " + url + ". Parameter must be a Walmart URL must be of the form: http://www.walmart.com/ip/<product_id>",\
# 			404)

# 	ret = media_for_url(url)
# 	return jsonify(ret)


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