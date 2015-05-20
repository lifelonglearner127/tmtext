from django.views.generic import DetailView, TemplateView, RedirectView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse_lazy

from .models import TestRun, Spider, FailedRequest


class AuthViewMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseRedirect(
                reverse_lazy('login_view')
            )
        return super(AuthViewMixin, self).dispatch(request, *args, **kwargs)


class DashboardView(AuthViewMixin, TemplateView):
    template_name = 'spiders.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['spiders'] = Spider.objects.all().order_by('name')
        return context
    # TODO: failed\success spiders, num of spiders checked in the last 3 days, num of test runs performed in the last 3 days, num of alerts sent (?)


class SpiderReview(AuthViewMixin, DetailView):
    model = Spider
    template_name = 'spider.html'

    def get_context_data(self, **kwargs):
        context = super(SpiderReview, self).get_context_data(**kwargs)
        context['running_runs'] = self.object.get_last_running_test_runs()
        context['failed_runs'] = self.object.get_last_failed_test_runs()
        context['passed_runs'] = self.object.get_last_successful_test_runs()
        return context


class TestRunReview(AuthViewMixin, DetailView):
    model = TestRun


class SpiderBySpiderName(AuthViewMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        spider = get_object_or_404(Spider, name=kwargs['name'])
        return reverse_lazy('tests_app_spider_review',
                            kwargs={'pk': spider.pk})