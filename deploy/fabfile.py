#!/usr/bin/env python
from __future__ import with_statement
from  fabric.api import env, run, local, sudo, settings, prefix
from fabric.contrib.console import confirm
from fabric.utils import puts
from fabric.colors import red, green
import cuisine
import os
import re
from contextlib import contextmanager

'''
Fabric deployment script for Web Runner

This script will help to deploy:
. Scrapyd
. Web Runner REST Server
. Web Runner Web
'''

'''
TODO:
1) deploy users and permissions
2) deploy keys
3) deploy dependencies
4) virtual environment creation
5) download repos on target machine
6) deploy scrapy project
7) deploy web runner project
8) create web-runner-web wheel package
9) deploy web-runner-web
11) Configure supervisord
12) configure nginx
13) work on updates.
'''

# For the moment the configuration will be constant defined here.
# Leter this info will be added to a configuration file.
#SSH_USER = 'vagrant'
#SSH_PASSWORD = 'vagrant'
#SSH_SERVER = '127.0.0.1'
#SSH_PORT = 2222

WEB_RUNNER_GROUP = 'web_runner'
WEB_RUNNER_USER = 'web_runner'
WEB_RUNNER_PASSWORD = 'web_runner'
WEB_RUNNER_CERT = None

VENV_PREFIX = '~/virtual-environments/'
VENV_SCRAPYD = 'scrapyd'
VENV_WEB_RUNNER = 'web-runner'
VENV_WEB_RUNNER_WEB = 'web-runner-web'

SSH_SUDO_USER = None
SSH_SUDO_PASSWORD = None
SSH_SUDO_CERT = None

REPO_BASE_PATH = '~/repos/'
REPO_URL = 'https://ContentSolutionsDeploy:Content2020@bitbucket.org/dfeinleib/tmtext.git'





@contextmanager
def virtualenv(environment):
    '''Define the virtual environment to use.

    This function is useful for fabric.api.run commands, because all run
    invocation will be called within the virtual environemnt. Example:

      with virtualenv(VENV_SCRAPYD):
        run('pip install scrapyd')
        run('pip install simplejson')

    The parameter environment is the name of the virtual environment
    followed by VENV_PREFIX
    '''

    venv_path = VENV_PREFIX + os.sep + environment
    venv_activate = 'source %s%sbin%sactivate' % (venv_path, os.sep, os.sep)

    with cuisine.cd(venv_path):
        with prefix(venv_activate):
            yield



def set_environment_vagrant():
    '''Define Vagrant's environment'''

    puts(green('Using Vagrant settings'))
    global SSH_SUDO_USER
    global SSH_SUDO_PASSWORD
    global SSH_SUDO_CERT
    global WEB_RUNNER_CERT

#    env.hosts = ['vagrant@127.0.0.1:2222']
    #SSH_SUDO_USER = 'vagrant'
    #SSH_SUDO_PASSWORD = 'vagrant'
    SSH_SUDO_USER = 'vagrant'
    SSH_SUDO_PASSWORD = 'vagrant'
    WEB_RUNNER_CERT = 'web_runner_rsa'

    env.hosts = ['127.0.0.1']
    env.port = 2222

    env.user = WEB_RUNNER_USER
    env.password = WEB_RUNNER_PASSWORD
    env.key_filename = WEB_RUNNER_CERT


def set_production():
    puts(red('Using production credentials'))

    global SSH_SUDO_USER
    global SSH_SUDO_PASSWORD
    global SSH_SUDO_CERT
    global WEB_RUNNER_CERT

    SSH_SUDO_USER = 'ubuntu'
    SSH_SUDO_PASSWORD = None
    SSH_SUDO_CERT = 'ubuntu_id_rsa'
    WEB_RUNNER_CERT = 'web_runner_rsa'

    env.user = WEB_RUNNER_USER
    env.password = WEB_RUNNER_PASSWORD
    env.key_filename = WEB_RUNNER_CERT


def setup_users():
    '''Add web runner group and users'''

    puts(green('Creating users and groups'))

    orig_user, orig_passw, orig_cert = env.user, env.password, env.key_filename
    env.user, env.password, env.key_filename = \
      SSH_SUDO_USER , SSH_SUDO_PASSWORD, SSH_SUDO_CERT

    cuisine.group_ensure(WEB_RUNNER_GROUP)
    cuisine.user_ensure(WEB_RUNNER_USER, gid=WEB_RUNNER_GROUP,
      shell='/bin/bash', passwd=WEB_RUNNER_PASSWORD, encrypted_passwd=False)

    # Create the ssh certificate for web_runner user
    rem_ssh_cert_file = '~%s/.ssh/authorized_keys' % WEB_RUNNER_USER
    if orig_cert and not sudo('test -e %s && echo OK ; true'
                             % (rem_ssh_cert_file)).endswith("OK"):
        sudo('mkdir -p ~%s/.ssh' % WEB_RUNNER_USER)
        sudo('chmod 700  ~%s/.ssh' % WEB_RUNNER_USER)

        cert_content = open('web_runner_rsa.pub', 'r').read()
        cuisine.file_write('/tmp/inst_cert', cert_content)
        sudo('mv /tmp/inst_cert ' + rem_ssh_cert_file)
        sudo('chmod 600 %s' % rem_ssh_cert_file)
        sudo('chown -R %s:%s ~%s/.ssh/' %
          (WEB_RUNNER_USER, WEB_RUNNER_GROUP, WEB_RUNNER_USER))

    env.user, env.password, env.key_filename = \
      orig_user, orig_passw, orig_cert


def setup_packages():
    '''Install all packages prerequirements'''

    puts(green('Installing packages'))

    orig_user, orig_passw, orig_cert = env.user, env.password, env.key_filename
    env.user, env.password, env.key_filename = \
      SSH_SUDO_USER , SSH_SUDO_PASSWORD, SSH_SUDO_CERT

    cuisine.package_ensure('python-software-properties')
    # TODO: verify if the repo must be added
    #cuisine.repository_ensure_apt('ppa:fkrull/deadsnakes')
    sudo('apt-get update')
    cuisine.package_ensure('python3.4 python3.4-dev')
    cuisine.package_ensure('python-dev')
    cuisine.package_ensure('python-pip python3-pip')
    cuisine.package_ensure('libffi-dev')
    cuisine.package_ensure('libxml2-dev libxslt1-dev')
    cuisine.package_ensure('libssl-dev')
    cuisine.package_ensure('git')
    cuisine.package_ensure('tmux')
    sudo('pip install virtualenv --upgrade')

    env.user, env.password, env.key_filename = \
      orig_user, orig_passw, orig_cert


def setup_tmux():
    # Verify if a new tmux session must be created
    try:
        tmux_ls = run('tmux list-windows -t webrunner')

        if not re.search('0: scrapyd', tmux_ls.stdout):
            run('tmux new-window -k -t webrunner:0 -n scrapyd')
        if not re.search('1: web_runner', tmux_ls.stdout):
            run('tmux new-window -k -t webrunner:1 -n web_runner')
        if not re.search('2: web_runner_web', tmux_ls.stdout):
            run('tmux new-window -k -t webrunner:2 -n web_runner_web')
        if not re.search('3: misc', tmux_ls.stdout):
            run('tmux new-window -k -t webrunner:3 -n misc')
    except:
        # The tmux session does not exists. Create everything
        run('tmux new-session -d -s webrunner -n scrapyd')
        run('tmux new-window -k -t webrunner:1 -n web_runner')
        run('tmux new-window -k -t webrunner:2 -n web_runner_web')
        run('tmux new-window -k -t webrunner:3 -n misc')


def _get_venv_path(venv):
    return VENV_PREFIX + os.sep + venv


def _get_repo_path():
    return REPO_BASE_PATH + os.sep + \
      re.search('.+\/([^\s]+?)\.git$',REPO_URL).group(1)


def _setup_virtual_env_scrapyd():
    '''Handle scrapyd virtual environment'''

    venv_scrapyd = _get_venv_path(VENV_SCRAPYD)
    if not cuisine.dir_exists(venv_scrapyd):
        run('virtualenv -p python2.7 ' + venv_scrapyd)

    with virtualenv(VENV_SCRAPYD):
        run('pip install scrapyd')
        run('pip install simplejson')


def _setup_virtual_env_web_runner():
    venv_webrunner = _get_venv_path(VENV_WEB_RUNNER)
    if not cuisine.dir_exists(venv_webrunner):
        run('virtualenv -p python2.7 ' + venv_webrunner)

    with virtualenv(VENV_WEB_RUNNER):
        run('pip install wheel')
        run('pip install Paste')


def _setup_virtual_env_web_runner():
    venv_webrunner = _get_venv_path(VENV_WEB_RUNNER)
    if not cuisine.dir_exists(venv_webrunner):
        run('virtualenv -p python2.7 ' + venv_webrunner)

    with virtualenv(VENV_WEB_RUNNER):
        run('pip install wheel')
        run('pip install Paste')


def _setup_virtual_env_web_runner_web():
    venv_webrunner_web = _get_venv_path(VENV_WEB_RUNNER_WEB)
    if not cuisine.dir_exists(venv_webrunner_web):
        run('virtualenv -p python3.4 ' + venv_webrunner_web)

    with virtualenv(VENV_WEB_RUNNER_WEB):
        run('pip install django')
        run('pip install requests')


def setup_virtual_env(scrapyd=True, web_runner=True, web_runner_web=True):
    '''Handle virtual envrironment installation'''
    puts(green('Installing virtual environments'))

    venv_webrunner = _get_venv_path(VENV_WEB_RUNNER)
    venv_webrunner_web = _get_venv_path(VENV_WEB_RUNNER_WEB)

    run('mkdir -p ' + VENV_PREFIX)
    if scrapyd:
        _setup_virtual_env_scrapyd()
    if web_runner:
        _setup_virtual_env_web_runner()
    if web_runner_web:
        _setup_virtual_env_web_runner_web()



def get_repos(branch='master'):
    '''Download and install the main source repository'''

    puts(green('Updating repositories'))

    repo_path = _get_repo_path()
    if not cuisine.dir_exists(repo_path):
        run('mkdir -p ' + REPO_BASE_PATH)
        run('cd %s && git clone %s && cd %s && git checkout %s' %
          (REPO_BASE_PATH, REPO_URL, repo_path, branch))
    else:
        run('cd %s && git checkout %s && git pull' %
          (repo_path, branch) )


def _configure_scrapyd():
    venv_scrapyd = _get_venv_path(VENV_SCRAPYD)
    repo_path = _get_repo_path()

    run('cp %s/web_runner/conf/instance_two/scrapyd.conf %s'
      % (repo_path, venv_scrapyd))


def _configure_web_runner():
    venv_webrunner = _get_venv_path(VENV_WEB_RUNNER)
    repo_path = _get_repo_path()

    run('cp %s/web_runner/conf/instance_two/instance_two.ini %s'
      % (repo_path, venv_webrunner))


def _configure_web_runner_web():
    venv_webrunner_web = _get_venv_path(VENV_WEB_RUNNER_WEB)
    venv_webrunner_web_activate = '%s%sbin%sactivate' \
      % (venv_webrunner_web, os.sep, os.sep)
    repo_path = _get_repo_path()

    settings_prod = repo_path + '/web_runner_web/web_runner_web/' \
      + 'settings.production.py'
    settings_link = repo_path + '/web_runner_web/web_runner_web/settings.py'

    # Create the settings.py
    if not cuisine.file_exists(settings_link):
        run('ln -s %s %s' % (settings_prod, settings_link))

    # Create the Django DB and Django users
    django_db = repo_path + '/web_runner_web/db.sqlite3'
    if not cuisine.file_exists(django_db):
        with virtualenv(VENV_WEB_RUNNER_WEB):
            run("cd %s/web_runner_web && ./manage.py syncdb --noinput" % repo_path)

        run('tmux new-window -k -t webrunner:4 -n django_config')
        run("tmux send-keys -t webrunner:4 'source %s' C-m" %
            venv_webrunner_web_activate)
        run("tmux send-keys -t webrunner:4 'cd %s' C-m" % repo_path)
        run("tmux send-keys -t webrunner:4 'cd web_runner_web' C-m")
        run("tmux send-keys -t webrunner:4 './manage.py shell' C-m")
        run("tmux send-keys -t webrunner:4 'from django.contrib.auth.models import User' C-m")
        run("tmux send-keys -t webrunner:4 'user = User.objects.create_user(username=\"admin\", password=\"Content\")' C-m")
        run("tmux send-keys -t webrunner:4 'exit()' C-m")




def configure():
    puts(green('Configuring the servers'))

    _configure_scrapyd()
    _configure_web_runner()
    _configure_web_runner_web()


def _install_web_runner():
    venv_webrunner = _get_venv_path(VENV_WEB_RUNNER)
    venv_webrunner_activate = '%s%sbin%sactivate' \
      % (venv_webrunner, os.sep, os.sep)
    repo_path = _get_repo_path()

    run("tmux send-keys -t webrunner:1 'source %s' C-m" %
        venv_webrunner_activate)
    run("tmux send-keys -t webrunner:1 'cd %s' C-m" % repo_path)
    run("tmux send-keys -t webrunner:1 'cd web_runner' C-m")
    run("tmux send-keys -t webrunner:1 'python setup.py bdist_wheel' C-m")
    run("tmux send-keys -t webrunner:1 '/usr/bin/yes | pip uninstall web-runner' C-m")

    with virtualenv(VENV_WEB_RUNNER):
        run('cd %s/web_runner && python setup.py bdist_wheel' % repo_path)
        run('cd %s/web_runner && pip install dist/web_runner-*.whl' % repo_path)


def install():
    _install_web_runner()


def _restart_scrapyd():
    puts(green('Stoping scrapyd'))

    try:
        run("tmux send-keys -t webrunner:0 C-c")
    except:
        pass


def _run_scrapyd_deploy():
    venv_scrapyd = _get_venv_path(VENV_SCRAPYD)
    venv_scrapyd_activate = '%s%sbin%sactivate' \
      % (venv_scrapyd, os.sep, os.sep)
    repo_path = _get_repo_path()

    run('tmux new-window -k -t webrunner:4 -n scrapyd_deploy')
    run("tmux send-keys -t webrunner:4 'source %s' C-m" % venv_scrapyd_activate)
    run("tmux send-keys -t webrunner:4 'cd %s' C-m" % repo_path)
    run("tmux send-keys -t webrunner:4 'cd product-ranking' C-m")
    run("tmux send-keys -t webrunner:4 'scrapyd-deploy' C-m")
    run("tmux send-keys -t webrunner:4 'exit' C-m")


def _run_scrapyd():
    venv_scrapyd = _get_venv_path(VENV_SCRAPYD)
    venv_scrapyd_activate = '%s%sbin%sactivate' \
      % (venv_scrapyd, os.sep, os.sep)

    run("tmux send-keys -t webrunner:0 'source %s' C-m" % venv_scrapyd_activate)
    run("tmux send-keys -t webrunner:0 'cd %s' C-m" % venv_scrapyd)
    run("tmux send-keys -t webrunner:0 'scrapyd' C-m")
    _run_scrapyd_deploy()


def _run_web_runner():
    venv_webrunner = _get_venv_path(VENV_WEB_RUNNER)
    venv_webrunner_activate = '%s%sbin%sactivate' \
      % (venv_webrunner, os.sep, os.sep)

    run("tmux send-keys -t webrunner:1 'source %s' C-m" % venv_webrunner_activate)
    run("tmux send-keys -t webrunner:1 'cd %s' C-m" % venv_webrunner)
    run("tmux send-keys -t webrunner:1 'pserve instance_two.ini --stop-daemon' C-m")
    run("tmux send-keys -t webrunner:1 'pserve instance_two.ini start' C-m")

#    with virtualenv(VENV_WEB_RUNNER):
#        if cuisine.file_exists('pyramid.pid'):
#            try:
#                run('pserve  instance_two.ini restart')
#            except:
#                run('pserve  instance_two.ini start')
#        else:
#            run('pserve  instance_two.ini start')


def _is_django_running():
    '''Return boolean representing if django is running or not'''
    process = processes = run("ps -ef | grep python | grep manage | grep runserver; true")
    return process.stdout.find('\n')>0

def _run_web_runner_web():
    venv_webrunner_web = _get_venv_path(VENV_WEB_RUNNER_WEB)
    venv_webrunner_web_activate = '%s%sbin%sactivate' \
      % (venv_webrunner_web, os.sep, os.sep)
    repo_path = _get_repo_path()

    if not _is_django_running():
        run("tmux send-keys -t webrunner:2 'source %s' C-m" % venv_webrunner_web_activate)
        run("tmux send-keys -t webrunner:2 'cd %s/web_runner_web' C-m" % repo_path)
        run("tmux send-keys -t webrunner:2 './manage.py runserver 0.0.0.0:8000' C-m")


def run_servers(restart_scrapyd=False):
    puts(green('Starting/restaring servers'))

    if restart_scrapyd:
        _restart_scrapyd()

    _run_scrapyd()
    _run_web_runner()
    _run_web_runner_web()



def _common_tasks():
    setup_users()
    setup_packages()
    setup_tmux()


def deploy_scrapyd(restart_scrapyd=False, branch='master'):

    _common_tasks()
    setup_virtual_env(web_runner=False, web_runner_web=False)
    get_repos(branch=branch)
    _configure_scrapyd()

    if restart_scrapyd:
        _restart_scrapyd()
    _run_scrapyd()



def deploy_web_runner(branch='master'):
    _common_tasks()
    setup_virtual_env(scrapyd=False, web_runner_web=False)
    get_repos(branch=branch)
    _configure_web_runner()
    _install_web_runner()
    _run_web_runner()


def deploy_web_runner_web(branch='master'):
    _common_tasks()
    setup_virtual_env(scrapyd=False, web_runner=False)
    get_repos(branch=branch)
    _configure_web_runner_web()
    _run_web_runner_web()



def deploy(restart_scrapyd=False, branch='master'):
    _common_tasks()
    setup_virtual_env()
    get_repos(branch=branch)
    configure()
    install()
    run_servers(restart_scrapyd)



# vim: set expandtab ts=4 sw=4: