from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^export/google-manufacturer/$', views.GoogleManufacturerView.as_view(),
        name='google-manufacturer'),
    url(r'^amazon-to-walmart/$', views.AmazonToWalmartView.as_view(),
        name='amazone-to-walmart'),
]