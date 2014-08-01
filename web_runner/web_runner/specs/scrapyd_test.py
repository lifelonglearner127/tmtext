import urlparse
from StringIO import StringIO

import mock
from pyspecs import given, when, then, and_, the, finish

from web_runner.config_util import SpiderConfig
from web_runner.scrapyd import ScrapydMediator


with given.a_configured_scrapyd_mediator:
    mediator = ScrapydMediator(
        {
            ScrapydMediator.SCRAPYD_BASE_URL: 'scrapyd url',
            ScrapydMediator.SCRAPYD_ITEMS_PATH: 'scrapyd items path',
        },
        SpiderConfig('spider name', 'spider project')
    )

    with when.starting_a_job:
        with mock.patch('web_runner.scrapyd.urllib2') as urllib2_mock:
            urllib2_mock.urlopen.side_effect = [
                StringIO('{"status": "ok", "jobid": "XXX"}'),
                StringIO('''{
                    "status": "ok",
                    "finished": [],
                    "running": [],
                    "pending": [{"id": "XXX", "spider": "spider1"}]
                }
                '''),
            ]

            job_id = mediator.start_job({}, timeout=0)

            with and_.it_should_return_the_parsed_response:
                the(job_id).should.equal("XXX")

    with when.reporting_on_a_job:
        with mock.patch('web_runner.scrapyd.urllib2') as urllib2_mock:
            urllib2_mock.reset_mock()
            urllib2_mock.urlopen.return_value = StringIO("""{
                "status": "ok",
                "pending": [
                    {
                        "id": "78391cc0fcaf11e1b0090800272a6d06",
                         "spider": "spider1"
                    }
                ],
                "running": [
                    {
                        "id": "422e608f9f28cef127b3d5ef93fe9399",
                        "spider": "spider2",
                        "start_time": "2012-09-12 10:14:03.594664"
                    }
                ],
                "finished": [
                    {
                        "id": "2f16646cfcaf11e1b0090800272a6d06",
                        "spider": "spider3",
                        "start_time": "2012-09-12 10:14:03.594664",
                        "end_time": "2012-09-12 10:24:03.594664"
                    }
                ]
            }
            """)

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