from django.contrib import admin
from django.core.urlresolvers import reverse_lazy

# Register your models here.
from .models import Job
from .forms import JobForm


COLORS = {
    'error': 'red',
    'success': 'green'
}


def link_to_csv_data_file(job):
    if not isinstance(job, int):
        job = job.pk
    return reverse_lazy('csv_data_file_view', kwargs={'job': job})


def admin_link_to_csv_data_file(job):
    return "<a href='%s'>CSV</a>" % (link_to_csv_data_file(job))
admin_link_to_csv_data_file.allow_tags = True


def link_to_log_file(job):
    if not isinstance(job, int):
        job = job.pk
    return reverse_lazy('log_file_view', kwargs={'job': job})


def admin_link_to_log_file(job):
    return "<a href='%s'>Log</a>" % (link_to_log_file(job))
admin_link_to_log_file.allow_tags = True


def admin_status(job):
    _template = "<span style='color:%s; font-weight:%s'>%s</span>"
    if job.status.lower() == 'finished':
        return _template % ('green', '', job.status)
    elif job.status.lower() == 'failed':
        return _template % ('red', '', job.status)
    elif job.status.lower() == 'pushed into sqs':
        return _template % ('', 'bold', job.status)
    return job.status
admin_status.allow_tags = True


class JobAdmin(admin.ModelAdmin):
    list_display = (
        'task_id', 'spider', 'name', 'searchterm_or_url', admin_status,
        'created', 'finished',
        admin_link_to_csv_data_file, admin_link_to_log_file
    )
    list_filter = ('status', 'created', 'finished')
    search_fields = ('name', 'spider', 'product_url', 'search_term',
                     'server_name')
    form = JobForm

    def reset_status_to_created(self, request, qs, *args, **kwargs):
        qs.update(status='created')

    def reset_status_to_pushed_into_sqs(self, request, qs, *args, **kwargs):
        qs.update(status='pushed into sqs')

    actions = (reset_status_to_created, reset_status_to_pushed_into_sqs)

admin.site.register(Job, JobAdmin)