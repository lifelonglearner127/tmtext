# Put anything here you want to be executed BY THE SUPERUSER right after
#  the instance spins up

import os
import sys
from subprocess import check_output, CalledProcessError, STDOUT

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
    """
    After running 'install' command, each package will be checked for succeeded
    installation process via 'dpkg -s'. In case, if any of these commands fail
    or return non-0 status code, http request will be sent to the url
    to indicate the error happened.
    """
    try:
        commands = ['sudo apt-get install -y %s', 'dpkg -s %s']
        for cmd in commands:
            check_output(cmd % package, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        data = dict(item=package, error=e.output)
        # check if error was caused by running script second time
        #  if so, ignore it
        if 'Could not get lock /var/lib/dpkg/lock' in data['error']:
            return
        try:
            import urllib2
            import urllib
            url = 'http://sqs-metrics.contentanalyticsinc.com/log_install_error'
            req = urllib2.Request(url, urllib.urlencode(data))
            req.add_header('Authorization', 'Basic YWRtaW46Q29udGVudDEyMzQ1')
            urllib2.urlopen(req)
        except Exception:
            pass


def main():
    f = open('/tmp/check_file_post_starter_root_new', 'w')
    f.write('1')
    f.close()
    # put anything you want here...
    # install extra system packages
    tmp_cron_name = 'mycron'
    os.system('crontab -l > %s' % tmp_cron_name)
    with open(tmp_cron_name, 'a') as f:
        cmd = \
        '* * * * * cd /home/spiders/repo/tmtext/deploy/sqs_ranking_spiders;'\
        ' source /home/spiders/virtual_environment/bin/activate && '\
        'python self_killer_script.py \n'
        f.write(cmd)
        f.write('\n')
    os.system('crontab %s' % tmp_cron_name)
    _install_system_package('tesseract-ocr')
    _install_system_package('phantomjs')
    _install_system_package('firefox')
    # disable marketplaces (they are too slow)
    disabler = '/tmp/stop_marketplaces'
    os.system('echo "1" > %s' % disabler)


if __name__ == '__main__':
    if not can_run():
        sys.exit()
    main()
    mark_as_finished()