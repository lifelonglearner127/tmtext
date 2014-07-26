#!/usr/bin/env python
import logging
import urlparse
import json
import os.path
import urllib
import urllib2

import enum
import pyramid.httpexceptions as exc
import requests
import json


LOG = logging.getLogger(__name__)


class ScrapydMediator(object):

    SCRAPYD_BASE_URL = 'spider._scrapyd.base_url'

    SCRAPYD_ITEMS_PATH = 'spider._scrapyd.items_path'

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

    def start_job(self, params):
        try:
            spider_name = self.config.spider_name.format(**params)
            project_name = self.config.project_name.format(**params)
        except KeyError as e:
            raise exc.HTTPBadRequest(
                detail="Query parameter %s is required." % e)

        url = urlparse.urljoin(self.scrapyd_base_url, 'schedule.json')
        # FIXME Handle multivalued setting as in setting.
        data = dict(params)
        data.update({
            'project': project_name,
            'spider': spider_name,
        })
        LOG.info("Calling Scrapyd on '%s' with parameters: %s", url, data)

        return self._fetch_json(url, urllib.urlencode(data))

    def report_on_job(self, jobid):
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

    def retrieve_job_data(self, jobid):
        """Returns a file like object with the job's result."""
        return open(self.retrieve_job_data_fn(jobid))

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
        conn = urllib2.urlopen(url, data)
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
        """Return if scrapyd is alive"""

        try:
            req = requests.get(self.scrapyd_url)
        except requests.exceptions.RequestException, e:
            return False

        return req.status_code == 200


    def get_projects(self):
        """Get the list of scrapyd project

        returns a tuple with:
         * 0: boolean with Scrapyd operational status
         * 1: list of scrapyd projects
        """
        url = self.scrapyd_url + 'listprojects.json'
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException, e:
            return (False, None)
       
        output = json.loads(req.text)
        status = output['status'].lower() == 'ok'
        projects = output['projects']

        return (status, projects)


    def get_spiders(self, project):
        """
        """
        if not project:
            return None

        url = "%slistspiders.json?project=%s" % (self.scrapyd_url, 
          project)
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException, e:
            return None

        output = json.loads(req.text)
        if output['status'].lower() == 'ok':
            spiders = output['spiders']
        else:
            spiders = None

        return spiders


    def get_jobids_status(self, projects=None):
        """Return the status of the jobids associated to a project

        The function returns a dictionary whose key is a jobid and the value
        is a dictionary of Scrapyd's listjobs request structure

        projects parameter is the list of project to query. If it is None,
        get_jobids_status will query all projects
        """

        if not projects:
            (status, projects) = self.get_projects()
            if not status:
                return None

        ret = {}
        for project in projects:
            url = '%slistjobs.json?project=%s' % (self.scrapyd_url,
              project)
            try:
                req = requests.get(url)
            except requests.exceptions.RequestException, e:
                return None

            req_output = req.json()
            if req_output['status'].lower() == 'ok':
                for status in ('running', 'finished', 'pending'):
                    for job_dict in req_output[status]:
                        id = job_dict['id']
                        ret[id] = job_dict
                        ret[id]['status'] = status
        
        return ret



if __name__ == '__main__':
    si = ScrapydInterface('http://localhost:6800/')

    (status, projects) = si.get_projects()
    print('projects: %s' % projects)

    spiders = {project: si.get_spiders(project) for project in projects}
    print('spiders: %s' % spiders)

    jobidsDict = si.get_jobids_status()
    print("jobids: %s" % jobidsDict)

# vim: set expandtab ts=4 sw=4:
