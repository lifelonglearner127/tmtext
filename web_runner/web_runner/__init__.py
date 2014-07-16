"""This REST service allows to run Scrapy spiders through
Scrapyd and to run commands over the resulting data.
"""
import logging
import os.path

from pyramid.config import Configurator


LOG = logging.getLogger(__name__)


def add_routes(settings, config):
    """Reads the configuration for commands and spiders and configures views to
    handle them.
    """
    for controller_type in ('command', 'spider'):
        names_key = '{}._names'.format(controller_type)
        for cfg_name in settings[names_key].split():
            resource_key = '{}.{}.resource'.format(controller_type, cfg_name)
            resource_path = os.path.normpath(settings[resource_key]) + '/'

            LOG.info("Configuring %s '%s' under '%s'.", controller_type,
                     cfg_name, resource_path)
            route_name = '{}-{}'.format(controller_type, cfg_name)
            config.add_route(route_name, resource_path)
            config.add_view(
                'web_runner.views.{}_start_view'.format(controller_type),
                route_name=route_name,
                request_method='POST',
            )


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    config = Configurator(settings=settings)

    config.add_route("spider pending jobs",
                     '/crawl/project/{project}/spider/{spider}/job/{jobid}/')
    config.add_route("spider job results",
                     '/result/project/{project}/spider/{spider}/job/{jobid}/')

    config.add_route("command pending jobs", '/command/{name}/pending/{jobid}/')
    config.add_route("command job results", '/command/{name}/result/{jobid}/')
    config.add_route("status", '/status/')

    add_routes(settings, config)

    config.scan()

    return config.make_wsgi_app()
