# Creates many test jobs

import os
import sys
import random
import argparse
import datetime

from django.core.management.base import BaseCommand, CommandError

CWD = os.path.dirname(os.path.abspath(__file__))

from gui.models import Job


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Load jobs from file.')
    parser.add_argument('file', help="a file to load jobs from (1 URL per line)")
    parser.add_argument('spider', help="the name of the spider")
    parser.add_argument('branch', help="the name of the branch to run the scrapers at")
    return parser.parse_args()


class Command(BaseCommand):
    help = 'Load jobs from file'

    def handle(self, *args, **options):
        cmd_args = parse_arguments()
        for line in open(cmd_args.file, 'r'):
            line = line.strip()
            if not line:
                continue
            Job.objects.create(
                name='jobs from file - spider %s, created at %s' % (
                    cmd_args.spider,
                    datetime.datetime.utcnow().strftime("%Y.%m.%d")),
                spider=cmd_args.spider,
                product_url=line,
                quantity=99,
                task_id=cmd_args.spider + random.randrange(100000, 900000),
                mode='no cache',
                branch_name=cmd_args.branch
            )
