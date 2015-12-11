from rest_framework import serializers


class WalmartApiRequestJsonSerializer(serializers.Serializer):
    request_json = serializers.CharField()



