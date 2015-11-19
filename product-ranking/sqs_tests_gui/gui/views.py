import os
import sys
import datetime
import random
import json
import base64
import tempfile
import mimetypes
import cPickle as pickle

from django.core.servers.basehttp import FileWrapper
from django.views.generic import RedirectView, View, ListView, TemplateView, FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse, HttpResponseRedirect
import boto
from boto.s3.connection import S3Connection

from .models import get_data_filename, get_log_filename, get_progress_filename,\
    Job, JobGrouperCache
from .forms import S3CacheSelectForm

from management.commands.update_jobs import LOCAL_AMAZON_LIST_CACHE,\
    AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_BUCKET_NAME, download_s3_file
import settings


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD,  '..', '..', '..',
                             'deploy', 'sqs_ranking_spiders'))
sys.path.append(os.path.join(CWD,  '..', '..'))
from add_task_to_sqs import read_access_and_secret_keys
from scrapy_daemon import PROGRESS_QUEUE_NAME
from product_ranking.extensions import amazon_public_key,\
    amazon_secret_key, bucket_name, get_cache_keys, _download_s3_file
from product_ranking.cache import get_partial_request_path
from product_ranking import settings as spider_settings


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


class ProgressFileView(AdminOnlyMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        prog_fname = get_progress_filename(kwargs['job'])
        if prog_fname.startswith('/'):
            prog_fname = prog_fname[1:]
        return settings.MEDIA_URL + prog_fname


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
        if not os.path.exists('/tmp/_enable_add_job'):
            return HttpResponse('/tmp/_enable_add_job does not exist, exit...')

        client_ip = get_client_ip(request)

        site = request.POST.get('site', '')
        searchterms_str = request.POST.get('searchterms_str', '')
        product_url = request.POST.get('product_url', '')

        name = ('AUTO|'+str(client_ip) + '|' + site
                + '|' + searchterms_str)

        if not '_products' in site:
            site = site.strip() + '_products'

        quantity = int(request.POST.get('quantity', 200))

        branch = ''

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

    def _connect(self, name=PROGRESS_QUEUE_NAME, region="us-east-1"):
        self.conn = boto.sqs.connect_to_region(region)
        self.q = self.conn.get_queue(name)

    def _msgs(self, num_messages=100, timeout=3):
        return [base64.b64decode(m.get_body())
                for m in self.q.get_messages(visibility_timeout=timeout)]

    def get_context_data(self, **kwargs):
        context = super(ProgressMessagesView, self).get_context_data(**kwargs)
        access, secret = read_access_and_secret_keys()
        self._connect()
        context['msgs'] = self._msgs()
        return context


class SearchFilesView(AdminOnlyMixin, TemplateView):
    template_name = 'search_s3_files.html'
    max_files = 400

    def get_context_data(self, **kwargs):
        result = []
        context = super(SearchFilesView, self).get_context_data(**kwargs)
        error = None
        warning = None
        searchterm = self.request.GET.get('searchterm', '')
        if not searchterm:
            return context  # not searched
        elif len(searchterm) < 4:
            error = 'Searchterm must be longer than 4 chars'
        else:
            with open(LOCAL_AMAZON_LIST_CACHE, 'r') as fh:
                for line in fh:
                    line = line.strip()
                    if '<Key:' in line and ',' in line:
                        line = line.split(',', 1)[1]
                        if line[-1] == '>':
                            line = line[0:-1]
                        if searchterm.lower() in line.lower():
                            result.append(line)
                        if len(result) > self.max_files:
                            warning = 'More than %i results matched' % self.max_files
                            break
        context['error'] = error
        context['warning'] = warning
        context['results'] = result
        context['searchterm'] = searchterm
        return context


class GetS3FileView(AdminOnlyMixin, View):
    template_name = 'search_s3_files.html'
    max_files = 400

    def get(self, request, **kwargs):
        fname = request.GET['file']
        ext = os.path.splitext(fname)
        if ext and len(ext) > 1 and isinstance(ext, (list, tuple)):
            ext = ext[1]
        # save to a temporary file
        tempfile_name = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        tempfile_name.close()
        download_s3_file(AMAZON_BUCKET_NAME, fname, tempfile_name.name)
        # create File response
        wrapper = FileWrapper(open(tempfile_name.name, 'rb'))
        content_type = mimetypes.guess_type(tempfile_name.name)[0]
        response = HttpResponse(wrapper, content_type=content_type)
        response['Content-Length'] = os.path.getsize(tempfile_name.name)
        response['Content-Disposition'] = 'attachment; filename=%s' % tempfile_name.name
        return response


#******** S3-cache Views ********
# This all will work this way:
# 1) a user selects spider, date, and searchterms (or product url)
# 2) the user then can download the cache, list all the pages and select a page to see
# 3) the user then can see the historical page as it was in the past
class SelectS3Cache(AdminOnlyMixin, FormView):
    form_class = S3CacheSelectForm
    template_name = 'select_s3_cache.html'

    @staticmethod
    def _get_dates_for_spider(spider):
        with open(settings.CACHE_MODELS_FILENAME, 'rb') as fh:
            cont = pickle.loads(fh.read())
        return cont[spider].keys()

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            # return dates
            template = ''
            # TODO: load dates for this spider
            # TODO: render template (options only)
            for date in self._get_dates_for_spider(request.GET.get('spider')):
                template += '<option value="%s">%s</option>' % (date, date)
            return HttpResponse(template)
        else:
            if 'spider' in request.GET and 'date' in request.GET:
                # download cache
                self.cache_downloading = True
                if 'downloading_started' not in request.GET:
                    # it's the first page visit - start downloading
                    import s3funnel
                    funnel = s3funnel.S3Funnel(
                        aws_key=amazon_public_key,
                        aws_secret_key=amazon_secret_key
                    )


                    # TODO: the things below should work in background
                    # ************************************************
                    _keys2download = get_cache_keys(  # TODO: cached "bucket.list()" call?
                        settings=spider_settings, bucket_name=bucket_name,
                        amazon_public_key=amazon_public_key, amazon_secret_key=amazon_secret_key,
                        spider_name=request.GET['spider'],
                        date=datetime.datetime.strptime(request.GET['date'], '%Y-%m-%d').date(),
                        dont_append_url=True)
                    print('Downloading keys...')
                    for key2download in _keys2download:
                        _download_s3_file(key2download, settings=spider_settings)
                    #funnel.get(bucket=bucket_name, ikeys=_keys2download)
                    # ************************************************


                    return HttpResponseRedirect(request.get_full_path()+'&downloading_started=1')
                else:
                    # wait for the downloader process to finish, and list available URLs
                    _cache_dir = get_partial_request_path(
                        spider_settings.HTTPCACHE_DIR, request.GET['spider'],
                        datetime.datetime.strptime(request.GET['date'], '%Y-%m-%d').date(),
                        dont_append_url=True)
                    self.cache_downloaded = True
                    self.available_st_and_urls = os.listdir(_cache_dir)
            # render template
            return super(SelectS3Cache, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SelectS3Cache, self).get_context_data(**kwargs)
        if getattr(self, 'cache_downloading', False):
            context['cache_downloading'] = True
        if getattr(self, 'cache_downloaded', False):
            context['cache_downloaded'] = True
            context['available_st_and_urls'] = self.available_st_and_urls
        return context