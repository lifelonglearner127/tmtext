import os
import sys
import json

from django.views.generic import TemplateView, FormView
from django.http import HttpResponse

from fcgi.views import AuthViewMixin


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD, '..', '..', 's3_reports'))

from jobs_per_server_per_site import dump_reports
from forms import ReportDateForm
from utils import run_report_generation, get_report_fname, dicts_to_ordered_lists


SCRIPT_DIR = REPORTS_DIR = os.path.join(CWD, '..', '..', 's3_reports')
LIST_FILE = os.path.join(CWD, '..', 'gui', 'management', 'commands', "_amazon_listing.txt")


class ReportSQSJobs(AuthViewMixin, FormView):
    template_name = 'sqs_jobs.html'
    form_class = ReportDateForm

    def get_context_data(self, **kwargs):
        context = super(ReportSQSJobs, self).get_context_data(**kwargs)
        form = self.get_form_class()(self.request.GET)
        if form.is_bound:
            if form.is_valid():
                date = form.cleaned_data.get('date')
                if not os.path.exists(self._get_report_fname(date)):
                    context['error_msg'] = ("Report does not exist. Now it's already being generated."
                                            "Please wait a few minutes and try again.")
                    run_report_generation(date)
                    return context
                with open(get_report_fname(date), 'r') as fh:
                    reports = json.loads(fh.read())
                context['by_server'] = sorted([(server, data) for server, data in
                                               dicts_to_ordered_lists(reports['by_server']).items()])
                context['by_spider'] = sorted([(spider, data) for spider, data in
                                               dicts_to_ordered_lists(reports['by_spider']).items()])
        return context
