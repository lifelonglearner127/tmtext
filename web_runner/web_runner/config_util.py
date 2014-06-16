import collections
from itertools import count


SpiderConfig = collections.namedtuple('SpiderConfig',
                                      ['spider_name', 'project_name'])


CommandConfig = collections.namedtuple(
    'CommandConfig', ['name', 'cmd', 'content_type', 'spider_configs'])


def find_spider_config_from_path(settings, path):
    path = path.strip('/')

    for name in settings['spider._names'].split():
        prefix = 'spider.{}.'.format(name)

        resource = settings[prefix + 'resource']
        if resource.strip('/') == path:
            return find_spider_config_from_name(settings, name)
    return None


def find_spider_config_from_name(settings, name):
    prefix = 'spider.{}.'.format(name)

    try:
        return SpiderConfig(
            settings[prefix + 'spider_name'],
            settings[prefix + 'project_name'],
        )
    except KeyError:
        return None


def find_command_config_from_path(settings, path):
    path = path.strip('/')

    cfg = None
    for name in settings['command._names'].split():
        prefix = 'command.{}.'.format(name)

        resource = settings[prefix + 'resource']
        if resource.strip('/') == path:
            cfg = find_command_config_from_name(settings, name)
            break

    return cfg


def find_command_config_from_name(settings, name):
    prefix = 'command.{}.'.format(name)
    return CommandConfig(
        name,
        settings[prefix + 'cmd'],
        settings[prefix + 'content_type'],
        list(find_command_crawls(settings, prefix + 'crawl.')),
    )


def find_command_crawls(settings, prefix):
    try:
        for i in count():
            spider_config_name = prefix + str(i) + '.spider_config_name'

            cfg = find_spider_config_from_name(
                settings, settings[spider_config_name])
            if cfg is None:
                raise Exception(
                    "Spider configuration name '%s' is not defined."
                    % spider_config_name)
            yield cfg
    except KeyError:
        pass  # No more crawlers.
