from rest_framework import serializers


class StringListField(serializers.ListField):
    child = serializers.CharField()


class WalmartApiItemsWithXmlFileRequestSerializer(serializers.Serializer):
    server_name = serializers.CharField(initial="rest_api_web_interface")
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
    xml_file_to_validate = serializers.FileField(style={'template': 'multiple_file_field.html'})
    """
    xml_file_to_validate_2 = serializers.FileField()
    xml_file_to_validate_3 = serializers.FileField()
    """


class WalmartDetectDuplicateContentRequestSerializer(serializers.Serializer):
    product_url_1 = serializers.CharField()
    product_url_2 = serializers.CharField()
    product_url_3 = serializers.CharField()
    product_url_4 = serializers.CharField()
    product_url_5 = serializers.CharField()

    detect_duplication_in_sellers_only = serializers.BooleanField(initial=False, style={'template': 'checkbox_next_to_submit_button.html'})


class WalmartDetectDuplicateContentFromCsvFileRequestSerializer(serializers.Serializer):
    csv_file_to_check = serializers.FileField()


class CheckItemStatusByProductIDSerializer(serializers.Serializer):
    numbers = serializers.CharField(
        max_length=2000, style={'base_template': 'textarea.html'})