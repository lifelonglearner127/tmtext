import unittest
from spiders_utils import Utils

class ProcessText_test(unittest.TestCase):

	def test_cleanurl(self):
		url = "http://www.target.com#stuff"
		self.assertEquals(Utils.clean_url(url,['#']), "http://www.target.com")

