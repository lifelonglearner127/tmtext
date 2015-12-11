from django.shortcuts import render
from rest_framework import viewsets
from walmart_api.serializers import WalmartApiRequestJsonSerializer
from rest_framework.response import Response
import requests
import xmltodict, json
import json
import os

# Create your views here.

class InvokeWalmartApiViewSet(viewsets.ViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = WalmartApiRequestJsonSerializer

    def list(self, request):
        return Response({'data': 'OK'})

    def retrieve(self, request, pk=None):
        return Response({'data': 'OK'})

    def create(self, request):
        try:
            request_json = request.DATA
            walmart_api_request_json = {}
            request_url = ""
            method = ""

            for key in request_json:
                if key == "request_url":
                    request_url = request_json[key]
                elif key == "method":
                    method = request_json[key]
                else:
                    walmart_api_request_json[key] = request_json[key]

            if method.lower() == "get":
                response = requests.get(request_url,  headers=walmart_api_request_json).text
                response = xmltodict.parse(response)
            elif method.lower() == "post":
                response = xmltodict.parse(requests.get(request_url, data=walmart_api_request_json).text)

            return Response(response)
        except:
            return Response({'data': "Failed to invoke Walmart API - invalid request data"})

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        return Response({'data': 'OK'})

    def destroy(self, request, pk=None):
        return Response({'data': 'OK'})
