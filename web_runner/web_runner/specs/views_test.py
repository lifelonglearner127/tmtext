from pyramid import testing
import pyramid.httpexceptions as exc
from pyspecs import given, when, then, the, finish

from web_runner import views


with given('a configuration with one spider'):
    settings = {
        'spider._names': 'spider_cfg',
        'spider._scrapyd.base_url': 'http://localhost:6800/',
        'spider._result.base_url': 'http://localhost:8000/',
        'spider.spider_cfg.resource': 'spider_resource',
        'spider.spider_cfg.spider_name': 'spider_name',
        'spider.spider_cfg.project_name': 'spider_project_name',
    }
    config = testing.setUp(settings=settings)

    def tearDown(self):
        testing.tearDown()

    with when('fetching an unknown resource'):
        request = testing.DummyRequest(path="/unexistant/path/")

        exception = None
        try:
            views.spider_start_view(request)
        except exc.HTTPNotFound as e:
            exception = e

        with then.it_should_be_not_found:
            the(views.spider_start_view(request)).should.raise_an(exc.HTTPNotFound)

if __name__ == '__main__':
    finish()
