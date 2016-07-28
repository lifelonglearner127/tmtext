import os
import json

from django.contrib import admin
from django.core.urlresolvers import reverse_lazy

# Register your models here.
from .models import Job, JobGrouperCache, get_progress_filename
from .forms import JobForm

from settings import MEDIA_ROOT


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


def link_to_progress_file(job):
    if not isinstance(job, int):
        job = job.pk
    return reverse_lazy('progress_file_view', kwargs={'job': job})


def admin_link_to_log_file(job):
    return "<a href='%s'>Log</a>" % (link_to_log_file(job))
admin_link_to_log_file.allow_tags = True


def admin_link_to_progress_file(job):
    # try to read progress from the file
    if not os.path.exists(MEDIA_ROOT + get_progress_filename(job)):
        return "<a href='%s'>Progress</a>" % (link_to_progress_file(job))
    else:
        with open(MEDIA_ROOT + get_progress_filename(job)) as fh:
            cont = fh.read()
        try:
            cont = json.loads(cont)
        except Exception as e:
            return "<a href='%s'>(Invalid JSON)</a>" % (link_to_progress_file(job))
        if not isinstance(cont, dict):
            return "<a href='%s'>(Not DICT)</a>" % (link_to_progress_file(job))
        progress = cont.get('progress', -1)
        return "<a href='%s'>%s products</a>" % (link_to_progress_file(job), progress)
admin_link_to_progress_file.allow_tags = True


def admin_status(job):
    _template = "<span style='color:%s; font-weight:%s'>%s</span>"
    if job.status.lower() == 'finished':
        return _template % ('green', '', job.status)
    elif job.status.lower() == 'failed':
        return _template % ('red', '', job.status)
    elif job.status.lower() == 'pushed into sqs':
        return _template % ('', 'bold', job.status)
    elif job.status.lower() == 'in progress':
        return _template % ('blue', 'bold', job.status)
    return job.status
admin_status.allow_tags = True


class JobAdmin(admin.ModelAdmin):
    list_display = (
        'task_id', 'spider', 'name', 'searchterm_or_url', 'branch_name', admin_status, 'mode',
        'created', 'finished',
        admin_link_to_csv_data_file, admin_link_to_log_file,
        admin_link_to_progress_file, Job.view_as_image
    )
    list_filter = ('status', 'created', 'finished',
                   'save_raw_pages')
    search_fields = ('name', 'spider', 'product_url', 'product_urls',
                     'search_term', 'server_name')
    form = JobForm

    def reset_status_to_created(self, request, qs, *args, **kwargs):
        qs.update(status='created')

    def reset_status_to_pushed_into_sqs(self, request, qs, *args, **kwargs):
        qs.update(status='pushed into sqs')

    actions = (reset_status_to_created, reset_status_to_pushed_into_sqs)


admin.site.register(Job, JobAdmin)

admin.site.register(JobGrouperCache)