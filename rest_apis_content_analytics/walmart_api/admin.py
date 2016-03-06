from django.contrib import admin

# Register your models here.
from models import SubmissionStatus, SubmissionHistory


admin.site.register(SubmissionStatus)

@admin.register(SubmissionHistory)
class SubmissionHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'feed_id']
    search_fields = ['feed_id', 'user__username']