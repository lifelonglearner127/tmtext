from django.contrib import admin

# Register your models here.
from models import SubmissionStatus, SubmissionHistory


admin.site.register(SubmissionStatus)
admin.site.register(SubmissionHistory)