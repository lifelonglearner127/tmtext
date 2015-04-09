from django.conf.urls import include, url
from django.contrib import admin

from gui.views import LogFileView, CSVDataFileView
from settings import STATIC_URL


urlpatterns = [
    # Examples:
    # url(r'^$', 'gui.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^log/(?P<job>[0-9]+)/$', LogFileView.as_view(),
        name='log_file_view'),
    url(r'^data/(?P<job>[0-9]+)/$', CSVDataFileView.as_view(),
        name='csv_data_file_view'),
]
