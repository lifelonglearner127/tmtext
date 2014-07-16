from django.conf.urls import patterns, url

from simple_cli import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'status/$', views.web_runner_status, name='web_runner_status'),
    url(r'logs/$', views.web_runner_logs, name='web_runner_logs'),
    url(r'logs/(?P<logfile_id>\d+)/$', views.web_runner_logs_view, name='web_runner_logs_view'),
)
# vim: set expandtab ts=4 sw=2:
