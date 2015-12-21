from django.conf.urls import url, include
from rest_framework import routers
from image_duplication.views import CompareTwoImageViewSet, ClassifyImagesBySimilarity, FindSimilarityInImageList
from walmart_developer_accounts.views import WalmartAccountViewSet
from walmart_api.views import InvokeWalmartApiViewSet, ItemsUpdateByWalmartApiViewSet, CheckFeedStatusByWalmartApiViewSet
from nutrition_info_images.views import ClassifyTextImagesByNutritionInfoViewSet

router = routers.SimpleRouter()
router.register(r'comparetwoimages', CompareTwoImageViewSet, 'comparetwoimages')
router.register(r'classifyimagesbysimilarity', ClassifyImagesBySimilarity, 'classifyimagesbysimilarity')
router.register(r'findsimilarityinimagelist', FindSimilarityInImageList, 'findsimilarityinimagelist')
router.register(r'walmartaccounts', WalmartAccountViewSet, 'walmartaccounts')
router.register(r'classifytextimagesbynutritioninfo', ClassifyTextImagesByNutritionInfoViewSet, 'classifytextimagesbynutritioninfo')
router.register(r'invokewalmartapi', InvokeWalmartApiViewSet, 'invokewalmartapi')
router.register(r'items_update_by_walmart_api', ItemsUpdateByWalmartApiViewSet, 'items_update_by_walmart_api')
router.register(r'check_feed_status_by_walmart_api', CheckFeedStatusByWalmartApiViewSet, 'check_feed_status_by_walmart_api')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

