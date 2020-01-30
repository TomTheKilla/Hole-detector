import numpy as np
import cv2 as cv


def ExtractObjectsFormFrame(test_img, medianFrame):
    foreground = cv.absdiff(test_img, medianFrame)
    # out = cv.resize(foreground, (0,0), fx=1/8, fy=1/8)
    # cv.imshow('foreground', out)

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
            cut_object = temp[(window[1]):(window[1] + window[3]), \
                         int(window[0]):int(window[0] + window[2]), :]

            extracted_objects.append(cut_object)

    return extracted_objects
