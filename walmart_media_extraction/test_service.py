#!/usr/bin/python
#
import unittest
from extract_walmart_media import DATA_TYPES, DATA_TYPES_SPECIAL
import requests
import sys

class WalmartData_test(unittest.TestCase):

#	def __init__(self, *args, **kwargs):
#		super(TestingClass, self).__init__(*args, **kwargs)
		

	def setUp(self):
		# take stdin as input url
		self.urls = None #sys.stdin.read().splitlines()

		# service address
		self.address = "http://localhost/get_walmart_data/%s"

		# if there was no url as input, use this hardcoded list
		if not self.urls:
			self.urls = ['http://www.walmart.com/ip/Ocuvite-W-Lutein-Antioxidants-Zinc-Tablets-Vitamin-Mineral-Supplement-120-ct/1412']

	# test a requested data type was not null
	def notnull_template(self, datatype):
		for url in self.urls:
			response = requests.get(self.address % url + "?data=" + datatype).json()
			self.assertTrue(datatype in response)
			self.assertNotEqual(response[datatype], "")
			self.assertIsNotNone(response[datatype])


	# test data extracted from product page is never null
	def test_name_notnull(self):
		self.notnull_template("name")

	def test_keywords_notnull(self):
		self.notnull_template("keywords")

	def test_shortdesc_notnull(self):
		self.notnull_template("short_desc")

	def test_longdesc_notnull(self):
		self.notnull_template("long_desc")

	def test_price_notnull(self):
		self.notnull_template("price")

	def test_Htags_notnull(self):
		self.notnull_template("htags")

	def test_pageload_notnull(self):
		self.notnull_template("load_time")

	def test_reviews_notnull(self):
		self.notnull_template("reviews")

	# def test_model_notnull(self):

	# def test_features_notnull(self):

	# def test_brand_notnull(self):

	# def test_title_notnull(self):

	# def test_nrfeatures_notnull(self):

	# def test_seller_notnull(self):

	# # test if seller in meta tag matches seller returned by servic

	# def test_seller_correct(self):


	# def test_anchors_notnull(self)


if __name__=='__main__':
	unittest.main()