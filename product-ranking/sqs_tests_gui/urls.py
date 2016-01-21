from django.conf.urls import include, url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

from gui.views import LogFileView, CSVDataFileView, AddJob, ProgressMessagesView,\
    ProgressFileView, SearchFilesView, GetS3FileView, SearchS3Cache, \
    RenderS3CachePage, ViewBase64Image


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
    url(r'^progress/(?P<job>[0-9]+)/$', ProgressFileView.as_view(),
        name='progress_file_view'),
    url(r'^add-job', csrf_exempt(AddJob.as_view()),
        name='add_job_view'),
    url(r'^view-base64-image/(?P<job>[0-9]+)/$', ViewBase64Image.as_view(),
        name='view_base64_image'),
    url(r'^progress/', ProgressMessagesView.as_view(), name='progress'),
    url(r'^search-files/', SearchFilesView.as_view(), name='search-files'),
    url(r'^get-file/', GetS3FileView.as_view(), name='get-file'),
    url(r'^s3-cache/$', SearchS3Cache.as_view(), name='s3-cache'),
    url(r'^render-s3-cache/$', RenderS3CachePage.as_view(), name='render-s3-cache'),

    url('^fcgi/$', include('fcgi.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)