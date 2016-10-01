import os
import sys
import json
import threading
import copy

from django.views.generic import TemplateView, FormView
from django.http import HttpResponse

from fcgi.views import AuthViewMixin


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD, '..', '..', 's3_reports'))

from jobs_per_server_per_site import dump_reports
from forms import ReportDateForm


SCRIPT_DIR = REPORTS_DIR = os.path.join(CWD, '..', '..', 's3_reports')
LIST_FILE = os.path.join(CWD, '..', 'gui', 'management', 'commands', "_amazon_listing.txt")


class ReportSQSJobs(AuthViewMixin, FormView):
    template_name = 'sqs_jobs.html'
    form_class = ReportDateForm

    def _get_report_fname(self, date):
        return os.path.join(REPORTS_DIR, 'sqs_jobs_%s.json.txt' % date.strftime('%Y-%m-%d'))

    def _run_report_generation(self, date):
        thread = threading.Thread(target=dump_reports, args=(LIST_FILE, date, self._get_report_fname(date)))
        thread.daemon = True
        thread.run()

    @staticmethod
    def _dicts_to_ordered_lists(dikt):
        if isinstance(dikt, (list, tuple)):
            dikt = dikt[0]
        result = copy.copy({})
        for key, value in dikt.items():
            value_list = copy.copy([])
            result[key] = value_list
            for val_key, val_val in value.items():
                result[key].append((val_key, val_val))
            result[key].sort(reverse=True, key=lambda i: i[1])
        return result

    def get_context_data(self, **kwargs):
        context = super(ReportSQSJobs, self).get_context_data(**kwargs)
        form = self.get_form_class()(self.request.GET)
        if form.is_bound:
            if form.is_valid():
                date = form.cleaned_data.get('date')
                if not os.path.exists(self._get_report_fname(date)):
                    context['error_msg'] = ("Report does not exist. Now it's already being generated."
                                            "Please wait a few minutes and try again.")
                    self._run_report_generation(date)
                    return context
                with open(self._get_report_fname(date), 'r') as fh:
                    reports = json.loads(fh.read())
                context['by_server'] = sorted([(server, data) for server, data in
                                               self._dicts_to_ordered_lists(reports['by_server']).items()])
                context['by_spider'] = sorted([(spider, data) for spider, data in
                                               self._dicts_to_ordered_lists(reports['by_spider']).items()])
        return context
