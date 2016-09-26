import os
import sys
import json

from django.views.generic import TemplateView, FormView
from django.http import HttpResponse

from fcgi.views import AuthViewMixin


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(os.path.join(CWD, '..', '..', 's3_reports'))

from jobs_per_server_per_site import dump_reports
from forms import ReportDateForm


REPORTS_DIR = os.path.join(CWD, '..', '..', 's3_reports')


class ReportSQSJobs(AuthViewMixin, FormView):
    template_name = 'sqs_jobs.html'

    def _get_report_fname(self, date):
        return os.path.join(REPORTS_DIR, 'sqs_jobs_%s.json.txt' % date.strftime('%Y-%m-%d'))

    def get_context_data(self, **kwargs):
        context = super(ReportSQSJobs, self).get_context_data(**kwargs)
        form = self.get_form(self.get_form_class())(self.request.DATA)
        if form.is_bound:
            if form.is_valid():
                date = form.cleaned_data.get('date')
                if not os.path.exists(self._get_report_fname(date)):
                    # TODO: run report?
                    context['error_msg'] = "Report does not exist. Wait until it's created"
                    return context
                with open(self._get_report_fname(date), 'r') as fh:
                    reports = json.loads(fh.read())
                context['reports'] = reports
        return context

    #def get_context_data(self, **kwargs):
    ##    context = super(ReportSQSJobs, self).get_context_data(**kwargs)
    #   date =
    #    context['']
