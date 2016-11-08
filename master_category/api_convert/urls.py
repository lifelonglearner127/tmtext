from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^export/google-manufacturer/$', views.GoogleManufacturerView.as_view(),
        name='google-manufacturer'),
]