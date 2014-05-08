#!/usr/bin/python

import urllib
import re
import sys
import json

# base URL for request containing video URL
BASE_URL_VIDEOREQ = "http://json.webcollage.net/apps/json/walmart?callback=jsonCallback&environment-id=live&cpi="
# base URL for request containing pdf URL
BASE_URL_PDFREQ = "http://content.webcollage.net/walmart/smart-button?ignore-jsp=true&ird=true&channel-product-id="

def _extract_product_id(product_page_url):
	#TODO: throw exception if not expected format
	product_id = product_page_url.split('/')[-1]
	return product_id

def video_url(product_page_url):
	request_url = BASE_URL_VIDEOREQ + _extract_product_id(product_page_url)

	#TODO: handle errors
	response_text = urllib.urlopen(request_url).read()

	video_url_candidates = re.findall('(?<=")[^"]+\.flv(?=")', response_text)
	if video_url_candidates:
		# remove escapes
		#TODO: better way to do this?
		video_url = re.sub('\\\\', "", video_url_candidates[0])
		#video_url = video_url_candidates[0].decode('string_escape')

		return video_url

	else:

		return None

def pdf_url(product_page_url):
	request_url = BASE_URL_PDFREQ + _extract_product_id(product_page_url)

	response_text = urllib.urlopen(request_url).read().decode('string-escape')

	pdf_url_candidates = re.findall('(?<=")http[^"]*media\.webcollage\.net[^"]*[^"]+\.pdf(?=")', response_text)
	if pdf_url_candidates:
		# remove escapes
		pdf_url = re.sub('\\\\', "", pdf_url_candidates[0])

		return pdf_url

	else:
		return None

if __name__=="__main__":
	product_page_url = sys.argv[1]

	# create json object with video and pdf urls
	results = {'video_url' : video_url(product_page_url), \
				'pdf_url' : pdf_url(product_page_url)}
	print json.dumps(results)