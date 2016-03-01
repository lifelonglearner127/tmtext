import json

from django.views.generic import TemplateView, View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from models import SubmitXMLItem


class StatsView(TemplateView):
    template_name = 'stats.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StatsView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StatsView, self).get_context_data(**kwargs)
        context['breadcrumblist'] = [('Statistics', self.request.path)]
        return context


class GetStatsAjax(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GetStatsAjax, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return json.dumps({})
        return json.dumps({
            'stats_all_walmart_xml_items': SubmitXMLItem.objects.filter(
                user=request.user).order_by('-when').distinct(),
            'stats_failed_walmart_xml_items': SubmitXMLItem.failed_xml_items(request),
            'stats_successful_walmart_xml_items': SubmitXMLItem.successful_xml_items(request),
            'stats_today_all_xml_items': SubmitXMLItem.today_all_xml_items(request),
            'stats_today_successful_xml_items': SubmitXMLItem.today_successful_xml_items(request),
        })