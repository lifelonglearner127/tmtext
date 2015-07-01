from sklearn import svm
import csv
from detect_text_houghlines import is_text_image
import numpy as np
import matplotlib.pyplot as plt

def read_training_set(path="nutrition_images_training.csv"):
    '''Reads the training set from a file, returns examples and their labels (2 lists)
    examples will have the following format:
    list of strings representing the image names
    list of tuples representing the features:
    (average slope, average distance between lines parallel to axes, nr of lines parallel to axes)
    labels will be 1 (text) or 0 (not text)
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
            is_text_image(image, is_url=True)
            examples.append((average_slope, average_differences, nr_straight_lines))
            labels.append(int(row[1]))
    return (names, examples, labels)


def train():
    imgs, X, y = read_training_set()
    clf = svm.SVC(kernel='linear')
    clf.fit(X, y)
    return imgs, clf

if __name__ == '__main__':
    trained, clf = train()
    imgs, examples, labels = read_training_set("nutrition_images_test.csv")
    nr_predicted = 0
    for idx, example in enumerate(examples):
        if imgs[idx] not in trained:
            predicted = clf.predict(example)
            print imgs[idx], labels[idx], predicted
            with open('nutrition_images_predicted.csv', 'a+') as out:
                out.write(",".join([imgs[idx], str(predicted[0])]) + "\n")
            nr_predicted += 1

    print "Predicted examples:", nr_predicted

    # Plot the decision boundary
    w = clf.coef_[0]
    print "coefs", clf.coef_
    a = -w[0] / w[1]
    xx = np.linspace(-5, 5)
    yy = a * xx - (clf.intercept_[0]) / w[1]

    plt.plot(xx, yy, 'k-')
    # plt.ylim([0,5])

    plt.scatter([e[0] for e in examples], [e[1] for e in examples], c=['red' if l==1 else 'blue' for l in labels])

    # plt.show()
