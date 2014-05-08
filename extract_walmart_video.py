#!/usr/bin/python

import urllib
import re
import sys

BASE_URL = "http://json.webcollage.net/apps/json/walmart?callback=jsonCallback&environment-id=live&cpi="

def _extract_product_id(product_page_url):
	#TODO: throw exception if not expected format
	product_id = product_page_url.split('/')[-1]
	return product_id

def video_url(product_page_url):
	request_url = BASE_URL + _extract_product_id(product_page_url)

	#TODO: handle errors
	response_text = urllib.urlopen(request_url).read()

	video_url_candidates = re.findall('"[^"]+\.flv"', response_text)
	if video_url_candidates:
		# remove escapes
		#TODO: better way to do this?
		video_url = re.sub('\\\\', "", video_url_candidates[0])
		#video_url = video_url_candidates[0].decode('string_escape')

		return video_url

	else:

		return None


if __name__=="__main__":
	product_page_url = sys.argv[1]

	print video_url(product_page_url)