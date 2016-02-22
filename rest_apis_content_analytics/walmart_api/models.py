from django.db import models
from django.contrib.auth.models import User


class SubmissionHistory(models.Model):
    """ Tracks the history of items uploaded to Walmart """
    user = models.ForeignKey(User, blank=True, null=True)
    feed_id = models.CharField(max_length=50)

    def get_statuses(self):
        return [s.status for s in SubmissionStatus.objects.filter(history=self)]

    def set_statuses(self, status_list):
        for status in status_list:
            SubmissionStatus.objects.create(history=self, status=status)

    def all_items_ok(self):
        return all([s.lower() == 'success' for s in self.get_statuses()])


class SubmissionStatus(models.Model):
    history = models.ForeignKey(SubmissionHistory)
    status = models.CharField(max_length=20)
