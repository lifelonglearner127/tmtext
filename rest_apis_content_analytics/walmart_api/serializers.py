from rest_framework import serializers


class WalmartApiItemsWithXmlFileRequestSerializer(serializers.Serializer):
    request_url = serializers.ChoiceField(
        choices=["https://marketplace.walmartapis.com/v2/feeds?feedType=item"])
    request_method = serializers.ChoiceField(
        choices=["POST"])
    xml_file_to_upload = serializers.FileField(style={'template': 'multiple_file_field.html'})
    submit_as_one_xml_file = serializers.BooleanField(initial=True,
                                                      style={'template': 'checkbox_next_to_submit_button.html'})

    """ There can be also the code below (our backend supports this):
    request_url_2 = serializers.ChoiceField(
        choices=["https://marketplace.walmartapis.com/v2/feeds?feedType=item"])
    request_method_2 = serializers.ChoiceField(
        choices=["POST"])
    xml_file_to_upload_2 = serializers.FileField(style={'template': 'multiple_file_field.html'})

    request_url_3 = serializers.ChoiceField(
        choices=["https://marketplace.walmartapis.com/v2/feeds?feedType=item"])
    request_method_3 = serializers.ChoiceField(
        choices=["POST"])
    xml_file_to_upload_3 = serializers.FileField(style={'template': 'multiple_file_field.html'})
    """


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

    request_url_2 = serializers.ChoiceField(
        choices=["https://marketplace.walmartapis.com/v2/feeds/{feedId}?includeDetails=true"])
    feed_id_2 = serializers.CharField()

    request_url_3 = serializers.ChoiceField(
        choices=["https://marketplace.walmartapis.com/v2/feeds/{feedId}?includeDetails=true"])
    feed_id_3 = serializers.CharField()


class WalmartApiValidateXmlTextRequestSerializer(serializers.Serializer):
    xml_content_to_validate = serializers.CharField(style={'base_template': 'textarea.html'})


class WalmartApiValidateXmlFileRequestSerializer(serializers.Serializer):
    xml_file_to_validate = serializers.FileField()
    xml_file_to_validate_2 = serializers.FileField()
    xml_file_to_validate_3 = serializers.FileField()