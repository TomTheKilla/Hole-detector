import sys
import os
import cv2 as cv
import numpy as np
import json

def showPicture(img):
    tmp = cv.resize(img, (4608//8, 3456//8))
    cv.imshow('test', tmp)

# read input arguments (directories
# 1. imgs
# 2. input json
# 3. output json

img_dir = sys.argv[1]
input_dir = sys.argv[2]
output_dir = sys.argv[3]

# print(img_dir)
# print(input_dir)
# print(output_dir)

# read input json
with open(input_dir) as file:
    input = json.load(file)

# read images
img_list = os.listdir(img_dir)
images = []
for name in img_list:
    img = cv.imread(f'{img_dir}/{name}')
    images.append(img)
# run detection algorithm
img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
blue_min = np.array([106, 84, 0], np.uint8)
blue_max = np.array([122, 255, 255], np.uint8)
blue = cv.inRange(img, blue_min, blue_max)

yellow_min = np.array([20, 69, 167], np.uint8)
yellow_max = np.array([63, 255, 255], np.uint8)
yellow = cv.inRange(img, yellow_min, yellow_max)

red_min = np.array([0, 47, 0], np.uint8)
red_max = np.array([13, 255, 255], np.uint8)
red = cv.inRange(img, red_min, red_max)

gray_min = np.array([45, 3, 0], np.uint8)
gray_max = np.array([105, 32, 141], np.uint8)
gray = cv.inRange(img, gray_min, gray_max)

white_min = np.array([34, 0, 175], np.uint8)
white_max = np.array([64, 255, 255], np.uint8)
white = cv.inRange(img, white_min, white_max)
# write output json
