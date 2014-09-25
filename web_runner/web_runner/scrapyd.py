# vim:fileencoding=UTF-8

from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import logging
import urlparse
import json
import os.path
import time
import thread
import urllib
import urllib2

import enum
import pyramid.httpexceptions as exc
import requests
import requests.exceptions
import repoze.lru

from .util import string_from_local2utc as local2utc


LOG = logging.getLogger(__name__)


class ScrapydJobException(Exception):
    """Base ScrapydMediator exception."""

    def __init__(self, message):
        super(ScrapydJobException, self).__init__()

        self.message = message


class ScrapydJobStartError(ScrapydJobException):
    """The job failed to start."""

    def __init__(self, status, message):
        super(ScrapydJobException, self).__init__(message)

        self.status = status


class ScrapydJobHelper(object):

    SCRAPYD_BASE_URL = 'spider._scrapyd.base_url'

    SCRAPYD_ITEMS_PATH = 'spider._scrapyd.items_path'

    _VERIFICATION_DELAY = 0.1

    class JobStatus(enum.Enum):
        unknown = 0
        running = 1
        finished = 2
        pending = 3

    def __init__(self, settings, spider_config):
        if spider_config is None:
            raise exc.HTTPNotFound("Unknown resource.")

        self.scrapyd_base_url = settings[ScrapydJobHelper.SCRAPYD_BASE_URL]
        self.scrapyd_items_path = settings[ScrapydJobHelper.SCRAPYD_ITEMS_PATH]

        self.config = spider_config

    def start_job(self, params, timeout=1.0):
        """Returns the job ID of the started Scrapyd job.

        :param params: Parameters for the job to be started.
        :param timeout: Seconds to wait for Scrapy to show the job.
        """
        try:
            spider_name = self.config.spider_name.format(**params)
            project_name = self.config.project_name.format(**params)
        except KeyError as e:
            raise ScrapydJobException("Parameter %s is required." % e)

        url = urlparse.urljoin(self.scrapyd_base_url, 'schedule.json')
        # Convert to a list of pairs to handle multivalued parameters.
        data = list(filter(
            lambda (k, _): k not in {'project', 'spider'},
            params.items()
        ))
        data.append(('project', project_name))
        data.append(('spider', spider_name))

        LOG.info("Calling Scrapyd on '%s' with parameters: %s", url, data)
        result = self._fetch_json(url, data)
        if result['status'] != "ok":
            raise ScrapydJobStartError(
                result['status'],
                "Failed to start job with parameters: %r" % data,
            )
        jobid = result['jobid']

        # Wait until the job appears in the list of jobs.
        queue_status = self.report_on_job_with_retry(jobid, timeout=timeout)
        if queue_status == ScrapydJobHelper.JobStatus.unknown:
            raise ScrapydJobStartError(
                "ok",
                "Timeout on waiting for Scrapyd to list job '%s'." % jobid,
            )

        return jobid

    def report_on_job(self, jobid):
        """Returns the status of a job."""
        url = urlparse.urljoin(self.scrapyd_base_url, 'listjobs.json') \
            + '?' + urllib.urlencode({'project': self.config.project_name})
        response = self._fetch_json(url)
        if response['status'] != "ok":
            LOG.error("Scrapyd was not OK: %s", json.dumps(response))
            raise exc.HTTPBadGateway(
                "Scrapyd was not OK, it was '{status}': {message}".format(
                    **response))

        if any(job_desc['id'] == jobid for job_desc in response['finished']):
            status = ScrapydJobHelper.JobStatus.finished
        elif any(job_desc['id'] == jobid for job_desc in response['pending']):
            status = ScrapydJobHelper.JobStatus.pending
        elif any(job_desc['id'] == jobid for job_desc in response['running']):
            status = ScrapydJobHelper.JobStatus.running
        elif os.path.exists(self.retrieve_job_data_fn(jobid)):
            LOG.warn("Scrapyd doesn't know the job but the file is present.")
            status = ScrapydJobHelper.JobStatus.finished
        else:
            status = ScrapydJobHelper.JobStatus.unknown

        return status

    def report_on_job_with_retry(self, jobid, timeout=1.0):
        """Returns the status of a job."""
        retry_count = 1 + timeout // ScrapydJobHelper._VERIFICATION_DELAY
        for _ in range(int(retry_count)):
            status = self.report_on_job(jobid)
            if status != ScrapydJobHelper.JobStatus.unknown:
                break

            LOG.debug(
                "Job %s not ready. Waiting %g before retrying.",
                jobid,
                ScrapydJobHelper._VERIFICATION_DELAY,
            )
            time.sleep(ScrapydJobHelper._VERIFICATION_DELAY)

        return status

    def retrieve_job_data(self, jobid):
        """Returns a file like object with the job's result."""
        try:
            return open(self.retrieve_job_data_fn(jobid))
        except IOError as e:
            msg = "Failed to open data file: %s" % e
            LOG.exception(msg)
            raise ScrapydJobException(msg)

    def retrieve_job_data_fn(self, jobid):
        """Returns the path to the job's data file."""
        path = os.path.normpath(os.path.expanduser(
            self.scrapyd_items_path.format(
                project_name=self.config.project_name,
                spider_name=self.config.spider_name,
            )
        ))
        return os.path.join(path, "%s.jl" % jobid)

    @staticmethod
    def _fetch_json(url, data=None):
        enc_data = None
        if data is not None:
            enc_data = urllib.urlencode(data)

        conn = urllib2.urlopen(url, enc_data)
        response = json.load(conn)
        conn.close()

        return response


class Scrapyd(object):
    """Interface to Scrapyd."""

    _CACHE = repoze.lru.ExpiringLRUCache(100, 10)
    _CACHE_LOCK = thread.allocate_lock()

    def __init__(self, url):
        self.scrapyd_url = url

    def _make_uncached_request(self, url):
        try:
            response = requests.get(url)
            LOG.debug(
                "Requested from scrapyd resource %s and got: %s",
                url,
                response.content,
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            msg = "Error contacting Scrapyd: %s" % e
            LOG.error(msg)
            raise exc.HTTPBadGateway(msg)

    def _make_request(self, resource, fresh=False, cache_time=None, **query):
        """Makes a request to the configured Scrapyd instance for the resource
        passing the given query string.

        :param resource: The resource to request.
        :type resource: unicode
        :param fresh: Whether to invalidate the cache.
        :type fresh: bool
        :param cache_time: For how many seconds a fresh response would be valid.
        :type cache_time: int
        :param query: The query string parameters.
        :return: The structure from the decoded JSON.
        """
        url = urlparse.urljoin(self.scrapyd_url, resource)
        if query:
            url += '?' + urllib.urlencode(query)

        if fresh:
            LOG.debug("Invalidated cache for %r.", url)
            Scrapyd._CACHE.invalidate(url)
            result = None
        else:
            result = Scrapyd._CACHE.get(url)

        if result is not None:
            LOG.debug("Cache hit for %r.", url)
        else:
            LOG.debug("Cache miss for %r.", url)
            # Will get exclusive access to the cache.
            with Scrapyd._CACHE_LOCK:
                # Before we got access, it may have been populated.
                result = Scrapyd._CACHE.get(url)
                if result is not None:
                    LOG.debug("Cache hit after locking for %r.", url)
                else:
                    result = self._make_uncached_request(url)

                    Scrapyd._CACHE.put(url, result, timeout=cache_time)

        # Check result response is successful.
        if result['status'].lower() != "ok":
            LOG.error("Scrapyd was not OK: %r", result)
            raise exc.HTTPBadGateway(
                "Scrapyd was not OK, it was '{status}': {message}".format(
                    **result))

        return result

    def is_alive(self):
        """Returns whether scrapyd is alive."""
        try:
            req = requests.get(self.scrapyd_url)
        except requests.exceptions.RequestException:
            return False

        return req.status_code == 200

    def get_projects(self):
        """Returns a list of Scrapyd projects."""
        projects_data = self._make_request('listprojects.json', cache_time=120)

        return projects_data['projects']

    def get_spiders(self, project):
        assert project, "A project is required."

        spiders_data = self._make_request(
            "listspiders.json", cache_time=120, project=project)

        return spiders_data['spiders']

    def get_jobs(self, projects=None):
        """Return jobs associated to a project.

        The function returns a dictionary whose key is a job's ID and the value
        is a dictionary of Scrapyd's listjobs request structure with the
        addition of the `status` key. For a finished  job, it looks like this:

        {
            "status": "finished",
            "id": "2f16646cfcaf11e1b0090800272a6d06",
            "spider": "spider3",
            "start_time": "2012-09-12 10:14:03.594664",
            "end_time": "2012-09-12 10:24:03.594664"
        }

        :param projects: The list of project to query. If it is None, all
                         projects will be queried.
        :rtype: dict
        """
        if not projects:
            projects = self.get_projects()

        jobs_by_id = {}
        for project in projects:
            jobs_by_status = self._make_request(
                'listjobs.json', project=project)

            for job_status, jobs in jobs_by_status.items():
                if job_status == "status":
                    continue  # This is not a real status, ironically.

                for job in jobs:
                    job_id = job['id']
                    # Convert the date from local to UTC
                    if 'start_time' in job:
                        job['start_time'] = local2utc(job['start_time'])
                    if 'end_time' in job:
                        job['end_time'] = local2utc(job['end_time'])
                    jobs_by_id[job_id] = job
                    jobs_by_id[job_id]['status'] = job_status

        return jobs_by_id

    def get_queues(self, projects=None):
        """Returns the scrapyd queue status.

        The function returns a dictionary whose key a project. The value
        is another dictionary with 'running', 'finished' and 'pending' queues.
        Also, there is another key called 'summary', with the total queues.

        :param projects: The list of project to query. If it is None, all
                         projects will be queried.
        :return: A list with the requested queues and the aggregate of the
                 states of all queues.
        :rtype: tuple
        """
        if not projects:
            projects = self.get_projects()

        summary = {'running': 0, 'finished': 0, 'pending': 0}
        queues = {}
        for project in projects:
            jobs_data = self._make_request('listjobs.json', project=project)

            queues[project] = {}
            for status in ('running', 'finished', 'pending'):
                queues[project][status] = len(jobs_data[status])
                summary[status] += len(jobs_data[status])

        return queues, summary

    def get_operational_status(self):
        """Returns a structure with a operational status summary for the
        Scrapyd instance as a dict.
        """
        alive = self.is_alive()
        if not alive:
            operational = False
            projects = None
            spiders = None
            queues = None
            summary_queues = None
        else:
            try:
                operational = True
                projects = self.get_projects()
                spiders = {proj: self.get_spiders(proj) for proj in projects}
                queues, summary_queues = self.get_queues(projects)
            except exc.HTTPError:
                operational = False
                projects = None
                spiders = None
                queues = None
                summary_queues = None

        status = {
            'scrapyd_alive': alive,
            'scrapyd_operational': operational,
            'scrapyd_projects': projects,
            'spiders': spiders,
            'queues': queues,
            'summarized_queue': summary_queues,
        }

        return status


# vim: set expandtab ts=4 sw=4:
