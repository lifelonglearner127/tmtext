#!/usr/bin/python

import numpy as np
import cv2
from matplotlib import pyplot as plt

# from the internet import this https://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_ml/py_knn/py_knn_opencv/py_knn_opencv.html
import sys
import os
import re

#import deskew
import segment_image


class CaptchaBreaker:

	HEIGHT = 50
	WIDTH = 50

	ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	

	knn = None

	# train model at init step
	def __init__(self, train_data, output_train_data_file=None, from_dir=False):
		if from_dir:
			self.knn = self.train_from_dir(train_data, output_train_data_file)
		else:
			self.knn = self.train_from_file(train_data)

	def letter_to_number(self, letter):
		return self.ALPHABET.index(letter)

	def number_to_letter(self, number):
		return self.ALPHABET[number]

	# turn to gray, threshold, erode and trim to contour
	def clean_image(self, image, trim=False):

		gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
		thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,1,11,2)

		#thresh = deskew.deskew(thresh)
		kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
		eroded = cv2.erode(thresh,kernel,iterations = 1)
		contours,hierarchy = cv2.findContours(eroded,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

		# assume first contour is what we are looking for
		#TODO: do some selection, reject if it's to small and move on to the next or smth
		[x,y,w,h] = cv2.boundingRect(contours[0])

		#TODO: intai deskew, apoi conturul
		#thresh = deskew.deskew(thresh)

		#TODO: experiment. try threshod, or just gray, or include erode...?
		#roi = gray[y:y+h,x:x+w]
		roi = thresh[y:y+h,x:x+w]

		#roi = thresh[y-5:y+h+5,x-5:x+w+5]s
		#ret = cv2.resize(roi, (self.WIDTH, self.HEIGHT))
		if trim:
			ret = self.add_borders(roi)
		else:
			ret = self.add_borders(thresh)


		# if write:
		#import random
		#cv2.imwrite('resizedtrain' + str(random.randint(0,100)) + ".jpg", ret)

		return ret

	# add borders to the image up to a size
	def add_borders(self, image):
		height, width = image.shape
		width_pad = (self.WIDTH - width) / 2.0
		left_pad = int(width_pad)

		# make sure rounding didn't affect the desired final size of the picture (=self.HEIGHTxself.WIDTH)
		# if it was not an integer (so .5), add 1 to the opposite pad
		if (left_pad != width_pad):
			right_pad = left_pad+1
		else:
			right_pad = left_pad

		height_pad = (self.HEIGHT - height) / 2.0
		top_pad = int(height_pad)
		# if it was not an integer (so .5), add 1 to the opposite pad
		if (top_pad!=height_pad):
			bottom_pad = top_pad+1
		else:
			bottom_pad = top_pad

		# if all borders are positive
		if height_pad > 0 and width_pad > 0:
			dst = cv2.copyMakeBorder(image, top_pad, bottom_pad, left_pad, right_pad, cv2.BORDER_CONSTANT, value=0)
		# else just resize
		else:	
			dst = cv2.resize(image,(self.HEIGHT,self.WIDTH))
			sys.stderr.write("Could not add borders, shape " + str(height) + "," + str(width) + "\n")
		return dst

	def get_images_from_dir(self, directory):
		train_images_names = os.listdir(directory)
		train_images = []
		train_labels = []

		#print 'images_names', train_images_names

		#TODO: some filetype checking, nr of files in dir etc
		for filename in train_images_names:
			train_images.append(cv2.imread(directory+"/"+filename))
			# get base filename
			m = re.match("(.*)\..*", filename)
			#print 'image: ', filename
			if m:
				base = m.group(1)
				letter = base[0]
				# take first letter as label (pass through dict to get number coreespondent)
				train_labels.append(self.letter_to_number(letter))

		for i in range(len(train_images)):
			train_images[i] = self.clean_image(train_images[i])
			#cv2.imwrite('resized' + str(i) + '.jpg', train_images[i])

		train_arrays = []
		for image in train_images:
			train_arrays.append(np.array(image))

		train_data = np.array(train_arrays)

		images = train_data.reshape(-1,self.HEIGHT*self.WIDTH).astype(np.float32)
		labels = np.array(train_labels)

		return (images, labels)

	def get_images_from_captcha(self, filename):
		images = segment_image.segment(cv2.imread(filename))

		for i in range(len(images)):
			images[i] = cv2.adaptiveThreshold(images[i],255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,1,11,2)
			#images[i] = deskew.deskew(images[i])
			#images[i] = cv2.resize(images[i], (self.WIDTH, self.HEIGHT))
			images[i] = self.add_borders(images[i])
			#cv2.imwrite('resized' + str(i) + '.jpg', images[i])
			#print images[i].shape

		image_arrays = []
		for image in images:
			image_arrays.append(np.array(image))

		data = np.array(image_arrays)

		ret_images = data.reshape(-1,self.HEIGHT*self.WIDTH).astype(np.float32)
		#print ret_images.shape[0]
		#labels = np.array(train_labels)

		return ret_images

	# trains a knn on the images in train_dir and returns the trained model
	# if datafile parameter is passed, it also saves the model to a data file
	def train_from_dir(self, train_dir, datafile=None):
		(train, train_labels) = self.get_images_from_dir(train_dir)
		knn = cv2.KNearest()
		knn.train(train,train_labels)

		# # TRAIN SVM
		# svm_params = dict( kernel_type = cv2.SVM_LINEAR,
		#                     svm_type = cv2.SVM_C_SVC,
		#                     C=2.67, gamma=5.383 )
		# svm = cv2.SVM()
		# svm.train(train,train_labels, params=svm_params)

		# if there was a file specified, save model to that file
		if datafile:
			# if it's knn, the model can't be saved, we just save the entire training set (as numpy array)
		#	knn.save(datafile)
			np.save(datafile + "_images", train)
			np.save(datafile + "_labels", train_labels)

		return knn


	#TODO: doesn't work
	def train_from_file(self, train_data_file):
		train = np.load(train_data_file + "_images.npy")
		train_labels = np.load(train_data_file + "_labels.npy")
		knn = cv2.KNearest()
		knn.train(train,train_labels)

		return knn


	# test one captcha image
	def test_captcha(self, captchafile):
		test = self.get_images_from_captcha(captchafile)
		ret,result,neighbours,dist = self.knn.find_nearest(test,k=1)
		#test SVM
		# result = svm.predict_all(test)

		# convert labels back to letters
		result_labels = []
		for label in result:
			result_labels.append(self.number_to_letter(int(label[0])))
		#print 'result', "".join(result_labels)

		return "".join(result_labels)

	# test on a directory of letter images
	def test_dir(self, test_dir):
		(test, test_labels) = self.get_images_from_dir(test_dir)
		ret,result,neighbours,dist = self.knn.find_nearest(test,k=2)
		test_letter_labels = []
		for label in test_labels:
			test_letter_labels.append(number_to_letter(label))
		print test_letter_labels

		# convert labels back to letters
		result_labels = []
		for label in result:
			result_labels.append(number_to_letter(int(label[0])))
		print 'result:\n', result_labels

		l1 = np.array(result_labels)
		l2 = np.array(test_letter_labels)
		matches = l1==l2
		correct = np.count_nonzero(matches)
		accuracy = correct*100.0/result.size
		print accuracy


if __name__=="__main__":

	np.set_printoptions(threshold=np.nan)
	# get train and test arguments
	train_data = sys.argv[1]

	if os.path.isdir(train_data):
		CB = CaptchaBreaker(train_data, from_dir=True)
	else:
		CB = CaptchaBreaker(train_data, from_dir=False)

	# iterate through all left arguments (they are considered to be test data)
	arg = 2
	while arg < len(sys.argv):
		test_data = sys.argv[arg]

		# # decide if training should be done from directory or data file
		# if os.path.isdir(train_data):
		# 	model = train_from_dir(train_data, "train_all_data")
		# else:
		# 	# doesn't work
		# 	model = train_from_file(train_data)

		# decide if testing should be done on directory or captcha
		if os.path.isdir(test_data):
			CB.test_dir(test_data)
		else:
			result = CB.test_captcha(test_data)
			# test accuracy
			m = re.match('.*/(.*)\.jpg', test_data)

			if not m:
				m = re.match("(.*)\.jpg", test_data)
			captcha_name = m.group(1)
			print result
			if result == captcha_name:
				print 'OK!'
			else:
				print 'NOT OK; actual', captcha_name
			print
		arg += 1
