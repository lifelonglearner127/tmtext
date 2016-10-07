#
# Sends an email with the report data
#

import os
import sys
import json
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from reports.email_utils import SESMessage
from django.template.loader import render_to_string


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD, '..', '..', '..', '..', 's3_reports'))

from jobs_per_server_per_site import dump_reports
from reports.utils import run_report_generation, get_report_fname, dicts_to_ordered_lists


SCRIPT_DIR = REPORTS_DIR = os.path.join(CWD, '..', '..', 's3_reports')
LIST_FILE = os.path.join(CWD, '..', 'gui', 'management', 'commands', "_amazon_listing.txt")


SEND_TO = ['no.andrey@gmail.com']


class Command(BaseCommand):

    @staticmethod
    def _get_mail_sent_marker(date):
        return os.path.join(CWD, 'email_sent_%s.marker' % date.strftime('%Y_%m_%d'))

    def handle(self, *args, **options):
        date = datetime.datetime.utcnow().today()
        # check if the email has already been sent

        if os.path.exists(self._get_mail_sent_marker(date)):
            return

        if not os.path.exists(get_report_fname(date)):
            run_report_generation(date)
            return

        context = {}
        context['is_email_template'] = 1
        with open(get_report_fname(date), 'r') as fh:
            reports = json.loads(fh.read())
        context['by_server'] = sorted([(server, data) for server, data in
                                       dicts_to_ordered_lists(reports['by_server']).items()])
        context['by_spider'] = sorted([(spider, data) for spider, data in
                                       dicts_to_ordered_lists(reports['by_spider']).items()])
        html_template = render_to_string('sqs_jobs.html', context=context)

        msg = SESMessage(
            'noreply@contentanalyticsinc.com',
            SEND_TO,
            'SQS Jobs statistics for %s' % date.strftime('%Y-%m-%d')
        )
        #msg.text = 'Text body'
        msg.html = html_template
        msg.send()

        with open(self._get_mail_sent_marker(date), 'w') as fh:
            fh.write('1')
