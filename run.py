import sys
import os
import cv2 as cv
import numpy as np
import json
import time

from my_lib import detectors
from my_lib import sorters
from my_lib.types import GroupOfBlocks





def showPicture(img, i):
    tmp = cv.resize(img, (4608 // 8, 3456 // 8))
    cv.imshow(f'test{i}', tmp)


# read input arguments (directories
# 1. imgs
# 2. input json
# 3. output json
            # TODO: handle / and \ in paths
img_dir = sys.argv[1]
input_dir = sys.argv[2]
output_dir = sys.argv[3]

# read input json
with open(input_dir) as file:
    input_block_count = json.load(file)

# # read images
# img_list = os.listdir(img_dir)
# images = []
# for name in img_list:
#     img = cv.imread(f'{img_dir}/{name}')
#     images.append(img)

# Create output dictionary
output_dict = dict.fromkeys(input_block_count.keys())

# run detection algorithm
frame_time = dict()  # Time measurement

# Read median background
medianFrame = cv.imread('my_lib/background.jpg')

# Iterate over every photo mentioned in input.json
for img_name, mentioned_blocks in input_block_count.items():

    # #TODO remve after tests!!!!
    # if img_name != 'img_009':
    #     continue


    # Read image
    img = cv.imread(f'{img_dir}/{img_name}.jpg')

    time_start = time.time()  # Time measurement
    objects = detectors.ExtractObjectsFormFrame(img_name, img, medianFrame)
    time_extract = time.time()  # Time measurement

    for obj in objects:
        circles, test = detectors.AdaptiveHoughCirlces(obj.img)
        circle_count = len(circles[0, :])
        obj.n_holes = circle_count
        obj.holes = circles[0, :]

        detected_blocks, colour_masks = detectors.CountColouredBlocks(obj.img)
        obj.blocks = detected_blocks
        obj.colour_masks = colour_masks

    time_describe = time.time()  # Time measurement

    # Assign objects from input json to detected objects
    confirmed_matches = sorters.Assign(img_name, mentioned_blocks, objects)

    time_assign = time.time()

    frame_time[img_name] = (time_extract - time_start,
                            time_describe - time_extract,
                            time_assign - time_describe)  # Time measurement

    # update_output_dict
    sorted_hole_count = []
    if confirmed_matches is None:
        print(f'Zeroes for objects in {img_name}!')
        for i in range(len(mentioned_blocks)):
            sorted_hole_count.append(0)    # TODO replace with something sensible
    else:
        for match in confirmed_matches:
            sorted_hole_count.append(objects[match].n_holes)

    output_dict[img_name] = sorted_hole_count
    print(f'Finnished processing {img_name}.jpg!')

    # TODO remove after tests
    for obj in objects:
        scale = 1/2
        temp = obj.img.copy()
        for i in obj.holes:
            # draw the outer circle
            cv.circle(temp, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv.circle(temp, (i[0], i[1]), 2, (0, 255, 0), 3)

        text = "Number of Circular Blobs: " + str(len(obj.holes))
        cv.putText(temp, text, (20, 30),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 255), 2)
        temp = cv.resize(temp, (0, 0), fx=scale, fy=scale)
        cv.imshow('test', temp)
        print(f'Description: {mentioned_blocks[obj.description]} \nHoles: {obj.n_holes}')
        cv.waitKey(0)

# write output json
with open(output_dir, 'w+') as file:
    output = json.dump(output_dict, file, indent=4)

with open('time_log.json', 'w+') as file:
    output = json.dump(frame_time, file, indent=4)
