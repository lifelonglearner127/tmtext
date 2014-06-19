#!/usr/bin/python

import urllib
import re
import sys
import json

# base URL for request containing video URL
BASE_URL_VIDEOREQ = "http://json.webcollage.net/apps/json/walmart?callback=jsonCallback&environment-id=live&cpi="
# base URL for request containing pdf URL
BASE_URL_PDFREQ = "http://content.webcollage.net/walmart/smart-button?ignore-jsp=true&ird=true&channel-product-id="
# base URL for request for product reviews - formatted string
BASE_URL_REVIEWSREQ = 'http://walmart.ugc.bazaarvoice.com/1336a/%20{0}/reviews.djs?format=embeddedhtml'

def check_url_format(product_page_url):
	m = re.match("http://www\.walmart\.com/ip/[0-9]+$", product_page_url)
	return not not m

def _extract_product_id(product_page_url):
	product_id = product_page_url.split('/')[-1]
	return product_id

def _video_url(product_page_url):
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

# return dictionary with one element containing the video url
def video_for_url(product_page_url):
	results = {'video_url' : _video_url(product_page_url)}
	return results

def _pdf_url(product_page_url):
	request_url = BASE_URL_PDFREQ + _extract_product_id(product_page_url)

	response_text = urllib.urlopen(request_url).read().decode('string-escape')

	pdf_url_candidates = re.findall('(?<=")http[^"]*media\.webcollage\.net[^"]*[^"]+\.pdf(?=")', response_text)
	if pdf_url_candidates:
		# remove escapes
		pdf_url = re.sub('\\\\', "", pdf_url_candidates[0])

		return pdf_url

	else:
		return None

# return dictionary with one element containing the PDF
def pdf_for_url(product_page_url):
	results = {"pdf_url" : _pdf_url(product_page_url)}

def media_for_url(product_page_url):
	# create json object with video and pdf urls
	results = {'video_url' : _video_url(product_page_url), \
				'pdf_url' : _pdf_url(product_page_url)}
	return results

def reviews_for_url(product_page_url):
	request_url = BASE_URL_REVIEWSREQ.format(_extract_product_id(product_page_url))
	content = urllib.urlopen(request_url).read()
	try:
		reviews_count = re.findall(r"BVRRNonZeroCount\\\"><span class=\\\"BVRRNumber\\\">([0-9,]+)<", content)[0]
		average_review = re.findall(r"class=\\\"BVRRRatingNormalOutOf\\\"> <span class=\\\"BVRRNumber BVRRRatingNumber\\\">([0-9\.]+)<", content)[0]
	except Exception, e:
		sys.stderr.write("Error extracting reviews info: No reviews info found for product " + product_page_url + "\n")
		return {"total_reviews": None, "average_review": None}
	return {"total_reviews": reviews_count, "average_review": average_review}

def main(args):
	# check if there is an argument
	if len(args) <= 1:
		sys.stderr.write("ERROR: No product URL provided.\nUsage:\n\tpython extract_walmart_media.py <walmart_product_url>\n")
		sys.exit(1)

	product_page_url = args[1]

	# check format of page url
	if not check_url_format(product_page_url):
		sys.stderr.write("ERROR: Invalid URL " + str(product_page_url) + "\nFormat of product URL should be\n\t http://www.walmart.com/ip/<product_id>\n")
		sys.exit(1)

	# create json object with video and pdf urls
#	return json.dumps(media_for_url(product_page_url))
	return json.dumps(reviews_for_url(product_page_url))

if __name__=="__main__":
	print main(sys.argv)
