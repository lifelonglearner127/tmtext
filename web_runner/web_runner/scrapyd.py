#!/usr/bin/env python
import logging
import urlparse
import json
import os.path
import time
import urllib
import urllib2

from util import string_from_local2utc as local2utc

import enum
import pyramid.httpexceptions as exc
import requests
import requests.exceptions


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


class ScrapydMediator(object):

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

        self.scrapyd_base_url = settings[ScrapydMediator.SCRAPYD_BASE_URL]
        self.scrapyd_items_path = settings[ScrapydMediator.SCRAPYD_ITEMS_PATH]

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
        if queue_status == ScrapydMediator.JobStatus.unknown:
            raise ScrapydJobStartError(
                "ok",
                "Timeout on waiting for Scrapyd to list job '%s'." % jobid,
            )

        return jobid

    def report_on_job(self, jobid, timeout=1.0):
        url = urlparse.urljoin(self.scrapyd_base_url, 'listjobs.json') \
            + '?' + urllib.urlencode({'project': self.config.project_name})
        response = self._fetch_json(url)
        if response['status'] != "ok":
            LOG.error("Scrapyd was not OK: %s", json.dumps(response))
            raise exc.HTTPBadGateway(
                "Scrapyd was not OK, it was '{status}': {message}".format(
                    **response))

        if any(job_desc['id'] == jobid for job_desc in response['finished']):
            status = ScrapydMediator.JobStatus.finished
        elif any(job_desc['id'] == jobid for job_desc in response['pending']):
            status = ScrapydMediator.JobStatus.pending
        elif any(job_desc['id'] == jobid for job_desc in response['running']):
            status = ScrapydMediator.JobStatus.running
        elif os.path.exists(self.retrieve_job_data_fn(jobid)):
            LOG.warn("Scrapyd doesn't know the job but the file is present.")
            status = ScrapydMediator.JobStatus.finished
        else:
            status = ScrapydMediator.JobStatus.unknown

        return status

    def report_on_job_with_retry(self, jobid, timeout=1.0):
        """Waits that a jobid appears in a valid scrapyd queue

        :returns False if it does not appears after retries
        """
        retry_count = 1 + int(timeout / ScrapydMediator._VERIFICATION_DELAY)
        for _ in range(retry_count):
            status = self.report_on_job(jobid)
            if status != ScrapydMediator.JobStatus.unknown:
                break
            LOG.debug(
                "Job %s not ready. Waiting %g before retrying.",
                jobid,
                ScrapydMediator._VERIFICATION_DELAY,
            )
            time.sleep(ScrapydMediator._VERIFICATION_DELAY)

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


class ScrapydInterface(object):
    """Interface to Scrapyd

    The main difference with ScrapydMediator, is that this class is not
    oriented to have a spider.
    This class is useful to return status and information about ScrapyD
    """

    def __init__(self, url):
        self.scrapyd_url = url

    def is_alive(self):
        """Returns whether scrapyd is alive."""
        try:
            req = requests.get(self.scrapyd_url)
        except requests.exceptions.RequestException:
            return False

        return req.status_code == 200

    def get_projects(self):
        """Get the list of scrapyd projects.

        :returns: A tuple with:
         * 0: boolean with Scrapyd operational status
         * 1: list of scrapyd projects
        """
        url = self.scrapyd_url + 'listprojects.json'
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return False, None
       
        output = json.loads(req.text)
        status = output['status'].lower() == 'ok'
        projects = output['projects']

        return status, projects

    def get_spiders(self, project):
        if not project:
            return None

        url = "%slistspiders.json?project=%s" % (self.scrapyd_url, project)
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None

        output = json.loads(req.text)
        if output['status'].lower() == 'ok':
            spiders = output['spiders']
        else:
            spiders = None

        return spiders

    def get_jobids_status(self, projects=None):
        """Return the status of the jobids associated to a project.

        The function returns a dictionary whose key is a jobid and the value
        is a dictionary of Scrapyd's listjobs request structure.

        :param projects: The list of project to query. If it is None, all
                         projects will be queried.
        """

        if not projects:
            status, projects = self.get_projects()
            if not status:
                return None

        ret = {}
        for project in projects:
            url = '%slistjobs.json?project=%s' % (self.scrapyd_url, project)
            try:
                req = requests.get(url)
            except requests.exceptions.RequestException:
                return None

            req_output = req.json()
            if req_output['status'].lower() == 'ok':
                for status in ('running', 'finished', 'pending'):
                    for job_dict in req_output[status]:
                        id = job_dict['id']
                        # Convert the date from local to UTC
                        if 'start_time' in job_dict:
                            job_dict['start_time'] = local2utc(job_dict['start_time'])
                        if 'end_time' in job_dict:
                            job_dict['end_time'] = local2utc(job_dict['end_time'])
                        ret[id] = job_dict
                        ret[id]['status'] = status
        
        return ret



    def get_queues(self, projects=None):
        """Returns the scrapyd queue status.

        The function returns a dictionary whose key a project. The value
        is another dictionary with 'running', 'finished' and 'pending' queues.
        Also, there is another key called 'summary', with the total queues.

        :param projects: The list of project to query. If it is None, all
                         projects will be queried.
        """
        if not projects:
            status, projects = self.get_projects()
            if not status:
                return None

        queues = {}
        for project in projects:
            url = '%slistjobs.json?project=%s' % (self.scrapyd_url, project)
            try:
                req = requests.get(url)
            except requests.exceptions.RequestException:
                return None

            req_output = req.json()
            summary = {'running':0, 'finished':0, 'pending':0}
            if req_output['status'].lower() == 'ok':
                queues[project] = {}
                for status in ('running', 'finished', 'pending'):
                    queues[project][status] = len(req_output[status])
                    summary[status] += len(req_output[status])
                    
        return (queues, summary)




if __name__ == '__main__':
    si = ScrapydInterface('http://localhost:6800/')

    status, projects = si.get_projects()
    print('projects: %s' % projects)

    spiders = {project: si.get_spiders(project) for project in projects}
    print('spiders:', spiders)

    jobidsDict = si.get_jobids_status()
    print("jobids:", jobidsDict)

# vim: set expandtab ts=4 sw=4:
