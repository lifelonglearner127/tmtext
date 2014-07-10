from django.conf.urls import patterns, url

from simple_cli import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'status/$', views.web_runner_status, name='web_runner_status'),
)
# vim: set expandtab ts=4 sw=2:
