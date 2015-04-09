from django.contrib import admin

# Register your models here.
from .models import Job
from .forms import JobForm


def link_to_csv_data_file(job):
    # TODO: implement
    return job.id


def link_to_log_file(job):
    # TODO: implement
    return job.id


class JobAdmin(admin.ModelAdmin):
    list_display = (
        'task_id', 'spider', 'name', 'status', 'created', 'finished',
        link_to_csv_data_file, link_to_log_file
    )
    list_filter = ('status', 'created', 'finished')
    search_fields = ('name', 'spider', 'product_url', 'search_term',
                     'server_name')
    form = JobForm

admin.site.register(Job, JobAdmin)