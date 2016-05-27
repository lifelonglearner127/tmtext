from django.contrib import admin

# Register your models here.
from models import SubmissionStatus, SubmissionHistory, SubmissionXMLFile


admin.site.register(SubmissionStatus)
admin.site.register(SubmissionXMLFile)

@admin.register(SubmissionHistory)
class SubmissionHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'feed_id', 'created', 'server_name', 'client_ip']
    search_fields = ['feed_id', 'user__username', 'server_name', 'client_ip']
