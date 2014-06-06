from __future__ import division, absolute_import, unicode_literals

import json
import logging
import subprocess
import urllib
import urllib2
import urlparse

import pyramid.httpexceptions as exc
from pyramid.view import view_config

from web_runner.util import find_spider_config, find_command_config


LOG = logging.getLogger(__name__)


SCRAPYD_BASE_URL = 'spider._scrapyd.base_url'
FILE_SERVER_BASE_URL = 'spider._result.base_url'


def command_view(request):
    """Runs a command blocking until it finishes."""
    settings = request.registry.settings

    # Get spider of resource.
    cfg = find_command_config(settings, request.path)
    if cfg is None:
        raise exc.HTTPNotFound("Unknown resource.")

    process = subprocess.Popen(
        cfg.cmd.format(**request.params),
        stdout=subprocess.PIPE,
        shell=True,
    )

    request.response.content_type = cfg.content_type
    request.response.body_file = process.stdout
    return request.response


def spider_start_view(request):
    """Starts job in Scrapyd and redirects to the "spider pending jobs" view."""
    settings = request.registry.settings

    # Get spider of resource.
    cfg = find_spider_config(settings, request.path)
    if cfg is None:
        raise exc.HTTPNotFound("Unknown resource.")

    scrapyd_base_url = settings[SCRAPYD_BASE_URL]
    try:
        spider_name = cfg.spider_name.format(**request.params)
        project_name = cfg.project_name.format(**request.params)
    except KeyError as e:
        raise exc.HTTPBadRequest(detail="Query parameter %s is required." % e)

    url = urlparse.urljoin(scrapyd_base_url, 'schedule.json')
    # FIXME Handle multivalued setting as in setting.
    data = dict(request.params)
    data.update({
        'project': project_name,
        'spider': spider_name,
    })
    LOG.info("Calling Scrapyd on '%s' with parameters: %s", url, data)
    conn = urllib2.urlopen(url, urllib.urlencode(data))
    response = json.load(conn)
    conn.close()

    if response['status'] != "ok":
        raise exc.HTTPBadGateway(
            "Scrapyd was not OK, it was '{status}': {message}".format(
                **response))
    raise exc.HTTPFound(
        location=request.route_path("spider pending jobs",
                                    project=project_name,
                                    spider=spider_name,
                                    jobid=response['jobid']),
        detail="Job '%s' started." % response['jobid'])


@view_config(route_name='spider pending jobs', request_method='GET')
def spider_pending_view(request):
    project_name = request.matchdict['project']
    spider_name = request.matchdict['spider']
    job_id = request.matchdict['jobid']

    base_url = request.registry.settings[SCRAPYD_BASE_URL]
    url = urlparse.urljoin(base_url, 'listjobs.json') \
        + '?' + urllib.urlencode({'project': project_name})
    conn = urllib2.urlopen(url)
    response = json.load(conn)
    conn.close()

    if response['status'] != "ok":
        LOG.error("Scrapyd was not OK: %s", json.dumps(response))
        raise exc.HTTPBadGateway(
            "Scrapyd was not OK, it was '{status}': {message}".format(
                **response))

    if any(job_desc['id'] == job_id for job_desc in response['finished']):
        raise exc.HTTPFound(
            location=request.route_path("spider job results",
                                        project=project_name,
                                        spider=spider_name,
                                        jobid=job_id),
            detail="Job finished.")
    state = 'Job state unknown.'
    if any(job_desc['id'] == job_id for job_desc in response['pending']):
        state = "Job still waiting to run"
    if any(job_desc['id'] == job_id for job_desc in response['running']):
        state = "Job running."
    raise exc.HTTPAccepted(detail=state)


@view_config(route_name='spider job results', request_method='GET',
             http_cache=3600)
def spider_results_view(request):
    project_name = request.matchdict['project']
    spider_name = request.matchdict['spider']
    job_id = request.matchdict['jobid']

    base_url = request.registry.settings[FILE_SERVER_BASE_URL]
    url = urlparse.urljoin(
        base_url, "{}/{}/{}.jl".format(project_name, spider_name, job_id))
    try:
        conn = urllib2.urlopen(url)
        request.response.body_file = conn
        return request.response
    except urllib2.HTTPError as e:
        raise exc.HTTPBadGateway(
            detail="The file server doesn't have the expected content: %s" % e)
