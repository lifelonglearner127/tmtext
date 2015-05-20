import sys
import os
import datetime

from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from boto import ses

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CWD, '..', '..', '..'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import settings
from tests_app.models import (Spider, TestRun, FailedRequest, Alert,
                              ThresholdSettings)


class Command(BaseCommand):
    can_import_settings = True

    def _what_is_broken(self):
        spiders = Spider.objects.filter(active=True)
        return [s for s in spiders if s.is_error()]

    def handle(self, *args, **options):
        # send a summary email
        email_subj = '[%s] SC Auto-tests: daily summary updates'
        if self._what_is_broken():
            email_subj %= 'FAILED'
        else:
            email_subj %= 'PASSED'

        email_template = """
%i spider(s) checked.

Test results:
""" % Spider.objects.filter(active=True).count()

        for spider in Spider.objects.filter(active=True).order_by('name'):
            if spider.is_error():
                email_template += "* [FAILED] %s" % spider.name
            else:
                email_template += "* [PASSED] %s" % spider.name
            email_template += ". Details: %s" % spider.get_absolute_url()
            email_template += '\n\n'

        email_template += "\n\nUTC time: %s" % datetime.datetime.utcnow()

        print email_template

        # send report email
        conn = ses.connect_to_region(
            'us-east-1',
            aws_access_key_id=settings.AMAZON_SES_KEY,
            aws_secret_access_key=settings.AMAZON_SES_SECRET,
        )
        to_email = ThresholdSettings.objects.all().first()
        if to_email:
            to_email = to_email.notify
            to_email = [e.strip() for e in to_email.split(',')]
            print "SENDING TO", to_email
            print conn.send_email(
                'contentanalyticsinc.autotests@gmail.com',
                email_subj,
                email_template,
                to_addresses=to_email,
                bcc_addresses=[]
            )
