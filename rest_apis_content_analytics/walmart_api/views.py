from rest_framework import viewsets
from walmart_api.serializers import WalmartApiRequestJsonSerializer
from rest_framework.response import Response
import xmltodict
import os
import unirest
import urllib2

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
            request_data = request.DATA

            try:
                file_content = urllib2.urlopen(request_data['upload_file_url']).read()

                with open(os.path.dirname(os.path.realpath(__file__)) + "/" + request_data['upload_file_url'].split("/")[-1], "wb") as download_file:
                    download_file.write(file_content)

                file_to_upload = open(os.path.dirname(os.path.realpath(__file__)) + "/" + request_data['upload_file_url'].split("/")[-1], "rb")
            except:
                file_to_upload = open(os.path.dirname(os.path.realpath(__file__)) + "/supplierTest2.xml", "rb")

            response = unirest.post("https://marketplace.walmartapis.com/v2/feeds?feedType=item",
                headers={
                    "Accept": "application/json",
                    "WM_CONSUMER.ID": "a8bab1e0-c18c-4be7-b47a-0411153b7514",
                    "WM_SVC.NAME": request_data["name"],
                    "WM_QOS.CORRELATION_ID": request_data["correlation_id"],
                    "WM_SVC.VERSION": request_data["version"],
                    "WM_SVC.ENV": request_data["env"],
                    "WM_SEC.AUTH_SIGNATURE": request_data["signature"],
                    "WM_SEC.TIMESTAMP": int(request_data["timestamp"])
                },
                params={
                    "file": file_to_upload,
                }
            )

            if type(response.body) is dict:
                return Response(response.body)
            else:
                return Response(xmltodict(response.body))
        except Exception, e:
            print e
            return Response({'data': "Failed to invoke Walmart API - invalid request data"})

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        return Response({'data': 'OK'})

    def destroy(self, request, pk=None):
        return Response({'data': 'OK'})
