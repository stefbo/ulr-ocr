# Demo how to recognize ultra-low resolution (ULR) text with OpenCV and tesseract.
# Copyright 2018, Stefan Bolus
#
import cv2
import numpy as np
import pytesseract
import sys

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

if len(sys.argv) != 2:
	print("Usage: {} <file>".format(sys.argv[0]))
	exit(1)

inFile = sys.argv[1]

img = cv2.imread(inFile, cv2.IMREAD_GRAYSCALE)
if img is None:
	print("Reading image from file {} failed.".format(inFile))
	exit(1)

# Extract the center part from the image. Quality of the OCR
# for the header line and result unit is poor. The parse the
# unit using template matching below.

# Re-scale the image before passing it to tesseract and do
# automatic thresholding using Otsu's algorithm.
scale_factor = 6
scaled_img = cv2.resize(img[10:50, 0:SCREEN_WIDTH], (0,0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
assert(scaled_img is not None)

thres,thres_img = cv2.threshold(scaled_img, 0, 255, cv2.THRESH_BINARY|cv2.THRESH_OTSU)
assert(thres_img is not None)

text = pytesseract.image_to_string(thres_img, config='--user-words words.txt config.txt')
print('Result text: "{}"'.format(text))

# Check which unit the result has. We assume the result is located
# in the bottom row.
unit_templates = [
	('templates/units/ug_L.png', 'ug/L'),
	('templates/units/per-mille.png', 'o/oo')
]
for (file,unit_id) in unit_templates:
	unit_img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
	assert(unit_img is not None)
	diff = cv2.matchTemplate(img[48:SCREEN_HEIGHT, SCREEN_WIDTH//2:SCREEN_WIDTH],unit_img,cv2.TM_SQDIFF)
	min_diff,_,min_loc,_ = cv2.minMaxLoc(diff)
	if min_diff <= 2:
		print("Unit of result is {}.".format(unit_id))
		break
