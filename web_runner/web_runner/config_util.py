import collections
from itertools import count


SpiderConfig = collections.namedtuple('SpiderConfig',
                                      ['spider_name', 'project_name'])


CommandConfig = collections.namedtuple(
    'CommandConfig',
    ['name', 'cmd', 'content_type', 'spider_configs', 'spider_params']
)


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

    crawl_configs, crawl_params = list(zip(
        *find_command_crawls(settings, prefix + 'crawl.')))

    return CommandConfig(
        name,
        settings[prefix + 'cmd'],
        settings[prefix + 'content_type'],
        crawl_configs,
        crawl_params,
    )


def find_command_crawls(settings, prefix):
    try:
        for i in count():
            spider_config_name_key = prefix + str(i) + '.spider_config_name'
            spider_config_name = settings[spider_config_name_key]

            cfg = find_spider_config_from_name(
                settings, spider_config_name)
            if cfg is None:
                raise Exception(
                    "Spider configuration name '%s' is not defined."
                    % spider_config_name)

            try:
                spider_params_name = prefix + str(i) + '.spider_params'
                params_list = settings[spider_params_name].split()
                params = dict(raw_param.split('=', 1)
                              for raw_param in params_list)
            except KeyError:
                params = {}  # No parameters defined.

            yield cfg, params
    except KeyError:
        pass  # No more crawlers.


def render_spider_config(spider_template_configs, params, global_params=None):
    """Renders the spider config from the given templates and parameters.

    :param spider_template_configs: A list of config templates.
    :param params: A list of dicts correlated with the list of templates.
    :param global_params: A dict to override parameters for all templates.
    :returns: A generator of rendered SpiderConfigs.
    """
    for template, p in zip(spider_template_configs, params):
        merged_params = p.copy()
        if global_params:
            merged_params.update(global_params)

        yield SpiderConfig(
            template.spider_name.format(**merged_params),
            template.project_name.format(**merged_params)
        )
