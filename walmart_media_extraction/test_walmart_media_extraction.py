import urllib
import sys
import unittest
import json
import extract_walmart_media
from extract_walmart_media import _extract_product_id, BASE_URL_VIDEOREQ

class ProcessText_test(unittest.TestCase):

	def setUp(self):
		self.urls = filter(None,map(lambda x: x.strip(), sys.stdin.read().splitlines()))

		self.urls_dict = []
		for url in self.urls:
			product = {}
			product['url'] = url
			product['page_content'] = urllib.urlopen(url).read()
			request_url = BASE_URL_VIDEOREQ + _extract_product_id(url)
			product['response'] = response = urllib.urlopen(request_url).read()
			self.urls_dict.append(product)

	# def test_errors(self):
	# 	for url in self.urls:
	# 		args = [1,url] # simlulate sys.argv
	# 		result = json.loads(extract_walmart_media.main(args))
	# 		self.assertTrue('error' not in result)

	def test_video_if_button(self):
		for product in self.urls_dict:

			if "'video')" in product['page_content']:
				print "YES", product['url']
			else:
				print "NO", product['url']

			if "'video')" in product['page_content']:
				self.assertTrue('flv' in product['response'])

	def test_button_if_video(self):
		for product in self.urls_dict:

			if "flv" in product['page_content']:
				print "YES", product['url']
			else:
				print "NO", product['url']

			if "flv" in product['response']:
				self.assertTrue("'video')" in product['page_content'])


	def tearDown(self):
		pass

if __name__=='__main__':
	unittest.main()