from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from tests_app.views import *


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'auto_tests.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'}, name='login_view'),

    url(r'^$', SpidersView.as_view(), name="spiders_view"),
    url(r'^reports/(?P<spider>[a-zA-Z_]+)/$', ReportsView.as_view(), name="reports_view"),
    url(r'^reports/(?P<report>[0-9]+)/$', ReportView.as_view(), name="report_view"),
)

if settings.DEBUG:
    #urlpatterns += static(settings.STATIC_URL,
    #                      document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

if 'django_ses' in settings.INSTALLED_APPS:
    urlpatterns += (url(r'^admin/django-ses/', include('django_ses.urls')),)