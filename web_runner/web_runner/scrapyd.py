import logging
import urlparse
import json
import urllib
import urllib2

import enum
import pyramid.httpexceptions as exc

from web_runner.config_util import find_spider_config


LOG = logging.getLogger(__name__)


class ScrapydMediator(object):

    SCRAPYD_BASE_URL = 'spider._scrapyd.base_url'

    FILE_SERVER_BASE_URL = 'spider._result.base_url'

    class JobStatus(enum.Enum):
        unknown = 0
        running = 1
        finished = 2
        pending = 3

    @staticmethod
    def from_resource(settings, path):
        return ScrapydMediator(settings, find_spider_config(settings, path))

    def __init__(self, settings, spider_config):
        if spider_config is None:
            raise exc.HTTPNotFound("Unknown resource.")

        self.scrapyd_base_url = settings[ScrapydMediator.SCRAPYD_BASE_URL]
        self.file_server_base_url = \
            settings[ScrapydMediator.FILE_SERVER_BASE_URL]

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
        else:
            status = ScrapydMediator.JobStatus.unknown

        return status

    def retrieve_job_data(self, jobid):
        url = urlparse.urljoin(
            self.file_server_base_url,
            "{}/{}/{}.jl".format(
                self.config.project_name, self.config.spider_name, jobid)
        )
        return urllib2.urlopen(url)

    @staticmethod
    def _fetch_json(url, data=None):
        conn = urllib2.urlopen(url, data)
        response = json.load(conn)
        conn.close()

        return response
