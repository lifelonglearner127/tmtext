from django.db import models
from django.contrib.auth.models import User


class SubmissionHistory(models.Model):
    """ Tracks the history of items uploaded to Walmart """
    user = models.ForeignKey(User, blank=True, null=True)
    feed_id = models.CharField(max_length=50)
    server_name = models.CharField(max_length=100, blank=True, null=True)
    client_ip = models.IPAddressField(blank=True, null=True)

    def get_statuses(self):
        return [s.status for s in SubmissionStatus.objects.filter(
            history__feed_id=self.feed_id, history__user=self.user)]

    def set_statuses(self, status_list):
        for status in status_list:
            SubmissionStatus.objects.create(history=self, status=status)

    def all_items_ok(self):
        return all([s.lower() == 'success' for s in self.get_statuses()])

    def partial_success(self):
        statuses = [s.lower() for s in self.get_statuses()]
        return 'success' in statuses and not self.all_items_ok()

    def in_progress(self):
        statuses = [s.lower() for s in self.get_statuses()]
        return 'inprogress' in statuses


class SubmissionStatus(models.Model):
    history = models.ForeignKey(SubmissionHistory)
    status = models.CharField(max_length=20, db_index=True)
