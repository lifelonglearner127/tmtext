from django.contrib import admin
from django.conf import settings


from .models import SearchTerm, Spider, TestRun, Report

admin.site.register(SearchTerm)
admin.site.register(Spider)
admin.site.register(TestRun)
admin.site.register(Report)