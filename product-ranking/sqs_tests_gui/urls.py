from django.conf.urls import include, url
from django.contrib import admin

from gui.views import LogFileView, CSVDataFileView


from django.conf import settings
from django.conf.urls.static import static


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

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)