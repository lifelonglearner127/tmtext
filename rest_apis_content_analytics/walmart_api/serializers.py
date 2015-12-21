from rest_framework import serializers


class WalmartApiItemsRequestJsonSerializer(serializers.Serializer):
    request_url = serializers.ChoiceField(
        choices=["https://marketplace.walmartapis.com/v2/feeds?feedType=item"])
    request_method = serializers.ChoiceField(
        choices=["POST"])
    xml_file_to_upload = serializers.FileField()

class WalmartApiFeedRequestJsonSerializer(serializers.Serializer):
    request_url = serializers.ChoiceField(
        choices=["https://marketplace.walmartapis.com/v2/feeds/{feedId}?includeDetails=true"])
    feed_id = serializers.CharField()