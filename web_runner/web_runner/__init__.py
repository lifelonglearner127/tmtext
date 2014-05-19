"""This simple REST interface allows to run Scrapy spiders through
Scrapyd and to run commands over the resulting data.

For spiders, the API is as follows: GET /{resource}/ redirects to
/spider/{spider}/job/{job}/ where the client will poll to see when the job is
complete. All query string parameters are passed to Scrapyd.
When complete, the a link to the raw result will be provided. The result will be
encoded in jsonlines.

For commands, the API is as follows: ...
"""
import logging
import os.path

from pyramid.config import Configurator


LOG = logging.getLogger(__name__)


def add_routes(settings, config):
    """Reads the configuration for commands and spiders and configures the
    controllers to handle them.
    """
    for controller_type in ('command', 'spider'):
        names_key = '{}._names'.format(controller_type)
        for cfg_name in settings[names_key].split():
            resource_key = '{}.{}.resource'.format(controller_type, cfg_name)
            resource_path = os.path.normpath('/' + settings[resource_key]) + '/'

            LOG.info("Configuring %s '%s' under '%s'.", controller_type,
                     cfg_name, resource_path)
            config.add_route(controller_type, resource_path,
                             request_method='GET')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route("spider pending jobs",
                     '/crawl/project/{project}/spider/{spider}/job/{jobid}/',
                     request_method='GET')
    config.add_route("spider job results",
                     '/result/project/{project}/spider/{spider}/job/{jobid}/',
                     request_method='GET')
    add_routes(settings, config)

    config.scan()
    return config.make_wsgi_app()
