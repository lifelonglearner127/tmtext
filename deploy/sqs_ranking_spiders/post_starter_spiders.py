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


def _download_http_proxies(url):
    import urllib
    content = urllib.urlopen(url).read()
    with open('/tmp/http_proxies.txt', 'w') as fh:
        fh.write(content)


def main():
    f = open('/tmp/check_file_post_starter_spiders', 'w')
    f.write('1')
    f.close()
    # put anything you want here...
    # add new PIP packages
    _install_pip_package('Pillow')
    _install_pip_package('pytesseract')
    _download_http_proxies(url='http://dpaste.com/172FAR0.txt')


if __name__ == '__main__':
    if not can_run():
        sys.exit()
    main()
    mark_as_finished()