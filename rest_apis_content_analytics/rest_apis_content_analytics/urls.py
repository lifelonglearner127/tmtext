from django.conf.urls import url, include
from rest_framework import routers
from image_duplication.views import CompareTwoImageViewSet, ClassifyImagesBySimilarity, FindSimilarityInImageList
from walmart_developer_accounts.views import WalmartAccountViewSet
from walmart_api.views import InvokeWalmartApiViewSet, ItemsUpdateWithXmlFileByWalmartApiViewSet, ItemsUpdateWithXmlTextByWalmartApiViewSet, CheckFeedStatusByWalmartApiViewSet, ValidateWalmartProductXmlTextViewSet, ValidateWalmartProductXmlFileViewSet
from nutrition_info_images.views import ClassifyTextImagesByNutritionInfoViewSet

router = routers.SimpleRouter()
router.register(r'comparetwoimages', CompareTwoImageViewSet, 'comparetwoimages')
router.register(r'classifyimagesbysimilarity', ClassifyImagesBySimilarity, 'classifyimagesbysimilarity')
router.register(r'findsimilarityinimagelist', FindSimilarityInImageList, 'findsimilarityinimagelist')
router.register(r'walmartaccounts', WalmartAccountViewSet, 'walmartaccounts')
router.register(r'classifytextimagesbynutritioninfo', ClassifyTextImagesByNutritionInfoViewSet, 'classifytextimagesbynutritioninfo')
router.register(r'invokewalmartapi', InvokeWalmartApiViewSet, 'invokewalmartapi')
router.register(r'items_update_with_xml_file_by_walmart_api', ItemsUpdateWithXmlFileByWalmartApiViewSet, 'items_update_with_xml_file_by_walmart_api')
router.register(r'items_update_with_xml_text_by_walmart_api', ItemsUpdateWithXmlTextByWalmartApiViewSet, 'items_update_with_xml_text_by_walmart_api')
router.register(r'check_feed_status_by_walmart_api', CheckFeedStatusByWalmartApiViewSet, 'check_feed_status_by_walmart_api')
router.register(r'validate_walmart_product_xml_text', ValidateWalmartProductXmlTextViewSet, 'validate_walmart_product_xml_text')
router.register(r'validate_walmart_product_xml_file', ValidateWalmartProductXmlFileViewSet, 'validate_walmart_product_xml_file')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

