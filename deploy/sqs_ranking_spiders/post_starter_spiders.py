# Put anything here you want to be executed BY THE SUPERUSER right after
#  the instance spins up

import os
import sys


main_folder = os.path.expanduser('~/repo/')

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


def main():
    f = open('/tmp/check_file_post_starter_spiders', 'w')
    f.write('1')
    f.close()
    # put anything you want here...
    # add new PIP packages
    _install_pip_package('Pillow')
    _install_pip_package('pytesseract')
    _install_pip_package('requests')
    _install_pip_package('tldextract')
    _install_pip_package('boto')
    _install_pip_package('s3peat')


if __name__ == '__main__':
    http_proxy_path = '/tmp/http_proxies.txt'
    if not os.path.exists(http_proxy_path):
        _create_http_proxies_list(fpath=http_proxy_path)

    if not can_run():
        sys.exit()

    main()
    mark_as_finished()