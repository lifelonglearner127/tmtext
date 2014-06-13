from pyspecs import given, when, then, the, finish

from web_runner.config_util import find_spider_config, SpiderConfig
from web_runner.config_util import find_command_config, CommandConfig


with given.a_configuration_of_a_spider:
    settings = {
        'spider._names': 'spider_cfg',

        'spider._scrapyd.base_url': 'http://localhost:6800/',
        'spider._result.base_url': 'http://localhost:8000/',

        'spider.spider_cfg.resource': 'spider_resource',
        'spider.spider_cfg.spider_name': 'spider_name',
        'spider.spider_cfg.project_name': 'spider_project_name',
    }

    with when.searching_for_that_resource:
        config = find_spider_config(settings, '/spider_resource/')

        with then.the_configuration_should_be_found:
            the(config).should.equal(
                SpiderConfig('spider_name', 'spider_project_name'))

    with when.searching_for_an_unexistant_resource:
        config = find_spider_config(settings, '/unexistant/')

        with then.it_should_return_none:
            the(config).should.be(None)


with given.a_configuration_of_a_command:
    settings = {
        'command._names': 'tst',

        'command.tst.cmd': 'echo {key1}',
        'command.tst.resource': '/tst-resource',
        'command.tst.content_type': 'text/plain',
        'command.tst.crawl.0.project-name': 'spider project',
        'command.tst.crawl.0.spider-name': 'spider name',
    }

    with when.searching_for_that_resource:
        config = find_command_config(settings, '/tst-resource/')

        with then.the_configuration_should_be_found:
            the(config).should.equal(CommandConfig(
                'echo {key1}',
                'text/plain',
                [SpiderConfig('spider name', 'spider project')]
            ))

    with when.searching_for_an_unexistant_resource:
        config = find_command_config(settings, '/unexistant/')

        with then.it_should_return_none:
            the(config).should.be(None)


if __name__ == '__main__':
    finish()