#!/usr/bin/python

import urllib
import re
import sys
import json

from lxml import html
import time

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

	# get first "src" value in response
	video_url_candidates = re.findall("src: \"([^\"]+)\"", response_text)
	if video_url_candidates:
		# remove escapes
		#TODO: better way to do this?
		video_url_candidate = re.sub('\\\\', "", video_url_candidates[0])

		# if it ends in flv, it's a video, ok
		if video_url_candidate.endswith(".flv"):
			return video_url_candidate

		# if it doesn't, it may be a url to make another request to, to get customer reviews video
		new_response = urllib.urlopen(video_url_candidate).read()
		video_id_candidates = re.findall("param name=\"video\" value=\"(.*)\"", new_response)

		if video_id_candidates:
			video_id = video_id_candidates[0]

			video_url_req = "http://client.expotv.com/vurl/%s?output=mp4" % video_id
			video_url = urllib.urlopen(video_url_req).url

			return video_url

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
	return results

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

# extract product info from walmart product page.
# (note: this is for info that can be extracted directly from the product page, not content generated through javascript)
# Additionally from _info_from_tree(), this method extracts page load time.
# parameter: types of info to be extracted as a list of strings
# return: dictionary with type of info as key and extracted info as value
def product_info(product_page_url, info_type_list):
	# build page xml tree. also measure time it took and assume it's page load time (the rest is neglijable)
	time_start = time.clock()
	tree = page_tree(product_page_url)
	time_end = time.clock()
	# don't pass load time as info to be extracted by _info_from_tree
	return_load_time = "load_time" in info_type_list
	info_type_list.remove("load_time")
	ret_dict = _info_from_tree(product_page_url, tree, info_type_list)
	# add load time to dictionary -- if it's in the list
	# TODO:
	#      - format for load_time?
	#      - what happens if there are requests to js info too? count that load time as well?
	if return_load_time:
		ret_dict["load_time"] = time_end - time_start
	return ret_dict

# method that returns xml tree of page, to extract the desired elemets from
def page_tree(product_page_url):
	contents = urllib.urlopen(product_page_url).read()
	tree_html = html.fromstring(contents)
	return tree_html

# Extract product info from its product page tree
# given its tree and a list of the type of info needed.
# Return dictionary containing type of info as keys and extracted info as values.
# This method is intended to act as a unitary way of getting all data needed,
# looking to avoid generating the html tree for each kind of data (if there is more than 1 requested).
def _info_from_tree(product_page_url, tree_html, info_type_list):
	# dictionary mapping type of info to be extracted to the method that does it
	info_to_method = { \
		"name" : _product_name_from_tree, \
		"keywords" : _meta_keywords_from_tree, \
		"short_desc" : _short_description_from_tree, \
		"long_desc" : _long_description_from_tree, \
		"price" : _price_from_tree, \
		"anchors" : _anchors_from_tree \
	}

	results_dict = {}

	for info in info_type_list:
		try:
			results = info_to_method[info](tree_html)
		except IndexError, e:
			sys.stderr.write("ERROR: No " + info + " for " + product_page_url + ":\n" + str(e) + "\n")
			results = None
		except Exception, e:
			sys.stderr.write("ERROR: Unknown error extracting " + info + " for " + product_page_url + ":\n" + str(e) + "\n")
			retults = None

		results_dict[info] = results

	return results_dict

# extract product name from its product page tree
# ! may throw exception if not found
def _product_name_from_tree(tree_html):
	return tree_html.xpath("//h1")[0].text

# extract meta "keywords" tag for a product from its product page tree
# ! may throw exception if not found
def _meta_keywords_from_tree(tree_html):
	return tree_html.xpath("//meta[@name='Keywords']/@content")[0]

# extract product short description from its product page tree
# ! may throw exception if not found
def _short_description_from_tree(tree_html):
	short_description = " ".join(tree_html.xpath("//span[@class='ql-details-short-desc']//text()")).strip()
	return short_description

# extract product long description from its product product page tree
# ! may throw exception if not found
# TODO:
#      - this includes the short description -- is this what we want?
#      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
def _long_description_from_tree(tree_html):
	full_description = " ".join(tree_html.xpath("//div[@itemprop='description']//text()")).strip()
	return full_description


# extract product price from its product product page tree
# ! may throw exception if not found
# TODO:
#      - what data type should this be? string like "$500"? or integer/float?
#      - test this for many products. xpath might not be general enough
def _price_from_tree(tree_html):
	return "".join(tree_html.xpath("//span[@class='clearfix camelPrice priceInfoOOS']//text()")).strip()

# extract product price from its product product page tree
# ! may throw exception if not found
# TODO:
#      - test
#      - is format ok?
def _anchors_from_tree(tree_html):
	# get all links that match "#.+" (return part after #)
	# filter empty matches with filter()
	# flatten list with sum()
	return sum(filter(None, map(lambda s: re.findall("#.+", s), tree_html.xpath("//a/@href"))), [])

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

	return json.dumps(product_info(sys.argv[1], ["name", "short_desc", "keywords", "price", "load_time", "anchors", "long_desc"]))

	# create json object with video and pdf urls
	#return json.dumps(media_for_url(product_page_url))
#	return json.dumps(reviews_for_url(product_page_url))

if __name__=="__main__":
	print main(sys.argv)

## TODO:
## Implemented:
## 	- name
##  - meta keywords
##  - short description
##  - long description
##  - price
##  - url of video
##  - url of pdf
##  - anchors
##  - page load time (?)
##  - number of reviews
##  
## To implement:
## 	- number of images, URLs of images
##  - number of videos, URLs of videos if more than 1
##  - number of pdfs
##  - number of features (?)
##  - H tags (?)
##  - category info (name, code, parents)
