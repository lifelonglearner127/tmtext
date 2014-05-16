import unittest

from pyramid import testing
import pyramid.exceptions as exc


class SpiderViewTests(unittest.TestCase):

    def setUp(self):
        self.settings = {
            'spider._names': 'spider_cfg',
            'spider._scrapyd.base_url': 'http://localhost:6800/',
            'spider._result.base_url': 'http://localhost:8000/',
            'spider.spider_cfg.resource': 'spider_resource',
            'spider.spider_cfg.spider_name': 'spider_name',
            'spider.spider_cfg.project_name': 'spider_project_name',
        }
        self.config = testing.setUp(settings=self.settings)

    def tearDown(self):
        testing.tearDown()

    def test_unknown_resource(self):
        from .views import spider_view
        request = testing.DummyRequest(path="/unexistant/path/")
        self.assertRaises(exc.HTTPNotFound, spider_view, request)
