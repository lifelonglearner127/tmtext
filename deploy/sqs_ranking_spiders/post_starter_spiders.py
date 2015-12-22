# Put anything here you want to be executed BY THE SUPERUSER right after
#  the instance spins up

import os
import sys
import random


main_folder = os.path.expanduser('~/repo/')
INSTALL_PACKAGES = [
    'Pillow', 'pytesseract', 'requests', 'tldextract', 'boto', 's3peat',
    'workerpool', 'sqlalchemy', 'psycopg2', 'hjson', 'pyyaml',
    'python-dateutil', 'psutil', 'service_identity', 'mmh3', 'flask',
    'selenium', 'requesocks'
]


def can_run():
    if os.path.exists(os.path.join(main_folder,
                      'remote_instance_starter.py.marker')):
        if os.path.exists(
                os.path.join(main_folder, 'post_starter_root.py.marker')):
            # this script wasn't executed yet
            if not os.path.exists(os.path.join(main_folder, __file__+'.marker')):
                return True


def mark_as_finished():
    """ Mark this machine as the one that has already executed this script """
    with open(os.path.join(main_folder, __file__+'.marker'), 'w') as fh:
        fh.write('1')


def _install_pip_package(package):
    VENV_PYTHON = '/home/spiders/virtual_environment/bin/python'
    PIP_PATH = '/usr/local/bin/pip'
    os.system('%s %s install %s' % (VENV_PYTHON, PIP_PATH, package))


def _create_http_proxies_list(fpath, host='tprox.contentanalyticsinc.com'):
    BASE_HTTP_PORT = 22100
    NUM_PROXIES = 300
    fh = open(fpath, 'w')
    for i in xrange(NUM_PROXIES):
        proxy = 'http://%s:%s' % (host, str(BASE_HTTP_PORT+i))
        fh.write(proxy+'\n')
    fh.close()


def git_checkout(branch):
    cmd = 'cd /home/spiders/repo/tmtext && ' \
          'git fetch && ' \
          'git checkout {0} && ' \
          'git pull origin {0}'.format(branch)
    os.system(cmd)


def main():
    f = open('/tmp/check_file_post_starter_spiders', 'w')
    f.write('1')
    f.close()
    # put anything you want here...
    # add new PIP packages
    # todo: enable line below after script call removed from scrapy settings
    # git_checkout('sc_production')
    for package in INSTALL_PACKAGES:
        _install_pip_package(package)


if __name__ == '__main__':
    http_proxy_path = '/tmp/http_proxies.txt'
    if not os.path.exists(http_proxy_path):
        _create_http_proxies_list(fpath=http_proxy_path)

    if not can_run():
        for package in INSTALL_PACKAGES:
            _install_pip_package(package)
            sys.exit()

    main()
    mark_as_finished()