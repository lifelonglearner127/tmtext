import os
import sys
import datetime
import random
import json
import base64

from django.views.generic import RedirectView, View, ListView, TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse

from .models import get_data_filename, get_log_filename, Job, JobGrouperCache
import settings


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD,  '..', '..', '..',
                             'deploy', 'sqs_ranking_spiders'))
from test_sqs_flow import _read_queue
from scrapy_daemon import PROGRESS_QUEUE_NAME


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


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class AddJob(View):
    """ For POSTing jobs """
    def post(self, request, *args, **kwargs):
        client_ip = get_client_ip(request)

        site = request.POST.get('site', '')
        searchterms_str = request.POST.get('searchterms_str', '')
        product_url = request.POST.get('product_url', '')

        name = ('AUTO|'+str(client_ip) + '|' + site
                + '|' + searchterms_str)

        if not '_products' in site:
            site = site.strip() + '_products'

        quantity = int(request.POST.get('quantity', 200))

        branch = 's3_cache'  # TODO: change to master after it's merged into master

        if product_url and not searchterms_str:
            # create a new 'grouper' object, not the real job
            JobGrouperCache.objects.get_or_create(
                spider=site, product_url=product_url,
                extra_args=json.dumps({
                    'name': name, 'branch_name': branch
                })
            )
            return HttpResponse('JobGrouperCache object created')
        else:
            Job.objects.get_or_create(
                name=name,
                spider=site,
                search_term=searchterms_str,
                product_url=product_url,
                quantity=quantity,
                task_id=random.randrange(100000, 900000),
                mode='no cache',
                save_s3_cache=True,
                branch_name=branch
            )
            return HttpResponse('Job object created')


class ProgressMessagesView(AdminOnlyMixin, TemplateView):
    template_name = 'progress_messages.html'
    max_messages = 999

    def get_context_data(self, **kwargs):
        context = super(ProgressMessagesView, self).get_context_data(**kwargs)
        context['msgs'] = [
            base64.decode(msg) for msg in
            _read_queue(PROGRESS_QUEUE_NAME)
        ]