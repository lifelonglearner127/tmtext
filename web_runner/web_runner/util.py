import collections
from itertools import count
import logging
import urlparse
import json
import urllib
import urllib2

import enum
import pyramid.httpexceptions as exc


LOG = logging.getLogger(__name__)


SpiderConfig = collections.namedtuple('SpiderConfig',
                                      ['spider_name', 'project_name'])


CommandConfig = collections.namedtuple(
    'CommandConfig', ['cmd', 'content_type', 'spider_configs'])


def find_spider_config(settings, path):
    path = path.strip('/')

    for type_name in settings['spider._names'].split():
        prefix = 'spider.{}.'.format(type_name)

        resource = settings[prefix + 'resource']
        if resource.strip('/') == path:
            return SpiderConfig(
                settings[prefix + 'spider_name'],
                settings[prefix + 'project_name'],
            )
    return None


def find_command_config(settings, path):
    path = path.strip('/')

    for type_name in settings['command._names'].split():
        prefix = 'command.{}.'.format(type_name)

        resource = settings[prefix + 'resource']
        if resource.strip('/') == path:
            return CommandConfig(
                settings[prefix + 'cmd'],
                settings[prefix + 'content_type'],
                list(find_command_crawls(settings, prefix + 'crawl.')),
            )
    return None


def find_command_crawls(settings, prefix):
    try:
        for i in count():
            project_name_key = prefix + str(i) + '.project-name'
            spider_name_key = prefix + str(i) + '.spider-name'
            yield SpiderConfig(
                settings[spider_name_key], settings[project_name_key])
    except KeyError:
        pass  # No more crawlers.


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
