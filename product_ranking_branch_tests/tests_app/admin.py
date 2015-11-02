from django.contrib import admin

from .models import SearchTerm, Spider, TestRun, Report, ReportSearchterm
from .forms import TestRunForm


admin.site.register(SearchTerm)
admin.site.register(Spider)
admin.site.register(Report)
admin.site.register(ReportSearchterm)


class TestRunAdmin(admin.ModelAdmin):
    form = TestRunForm
admin.site.register(TestRun, TestRunAdmin)