import numpy as np
import cv2 as cv
from my_lib.types import GroupOfBlocks

# Color definitions
blue_min = np.array([106, 84, 0], np.uint8)
blue_max = np.array([122, 255, 255], np.uint8)

yellow_min = np.array([20, 69, 167], np.uint8)
yellow_max = np.array([63, 255, 255], np.uint8)

red_min = np.array([0, 47, 0], np.uint8)
red_max = np.array([13, 255, 255], np.uint8)

gray_min = np.array([45, 3, 0], np.uint8)
gray_max = np.array([105, 32, 141], np.uint8)

white_min = np.array([38, 6, 181], np.uint8)
white_max = np.array([80, 45, 228], np.uint8)


def ExtractObjectsFormFrame(img_name, test_img, medianFrame):
    foreground = cv.absdiff(test_img, medianFrame)

    gray_f = cv.cvtColor(foreground, cv.COLOR_BGR2GRAY)
    gray_f_blur = cv.GaussianBlur(gray_f, (3, 3), cv.BORDER_DEFAULT)
    ret, thresh = cv.threshold(gray_f_blur, 10, 255, cv.THRESH_BINARY)
    kernel = np.ones((3, 3), np.uint8)
    # morph = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=1)
    morph = cv.dilate(thresh, kernel, iterations=4)
    # canny?
    contours, hierarchy = cv.findContours(morph, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    mask = np.zeros(test_img.shape[:2])
    extracted_objects = []
    for cont in contours:
        if cv.contourArea(cont) >= 30000:
            
            shape = mask.copy()
            temp = test_img.copy()
            # cv.drawContours(shape, [cont], -1, (255), cv.FILLED)

            contours_poly = cv.approxPolyDP(cont, 3, True)

            # Generate straight bbox and use it to cut the object out of the test_image
            window = cv.boundingRect(contours_poly)

            # Find rotated bbox to remove any potential fragments form other blocks
            bbox = cv.minAreaRect(cont)
            box = cv.boxPoints(bbox)
            box = np.intp(box)
            cv.drawContours(shape, [box], 0, (255), cv.FILLED)

            # Mask unnecessary parts of the image
            temp[shape == 0] = (0, 0, 0)

            # Cut object form test_img with removed background
            cut_object = temp[(window[1]):(window[1] + window[3]),
                         int(window[0]):int(window[0] + window[2]), :]

            obj = GroupOfBlocks(img_name, cut_object, box, window)
            extracted_objects.append(obj)
    return extracted_objects


def SimpleHoughCircles(img):
    img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
    circles = cv.HoughCircles(img, cv.HOUGH_GRADIENT, 1, 75,
                              param1=16, param2=30, minRadius=14, maxRadius=29)
    if circles is not None:
        circles = np.uint16(np.around(circles))

        temp = img.copy()
        for i in circles[0, :]:
            # draw the outer circle
            cv.circle(temp, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv.circle(temp, (i[0], i[1]), 2, (0, 255, 0), 3)
        return circles, temp
    else:
        return None


def CountColouredBlocks(img):
    img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    colour_masks = [cv.inRange(img, red_min, red_max),
                    cv.inRange(img, blue_min, blue_max),
                    cv.inRange(img, white_min, white_max),
                    cv.inRange(img, gray_min, gray_max),
                    cv.inRange(img, yellow_min, yellow_max)]

    colours = []
    for colour in colour_masks:
        hist = cv.calcHist([colour], [0], None, [256], (0, 256), accumulate=False)

        if hist[255, 0] > 7500.0:

            kernel = np.ones((3, 3), np.uint8)
            morph = cv.morphologyEx(colour, cv.MORPH_OPEN, kernel, iterations=0)
            contours, hierarchy = cv.findContours(morph, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
            cont_count = 0
            for cont in contours:
                area = cv.contourArea(cont)
                if 5000 <= area < 150000:
                    cv.drawContours(colour, [cont], -1, (127), cv.FILLED)
                    cont_count += 1
                elif area > 150000:
                    cv.drawContours(colour, [cont], -1, (127), cv.FILLED)
                    cont_count += 2

            # bw = cv.resize(colour, (0, 0), fx=1/2, fy=1/2)
            # cv.imshow('test2', bw)
            # cv.waitKey(0)

            colours.append(cont_count)
        else:
            colours.append(0)

    blocks = {
        'red': colours[0],
        'blue': colours[1],
        'white': colours[2],
        'grey': colours[3],
        'yellow': colours[4],
    }
    return blocks
