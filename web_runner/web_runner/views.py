from __future__ import division, absolute_import, unicode_literals

import logging
import subprocess
import urllib2

import pyramid.httpexceptions as exc
from pyramid.view import view_config

from web_runner.config_util import find_command_config, SpiderConfig
from web_runner.scrapyd import ScrapydMediator


LOG = logging.getLogger(__name__)


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

    mediator = ScrapydMediator.from_resource(settings, request.path)
    response = mediator.start_job(request.params)

    if response['status'] != "ok":
        raise exc.HTTPBadGateway(
            "Scrapyd was not OK, it was '{status}': {message}".format(
                **response))
    raise exc.HTTPFound(
        location=request.route_path("spider pending jobs",
                                    project=mediator.config.project_name,
                                    spider=mediator.config.spider_name,
                                    jobid=response['jobid']),
        detail="Job '%s' started." % response['jobid'])


@view_config(route_name='spider pending jobs', request_method='GET')
def spider_pending_view(request):
    project_name = request.matchdict['project']
    spider_name = request.matchdict['spider']
    job_id = request.matchdict['jobid']

    mediator = ScrapydMediator(
        request.registry.settings, SpiderConfig(spider_name, project_name))
    status = mediator.report_on_job(job_id)

    if status is ScrapydMediator.JobStatus.finished:
        raise exc.HTTPFound(
            location=request.route_path("spider job results",
                                        project=project_name,
                                        spider=spider_name,
                                        jobid=job_id),
            detail="Job finished.")

    state = 'Job state unknown.'
    if status is ScrapydMediator.JobStatus.pending:
        state = "Job still waiting to run"
    elif status is ScrapydMediator.JobStatus.running:
        state = "Job running."
    raise exc.HTTPAccepted(detail=state)


@view_config(route_name='spider job results', request_method='GET',
             http_cache=3600)
def spider_results_view(request):
    project_name = request.matchdict['project']
    spider_name = request.matchdict['spider']
    job_id = request.matchdict['jobid']

    mediator = ScrapydMediator(
        request.registry.settings, SpiderConfig(spider_name, project_name))
    try:
        data_stream = mediator.retrieve_job_data(job_id)
        request.response.body_file = data_stream
        return request.response
    except urllib2.HTTPError as e:
        raise exc.HTTPBadGateway(
            detail="The file server doesn't have the expected content: %s" % e)
