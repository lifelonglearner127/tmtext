from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from image_duplication.views import CompareTwoImageViewSet, ClassifyImagesBySimilarity, FindSimilarityInImageList
from walmart_developer_accounts.views import WalmartAccountViewSet
from walmart_api.views import (InvokeWalmartApiViewSet, ItemsUpdateWithXmlFileByWalmartApiViewSet,
                               ItemsUpdateWithXmlTextByWalmartApiViewSet, CheckFeedStatusByWalmartApiViewSet,
                               ValidateWalmartProductXmlTextViewSet, ValidateWalmartProductXmlFileViewSet,
                               FeedIDRedirectView, DetectDuplicateContentBySeleniumViewset, DetectDuplicateContentByMechanizeViewset,
                               DetectDuplicateContentFromCsvFilesByMechanizeViewset)
from nutrition_info_images.views import ClassifyTextImagesByNutritionInfoViewSet


# API endpoints
urlpatterns = format_suffix_patterns([
    url(r'^items_update_with_xml_file_by_walmart_api/$',
        ItemsUpdateWithXmlFileByWalmartApiViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='items_update_with_xml_file_by_walmart_api'),
    url(r'^check_feed_status_by_walmart_api/$',
        CheckFeedStatusByWalmartApiViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='check_feed_status_by_walmart_api'),
    url(r'^validate_walmart_product_xml_file/$',
        ValidateWalmartProductXmlFileViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='validate_walmart_product_xml_file'),
])

urlpatterns += [
    url(r'^feed-redirect/(?P<feed_id>[A-Za-z0-9\-]+)', FeedIDRedirectView.as_view(), name='feed_redirect')
]

router = routers.SimpleRouter()
router.register(r'comparetwoimages', CompareTwoImageViewSet, 'comparetwoimages')
router.register(r'classifyimagesbysimilarity', ClassifyImagesBySimilarity, 'classifyimagesbysimilarity')
router.register(r'findsimilarityinimagelist', FindSimilarityInImageList, 'findsimilarityinimagelist')
router.register(r'walmartaccounts', WalmartAccountViewSet, 'walmartaccounts')
router.register(r'classifytextimagesbynutritioninfo', ClassifyTextImagesByNutritionInfoViewSet, 'classifytextimagesbynutritioninfo')
router.register(r'invokewalmartapi', InvokeWalmartApiViewSet, 'invokewalmartapi')
#router.register(r'items_update_with_xml_file_by_walmart_api',
#                ItemsUpdateWithXmlFileByWalmartApiViewSet,
#                'items_update_with_xml_file_by_walmart_api')
router.register(r'items_update_with_xml_text_by_walmart_api', ItemsUpdateWithXmlTextByWalmartApiViewSet, 'items_update_with_xml_text_by_walmart_api')
#router.register(r'check_feed_status_by_walmart_api',
#                CheckFeedStatusByWalmartApiViewSet,
#                'check_feed_status_by_walmart_api')
router.register(r'validate_walmart_product_xml_text', ValidateWalmartProductXmlTextViewSet, 'validate_walmart_product_xml_text')
router.register(r'detect_duplicate_content', DetectDuplicateContentBySeleniumViewset, 'detect_duplicate_content')
router.register(r'detect_duplicate_content_by_mechanize', DetectDuplicateContentByMechanizeViewset, 'detect_duplicate_content_by_mechanize')
router.register(r'detect_duplicate_content_from_csv_file_by_mechanize', DetectDuplicateContentFromCsvFilesByMechanizeViewset, 'detect_duplicate_content_from_csv_file_by_mechanize')
#router.register(r'validate_walmart_product_xml_file',
#                ValidateWalmartProductXmlFileViewSet,
#                'validate_walmart_product_xml_file')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns += [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

