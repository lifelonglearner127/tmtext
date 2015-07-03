from sklearn import svm
import csv
import numpy as np
import matplotlib.pyplot as plt
import sys
from math import sin, cos, sqrt, pi
import cv2.cv as cv
import urllib2
from numpy import array as nparray, median as npmedian
from sklearn.externals import joblib

# toggle between CV_HOUGH_STANDARD and CV_HOUGH_PROBILISTIC
USE_STANDARD = False

def extract_features(filename, is_url=False):
    '''Extracts features to be used in text image classifier.
    :param filename: input image
    :param is_url: is input image a url or a file path on disk
    :return: tuple of features:
    (average_slope, median_slope, average_tilt, median_tilt, median_differences, average_differences, nr_straight_lines)
    Most relevant ones are average_slope, average_differences and nr_straight_lines.
    '''

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
            average_slope, median_slope, average_tilt, median_tilt, median_differences, average_differences, nr_lines = extract_features(image)
            example = {'name': image, 'label': label, 'coords': (average_slope, average_differences, nr_lines)}
            examples.append(example)
        return examples

    def get_examples_from_files():
        examples_file = '/home/ana/code/tmtext/special_crawler/nutrition_info_images/nutrition_images_training.csv'
        examples = []
        with open(examples_file) as f:
            # skip headers line
            f.readline()
            ireader = csv.reader(f)
            for row in ireader:
                label_raw = row[1]
                image = row[0]
                label = 'TP' if label_raw == '1' else 'TN'
                average_slope, median_slope, average_tilt, median_tilt, median_differences, average_differences, nr_lines = extract_features(image, is_url=True)
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

def extract_features_main():
    # if len(sys.argv) > 1:
    #     filename = sys.argv[1]
    #     src = cv.LoadImage(filename, cv.CV_LOAD_IMAGE_GRAYSCALE)
    # else:
    #     import sys
    #     sys.exit(0)
    
    # extract_features(filename)

    plot_examples()


def read_images_set(path="nutrition_images_training.csv"):
    '''Reads the training set from a file, returns examples and their labels (2 lists)
    examples will have the following format:
    tuple of:
    - list of strings representing the image names
    - list of tuples representing the features:
    (average slope, average distance between lines parallel to axes, nr of lines parallel to axes)
    - list of labels: labels will be 1 (text) or 0 (not text)
    '''

    examples = []
    labels = []
    names = []
    with open(path) as f:
        reader = csv.reader(f, delimiter=',')
        # omit headers
        f.readline()
        for row in reader:
            image = row[0]
            names.append(image)

            average_slope, median_slope, average_tilt, median_tilt, median_differences, average_differences, nr_straight_lines = \
            extract_features(image, is_url=True)
            examples.append((average_slope, average_differences, nr_straight_lines))
            labels.append(int(row[1]))
    return (names, examples, labels)


def train(training_set, serialize_file=None):
    '''Trains text image classifier.
    :param training_set: training set of images, tuple of lists:
    images, features and labels, as returned by read_images_set.
    :param serialize_file: the path of the file to serialize the classifier to, optional
    :return: tuple of images list and classifier object
    '''
    imgs, X, y = training_set
    clf = svm.SVC(kernel='linear')
    clf.fit(X, y)

    if serialize_file:
        joblib.dump(clf, serialize_file)

    return imgs, clf    

def predict(test_set, clf=None, from_serialized_file=None):
    '''Predicts labels (text image/not) for an input test set.
    :param test_set: test set of images, tuple of lists:
    images, features and labels, as returned by read_images_set.
    :param clf: the classifier object, if passed directly
    :param from_serialized_file: the path of the file containing the serialized classfier, if any
    :return: list of tuples (image_url, label)
    '''
    if from_serialized_file:
        clf = joblib.load(from_serialized_file)

    imgs, examples, labels = test_set
    predicted_examples = []
    for idx, example in enumerate(examples):
        predicted = clf.predict(example)
        # print imgs[idx], labels[idx], predicted
        predicted_examples.append((imgs[idx], predicted[0]))
    return predicted_examples

def predict_one(image, clf=None, from_serialized_file="serialized_classifier/nutrition_image_classifier.pkl", is_url=False):
    '''Predicts label (text image/not) for an input image.
    :param image: image url or path
    :param clf: the classifier object, if passed directly
    :param from_serialized_file: the path of the file containing the serialized classfier, if any
    :param is_url: image is a url, not a file path on disk
    :return: predicted label
    '''
    if from_serialized_file:
        clf = joblib.load(from_serialized_file)
    average_slope, median_slope, average_tilt, median_tilt, median_differences, average_differences, nr_straight_lines = \
    extract_features(image, is_url=is_url)
    example = (average_slope, average_differences, nr_straight_lines)

    predicted = clf.predict(example)
    return predicted

def classifier_main():
    training_set = read_images_set()
    trained, clf = train(training_set, serialize_file="serialized_classifier/nutrition_image_classifier.pkl")
    test_set = read_images_set("nutrition_images_test.csv")
    imgs, examples, labels = test_set
    nr_predicted = 0
    predicted = predict(test_set, clf, from_serialized_file="serialized_classifier/nutrition_image_classifier.pkl")
    accurate = 0
    with open('nutrition_images_predicted.csv', 'w+') as out:
        for example in predicted:
            out.write(",".join([example[0], str(example[1])]) + "\n")
            if example[1]!=labels[nr_predicted]:
                print "Inaccurate:", example[0]
            else:
                accurate+=1

            nr_predicted += 1

    accuracy = float(accurate)/len(predicted)*100

    print "Accuracy: {0:.2f}%".format(accuracy)

    # Plot the decision boundary
    w = clf.coef_[0]
    print "coefs", clf.coef_
    a = -w[0] / w[1]
    xx = np.linspace(-5, 5)
    yy = a * xx - (clf.intercept_[0]) / w[1]

    plt.plot(xx, yy, 'k-')
    # plt.ylim([0,5])

    plt.scatter([e[0] for e in examples], [e[1] for e in examples], c=['red' if l==1 else 'blue' for l in labels])

    plt.show()

def classifier_predict_one(image_url):
    predicted = predict_one(image_url, None, from_serialized_file="serialized_classifier/nutrition_image_classifier.pkl", is_url=True)
    return predicted[0]

if __name__ == '__main__':
    # classifier_main()
    print classifier_predict_one(sys.argv[1])
