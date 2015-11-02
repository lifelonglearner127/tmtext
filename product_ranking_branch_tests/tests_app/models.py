import os
import sys

from django.db import models

from jsonfield import JSONField  # pip install jsonfield
from multiselectfield import MultiSelectField

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD, '..', '..', '..', '..'))
from utils import get_sc_fields, generate_spider_choices


DEFAULT_EXCLUDE_FIELDS = [
    '_statistics'
]


class SearchTerm(models.Model):
    searchterm = models.CharField(max_length=100)
    quantity = models.IntegerField(default=300)

    def __unicode__(self):
        return u'%s [%s]' % (self.searchterm, self.quantity)


class Spider(models.Model):
    name = models.CharField(
        max_length=100, unique=True, choices=generate_spider_choices())
    searchterms = models.ManyToManyField(SearchTerm, help_text="Choose at least 3.")

    def __unicode__(self):
        return self.name


class TestRun(models.Model):
    _status_choices = ('stopped', 'running', 'passed', 'failed')

    when_started = models.DateTimeField(auto_now_add=True)
    when_finished = models.DateTimeField(blank=True, null=True)

    branch1 = models.CharField(max_length=150)
    branch2 = models.CharField(max_length=150)

    spider = models.ForeignKey(Spider, related_name='spider_test_runs')
    status = models.CharField(
        choices=[(c, c) for c in _status_choices], max_length=20,
        default='stopped'
    )

    exclude_fields = MultiSelectField(
        choices=[(k,k) for k in sorted(get_sc_fields())],
        null=True, blank=True,
        default=DEFAULT_EXCLUDE_FIELDS)
    skip_urls = models.CharField(
        max_length=150, blank=True, null=True,
        help_text="All URLs containing this pattern will be skipped")
    strip_get_args = models.BooleanField(default=False)

    def __unicode__(self):
        return 'Branches [%s - %s], Spider [%s], started %s, %s' % (
            self.branch1, self.branch2, self.spider.name, self.when_started,
            self.status.upper())


class Report(models.Model):
    when_created = models.DateTimeField(auto_now_add=True)
    testrun = models.ForeignKey(TestRun, related_name="testrun_reports")

    def not_enough_matched_urls(self):
        for searchterm in self.report_searchterms.all():
            if searchterm.not_enough_matched_urls():
                return True

    def diffs_found(self):
        for searchterm in self.report_searchterms.all():
            if searchterm.diffs:
                return True

    def __unicode__(self):
        return 'Test run %s' % (self.testrun.__unicode__().lower())


class ReportSearchterm(models.Model):
    report = models.ForeignKey(Report, related_name="report_searchterms")
    searchterm = models.ForeignKey(SearchTerm, related_name="searchterm_reports")

    total_urls = models.IntegerField(blank=True, null=True, help_text="Do not fill")
    matched_urls = models.IntegerField(blank=True, null=True, help_text="Do not fill")
    diffs = JSONField(blank=True, null=True, help_text="Do not fill")

    when_created = models.DateTimeField(auto_now_add=True)

    def not_enough_matched_urls(self):
        """ Returns True if the number of matched URLs is too low
            (so the report is not precise enough)
        """
        if self.total_urls is not None and self.matched_urls is not None:
            if self.matched_urls < self.total_urls / 2:
                return True
        if self.matched_urls == 0:
            return True
        if self.matched_urls and self.matched_urls < 10:
            return True

    def __unicode__(self):
        return '[%s] [%s]' % (self.report.__unicode__().lower(),
                              self.searchterm.__unicode__())