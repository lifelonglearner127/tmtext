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
	m = re.match("http://www\.walmart\.com(/.*)?/[0-9]+$", product_page_url)
	return not not m

# TODO:
#      better way of extracting id now that URL format is more permissive
#      though this method still seems to work...
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
# parameter: types of info to be extracted as a list of strings, or None for all info
# return: dictionary with type of info as key and extracted info as value
def product_info(product_page_url, info_type_list = None):

	if not info_type_list:
		info_type_list = DATA_TYPES.keys()
	
	# copy of info list to send to _info_from_tree
	info_type_list_copy = list(info_type_list)

	# build page xml tree. also measure time it took and assume it's page load time (the rest is neglijable)
	time_start = time.time()
	tree = page_tree(product_page_url)
	time_end = time.time()
	# don't pass load time as info to be extracted by _info_from_tree
	return_load_time = "load_time" in info_type_list_copy
	if return_load_time:
		info_type_list_copy.remove("load_time")

	# remove special info that is not to be extracted from the product page (and handled separately)
	for special_info in DATA_TYPES_SPECIAL.keys():
		if special_info in info_type_list_copy:
			info_type_list_copy.remove(special_info)
	ret_dict = _info_from_tree(product_page_url, tree, info_type_list_copy)
	# add load time to dictionary -- if it's in the list
	# TODO:
	#      - format for load_time?
	#      - what happens if there are requests to js info too? count that load time as well?
	if return_load_time:
		ret_dict["load_time"] = round(time_end - time_start, 2)

	# add special data
	for special_info in DATA_TYPES_SPECIAL:
		if special_info in info_type_list:
			ret_dict.update(DATA_TYPES_SPECIAL[special_info](product_page_url))

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
	results_dict = {}

	for info in info_type_list:

		try:
			results = DATA_TYPES[info](tree_html)
		except IndexError, e:
			sys.stderr.write("ERROR: No " + info + " for " + product_page_url + ":\n" + str(e) + "\n")
			results = None
		except Exception, e:
			sys.stderr.write("ERROR: Unknown error extracting " + info + " for " + product_page_url + ":\n" + str(e) + "\n")
			results = None

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

# extract meta "brand" tag for a product from its product page tree
# ! may throw exception if not found
def _meta_brand_from_tree(tree_html):
	return tree_html.xpath("//meta[@itemprop='brand']/@content")[0]


# extract product short description from its product page tree
# ! may throw exception if not found
def _short_description_from_tree(tree_html):
	short_description = " ".join(tree_html.xpath("//span[@class='ql-details-short-desc']//text()")).strip()
	return short_description

# extract product long description from its product product page tree
# ! may throw exception if not found
# TODO:
#      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
def _long_description_from_tree(tree_html):
	full_description = " ".join(tree_html.xpath("//div[@itemprop='description']//text()")).strip()
	return full_description


# extract product price from its product product page tree
# ! may throw exception if not found
# TODO:
#      - test this for many products. xpath might not be general enough
def _price_from_tree(tree_html):
	price = "".join(tree_html.xpath("//*[contains(@class, 'camelPrice')]//text()")).strip()
	# don't return the empty string
	if not price:
		return None

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

# extract htags (h1, h2) from its product product page tree
def _htags_from_tree(tree_html):
	htags_dict = {}

	# add h1 tags text to the list corresponding to the "h1" key in the dict
	htags_dict["h1"] = map(lambda t: _clean_text(t), tree_html.xpath("//h1//text()[normalize-space()!='']"))
	# add h2 tags text to the list corresponding to the "h2" key in the dict
	htags_dict["h2"] = map(lambda t: _clean_text(t), tree_html.xpath("//h2//text()[normalize-space()!='']"))

	return htags_dict

# extract product model from its product product page tree
# ! may throw exception if not found
def _model_from_tree(tree_html):
	return tree_html.xpath("//table[@class='SpecTable']//td[contains(text(),'Model')]/following-sibling::*/text()")[0]

# extract product features list from its product product page tree, return as string
def _features_from_tree(tree_html):
	# join all text in spec table; separate rows by newlines and eliminate spaces between cells
	rows = tree_html.xpath("//table[@class='SpecTable']//tr")
	# list of lists of cells (by rows)
	cells = map(lambda row: row.xpath(".//td//text()"), rows)
	# list of text in each row
	rows_text = map(\
		lambda row: "".join(\
			map(lambda cell: cell.strip(), row)\
			), \
		cells)
	all_features_text = "\n".join(rows_text)

	return all_features_text

# extract number of features from tree
# ! may throw exception if not found
def _nr_features_from_tree(tree_html):
	# select table rows with more than 2 cells (the others are just headers), count them
	return len(filter(lambda row: len(row.xpath(".//td"))>1, tree_html.xpath("//table[@class='SpecTable']//tr")))

# extract page title from its product product page tree
# ! may throw exception if not found
def _title_from_tree(tree_html):
	return tree_html.xpath("//title//text()")[0].strip()

# extract product seller meta keyword from its product product page tree
# ! may throw exception if not found
def _seller_meta_from_tree(tree_html):
	return tree_html.xpath("//meta[@itemprop='brand']/@content")[0]

# extract product seller information from its product product page tree (using h2 visible tags)
# TODO:
#      test this in conjuction with _seller_meta_from_tree; also test at least one of the values is 1
def _seller_from_tree(tree_html):
	seller_info = {}
	h2_tags = map(lambda text: _clean_text(text), tree_html.xpath("//h2//text()"))
	seller_info['owned'] = 1 if "Buy from Walmart" in h2_tags else 0
	seller_info['marketplace'] = 1 if "Buy from Marketplace" in h2_tags else 0

	return seller_info

# clean text inside html tags - remove html entities, trim spaces
def _clean_text(text):
	return re.sub("&nbsp;", " ", text).strip()


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


# TODO:
#      figure out how to declare this in the beginning?
# dictionaries mapping type of info to be extracted to the method that does it
# also used to define types of data that can be requested to the REST service
# 
# data extracted from product page
# their associated methods return the raw data
DATA_TYPES = { \
	# Info extracted from product page
	"name" : _product_name_from_tree, \
	"keywords" : _meta_keywords_from_tree, \
	"brand" : _meta_brand_from_tree, \
	"short_desc" : _short_description_from_tree, \
	"long_desc" : _long_description_from_tree, \
	"price" : _price_from_tree, \
	"anchors" : _anchors_from_tree, \
	"htags" : _htags_from_tree, \
	"model" : _model_from_tree, \
	"features" : _features_from_tree, \
	"nr_features" : _nr_features_from_tree, \
	"title" : _title_from_tree, \
	"seller": _seller_from_tree, \

	"load_time": None \
	}

# special data that can't be extracted from the product page
# associated methods return already built dictionary containing the data
DATA_TYPES_SPECIAL = { \
	"video_url" : video_for_url, \
	"pdf_url" : pdf_for_url, \
	"reviews" : reviews_for_url \
}


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
##  - anchors (?)
##  - H tags 
##  - page load time (?)
##  - number of reviews
##  - model
##  - list of features
##  - meta brand tag
##  - page title
##  - number of features
##  - sold by walmart / sold by marketplace sellers

##  
## To implement:
## 	- number of images, URLs of images
##  - number of videos, URLs of videos if more than 1
##  - number of pdfs
##  - category info (name, code, parents)
##  - minimum review value, maximum review value
