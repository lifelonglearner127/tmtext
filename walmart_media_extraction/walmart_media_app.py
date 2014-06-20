#!/usr/bin/python

from flask import Flask, jsonify, abort, request
from extract_walmart_media import media_for_url, check_url_format, reviews_for_url, \
pdf_for_url, video_for_url

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

def check_input(url):
	if not url:
		raise InvalidUsage("No Walmart URL was provided. API must be called with URL like <host>/get_media/<walmart_url>"), 404

	if not check_url_format(url):
		raise InvalidUsage(\
			"Invalid parameter " + str(url) + " Parameter must be a Walmart URL of the form: http://www.walmart.com/ip/<product_id>",\
			404)

# get all data: PDF, video and reviews
@app.route('/get_walmart_data/<path:url>', methods=['GET'])
def get_all_data(url):
	check_input(url)

	media_data = media_for_url(url)
	reviews_data = reviews_for_url(url)
	ret = dict(media_data.items() + reviews_data.items())
	return jsonify(ret)

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