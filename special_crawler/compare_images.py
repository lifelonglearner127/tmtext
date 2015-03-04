import os
import sys
import cv2
from PIL import Image
import urllib
import re

images = []
hist = []
matches = 0
# images = [sys.argv[1], sys.argv[2]]

def get_calcHist(hsv):
    return cv2.calcHist( [hsv], [0, 1], None, [180, 256], [0, 180, 0, 256] )

def compare_images(img1, img2):
    """ Takes 2 images, as local paths or URLs.
        Returns a float [0, 1) representing the similarities of the images.
    """

    for image in  (img1, img2):
        path, ext = os.path.splitext(image)
        path += ".jpg"

        is_local = os.path.isfile(image)
        if bool(re.findall("^[a-zA-Z]+://", image)):
            path = "1000.jpg"
            urllib.urlretrieve(image, path)

        if ext not in (".jpg", ".jpeg", ".png"):
            Image.open(path).convert('RGB').save(path)

        img = cv2.imread(path)
        hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        hist.append(get_calcHist(hsv))
        if not is_local:
            os.remove(path)

    # Test all 4 comparison methods? iterate over methods in cycle
    #for i in range(0, 4):
    #    comp = cv2.compareHist(hist[0], hist[1], i)
    #    print comp

    correlation = cv2.compareHist(hist[0], hist[1], 0)
    return correlation


if __name__ == '__main__':
    i1 = 'http://www.viralnovelty.net/wp-content/uploads/2014/07/121.jpg'
    i2 = 'http://upload.wikimedia.org/wikipedia/commons/3/36/Hopetoun_falls.jpg'

    print compare_images(i1, i2)