import collections
from itertools import count


SpiderConfig = collections.namedtuple('SpiderConfig',
                                      ['spider_name', 'project_name'])


CommandConfig = collections.namedtuple(
    'CommandConfig', ['name', 'cmd', 'content_type', 'spider_configs'])


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


def find_command_config_from_path(settings, path):
    path = path.strip('/')

    for name in settings['command._names'].split():
        prefix = 'command.{}.'.format(name)

        resource = settings[prefix + 'resource']
        if resource.strip('/') == path:
            return find_command_config_from_name(settings, name)
    return None


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
            project_name_key = prefix + str(i) + '.project-name'
            spider_name_key = prefix + str(i) + '.spider-name'
            yield SpiderConfig(
                settings[spider_name_key], settings[project_name_key])
    except KeyError:
        pass  # No more crawlers.
