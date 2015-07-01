#!/usr/bin/python
# This is a standalone program. Pass an image name as a first parameter of the program.

import sys
from math import sin, cos, sqrt, pi
import cv2.cv as cv
import urllib2
from numpy import array as nparray, median as npmedian
import csv

# toggle between CV_HOUGH_STANDARD and CV_HOUGH_PROBILISTIC
USE_STANDARD = False

def is_text_image(filename, is_url=False):

    if is_url:
        filedata = urllib2.urlopen(filename).read()
        imagefiledata = cv.CreateMatHeader(1, len(filedata), cv.CV_8UC1)
        cv.SetData(imagefiledata, filedata, len(filedata))
        src = cv.DecodeImageM(imagefiledata, cv.CV_LOAD_IMAGE_GRAYSCALE)
    else:
        src = cv.LoadImage(filename, cv.CV_LOAD_IMAGE_GRAYSCALE)
    dst = cv.CreateImage(cv.GetSize(src), 8, 1)
    color_dst = cv.CreateImage(cv.GetSize(src), 8, 3)
    storage = cv.CreateMemStorage(0)

    cv.Canny(src, dst, 50, 200, 3)
    cv.CvtColor(dst, color_dst, cv.CV_GRAY2BGR)

    slopes = []
    # difference between xs or ys - variant of slope
    tilts = []
    # x coordinates of horizontal lines
    horizontals = []
    # y coordinates of vertical lines
    verticals = []

    if USE_STANDARD:
        coords = cv.HoughLines2(dst, storage, cv.CV_HOUGH_STANDARD, 1, pi / 180, 50, 50, 10)
        lines = []
        for coord in coords:
            (rho, theta) = coord
            a = cos(theta)
            b = sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (cv.Round(x0 + 1000*(-b)), cv.Round(y0 + 1000*(a)))
            pt2 = (cv.Round(x0 - 1000*(-b)), cv.Round(y0 - 1000*(a)))
            lines += [(pt1, pt2)]

    else:
        lines = cv.HoughLines2(dst, storage, cv.CV_HOUGH_PROBABILISTIC, 1, pi / 180, 50, 50, 10)

    # eliminate duplicates - there are many especially with the standard version
    # first round the coordinates to integers divisible with 5 (to eliminate different but really close ones)
    # TODO
    # lines = list(set(map(lambda l: tuple([int(p) - int(p)%5 for p in l]), lines)))

    nr_straight_lines = 0
    for line in lines:
        (pt1, pt2) = line

        # compute slope, rotate the line so that the slope is smallest
        # (slope is either delta x/ delta y or the reverse)
        # add smoothing term in denominator in case of 0
        slope = min(abs(pt1[1] - pt2[1]), (abs(pt1[0] - pt2[0]))) / (max(abs(pt1[1] - pt2[1]), (abs(pt1[0] - pt2[0]))) + 0.01)
        # if slope < 0.1:
        # if slope < 5:
        if slope < 0.05:
            if abs(pt1[0] - pt2[0]) < abs(pt1[1] - pt2[1]):
                # means it's a horizontal line
                horizontals.append(pt1[0])
            else:
                verticals.append(pt1[1])
        if slope < 0.05:
        # if slope < 5:
        # if slope < 0.1:
            nr_straight_lines += 1
        slopes.append(slope)
        tilts.append(min(abs(pt1[1] - pt2[1]), (abs(pt1[0] - pt2[0]))))
        # print slope
    average_slope = sum(slopes)/float(len(slopes))
    median_slope = npmedian(nparray(slopes))
    average_tilt = sum(tilts)/float(len(tilts))
    median_tilt = npmedian(nparray(tilts))
    differences = []
    horizontals = sorted(horizontals)
    verticals = sorted(verticals)
    print "x_differences:"
    for (i, x) in enumerate(horizontals):
        if i > 0:
            # print abs(horizontals[i] - horizontals[i-1])
            differences.append(abs(horizontals[i] - horizontals[i-1]))
    print "y_differences:"
    for (i, y) in enumerate(verticals):
        if i > 0:
            # print abs(verticals[i] - verticals[i-1])
            differences.append(abs(verticals[i] - verticals[i-1]))

    print "average_slope:", average_slope
    print "median_slope:", median_slope
    print "average_tilt:", average_tilt
    print "median_tilt:", median_tilt
    median_differences = npmedian(nparray(differences))
    print "median_differences:", median_differences
    average_differences = sum(differences)/float(len(differences))
    print "average_differences:", average_differences
    print "nr_lines:", nr_straight_lines

    # print "sorted xs:", sorted(lines)

    return (average_slope, median_slope, average_tilt, median_tilt, median_differences, average_differences, nr_straight_lines)

def plot_examples(examples=None):
    '''Plots in 2D space the points in the 4 lists given as input
    :param examples: list of nutrition images,
    dictionaries with keys:
    'name' - image title
    'label' - one of 'TP', 'TN', 'FP', 'FN' (true/false positives/negatives)
    'coords' - tuple of coordinates
    '''

    def get_examples_from_images():
        images = [
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/notnutrition2.jpg', 'TN'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/notnutrition3_falsepos.jpg', 'FP'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/notnutrition4_falsepos.jpg', 'FP'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/notnutrition5_falsepos.jpg', 'FP'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/notnutrition6_falsepos.jpg', 'FP'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/notnutrition.jpg', 'TN'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/nutrition_image10_falseneg.jpg', 'FN'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/nutrition_image11_falseneg.jpg', 'FN'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/nutrition_image2.png', 'TP'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/nutrition_image3.jpg', 'TP'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/nutrition_image4.jpg', 'TP'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/nutrition_image5.jpg', 'TP'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/nutrition_image6.jpg', 'TP'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/nutrition_image7.jpg', 'TP'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/nutrition_image8.jpg', 'TP'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/nutrition_image9.jpg', 'TP'),
                        ('/home/ana/code/tmtext/special_crawler/nutrition_info_images/examples/nutrition_image.jpg', 'TP')
                    ]
        examples = []
        for image, label in images:
            average_slope, median_slope, average_tilt, median_tilt, median_differences, average_differences, nr_lines = is_text_image(image)
            example = {'name': image, 'label': label, 'coords': (average_slope, average_differences, nr_lines)}
            examples.append(example)
        return examples

    def get_examples_from_files():
        examples_file = '/home/ana/code/tmtext/special_crawler/nutrition_info_images/nutrition_images/nutrition_images_actual.csv'
        examples = []
        with open(examples_file) as f:
            # skip headers line
            f.readline()
            ireader = csv.reader(f)
            for row in ireader:
                label_bool = row[1]
                image = row[2]
                label = 'TP' if label_bool == 'True' else 'TN'
                average_slope, median_slope, average_tilt, median_tilt, median_differences, average_differences, nr_lines = is_text_image(image, is_url=True)
                example = {'name': image, 'label': label, 'coords': (average_slope, average_differences, nr_lines)}
                examples.append(example)
        return examples

    # hardcode list of examples
    if not examples:
        examples = get_examples_from_files()
        examples += get_examples_from_images()

    labels_to_colors = {
    'TP' : 'red',
    'FN' : 'orange',
    'TN' : 'blue',
    'FP' : 'green',
    }

    points = []

    import matplotlib.pyplot as plt

    X = []
    Y = []
    colors = []
    areas = []

    print examples
    for example in examples:
        x, y = example['coords'][:2]

        X.append(x)
        Y.append(y)
        color = labels_to_colors[example['label']]
        colors.append(color)
        areas.append(example['coords'][2])

    plt.scatter(X, Y, s=areas, c=colors)
    plt.savefig('/tmp/nutrition.png')
    plt.show()

if __name__ == "__main__":
    # if len(sys.argv) > 1:
    #     filename = sys.argv[1]
    #     src = cv.LoadImage(filename, cv.CV_LOAD_IMAGE_GRAYSCALE)
    # else:
    #     import sys
    #     sys.exit(0)
    
    # is_text_image(filename)

    plot_examples()
