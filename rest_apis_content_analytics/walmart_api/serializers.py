from rest_framework import serializers


class WalmartApiItemsWithXmlFileRequestSerializer(serializers.Serializer):
    request_url = serializers.ChoiceField(
        choices=["https://marketplace.walmartapis.com/v2/feeds?feedType=item"])
    request_method = serializers.ChoiceField(
        choices=["POST"])
    xml_file_to_upload = serializers.FileField()


class WalmartApiItemsWithXmlTextRequestSerializer(serializers.Serializer):
    request_url = serializers.ChoiceField(
        choices=["https://marketplace.walmartapis.com/v2/feeds?feedType=item"])
    request_method = serializers.ChoiceField(
        choices=["POST"])
    xml_content_to_upload = serializers.CharField(style={'base_template': 'textarea.html'})


class WalmartApiFeedRequestSerializer(serializers.Serializer):
    request_url = serializers.ChoiceField(
        choices=["https://marketplace.walmartapis.com/v2/feeds/{feedId}?includeDetails=true"])
    feed_id = serializers.CharField()


class WalmartApiValidateXmlRequestSerializer(serializers.Serializer):
    xml_content_to_validate = serializers.CharField(style={'base_template': 'textarea.html'})
