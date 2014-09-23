# vim:fileencoding=UTF-8

from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import unittest

import mock

from web_runner.scrapyd import ScrapydInterface


class ScrapydInterfaceTest(unittest.TestCase):

    URL = 'http://example.com'

    EXPECTED_URL = URL + 'listjobs.json?project=test'

    EMPTY_QUEUE = {'running': 0, 'finished': 0, 'pending': 0}

    def test_when_queues_are_empty_then_it_should_return_empty_queues(self):
        subject = ScrapydInterface(ScrapydInterfaceTest.URL)

        with mock.patch('web_runner.scrapyd.requests') as mock_requests:
            response = mock_requests.get.return_value
            response.json.return_value = {
                "status": "ok", "pending": [], "running": [], "finished": [],
            }

            queues, summary = subject.get_queues(['test'])

            self.assertEqual({'test': self.EMPTY_QUEUE}, queues)
            self.assertEqual(self.EMPTY_QUEUE, summary)

            mock_requests.get.assert_called_once_with(self.EXPECTED_URL)

    def test_when_queues_have_jobs_then_it_should_return_their_state(self):
        subject = ScrapydInterface(ScrapydInterfaceTest.URL)

        with mock.patch('web_runner.scrapyd.requests') as mock_requests:
            response = mock_requests.get.return_value
            response.json.return_value = {
                "status": "ok",
                "pending": [
                    {
                        "id": "78391cc0fcaf11e1b0090800272a6d06",
                        "project_name": "spider1",
                    }
                ],
                "running": [],
                "finished": [
                    {
                        "id": "2f16646cfcaf11e1b0090800272a6d06",
                        "spider": "spider3",
                        "start_time": "2012-09-12 10:14:03.594664",
                        "end_time": "2012-09-12 10:24:03.594664"
                    }
                ],
            }

            queues, summary = subject.get_queues(['test'])

            expected_queue = {'running': 0, 'finished': 1, 'pending': 1}

            self.assertEqual({'test': expected_queue}, queues)
            self.assertEqual(expected_queue, summary)

            mock_requests.get.assert_called_once_with(self.EXPECTED_URL)
