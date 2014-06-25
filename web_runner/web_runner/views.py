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

from web_runner.config_util import find_command_config_from_path, \
    find_command_config_from_name, find_spider_config_from_path, SpiderConfig
from web_runner.scrapyd import ScrapydMediator
from web_runner.util import RequestsLinePumper


LOG = logging.getLogger(__name__)


def encode_ids(ids):
    return base64.urlsafe_b64encode(
        zlib.compress(
            pickle.dumps(ids, pickle.HIGHEST_PROTOCOL),
            zlib.Z_BEST_COMPRESSION))


def decode_ids(s):
    return pickle.loads(zlib.decompress(base64.urlsafe_b64decode(
        # Pyramid will automatically decode it as Unicode but it's ASCII.
        s.encode('ascii'))))


def render_spider_config(request, spider_template_configs):
    for config_template in spider_template_configs:
        yield SpiderConfig(
            config_template.spider_name.format(**request.params),
            config_template.project_name.format(**request.params)
        )


def command_start_view(request):
    """Schedules running a command plus spiders."""
    settings = request.registry.settings
    cfg_templates = find_command_config_from_path(settings, request.path)
    if cfg_templates is None:
        raise exc.HTTPNotFound("Unknown resource.")

    spider_cfgs = render_spider_config(request, cfg_templates.spider_configs)

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
    cfg_template = find_command_config_from_name(settings, name)
    if cfg_template is None:
        raise exc.HTTPNotFound("Unknown resource.")

    spider_cfgs = render_spider_config(request, cfg_template.spider_configs)

    running = 0
    for job_id, spider_cfg in zip(job_ids, spider_cfgs):
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
    cfg_template = find_command_config_from_name(settings, name)
    if cfg_template is None:
        raise exc.HTTPNotFound("Unknown resource.")

    spider_cfgs = render_spider_config(request, cfg_template.spider_configs)

    # Create pipes.
    # This is slightly dangerous. Under load, by opening all connections at
    # once we may run out of file descriptors. We cannot keep everything in
    # memory either so the safer alternative would be to save to disk although
    # we can run out of disc space... oh well.
    LOG.info("Setting up pipes for command jobs: %s", job_ids)
    filenames = []
    input_streams = []
    for job_id, spider_cfg in zip(job_ids, spider_cfgs):
        try:
            input_streams.append(ScrapydMediator(
                settings, spider_cfg).retrieve_job_data(job_id, stream=True))

            # Create named pipes for each data stream.
            filename = tempfile.mktemp()
            os.mkfifo(filename)
            filenames.append(filename)
        except urllib2.HTTPError as e:
            raise exc.HTTPBadGateway(
                "File server error.", comment="Error message: %s" % e)

    args = dict(request.params)
    for i, fn in enumerate(filenames):
        args['spider %d' % i] = fn
    cmd_line = cfg_template.cmd.format(**args)
    LOG.info("Starting command: %s", cmd_line)
    process = subprocess.Popen(
        cmd_line,
        stdout=subprocess.PIPE,
        shell=True,
    )

    # Make sure it started.
    try:
        process.wait(timeout=0.1)

        msg = "Command died before sending data: %s" % cmd_line
        LOG.error(msg)
        raise exc.HTTPBadGateway(msg)
    except subprocess.TimeoutExpired:
        pass

    # Open the pipes for writing. This might block.
    LOG.info("Opening pipes for writing for: %s", cmd_line)
    pumpers = []
    output_pipes = []
    for fn, input_stream in zip(filenames, input_streams):
        write_fifo_fd = os.open(fn, os.O_WRONLY)

        pumpers.append(RequestsLinePumper(input_stream, write_fifo_fd))
        output_pipes.append(write_fifo_fd)

    # Feed the pipes without blocking until the command terminates.
    LOG.info("Pumping IO for: %s", cmd_line)
    output = []  # FIXME: This is bad as we are buffering in memory.
    while pumpers:
        try:
            stdout, _ = process.communicate(timeout=0.01)
            output.append(stdout)
            break
        except subprocess.TimeoutExpired:
            for pumper in pumpers[:]:
                if not pumper.pump():
                    pumpers.remove(pumper)

    # Cleanup. Close named pipes.
    # Don't close input files as they belong to the framework.
    LOG.info("Clean up for: %s", cmd_line)
    for fn, fd in zip(filenames, output_pipes):
        try:
            os.close(fd)
        except:
            # If failed to close, it's bad but continue.
            LOG.info("Failed to close file '%s'.", fn)
        finally:
            os.unlink(fn)

    try:
        LOG.info("Waiting for process to finish...")
        stdout, _ = process.communicate(timeout=5)
        output.append(stdout)
        LOG.info("Process finished.")
    except subprocess.TimeoutExpired:
        process.kill()
        LOG.warn("Process killed as it took too long.")

    LOG.info("Command generated %s bytes.", sum(map(len, output)))

    request.response.content_type = cfg_template.content_type
    request.response.text = ''.join(output)
    return request.response


def spider_start_view(request):
    """Starts job in Scrapyd and redirects to the "spider pending jobs" view."""
    settings = request.registry.settings

    cfg_template = find_spider_config_from_path(settings, request.path)
    cfg = render_spider_config(request, cfg_template)

    mediator = ScrapydMediator(settings, cfg)
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
