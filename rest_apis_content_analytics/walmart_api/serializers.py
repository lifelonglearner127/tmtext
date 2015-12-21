from rest_framework import serializers


class WalmartApiRequestJsonSerializer(serializers.Serializer):
    request_url = serializers.ChoiceField(
        choices=["https://marketplace.walmartapis.com/v2/feeds?feedType=item"])
    request_method = serializers.ChoiceField(
        choices=["POST"])
#    xml_file_content = serializers.CharField(style={'base_template': 'textarea.html'})
    xml_file_to_upload = serializers.FileField()
