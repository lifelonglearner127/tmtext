from django.views.generic import FormView
from .forms import ReloadFcgiForm
from tests_app.views import AuthViewMixin


class ReloadFcgiView(AuthViewMixin, FormView):
    form_class = ReloadFcgiForm
    template_name = 'reload_fcgi.html'
    success_url = '/'

    def form_valid(self, form):
        form.reload_fcgi()
        return super(ReloadFcgiView, self).form_valid(form)