import random

from django.core.management import BaseCommand
from django.contrib.auth.models import User

from walmart_api.models import *
from walmart_api.views import (parse_walmart_api_log, get_walmart_api_invoke_log,
                               get_feed_status)
from statistics.models import *


class Command(BaseCommand):
    help = 'Updates feed history and statistics for all users'

    def handle(self, *args, **options):
        for user in User.objects.all():
            for log_rec in parse_walmart_api_log(user):
                date = log_rec['datetime']
                upc = log_rec['upc'].strip()
                feed_id = log_rec['feed_id'].strip()
                print 'Feed ID %s' % feed_id

                # 1. Update old "incomplete" statuses - remove SubmissionHistory records and Statistics
                for sub_history in SubmissionHistory.objects.filter(
                        user=user, feed_id=feed_id):
                    if not sub_history.all_items_ok():
                        _statuses = [s.lower() for s in sub_history.get_statuses()]
                        if 'received' in _statuses or 'inprogress' in _statuses:
                            print 'REFRESHING STATUS %s' % feed_id, _statuses
                            print 'Removing existing SubmissionHistory and Statistics for feed ID %s' % feed_id
                            SubmissionHistory.objects.filter(user=user, feed_id=feed_id).delete()
                            SubmitXMLItem.objects.filter(user=user, item_metadata__feed_id=feed_id).delete()
                            continue
                """
                        new_status = get_feed_status(user, feed_id, date=date, check_auth=False)
                        # check if stats item already exist
                        metadata = SubmitXMLItem.objects.filter(
                            user=user, auth='session', when=date, item_metadata__feed_id=feed_id,
                            item_metadata__upc=upc)
                        if new_status.get('ok', None):
                            metadata.update(status='successful')
                """
                # process feed statuses for unprocessed items
                print get_feed_status(user, feed_id, date=date,
                                      process_check_feed=True, check_auth=False)
