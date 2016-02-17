from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class StatsView(TemplateView):
    template_name = 'stats.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StatsView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StatsView, self).get_context_data(**kwargs)
        context['breadcrumblist'] = [('Statistics', self.request.path)]
        return context
