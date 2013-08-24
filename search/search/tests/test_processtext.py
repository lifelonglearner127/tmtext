from nose.tools import assert_true, assert_false, assert_not_equal, assert_equal
import unittest
#from ..spiders.search_spider import ProcessText
from ..spiders.search_spider import ProcessText

class ProcessText_test(unittest.TestCase):

	def runTest(self):
		text = "Sony BRAVIA KDL55HX750 55-Inch 240Hz 1080p 3D LED Internet TV, Black"
		expected_res = ['sony', 'bravia', 'kdl55hx750', '55\"', '240hz', '1080p', '3d', 'led', 'internet', 'tv', 'black', 'kdl55hx75']
		
		# text = "27in"
		# expected_res = ["27\""]

		res = self.p.normalize(text)
		assert_equal(res, expected_res)

	def setUp(self):
		self.p = ProcessText()

	def tearDown(self):
		pass



