#!/usr/bin/python

import numpy as np
import cv2

import sys

def segment(im):

	gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
	#blur = cv2.GaussianBlur(gray,(5,5),0)

	#cv2.threshold(blur,220,255,cv2.THRESH_BINARY_INV, thresh)
	thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,1,11,2)

	#cv2.imshow('thresh', thresh)

	#################      Now finding Contours         ###################
	kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))

	#TODO: try to vary iterations
	thresh = cv2.erode(thresh,kernel,iterations = 1)

	#cv2.imwrite('thresh.jpg', thresh)
	contours,hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

	#i=0
	rois = []
	im2 = np.copy(im)
	for cnt in contours:
	  
	    #print "area above 50"
	    [x,y,w,h] = cv2.boundingRect(cnt)

	    # reject subimages with height or width below 5 pixels
	    if (h<5) or (w<5):
	    	continue

	    #print "height above 10"
	    
	    cv2.rectangle(im2,(x,y),(x+w,y+h),(0,0,255),2)
    
	    roi = gray[y:y+h,x:x+w]

	    # if y>5 and x>5:
	    # 	roi = gray[y-5:y+h+5,x-5:x+w+5]

	    # store roi and x coordinate to sort by
	    rois.append((roi, x))
	    # cv2.imwrite('letter'+str(i)+'.jpg',roi)
	    # i+=1

	    # roismall = cv2.resize(roi,(10,10))

	#cv2.imwrite('segmented.jpg', im2)

	# sort rois by x coordinate
	ret = map(lambda x: x[0],sorted(rois, key=lambda x: x[1]))

	return ret

if __name__=='__main__':

	import random
	import re
    
	im = cv2.imread(sys.argv[1])
	cv2.imwrite('orig.jpg',im)

	subimages = segment(im)
	#print len(subimages)

	# extract image name
	m = re.match(".*/(.*).jpg",sys.argv[1])
	if not m:
		m = re.match("(.*).jpg", sys.argv[1])

	captcha_name = m.group(1)

	t=0
	for im in subimages:
		cv2.imshow('norm',im)

		# make sure the segmented directory exists for this to work
		if t>=len(captcha_name):
			print "INDEX ERROR", t, captcha_name
		else:
			letter_name = "segmented/" + captcha_name[t]+'_'+ str(t) + "_" + str(random.randint(0,1000)) + '.jpg'
		#print 'segmented', letter_name
		# name will be corresponding letter in image name - assume the name is the solved captcha
		cv2.imwrite(letter_name,im)
		t+=1

		#cv2.waitKey(0)
       