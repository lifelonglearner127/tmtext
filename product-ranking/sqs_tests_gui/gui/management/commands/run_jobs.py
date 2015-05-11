import os
import sys

from django.core.management.base import BaseCommand, CommandError

CWD = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(CWD, '..', '..', '..', '..'))

from gui.models import Job, get_data_filename, get_log_filename


sys.path.append(os.path.join(CWD,  '..', '..', '..', '..', '..',
                             'deploy', 'sqs_ranking_spiders'))
from add_task_to_sqs import put_msg_to_sqs


class Command(BaseCommand):
    help = ('Takes up to 10 oldest newly created Jobs'
            ' and pushes them into the test SQS queue')

    def handle(self, *args, **options):
        jobs = Job.objects.filter(status='created').order_by(
            'created').distinct()[0:10]
        for job in jobs:
            msg = {
                'task_id': int(job.task_id),
                'site': job.spider.replace('_products', ''),
                'server_name': job.server_name,
                'cmd_args': {'quantity': job.quantity}
            }
            if not job.quantity:
                del msg['cmd_args']['quantity']
            if not msg['cmd_args']:
                del msg['cmd_args']
            if job.search_term:
                msg['searchterms_str'] = job.search_term
            elif job.product_url:
                msg['url'] = job.product_url
            if job.with_best_seller_ranking:
                msg['with_best_seller_ranking'] = True
            if job.branch_name:
                msg['branch_name'] = job.branch_name
            put_msg_to_sqs(msg, job.get_input_queue())
            job.status = 'pushed into sqs'
            job.save()

            self.stdout.write('Job %i pushed into SQS' % job.pk)