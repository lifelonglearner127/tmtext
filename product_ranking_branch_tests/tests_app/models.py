from django.db import models

from jsonfield import JSONField  # pip install jsonfield
from multiselectfield import MultiSelectField

from utils import get_sc_fields, generate_spider_choices


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
        null=True, blank=True)
    skip_urls = models.CharField(
        max_length=150, blank=True, null=True,
        help_text="All URLs containing this pattern will be skipped")
    strip_get_args = models.BooleanField(default=False)

    def __unicode__(self):
        return 'Branches [%s - %s], Spider [%s], started %s, %s' % (
            self.branch1, self.branch2, self.spider.name, self.when_started,
            self.status.upper())


class Report(models.Model):
    testrun = models.ForeignKey(TestRun, related_name="testrun_reports")

    total_urls = models.IntegerField(blank=True, null=True, help_text="Do not fill")
    matched_urls = models.IntegerField(blank=True, null=True, help_text="Do not fill")
    diffs = JSONField(blank=True, null=True, help_text="Do not fill")

    when_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return 'Test run %s' % (self.testrun.__unicode__().lower())