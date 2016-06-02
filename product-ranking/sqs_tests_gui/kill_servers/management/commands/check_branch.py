import os
import sys
import shutil
import hashlib
import time

from django.core.management.base import BaseCommand, CommandError

CWD = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(CWD, '..', '..', '..', '..'))

from kill_servers.models import ProductionBranchUpdate, ServerKill
from sqs_stats import AUTOSCALE_GROUPS, set_autoscale_group_capacity,\
    get_number_of_instances_in_autoscale_groups


sys.path.append(os.path.join(CWD,  '..', '..', '..', '..', '..',
                             'deploy', 'sqs_ranking_spiders'))
#from add_task_to_sqs import put_msg_to_sqs


class Command(BaseCommand):
    help = 'Tracks changes of the SC production branch'

    repo_dir = '/tmp/_repo/tmtext'
    git_log_file = '/tmp/_git_log_file'

    def _clone_repo(self, branch):
        old_dir = os.getcwd()
        if os.path.exists(self.repo_dir):
            shutil.rmtree(self.repo_dir)
        if not os.path.exists(os.path.dirname(self.repo_dir)):
            os.makedirs(os.path.dirname(self.repo_dir))
        os.chdir(os.path.dirname(self.repo_dir))
        os.system('git clone git@bitbucket.org:dfeinleib/tmtext.git')
        os.chdir(self.repo_dir)
        os.system('git checkout %s' % branch)
        os.system('git pull origin %s' % branch)
        os.chdir(old_dir)

    def _repo_hashsum(self):
        old_dir = os.getcwd()
        os.chdir(self.repo_dir)
        os.system('git log -n 100 > %s' % self.git_log_file)
        os.chdir(old_dir)
        with open(self.git_log_file, 'r') as fh:
            cont = fh.read()
        return hashlib.sha1(cont).hexdigest()

    def _cleanup(self):
        shutil.rmtree(self.repo_dir)
        os.remove(self.git_log_file)

    def _set_autoscale_capacities_to_zero(self):
        global AUTOSCALE_GROUPS
        for group in AUTOSCALE_GROUPS:
            set_autoscale_group_capacity(group, 0, attributes=('max_size', 'desired_capacity'))

    def _set_autoscale_max_instances(self, max_instances=100):
        global AUTOSCALE_GROUPS
        for group in AUTOSCALE_GROUPS:
            set_autoscale_group_capacity(group, max_instances, attributes=('max_size',))

    def handle(self, *args, **options):
        branch = ProductionBranchUpdate.branch_to_track
        # get last commit id
        last_commit_hashsum = ProductionBranchUpdate.objects.all().order_by('-when_updated')
        if last_commit_hashsum:
            last_commit_hashsum = last_commit_hashsum[0].last_commit_hashsum
        else:
            last_commit_hashsum = '-111'  # non-existing, invalid commit ID

        self._clone_repo(branch)
        repo_hashsum = self._repo_hashsum()
        self._cleanup()

        if repo_hashsum != last_commit_hashsum:
            if ProductionBranchUpdate.objects.count():
                print('Need to restart servers')
                print('Setting autoscale groups to zero')
                self._set_autoscale_capacities_to_zero()
                while 1:
                    time.sleep(10)
                    sizes_sum = 0
                    a_groups = get_number_of_instances_in_autoscale_groups()
                    for g_name, g_size in a_groups.items():
                        g_size = g_size['current_size']
                        sizes_sum += g_size
                    if sizes_sum == 0:
                        print('Autoscale groups are empty now')
                        break  # ok we have finally killed all the instances
                self._set_autoscale_max_instances()
                print('Restored autoscale groups sizes back')
            ProductionBranchUpdate.objects.create(last_commit_hashsum=repo_hashsum)
        else:
            print('No restart needed')
