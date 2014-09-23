# vim:fileencoding=UTF-8

from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import logging
import unittest

import mock
import pyramid.httpexceptions as exc

from web_runner.scrapyd import ScrapydInterface


logging.basicConfig(level=logging.FATAL)


class ScrapydInterfaceTest(unittest.TestCase):

    maxDiff = None

    URL = 'http://example.com'

    EXPECTED_LIST_JOBS_URL = URL + '/listjobs.json?project=test'
    EXPECTED_LIST_PROJECTS_URL = URL + '/listprojects.json'
    EXPECTED_LIST_SPIDERS_URL = URL + '/listspiders.json?project=test'

    EMPTY_QUEUE = {'running': 0, 'finished': 0, 'pending': 0}

    def setUp(self):
        # Always clear the cache so that tests are independent.
        ScrapydInterface._CACHE.clear()

        self.subject = ScrapydInterface(ScrapydInterfaceTest.URL)

    def test_when_status_is_not_ok_then_it_should_report_an_error(self):
        with mock.patch('web_runner.scrapyd.requests') as mock_requests:
            response = mock_requests.get.return_value
            response.json.return_value = {"status": "ERROR", "message": "Test"}

            self.assertRaises(
                exc.HTTPBadGateway, self.subject.get_queues, ['test'])

            mock_requests.get.assert_called_once_with(
                self.EXPECTED_LIST_JOBS_URL)

    def test_when_queues_are_empty_then_it_should_return_empty_queues(self):
        with mock.patch('web_runner.scrapyd.requests') as mock_requests:
            response = mock_requests.get.return_value
            response.json.return_value = {
                "status": "ok", "pending": [], "running": [], "finished": [],
            }

            queues, summary = self.subject.get_queues(['test'])

            self.assertEqual({'test': self.EMPTY_QUEUE}, queues)
            self.assertEqual(self.EMPTY_QUEUE, summary)

            mock_requests.get.assert_called_once_with(
                self.EXPECTED_LIST_JOBS_URL)

    def test_when_queues_have_jobs_then_it_should_return_their_state(self):
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

            queues, summary = self.subject.get_queues(['test'])

            expected_queue = {'running': 0, 'finished': 1, 'pending': 1}

            self.assertEqual({'test': expected_queue}, queues)
            self.assertEqual(expected_queue, summary)

            mock_requests.get.assert_called_once_with(
                self.EXPECTED_LIST_JOBS_URL)

    def test_when_a_request_is_repeated_then_it_should_query_just_once(self):
        with mock.patch('web_runner.scrapyd.requests') as mock_requests:
            response = mock_requests.get.return_value
            response.json.return_value = {
                "status": "ok", "pending": [], "running": [], "finished": [],
            }

            queues, summary = self.subject.get_queues(['test'])
            self.assertEqual({'test': self.EMPTY_QUEUE}, queues)
            self.assertEqual(self.EMPTY_QUEUE, summary)

            queues, summary = self.subject.get_queues(['test'])
            self.assertEqual({'test': self.EMPTY_QUEUE}, queues)
            self.assertEqual(self.EMPTY_QUEUE, summary)

            mock_requests.get.assert_called_once_with(
                self.EXPECTED_LIST_JOBS_URL)

    def test_when_there_are_no_project_then_it_should_get_an_empty_list(self):
        with mock.patch('web_runner.scrapyd.requests') as mock_requests:
            response = mock_requests.get.return_value
            response.json.return_value = {"status": "ok", "projects": []}

            projects = self.subject.get_projects()
            self.assertEqual([], projects)

            mock_requests.get.assert_called_once_with(
                self.EXPECTED_LIST_PROJECTS_URL)

    def test_when_there_are_projects_then_it_should_get_a_list(self):
        with mock.patch('web_runner.scrapyd.requests') as mock_requests:
            response = mock_requests.get.return_value
            response.json.return_value = {
                "status": "ok",
                "projects": [
                    "proj1",
                    "proj2",
                ],
            }

            projects = self.subject.get_projects()
            self.assertEqual(["proj1", "proj2"], projects)

            mock_requests.get.assert_called_once_with(
                self.EXPECTED_LIST_PROJECTS_URL)

    def test_when_there_are_no_jobs_then_it_should_get_an_empty_dict(self):
        with mock.patch('web_runner.scrapyd.requests') as mock_requests:
            response = mock_requests.get.return_value
            response.json.return_value = {
                "status": "ok", "pending": [], "running": [], "finished": [],
            }

            jobs = self.subject.get_jobs(['test'])

            self.assertEqual({}, jobs)

            mock_requests.get.assert_called_once_with(
                self.EXPECTED_LIST_JOBS_URL)

    def test_when_there_are_jobs_then_it_should_return_them(self):
        # Had to remove dates from jobs to make tests reliable.
        # The time conversion that's performed adds a configuration dependent
        # offset and a small, millisecond, error.
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
                    }
                ],
            }

            jobs = self.subject.get_jobs(['test'])

            expected = {
                '2f16646cfcaf11e1b0090800272a6d06': {
                    'id': '2f16646cfcaf11e1b0090800272a6d06',
                    'spider': 'spider3',
                    'status': 'finished',
                },
                '78391cc0fcaf11e1b0090800272a6d06': {
                    'id': '78391cc0fcaf11e1b0090800272a6d06',
                    'project_name': 'spider1',
                    'status': 'pending',
                },
            }
            self.assertEqual(expected, jobs)

            mock_requests.get.assert_called_once_with(
                self.EXPECTED_LIST_JOBS_URL)

    def test_when_there_are_no_spiders_then_it_should_get_an_empty_list(self):
        with mock.patch('web_runner.scrapyd.requests') as mock_requests:
            response = mock_requests.get.return_value
            response.json.return_value = {"status": "ok", "spiders": []}

            jobs = self.subject.get_spiders('test')

            self.assertEqual([], jobs)

            mock_requests.get.assert_called_once_with(
                self.EXPECTED_LIST_SPIDERS_URL)

    def test_when_there_are_spiders_then_it_should_return_them(self):
        # Had to remove dates from jobs to make tests reliable.
        # The time conversion that's performed adds a configuration dependent
        # offset and a small, millisecond, error.
        with mock.patch('web_runner.scrapyd.requests') as mock_requests:
            response = mock_requests.get.return_value
            response.json.return_value = {
                "status": "ok",
                "spiders": ["spider1", "spider2", "spider3"],
            }

            jobs = self.subject.get_spiders('test')

            self.assertEqual(["spider1", "spider2", "spider3"], jobs)

            mock_requests.get.assert_called_once_with(
                self.EXPECTED_LIST_SPIDERS_URL)
