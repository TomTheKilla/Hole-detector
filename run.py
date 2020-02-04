import sys
import os
import cv2 as cv
import numpy as np
import json
import time
from enum import Enum

from my_lib import detectors


class Colours(Enum):
    red = 0
    blue = 1
    white = 2
    grey = 3
    yellow = 4


def showPicture(img, i):
    tmp = cv.resize(img, (4608 // 8, 3456 // 8))
    cv.imshow(f'test{i}', tmp)


# read input arguments (directories
# 1. imgs
# 2. input json
# 3. output json

img_dir = sys.argv[1]
input_dir = sys.argv[2]
output_dir = sys.argv[3]

# read input json
with open(input_dir) as file:
    input_block_count = json.load(file)

# read images
img_list = os.listdir(img_dir)
images = []
for name in img_list:
    img = cv.imread(f'{img_dir}/{name}')
    images.append(img)

# run detection algorithm
frame_time = dict()  # Time measurement
medianFrame = cv.imread('my_lib/background.jpg')
for i, img in enumerate(images[:1]):  # TODO: iterate over every photo
    time_start = time.time()  # Time measurement
    objects = detectors.ExtractObjectsFormFrame(img, medianFrame)
    time_extract = time.time()  # Time measurement

    circles_in_objects = []
    blocks_in_objects = []
    for obj in objects:
        circles, test = detectors.SimpleHoughCircles(obj)
        circle_count = len(circles[0, :])
        circles_in_objects.append(circle_count)

        detected_blocks = detectors.CountColouredBlocks(obj)
        blocks_in_objects.append(detected_blocks)

    time_describe = time.time()  # Time measurement

    # assign objects from input json to detected objects
    input_data = input_block_count.get('img_001')  # TODO: get data from json
    if len(input_data) == len(blocks_in_objects):
        gate_matrix = np.zeros((len(input_data), len(input_data)), bool)
        for input_n, input in enumerate(input_data):
            for detected_n, detected in enumerate(blocks_in_objects):
                # cv.imshow('test', objects[detected_n])
                # cv.waitKey(0)
                possible = False
                for colour in Colours:
                    current_colour = colour.name
                    if int(input.get(current_colour)) >= detected.get(current_colour):
                        possible = True
                    else:
                        possible = False
                        break

                gate_matrix[input_n, detected_n] = possible

    time_assign = time.time()
    frame_time[f'{i}'] = (time_extract - time_start,
                          time_describe - time_extract,
                          time_assign - time_describe)  # Time measurement

# write output json
with open(output_dir, 'w+') as file:
    output = json.dump(frame_time, file, indent=4)



