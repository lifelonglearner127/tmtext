import urlparse

import mock
from pyspecs import given, when, then, and_, the, finish

from web_runner.util import find_spider_config, SpiderConfig, ScrapydMediator
from web_runner.util import find_command_config, CommandConfig


with given.a_configuration_of_a_spider:
    settings = {
        'spider._names': 'spider_cfg',

        'spider._scrapyd.base_url': 'http://localhost:6800/',
        'spider._result.base_url': 'http://localhost:8000/',

        'spider.spider_cfg.resource': 'spider_resource',
        'spider.spider_cfg.spider_name': 'spider_name',
        'spider.spider_cfg.project_name': 'spider_project_name',
    }

    with when.searching_for_that_resource:
        config = find_spider_config(settings, '/spider_resource/')

        with then.the_configuration_should_be_found:
            the(config).should.equal(
                SpiderConfig('spider_name', 'spider_project_name'))

    with when.searching_for_an_unexistant_resource:
        config = find_spider_config(settings, '/unexistant/')

        with then.it_should_return_none:
            the(config).should.be(None)


with given.a_configuration_of_a_command:
    settings = {
        'command._names': 'tst',

        'command.tst.cmd': 'echo {key1}',
        'command.tst.resource': '/tst-resource',
        'command.tst.content_type': 'text/plain',
        'command.tst.crawl.0.project-name': 'spider project',
        'command.tst.crawl.0.spider-name': 'spider name',
    }

    with when.searching_for_that_resource:
        config = find_command_config(settings, '/tst-resource/')

        with then.the_configuration_should_be_found:
            the(config).should.equal(CommandConfig(
                'echo {key1}',
                'text/plain',
                [SpiderConfig('spider name', 'spider project')]
            ))

    with when.searching_for_an_unexistant_resource:
        config = find_command_config(settings, '/unexistant/')

        with then.it_should_return_none:
            the(config).should.be(None)


with given.a_configured_spider_mediator:
    mediator = ScrapydMediator(
        {
            ScrapydMediator.SCRAPYD_BASE_URL: 'scrapyd url',
            ScrapydMediator.FILE_SERVER_BASE_URL: 'file server url',
        },
        SpiderConfig('spider name', 'spider project')
    )

    with mock.patch('web_runner.util.urllib2') as urllib2_mock:
        conn = urllib2_mock.urlopen.return_value

        with when.starting_a_job:
            conn.read.return_value = '["a json response"]'

            response = mediator.start_job({})

            with then.it_should_post_a_request:
                pass  # FIXME: Assert!

            with and_.it_should_return_the_parsed_response:
                the(response).should.equal(["a json response"])

        with when.reporting_on_a_job:
            conn.read.return_value = """{"status": "ok",
                "pending": [{"id": "78391cc0fcaf11e1b0090800272a6d06", "spider": "spider1"}],
                "running": [{"id": "422e608f9f28cef127b3d5ef93fe9399", "spider": "spider2", "start_time": "2012-09-12 10:14:03.594664"}],
                "finished": [{"id": "2f16646cfcaf11e1b0090800272a6d06", "spider": "spider3", "start_time": "2012-09-12 10:14:03.594664", "end_time": "2012-09-12 10:24:03.594664"}]}
            """

            status = mediator.report_on_job(
                "422e608f9f28cef127b3d5ef93fe9399")

            with then.it_should_fetch_job_status:
                urllib2_mock.urlopen.assert_called_with(
                    urlparse.urljoin(
                        mediator.SCRAPYD_BASE_URL,
                        'listjobs.json?project=spider+project',
                    ),
                    None
                )

            with and_.it_should_return_status_of_correct_job:
                the(status).should.be(ScrapydMediator.JobStatus.running)


if __name__ == '__main__':
    finish()
