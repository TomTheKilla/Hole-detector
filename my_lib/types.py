import cv2 as cv
import numpy as np
from enum import Enum


class Colours(Enum):
    red = 0
    blue = 1
    white = 2
    grey = 3
    yellow = 4


class GroupOfBlocks:
    def __init__(self, origin, img, bbox, window, total_area):
        self.origin = origin
        self.img = img
        self.bbox = bbox
        self.window = window
        self.total_area = total_area
        self.n_holes = None
        self.blocks = None
        self.description = None
        self.colour_masks = None

    def ColourArea(self, colour):
        hist = cv.calcHist([self.colour_masks[colour.value]], [0], None, [256], (0, 256), accumulate=False)
        colour_area = hist[255, 0]
        return colour_area
