from __future__ import division, absolute_import, unicode_literals

from itertools import repeat, starmap
import logging
import urllib2

import pyramid.httpexceptions as exc
from pyramid.view import view_config

import subprocess32 as subprocess

from web_runner.config_util import find_command_config_from_name, \
    find_command_config_from_path, find_spider_config_from_path, SpiderConfig, \
    render_spider_config
from web_runner.scrapyd import ScrapydMediator, ScrapydInterface, \
    ScrapydJobStartError, ScrapydJobException
from web_runner.util import encode_ids, decode_ids, get_request_status, \
    string2datetime
import web_runner.db
import datetime


LOG = logging.getLogger(__name__)


FINISH = web_runner.util.FINISH
UNAVAILABLE = web_runner.util.UNAVAILABLE
RUNNING = web_runner.util.RUNNING
PENDING = web_runner.util.PENDING


# TODO Move command handling logic to a CommandMediator.


def command_start_view(request):
    """Schedules running a command plus spiders."""
    settings = request.registry.settings
    cfg_template = find_command_config_from_path(settings, request.path)
    if cfg_template is None:
        raise exc.HTTPNotFound("Unknown resource.")

    spider_cfgs = starmap(
        render_spider_config,
        zip(
            cfg_template.spider_configs,
            cfg_template.spider_params,
            repeat(request.params),
        )
    )

    spider_job_ids = []
    try:
        for spider_cfg in spider_cfgs:
            jobid = ScrapydMediator(settings, spider_cfg).start_job(
                request.params)
            spider_job_ids.append(jobid)
            LOG.info(
                "For command at '%s', started crawl job with id '%s'.",
                cfg_template.name,
                jobid,
            )
    except ScrapydJobStartError as e:
        raise exc.HTTPBadGateway(
            "Failed to start a required crawl for command '{}'."
            " Scrapyd was not OK, it was '{}': {}".format(
                cfg_template.name, e.status, e.message)
        )
    except ScrapydJobException as e:
        raise exc.HTTPBadGateway(
            "For command {}, unexpected error when contacting Scrapyd:"
            " {}".format(cfg_template.name, e.message)
        )

    # Storing the request in the internal DB
    dbinterf = web_runner.db.DbInterface(
        settings['db_filename'], recreate=False)
    command_name = request.path.strip('/')
    dbinterf.new_command(
        command_name, dict(request.params), spider_job_ids, request.remote_addr)
    dbinterf.close()

    raise exc.HTTPFound(
        location=request.route_path(
            "command pending jobs",
            name=cfg_template.name,
            jobid=encode_ids(spider_job_ids),
            _query=request.params,
        ),
        detail="Command '{}' started with {} crawls.".format(
            cfg_template.name, len(spider_job_ids))
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

    spider_cfgs = starmap(
        render_spider_config,
        zip(
            cfg_template.spider_configs,
            cfg_template.spider_params,
            repeat(request.params),
        )
    )

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

    spider_cfgs = starmap(
        render_spider_config,
        zip(
            cfg_template.spider_configs,
            cfg_template.spider_params,
            repeat(request.params),
        )
    )

    args = dict(request.params)
    for i, (job_id, spider_cfg) in enumerate(zip(job_ids, spider_cfgs)):
        fn = ScrapydMediator(settings, spider_cfg).retrieve_job_data_fn(job_id)
        args['spider %d' % i] = fn

    cmd_line = cfg_template.cmd.format(**args)
    LOG.info("Starting command: %s", cmd_line)
    process = subprocess.Popen(
        cmd_line,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )

    LOG.info("Waiting until conn timeout for command to finish...")
    stdout, stderr = process.communicate()
    LOG.info("Process finished.")

    if process.returncode != 0:
        msg = "The command terminated with an return value of %s." \
              " Process' standard error: %s" \
              % (process.returncode, stderr)
        LOG.warn(msg)
        raise exc.HTTPBadGateway(detail=msg)

    LOG.info("Command generated %s bytes.", len(stdout))
    request.response.content_type = cfg_template.content_type
    request.response.body = stdout
    return request.response


def spider_start_view(request):
    """Starts job in Scrapyd and redirects to the "spider pending jobs" view."""
    settings = request.registry.settings

    cfg_template = find_spider_config_from_path(settings, request.path)
    cfg = render_spider_config(cfg_template, request.params)

    try:
        mediator = ScrapydMediator(settings, cfg)
        jobid = mediator.start_job(request.params)

        # Storing the request in the internal DB.
        dbinterf = web_runner.db.DbInterface(
            settings['db_filename'], recreate=False)
        dbinterf.new_spider(
            cfg.spider_name,
            dict(request.params),
            jobid,
            request.remote_addr,
        )
        dbinterf.close()

        raise exc.HTTPFound(
            location=request.route_path(
                "spider pending jobs",
                project=cfg.project_name,
                spider=cfg.spider_name,
                jobid=jobid,
            ),
            detail="Job '%s' started." % jobid)
    except ScrapydJobStartError as e:
        raise exc.HTTPBadGateway(
            "Scrapyd error when starting job. Status '{}': {}".format(
                e.status, e.message))
    except ScrapydJobException as e:
        raise exc.HTTPBadGateway(
            "When contacting Scrapyd there was an unexpected error: {}".format(
                e.message))


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


@view_config(route_name='status', request_method='GET', renderer='json')
def status(request):
    """Check the Web Runner and Scrapyd Status"""

    settings = request.registry.settings
    scrapyd_baseurl = settings['spider._scrapyd.base_url']

    scrapyd_interf = ScrapydInterface(scrapyd_baseurl)
    alive = scrapyd_interf.is_alive()
    (operational, projects) = scrapyd_interf.get_projects()

    # Get the spiders for all projects
    if alive and operational:
        spiders = {proj: scrapyd_interf.get_spiders(proj) for proj in projects}
    else:
        spiders = None

    output = {
        'scrapyd_alive': alive,
        'scrapyd_operational': operational,
        'scrapyd_projects': projects,
        'spiders': spiders,
        'webRunner': True,
    }

    return output


@view_config(route_name='last request status', request_method='GET',
             renderer='json')
def last_request_status(request):
    """Returns the last requests requested.

    The request accepts an optional parameter size, which is the maximum number
    of items returned.
    """ 
    settings = request.registry.settings

    default_size = 10
    size_str = request.params.get('size', default_size)
    try:
        size = int(size_str)
    except ValueError:
        raise exc.HTTPBadGateway(detail="Size parameter has incorrect value")

    # Get last requests
    dbinterf = web_runner.db.DbInterface(
        settings['db_filename'], recreate=False)
    reqs = dbinterf.get_last_requests(size)
    dbinterf.close()

    # Get the jobid status dictionary.
    scrapyd_baseurl = settings['spider._scrapyd.base_url']
    scrapyd_interf = ScrapydInterface(scrapyd_baseurl)
    jobids_status = scrapyd_interf.get_jobids_status()
    
    # For each request, determine the request status gathering 
    # the information from all jobids related to it
    for req in reqs:
        req['status'] = get_request_status(req, jobids_status)

    return reqs



@view_config(route_name='request history', request_method='GET',
             renderer='json')
def request_history(request):
    """Returns the history of a request"""
    settings = request.registry.settings

    try:
        requestid = int(request.matchdict['requestid'])
    except ValueError:
        raise exc.HTTPBadGateway(detail="Request id is not valid")

    # Get request info
    dbinterf = web_runner.db.DbInterface(
        settings['db_filename'], recreate=False)
    request_info = dbinterf.get_request(requestid)
    dbinterf.close()

    if not request_info:
        # The requestid is not recognized
        raise exc.HTTPBadGateway(detail="No info from Request id")

    # Get the jobid status dictionary.
    scrapyd_baseurl = settings['spider._scrapyd.base_url']
    scrapyd_interf = ScrapydInterface(scrapyd_baseurl)
    jobids_status = scrapyd_interf.get_jobids_status()

    try:   
        jobids_info = {jobid: jobids_status[jobid]  # Get only the jobids of 
          for jobid in request_info['jobids']}      # the current request
    except KeyError:
        jobids_info = None

    if jobids_info:
        history = _get_history(requestid, request_info, jobids_info)
        status = get_request_status(request_info, jobids_status)
    else:
        history = None

    info = {'request': request_info,
            'jobids_info': jobids_info,
            'history': history,
            'status': status }

    return info


def _get_history(requestid, request_info, jobids_info):
    class Log:
        def __init__(self):
            self.date = None
            self.delta = None
            self.comment = None

        def __repr__(self):
            now = datetime.datetime.utcnow()
            self.delta = now - self.date
            # Erase the microseconds
            self.delta -= datetime.timedelta(microseconds=self.delta.microseconds)
            return [str(self.date), str(self.delta), self.comment]

        def setDate(self, dateStr):
            self.date = string2datetime(dateStr)
    

    history = []
    # Insert starting log
    creation = Log()
    creation.setDate(request_info['creation'])
    creation.comment = 'Request arrived from %s.' % request_info['remote_ip']
    history.append(creation)
 
    request_finished = True
    date_last_finished_spider = None
    for jobid in request_info['jobids']:
        status = jobids_info[jobid]['status']
        if status == FINISH:    
            # Note: I'm not able to know when the spider started if it has
            # not finished. Scrapyd does not provide that info.
            # Log when the spider started
            start_log = Log()
            start_log.setDate(jobids_info[jobid]['start_time'])
            start_log.comment = 'Spider %s started.' % jobids_info[jobid]['spider']
            history.append(start_log)

            # Log when spider finished
            finish_log = Log()
            finish_log.setDate(jobids_info[jobid]['end_time'])
            spider_time = finish_log.date - start_log.date
            spider_time -= datetime.timedelta(
                           microseconds=spider_time.microseconds)
            finish_log.comment = 'Spider %s finished. Took %s.' % (
              jobids_info[jobid]['spider'], spider_time)
            history.append(finish_log)

            # set what is the date of the last finished spider
            if ( date_last_finished_spider == None or 
              date_last_finished_spider < finish_log.date):
                date_last_finished_spider = finish_log.date
        else:
            request_finished = False

    # Add the request finish status
    if request_finished:
        finish = Log()
        finish.date = date_last_finished_spider
        request_time = finish.date - creation.date
        request_time -= datetime.timedelta(
                        microseconds=request_time.microseconds)
        finish.comment = 'Request finished. Took %s since created.' % request_time
        history.append(finish)

    # Sort the history by date
    sort_history = sorted(history, key=lambda x: x.date)
    return map((lambda x: x.__repr__()), sort_history)


# vim: set expandtab ts=4 sw=4:
