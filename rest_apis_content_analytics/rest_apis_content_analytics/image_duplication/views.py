import os
import re
import cv2
import urllib
import cStringIO
import copy
import sys
import traceback

from PIL import Image
import numpy as np
from StringIO import StringIO

from walmart_developer_accounts.models import Account
from rest_framework import viewsets
from rest_apis_content_analytics.image_duplication.serializers import ImageUrlSerializer
from rest_apis_content_analytics.image_duplication.compare_images import url_to_image, compare_two_images_a, compare_two_images_b, compare_two_images_c
from rest_framework.response import Response


class CompareTwoImageViewSet(viewsets.ViewSet):
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

        if serializer.is_valid():
            try:
                urls = serializer.data["urls"]

                if not urls:
                    urls = request.DATA["urls"].split(" ")

                images_a  = []
                images_b = []
                images_c = []

                for url in urls:
                    path, ext = os.path.splitext(url)
                    path += ".jpg"

                    is_local = os.path.isfile(url)

                    if bool(re.findall("^[a-zA-Z]+://", url)):
                        resp = urllib.urlopen(url).read()
                        image = np.asarray(bytearray(resp), dtype="uint8")
                        images_a.append(cv2.imdecode(image, cv2.IMREAD_COLOR))
                        images_b.append(Image.open(cStringIO.StringIO(resp)))
                        images_c.append(Image.open(cStringIO.StringIO(resp)))

                    if ext not in (".jpg", ".jpeg", ".png"):
                        if is_local:
                            Image.open(path).convert('RGB').save(path)
                            image = cv2.imread(path)
                        else:
                            im = Image.open(StringIO(urllib.urlopen(url).read()))
                            file_mem = StringIO()
                            im.convert('RGB').save(file_mem, format="PNG")
                            file_mem.seek(0)
                            img_array = np.asarray(bytearray(file_mem.read()), dtype=np.uint8)
                            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                            file_mem.close()

                        images_a.append(image)

                similarity_rate = float(compare_two_images_b(images_b[0], images_b[1])) * float(compare_two_images_c(images_c[0], images_c[1]))

                if similarity_rate >= 0.5:
                    return Response({'Are two images similar?': "Yes"})
                else:
                    return Response({'Are two images similar?': "No"})
            except:
                var = traceback.format_exc()

        return Response({'data': var})

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        return Response({'data': 'OK'})

    def destroy(self, request, pk=None):
        return Response({'data': 'OK'})


class ClassifyImagesBySimilarity(viewsets.ViewSet):
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

        if serializer.is_valid():
            try:
                urls = serializer.data["urls"]

                if not urls:
                    urls = request.DATA["urls"].split(" ")

                images = []

                for url in urls:
                    if bool(re.findall("^[a-zA-Z]+://", url)):
                        resp = urllib.urlopen(url).read()
                        images.append(Image.open(cStringIO.StringIO(resp)))

                images = dict(zip(urls, images))

                rest_images = copy.copy(images)
                results = []

                for url1 in images:
                    if not rest_images:
                        break

                    if url1 not in rest_images:
                        continue

                    del rest_images[url1]
                    group_image_indexes = [url1]

                    processed_images = []

                    for url2 in rest_images:

                        similarity_rate = float(compare_two_images_c(images[url1], rest_images[url2])) * float(compare_two_images_b(images[url1], rest_images[url2]))

                        if similarity_rate >= 0.5:
                            processed_images.append(url2)
                            group_image_indexes.append(url2)

                    for url in processed_images:
                        del rest_images[url]

                    results.append(group_image_indexes)

                return Response(results)
            except:
                pass

        return Response({'data': 'NO OK'})

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        return Response({'data': 'OK'})

    def destroy(self, request, pk=None):
        return Response({'data': 'OK'})


class FindSimilarityInImageList(viewsets.ViewSet):
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

        if serializer.is_valid():
            try:
                urls = serializer.data["urls"]

                images = []

                for url in urls:
                    if bool(re.findall("^[a-zA-Z]+://", url)):
                        resp = urllib.urlopen(url).read()
                        images.append(Image.open(cStringIO.StringIO(resp)))

                images = dict(zip(urls, images))

                rest_images = copy.copy(images)
                results = {}

                url1 = urls[0]

                del rest_images[url1]
                group_image_indexes = []

                processed_images = []

                for url2 in rest_images:

                    similarity_rate = float(compare_two_images_c(images[url1], rest_images[url2])) * float(compare_two_images_b(images[url1], rest_images[url2]))

                    if similarity_rate >= 0.5:
                        processed_images.append(url2)
                        group_image_indexes.append(url2)

                if group_image_indexes:
                    results["similar_images"] = group_image_indexes
                    results["result"] = "Yes"
                else:
                    results["similar_images"] = None
                    results["result"] = "No"

                return Response(results)
            except:
                pass

        return Response({'data': 'NO OK'})

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        return Response({'data': 'OK'})

    def destroy(self, request, pk=None):
        return Response({'data': 'OK'})


