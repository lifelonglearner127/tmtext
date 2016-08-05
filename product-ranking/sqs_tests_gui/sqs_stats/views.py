from django.views.generic import TemplateView

from fcgi.views import AuthViewMixin
from . import get_number_of_messages_in_queues, get_number_of_instances_in_autoscale_groups


class SQSAutoscaleStats(AuthViewMixin, TemplateView):
    template_name = 'sqs_autoscale_stats.html'

    def get_context_data(self, **kwargs):
        context = super(SQSAutoscaleStats, self).get_context_data(**kwargs)
        context['queues_data'] = get_number_of_messages_in_queues()
        context['groups_data'] = get_number_of_instances_in_autoscale_groups()
        return context
