import cv2 as cv
import numpy as np
from enum import Enum


class GroupOfBlocks:
    def __init__(self, origin, img, bbox, window):
        self.origin = origin
        self.img = img
        self.bbox = bbox
        self.window = window
        self.n_holes = None
        self.blocks = None
        self.place_in_order = None


class Colours(Enum):
    red = 0
    blue = 1
    white = 2
    grey = 3
    yellow = 4
