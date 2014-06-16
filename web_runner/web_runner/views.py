from __future__ import division, absolute_import, unicode_literals

import base64
import logging
import os
import pickle
import tempfile
import urllib2
import zlib

import pyramid.httpexceptions as exc
from pyramid.view import view_config
import subprocess32 as subprocess
from toolz.itertoolz import first

from web_runner.config_util import find_command_config_from_path, \
    find_command_config_from_name, SpiderConfig
from web_runner.scrapyd import ScrapydMediator
from web_runner.util import pump


LOG = logging.getLogger(__name__)


def encode_ids(ids):
    return base64.urlsafe_b64encode(
        zlib.compress(
            pickle.dumps(ids, pickle.HIGHEST_PROTOCOL),
            zlib.Z_BEST_COMPRESSION))


def decode_ids(s):
    return pickle.loads(zlib.decompress(base64.urlsafe_b64decode(
        # The framework will automatically decode it as Unicode but it's ASCII.
        s.encode('ascii'))))


def command_start_view(request):
    """Schedules running a command plus spiders."""
    settings = request.registry.settings
    cfg_templates = find_command_config_from_path(settings, request.path)
    if cfg_templates is None:
        raise exc.HTTPNotFound("Unknown resource.")

    spider_cfgs = []
    for cfg_template in cfg_templates.spider_configs:
        spider_cfgs.append(SpiderConfig(
            cfg_template.spider_name.format(request.params),
            cfg_template.project_name.format(request.params)
        ))

    spider_job_ids = []
    for spider_cfg in spider_cfgs:
        response = ScrapydMediator(settings, spider_cfg).start_job(
            request.params)
        if response['status'] != "ok":
            raise exc.HTTPBadGateway(
                "Failed to start a required crawl for command '{}'."
                " Scrapyd was not OK, it was '{status}': {message}".format(
                    cfg_templates.name, **response)
            )
        spider_job_ids.append(response['jobid'])
        LOG.info("For command at '%s', started crawl job with id '%s'.",
                 cfg_templates.name, response['jobid'])

    raise exc.HTTPFound(
        location=request.route_path(
            "command pending jobs",
            name=cfg_templates.name,
            jobid=encode_ids(spider_job_ids),
            _query=request.params,
        ),
        detail="Command '{}' started with {} crawls.".format(
            cfg_templates.name, len(spider_job_ids))
    )


@view_config(route_name='command pending jobs', request_method='GET',
             http_cache=1)  # Not to get hammered.
def command_pending(request):
    """Report on running job status."""
    name = request.matchdict['name']
    encoded_job_ids = request.matchdict['jobid']
    job_ids = decode_ids(encoded_job_ids)

    settings = request.registry.settings
    cfg = find_command_config_from_name(settings, name)
    if cfg is None:
        raise exc.HTTPNotFound("Unknown resource.")

    running = 0
    for job_id, spider_cfg in zip(job_ids, cfg.spider_configs):
        status = ScrapydMediator(settings, spider_cfg).report_on_job(job_id)
        if status is ScrapydMediator.JobStatus.unknown:
            msg = "Job for spider '{}' with id '{}' has an unknown status." \
                " Aborting command run.".format(spider_cfg.spider_name, job_id)
            LOG.error(msg)
            raise exc.HTTPNotFound(msg)

        if status is not ScrapydMediator.JobStatus.finished:
            running += 1

    if running:
        raise exc.HTTPAccepted(detail="Crawlers still running: %d" % running)
    else:
        raise exc.HTTPFound(
            location=request.route_path(
                "command job results",
                name=name,
                jobid=encoded_job_ids,
                _query=request.params,
            ),
            detail="Crawlers finished.")


@view_config(route_name='command job results', request_method='GET',
             http_cache=3600)
def command_result(request):
    """Report result of job."""
    name = request.matchdict['name']
    encoded_job_ids = request.matchdict['jobid']
    job_ids = decode_ids(encoded_job_ids)

    settings = request.registry.settings
    cfg = find_command_config_from_name(settings, name)
    if cfg is None:
        raise exc.HTTPNotFound("Unknown resource.")

    # This is slightly dangerous. Under load, by opening all connections at
    # once we may run out of file descriptors. We cannot keep everything in
    # memory either so the safer alternative would be to save to disk although
    # we can run out of disc space... oh well.
    pipes = []
    for job_id, spider_cfg in zip(job_ids, cfg.spider_configs):
        data_stream = ScrapydMediator(settings, spider_cfg).retrieve_job_data(
            job_id)

        # Create named pipes for each data stream.
        filename = tempfile.mktemp()
        os.mkfifo(filename)
        fifo_fd = os.open(filename, os.O_WRONLY | os.O_NONBLOCK)
        pipes.append((
            filename,
            pump(data_stream.fileno, fifo_fd),
            fifo_fd,
        ))

    process = subprocess.Popen(
        cfg.cmd.format(**request.params) + ' ' + ' '.join(map(first, pipes)),
        stdout=subprocess.PIPE,
        shell=True,
    )

    # Feed the pipes non-blocking until there's no more data or the command
    # terminates.
    while True:
        try:
            process.wait(timeout=0.01)
            break
        except subprocess.TimeoutExpired:
            for pumper, _, _ in pipes:
                next(pumper)  # Exercise the pumps.

    # Cleanup. Close named pipes. Don't close input files as they belong to the
    # framework.
    for fn, _, fd in pipes:
        os.close(fd)
        os.unlink(fn)

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
