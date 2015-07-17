from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from nutrition_info_images.serializers import ImageUrlSerializer

# Create your views here.


class ClassifyTextImagesByNutritionInfoViewSet(viewsets.ViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = ImageUrlSerializer

    def list(self, request):
        return Response({'data': 'OK'})

    def retrieve(self, request, pk=None):
        return Response({'data': 'OK'})

    def create(self, request):
        serializer = self.serializer_class(data=request.DATA)

        return Response({'data': 'NO OK'})

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        return Response({'data': 'OK'})

    def destroy(self, request, pk=None):
        return Response({'data': 'OK'})
