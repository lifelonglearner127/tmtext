# Put anything here you want to be executed BY THE SUPERUSER right after
#  the instance spins up

import os
import sys


main_folder = '/home/spiders/repo/'


def can_run():
    if os.path.exists(os.path.join(main_folder,
                                   'remote_instance_starter.py.marker')):
        # this script wasn't executed yet
        if not os.path.exists(os.path.join(main_folder, __file__+'.marker')):
            return True


def mark_as_finished():
    """ Mark this machine as the one that has already executed this script """
    with open(os.path.join(main_folder, __file__+'.marker'), 'w') as fh:
        fh.write('1')


def _install_system_package(package):
    os.system('apt-get install -y %s')


def main():
    f = open('/tmp/check_file_post_starter_root_new', 'w')
    f.write('1')
    f.close()
    # put anything you want here...
    # install extra system packages
    _install_system_package('tesseract-ocr')


if __name__ == '__main__':
    if not can_run():
        sys.exit()
    main()
    mark_as_finished()