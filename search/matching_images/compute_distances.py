import distance
import re
from imagehash import phash
import cv2
import numpy as np
import sys
from matplotlib import pyplot as plt
import numpy

image_hashes_a = {}
image_hashes_w = {}
image_hists_a = {}
image_hists_w = {}

closest = []

def hash_hamming(h1, h2):
    '''Hamming distance between two hashes, convert to binary first'''
    # convert to binary and pad up to 256 bits
    b1 = bin(int(h1,16))[2:].zfill(256)
    b2 = bin(int(h2,16))[2:].zfill(256)
    return distance.hamming(b1,b2)

def hash_similarity(h1, h2):
    '''Similarity between 2 hashes (0-100), based on hamming distance
    Hashes are assumed to be 64-char long (256 bits)
    '''
    d = hash_hamming(h1, h2)
    s = 100 - (d/256.)*100
    return s

def compute_histogram(image_path, equalize=True):
    image = cv2.imread(image_path)
    if equalize:
        image = equalize_hist_color(image)
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8],[0, 256, 0, 256, 0, 256])
    return hist   

def histogram_similarity(image1, image2):
    hist1 = cv2.calcHist([image1], [0, 1, 2], None, [8, 8, 8],[0, 256, 0, 256, 0, 256])
    hist2 = cv2.calcHist([image2], [0, 1, 2], None, [8, 8, 8],[0, 256, 0, 256, 0, 256])
    score = cv2.compareHist(hist1.flatten(), hist2.flatten(), cv2.cv.CV_COMP_CORREL)
    return score

def histogram_to_string(image_path, equalize=True):
    '''Take an image path, compute its color histogram,
    flatten it to a list and then output it to a comma-separated string
    '''
    hist = compute_histogram(image_path, equalize)
    histf = cv2.normalize(hist).flatten()
    lhistf = list(histf)
    hists = ','.join(map(str,lhistf))
    return hists

def equalize_hist_color(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YCR_CB)
    channels = cv2.split(image)
    channels[0] = cv2.equalizeHist(channels[0])
    image = cv2.merge(channels)
    image = cv2.cvtColor(image, cv2.COLOR_YCR_CB2BGR)
    return image

def hist_similarity(hstr1, hstr2):
    '''Input strings representing flattened histograms
    Output similarity
    '''

    h1 = a = np.array(map(float,hstr1.split(','))).astype(np.float32)
    h2 = np.array(map(float,hstr2.split(','))).astype(np.float32)

    try:
        s = cv2.compareHist(h1,h2,cv2.cv.CV_COMP_CORREL)
    except Exception, e:
        sys.stderr.write(str(e) + "\n")
        return 0

    return s*100

def combined_similarity(hash1, hash2, hist1, hist2):
    s1 = hash_similarity(hash1, hash2)
    s2 = hist_similarity(hist1, hist2)
    return (s1+s2)/2.

def compute_similarities():
    with open("image_blockhashes_nows.txt") as fin:
        for line in fin:
            image, hashv = line.split()
            if image.startswith("nows"):
                nows, imagenr, site = image.split("_")
            else:
                imagenr, site = image.split("_")
            if site.startswith("amazon"):
                image_hashes_a[image] = hashv
            if site.startswith("walmart"):
                image_hashes_w[image] = hashv

    with open("image_histograms_nows.txt") as fin:
        for line in fin:
            image, hist = line.split()
            if image.startswith("nows"):
                nows, imagenr, site = image.split("_")
            else:
                imagenr, site = image.split("_")
            if site.startswith("amazon"):
                image_hists_a[image] = hist
            if site.startswith("walmart"):
                image_hists_w[image] = hist


    print "image,most_similar,match,most_similar_similarity,match_similarity,hash_similarity,hist_similarity"
    for image in image_hashes_w:
        most_similar = max(image_hashes_a.keys(), key=lambda i:\
            # hist_similarity(image_hashes_w[image], image_hashes_a[i]))
            combined_similarity(image_hashes_w[image], image_hashes_a[i], image_hists_w[image], image_hists_a[i]))
        image_match = re.sub("walmart", "amazon", image)
        
        try:
            closest.append((image, most_similar, \
                image_match,\
                combined_similarity(image_hashes_w[image], image_hashes_a[most_similar], image_hists_w[image], image_hists_a[most_similar]), \
                combined_similarity(image_hashes_w[image], image_hashes_a[image_match], image_hists_w[image], image_hists_a[most_similar]), \
                hash_similarity(image_hashes_w[image], image_hashes_a[image_match]), \
                hist_similarity(image_hists_w[image], image_hists_a[image_match])))

        except Exception, e:
            sys.stderr.write(str(e))

    for t in closest:
        print ",".join(map(str, t))


    # average_distance = sum([(t[3]+t[4])/2. for t in closest])/len(closest)
    # for how many the most similar was the actual match
    # nows images
    accuracy1 = len(filter(lambda t: t[0].split("_")[1]==t[1].split("_")[1], closest)) / float(len(closest))
    # normal images
    # accuracy1 = len(filter(lambda t: t[0].split("_")[0]==t[1].split("_")[0], closest)) / float(len(closest))
    print accuracy1
    # for how many the similarity with the actual match was > threshold
    accuracy2 = len(filter(lambda t: t[4] > 70, closest)) / float(len(closest))
    print accuracy2

def draw_histogram(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YCR_CB)
    channels = cv2.split(image)
    hist = compute_histogram(image_path, equalize=False)
    # plt.axis([0, 256, 0, 300])

    plt.hist(channels[0], bins=8)
    plt.savefig("/tmp/hist_" + image_path)
    plt.clf()
    plt.close()

    image = equalize_hist_color(image)
    channels = cv2.split(image)
    histeq = compute_histogram(image_path, equalize=False)
    plt.hist(channels[0], bins=8)
    plt.savefig("/tmp/hist_" + image_path[:-4] + "_eq.jpg")
    plt.clf()

    plt.close()

def _show(image):
    cv2.imshow("image", image)
    cv2.waitKey(0)

def images_similarity(image1_path, image2_path):
    '''Computes similarity between 2 images (opencv data structures)
    '''

    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)
    
    stdsize = (image1.shape[1], image1.shape[0])
    image1 = _normalize_image(image1)
    image2 = _normalize_image(image2, stdsize)

    # 5. compare histograms
    return histogram_similarity(image1, image2)

def _normalize_image(image, size=None):
    # image = cv2.imread(image_path)
    
    image = cv2.GaussianBlur(image,(3,3),0)
    
    # 1. threshold off-white pixels
    image = _threshold_light(image)

    # 2. remove white borders
    image = _remove_whitespace(image)


    # # 3. resize to same size
    # if size and size!= (image.shape[1], image.shape[0]):
    #     image = cv2.resize(image, size)    

    # 4. equalize color histogram
    image = equalize_hist_color(image)
    _show(image)
    return image

def _threshold_light(image):
    '''Threshold pixels close to white (very light greys),
    set them to white
    '''
    THRESH = 230
    # TODO try adaptive threshold?
    image[numpy.where(image > THRESH)] = 255
    return image

def _remove_whitespace(image):
    '''Crop image to remove whitespace around object
    '''

    imagec = numpy.copy(image)
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    _,thresh = cv2.threshold(gray,210,255,cv2.THRESH_BINARY_INV)
    contours,hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

    rois = []

    for cnt in contours:
        [x,y,w,h] = cv2.boundingRect(cnt)
        if (h<5) or (w<5):
            continue
        cv2.rectangle(imagec,(x,y),(x+w,y+h),(0,0,255),2)
        roi = image[y:y+h,x:x+w]

        # if y>5 and x>5:
        #     roi = gray[y-5:y+h+5,x-5:x+w+5]

        # store roi and x coordinate to sort by
        rois.append((roi, x))

    # sort rois by size
    ret = map(lambda x: x[0],sorted(rois, key=lambda x: -len(x[0])))
    return ret[0]

if __name__=="__main__":
    import sys
    # # compute_similarities()
    # for i in [36, 38, 40, 31, 48]:
    #     image1 = "nows_%s_amazon.jpg" % str(i)
    #     image2 = "nows_%s_walmart.jpg" % str(i)
    #     draw_histogram(image1)
    #     draw_histogram(image2)

    nr = sys.argv[1]
    print images_similarity("nows_%s_walmart.jpg" % nr, "nows_%s_amazon.jpg" % nr)
    # _normalize_image(cv2.imread("nows_40_amazon.jpg"))