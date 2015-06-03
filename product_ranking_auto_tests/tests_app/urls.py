from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^$', views.DashboardView.as_view(), name='tests_app_dashboard'),
    url(r'spider/(?P<pk>\d+)/$', views.SpiderReview.as_view(),
        name='tests_app_spider_review'),
    url(r'test-run/(?P<pk>\d+)/$', views.TestRunReview.as_view(),
        name='tests_app_test_run_review'),
    url(r'spider-by-name/(?P<name>[\d\w_]+)/$',
        views.SpiderBySpiderName.as_view(),
        name='tests_app_spider_by_spider_name'),
    url(r'json-to-csv/(?P<json>.+)$', views.JSONToCSV.as_view(),
        name='json_to_csv')
)