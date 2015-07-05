from django.views.generic import RedirectView, View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse

from .models import get_data_filename, get_log_filename
import settings


class AdminOnlyMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponse('you must be admin')
        return super(AdminOnlyMixin, self).dispatch(request, *args, **kwargs)


class CSVDataFileView(AdminOnlyMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        data_fname = get_data_filename(kwargs['job'])
        if data_fname.startswith('/'):
            data_fname = data_fname[1:]
        return settings.MEDIA_URL + data_fname


class LogFileView(AdminOnlyMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        log_fname = get_log_filename(kwargs['job'])
        if log_fname.startswith('/'):
            log_fname = log_fname[1:]
        return settings.MEDIA_URL + log_fname


class AddJob(View):
    """ For POSTing jobs """
    def post(self, request, *args, **kwargs):
        with open('/tmp/_add_job.txt', 'a') as fh:
            import datetime
            _str = ''
            for key, value in request.POST.iteritems():
                _str += '    %s - %s' % (key, value)
            fh.write(str(datetime.datetime.now()) + '\n' + _str + '\n\n')