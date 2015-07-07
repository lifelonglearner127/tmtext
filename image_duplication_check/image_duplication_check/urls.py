from django.conf.urls import url, include
from rest_framework import routers
from image_duplication_check.image_duplication.views import CompareTwoImageViewSet, ClassifyImagesBySimilarity, FindSimilarityInImageList

router = routers.SimpleRouter()
router.register(r'comparetwoimages', CompareTwoImageViewSet, 'comparetwoimages')
router.register(r'classifyimagesbysimilarity', ClassifyImagesBySimilarity, 'classifyimagesbysimilarity')
router.register(r'findsimilarityinimagelist', FindSimilarityInImageList, 'findsimilarityinimagelist')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

