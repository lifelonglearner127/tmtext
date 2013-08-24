from nose.tools import assert_true, assert_false, assert_not_equal, assert_equal
import unittest
#from ..spiders.search_spider import ProcessText
from ..spiders.search_spider import ProcessText

class ProcessText_test(unittest.TestCase):

	def runTest(self):
		#text = "Sony BRAVIA KDL55HX750 55-Inch 240Hz 1080p 3D LED Internet TV, Black"
		#
		text = "27in"
		res = self.p.normalize(text)
		expected_res = ["27\""]
		assert_equal(res, expected_res)

	def setUp(self):
		self.p = ProcessText()

	def tearDown(self):
		pass



