from sklearn import svm
import csv

def read_training_set():
    '''Reads the training set from a file, returns examples and their labels (2 lists)
    examples will have the following format:
    list of tuples representing the features:
    (median slope, average slope)
        later also: (median difference between lines, number of lines)
    labels will be 1 (text) or 0 (not text)
    '''

    examples = []
    labels = []
    with open("nutrition_images/nutrition_images.csv.bak") as f:
        reader = csv.reader(f, delimiter=',')
        # omit headers
        f.readline()
        for row in reader:
            # examples.append((row[0], row[3]))
            examples.append((row[0], row[0]))
            labels.append(1 if row[1]=='True' else 0)
    return (examples, labels)


def train():
    X, y = read_training_set()
    clf = svm.SVC()
    clf.fit(X, y)
    return clf

if __name__ == '__main__':
    clf = train()
    print clf.predict((10,10))
    print clf.support_vectors_
