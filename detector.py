import sys
import os
import cv2 as cv
import numpy as np
import json

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


# write output json
