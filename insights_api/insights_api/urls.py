"""insights_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers

from product_list.views import ProductListViewSet, SitesViewSet, \
    SearchTermsViewSet, DateViewSet, BrandsViewSet, \
    SearchTermsGroupsViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'product_lists', ProductListViewSet)
router.register(r'search_terms', SearchTermsViewSet)
router.register(r'search_terms_groups', SearchTermsGroupsViewSet)
router.register(r'sites', SitesViewSet, base_name='sites')
router.register(r'brands', BrandsViewSet, base_name='brands')
router.register(r'dates', DateViewSet, base_name='dates')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
]
